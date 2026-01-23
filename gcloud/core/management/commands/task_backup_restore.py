import json
import logging
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django_celery_beat.models import PeriodicTask as DjangoCeleryBeatPeriodicTask

from gcloud.clocked_task.models import ClockedTask
from gcloud.constants import CLOCKED_TASK_NOT_STARTED
from gcloud.core.models import Project
from gcloud.periodictask.models import PeriodicTask

logger = logging.getLogger("root")


class Command(BaseCommand):
    help = "批量导出导入周期任务和计划任务：支持根据业务ID导出开启的任务并关闭，以及导入恢复任务"

    def add_arguments(self, parser):
        parser.add_argument("--export", action="store_true", dest="export", help="导出模式：找出指定业务中开启的周期任务和未执行的计划任务，导出并关闭")
        parser.add_argument("--import", action="store_true", dest="import", help="导入模式：根据导出的文件恢复对应的周期任务和计划任务")
        parser.add_argument("--business-ids", type=str, dest="business_ids", help="业务ID列表，多个用逗号分隔，如：1,2,3")
        parser.add_argument("--file", type=str, dest="file_path", help="导出文件路径（导出时自动生成，导入时需指定）")
        parser.add_argument("--dry-run", action="store_true", dest="dry_run", help="模拟运行，不实际执行操作")

    def _export_tasks(self, business_ids, file_path=None, dry_run=False):
        """导出任务到文件"""
        self.stdout.write("=== 开始导出任务 ===")

        # 获取任务数据
        periodic_task = PeriodicTask.objects.filter(task__celery_task__enabled=True, project_id__in=business_ids)
        clocked_task = ClockedTask.objects.filter(state=CLOCKED_TASK_NOT_STARTED, project_id__in=business_ids)

        if not periodic_task and not clocked_task:
            self.stdout.write("没有找到需要导出的任务")
            return None

        periodic_task_ids = list(periodic_task.values_list("id", flat=True))
        clocked_task_ids = list(clocked_task.values_list("clocked_task_id", flat=True))

        # 构建导出数据
        export_data = {
            "export_time": datetime.now().isoformat(),
            "periodic_task_ids": periodic_task_ids,
            "clocked_task_ids": clocked_task_ids,
        }

        # 生成文件路径
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"task_export_{timestamp}.json"

        if dry_run:
            self.stdout.write(f"[模拟] 将导出数据到文件: {file_path}")
            return file_path

        # 写入文件
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            with transaction.atomic():
                # 关闭周期任务
                for task in periodic_task:
                    try:
                        task.set_enabled(False)
                        self.stdout.write(f"✓ 已关闭周期任务: ID={task.id}, 名称={task.name}")
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"关闭周期任务失败: ID={task.id}, 错误={e}"))
                # 关闭计划任务
                DjangoCeleryBeatPeriodicTask.objects.filter(id__in=clocked_task_ids).update(enabled=False)

            self.stdout.write(f"✓ 任务数据已导出到: {file_path}")
            self.stdout.write(f"✓ 周期任务: {len(periodic_task_ids)} 个")
            self.stdout.write(f"✓ 计划任务: {len(clocked_task_ids)} 个")

            return file_path
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"导出文件失败: {e}"))
            return None

    def _import_tasks(self, file_path, dry_run=False):
        """从文件导入任务"""
        self.stdout.write("=== 开始导入任务 ===")

        if not file_path or not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"文件不存在: {file_path}"))
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"读取导入文件失败: {e}"))
            return False

        # 验证导入数据格式
        required_fields = ["periodic_task_ids", "clocked_task_ids"]
        for field in required_fields:
            if field not in import_data:
                self.stdout.write(self.style.ERROR(f"导入文件格式错误: 缺少 {field} 字段"))
                return False

        periodic_task_ids = import_data.get("periodic_task_ids", [])
        clocked_task_ids = import_data.get("clocked_task_ids", [])

        # 启用任务
        with transaction.atomic():
            tasks = PeriodicTask.objects.filter(id__in=periodic_task_ids)
            for task in tasks:
                try:
                    task.set_enabled(True)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"启用周期任务失败: ID={task.id}, 错误={e}"))
            date_time = datetime.now()
            future_clocked_task_ids = list(
                ClockedTask.objects.filter(plan_start_time__gt=date_time).values_list("clocked_task_id", flat=True)
            )
            valid_clocked_task_ids = [task_id for task_id in clocked_task_ids if task_id in future_clocked_task_ids]

            if valid_clocked_task_ids:
                DjangoCeleryBeatPeriodicTask.objects.filter(id__in=valid_clocked_task_ids).update(enabled=True)
            else:
                self.stdout.write("没有找到符合条件的计划任务")

    def handle(self, *args, **options):
        export_mode = options["export"]
        import_mode = options["import"]
        business_ids_str = options.get("business_ids")
        file_path = options.get("file_path")
        dry_run = options.get("dry_run", False)

        # 验证参数
        if not export_mode and not import_mode:
            self.stdout.write(self.style.ERROR("必须指定 --export 或 --import 模式"))
            return

        if export_mode and import_mode:
            self.stdout.write(self.style.ERROR("不能同时使用 --export 和 --import"))
            return

        if export_mode and not business_ids_str:
            self.stdout.write(self.style.ERROR("导出模式必须指定 --business-ids"))
            return

        if import_mode and not file_path:
            self.stdout.write(self.style.ERROR("导入模式必须指定 --file"))
            return

        if export_mode:
            # 解析业务ID
            business_ids_list = [int(biz_id.strip()) for biz_id in business_ids_str.split(",") if biz_id.strip()]
            business_ids = list(Project.objects.filter(bk_biz_id__in=business_ids_list).values_list("id", flat=True))

            self.stdout.write("开始执行任务导出操作...")
            self.stdout.write(f"业务ID: {business_ids}")
            self.stdout.write(f"文件路径: {file_path or '自动生成'}")

            if dry_run:
                self.stdout.write("=== 模拟运行模式 ===")
            # 导出任务
            self._export_tasks(business_ids, file_path, dry_run)

        elif import_mode:
            self.stdout.write("开始执行任务导入操作...")
            self.stdout.write(f"导入文件: {file_path}")

            if dry_run:
                self.stdout.write("=== 模拟运行模式 ===")

            # 导入任务
            self._import_tasks(file_path, dry_run)
            self.stdout.write(self.style.SUCCESS("任务导入操作完成"))
