import logging

from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask as DjangoCeleryBeatPeriodicTask

from gcloud.clocked_task.models import ClockedTask
from gcloud.constants import CLOCKED_TASK_NOT_STARTED
from gcloud.core.models import Project
from gcloud.periodictask.models import PeriodicTask

logger = logging.getLogger("root")


class Command(BaseCommand):
    help = "检测周期任务和计划任务状态，支持检测全部关闭或全部启动，可指定业务范围"

    def add_arguments(self, parser):
        parser.add_argument(
            "--check-type",
            type=str,
            choices=["all_closed", "all_success"],
            default="all_closed",
            help="检测类型：all_closed(全部关闭) 或 all_success(全部启动)，默认为all_closed",
        )
        parser.add_argument(
            "--business-ids",
            type=str,
            dest="business_ids",
            help="业务ID列表，多个用逗号分隔，如：1,2,3。不指定则检测所有业务",
        )

    def _check_periodic_tasks(self, check_type, business_ids=None):
        """检测周期任务状态"""
        self.stdout.write("\n=== 检测周期任务状态 ===")

        # 构建查询条件
        query = {}
        if business_ids:
            query["project_id__in"] = business_ids

        if check_type == "all_closed":
            # 检测是否全部关闭：查找所有开启的任务
            query["task__celery_task__enabled"] = True
            tasks = PeriodicTask.objects.filter(**query)
            task_count = tasks.count()

            if task_count == 0:
                self.stdout.write("✓ 所有周期任务已关闭")
                return True
            else:
                self.stdout.write(f"✗ 发现 {task_count} 个开启的周期任务")
                return False

        elif check_type == "all_success":
            # 检测是否全部开启：查找所有关闭的任务
            query["task__celery_task__enabled"] = False
            tasks = PeriodicTask.objects.filter(**query)
            task_count = tasks.count()

            if task_count == 0:
                self.stdout.write("✓ 所有周期任务已开启")
                return True
            else:
                self.stdout.write(f"✗ 发现 {task_count} 个关闭的周期任务")
                return False

    def _check_clocked_tasks(self, check_type, business_ids=None):
        """检测计划任务状态"""
        self.stdout.write("\n=== 检测计划任务状态 ===")

        # 构建查询条件
        query = {}
        query["state"] = CLOCKED_TASK_NOT_STARTED
        if business_ids:
            query["project_id__in"] = business_ids

        tasks = ClockedTask.objects.filter(**query)
        clocked_task_ids = tasks.values_list("clocked_task_id", flat=True)

        if check_type == "all_closed":
            # 检测是否全部关闭
            task_count = DjangoCeleryBeatPeriodicTask.objects.filter(id__in=clocked_task_ids, enabled=True).count()

            if task_count == 0:
                self.stdout.write("计划任务已关闭")
                return True
            else:
                self.stdout.write(f"发现 {task_count} 个未关闭的计划任务")
                return False

        elif check_type == "all_success":
            # 检测是否全部启动
            task_count = DjangoCeleryBeatPeriodicTask.objects.filter(id__in=clocked_task_ids, enabled=False).count()

            if task_count == 0:
                self.stdout.write("计划任务已启动")
                return True
            else:
                self.stdout.write(f"发现 {task_count} 个未启动的计划任务")
                return False

    def handle(self, *args, **options):
        check_type = options["check_type"]
        business_ids_str = options.get("business_ids")

        self.stdout.write("开始执行任务状态检测...")
        self.stdout.write(f"检测类型: {check_type}")

        # 解析业务ID
        business_ids = None
        if business_ids_str:
            business_ids_list = [int(biz_id.strip()) for biz_id in business_ids_str.split(",") if biz_id.strip()]
            business_ids = list(Project.objects.filter(bk_biz_id__in=business_ids_list).values_list("id", flat=True))
            self.stdout.write(f"指定业务ID: {business_ids_list}")
        else:
            self.stdout.write("检测范围: 所有业务")

        # 检测周期任务
        periodic_result = self._check_periodic_tasks(check_type, business_ids)

        # 检测计划任务
        clocked_result = self._check_clocked_tasks(check_type, business_ids)

        # 汇总结果
        self.stdout.write("\n=== 检测结果汇总 ===")

        if check_type == "all_closed":
            if periodic_result and clocked_result:
                self.stdout.write(self.style.SUCCESS("✓ 所有任务已关闭"))
            else:
                self.stdout.write(self.style.ERROR("✗ 存在未关闭的任务"))

        elif check_type == "all_success":
            if periodic_result and clocked_result:
                self.stdout.write(self.style.SUCCESS("✓ 所有任务已启动"))
            else:
                self.stdout.write(self.style.ERROR("✗ 存在未启动的任务"))

        self.stdout.write("任务状态检测完成")
