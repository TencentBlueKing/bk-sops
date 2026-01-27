import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from django_celery_beat.models import PeriodicTask as DjangoCeleryBeatPeriodicTask

from gcloud.clocked_task.models import ClockedTask
from gcloud.constants import CLOCKED_TASK_NOT_STARTED
from gcloud.periodictask.models import PeriodicTask

logger = logging.getLogger("root")


class Command(BaseCommand):
    help = "关闭开启状态的周期任务和未执行的计划任务"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="模拟运行，不实际执行关闭操作",
        )
        parser.add_argument(
            "--project-id",
            type=int,
            dest="project_id",
            help="指定项目ID，只关闭该项目的任务",
        )

    def _close_periodic_tasks(self, dry_run, project_id):
        """关闭周期任务"""
        self.stdout.write("\n=== 处理周期任务 ===")

        tasks = PeriodicTask.objects.filter(task__celery_task__enabled=True)
        if project_id:
            tasks = tasks.filter(project_id=project_id)

        task_count = tasks.count()
        self.stdout.write(f"找到 {task_count} 个开启状态的周期任务")

        if task_count == 0:
            self.stdout.write("没有需要关闭的周期任务")
            return

        if dry_run:
            self.stdout.write(f"[模拟] 将关闭 {task_count} 个周期任务")
            return

        # 批量关闭操作
        with transaction.atomic():
            try:
                # 批量关闭所有周期任务
                # 使用Django查询语法获取celery_task的ID
                clocked_task_ids = list(tasks.values_list("task__celery_task__id", flat=True))
                closed_count = DjangoCeleryBeatPeriodicTask.objects.filter(id__in=clocked_task_ids).update(
                    enabled=False
                )
                self.stdout.write(f"成功关闭 {closed_count} 个周期任务")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ 批量关闭周期任务失败: {e}"))
                logger.error(f"批量关闭周期任务失败: {e}")

    def _close_clocked_tasks(self, dry_run, project_id):
        """关闭未执行的计划任务"""
        self.stdout.write("\n=== 处理计划任务 ===")

        # 查询未执行的计划任务（状态为未开始）
        tasks = ClockedTask.objects.filter(state=CLOCKED_TASK_NOT_STARTED)
        if project_id:
            tasks = tasks.filter(project_id=project_id)

        task_count = tasks.count()
        self.stdout.write(f"找到 {task_count} 个未执行的计划任务")

        if task_count == 0:
            self.stdout.write("没有需要关闭的计划任务")
            return

        if dry_run:
            self.stdout.write(f"[模拟] 将关闭 {task_count} 个计划任务")
            return

        # 批量关闭操作
        with transaction.atomic():
            try:
                # 获取所有需要关闭的clocked_task_id
                clocked_task_ids = list(tasks.values_list("clocked_task_id", flat=True))

                if clocked_task_ids:
                    # 批量更新django_celery_beat的PeriodicTask状态
                    updated_count = DjangoCeleryBeatPeriodicTask.objects.filter(id__in=clocked_task_ids).update(
                        enabled=False
                    )
                    self.stdout.write(f"成功批量关闭 {updated_count} 个计划任务")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ 批量关闭计划任务失败: {e}"))
                logger.error(f"批量关闭计划任务失败: {e}")

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        project_id = options.get("project_id")

        self.stdout.write("开始执行任务关闭操作...")

        if dry_run:
            self.stdout.write("=== 模拟运行模式 ===")

        # 关闭周期任务
        self._close_periodic_tasks(dry_run, project_id)
        # 关闭计划任务
        self._close_clocked_tasks(dry_run, project_id)

        self.stdout.write(self.style.SUCCESS("任务关闭操作完成"))
