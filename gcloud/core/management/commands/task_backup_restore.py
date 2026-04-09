import logging

import pymysql
from django.core.management.base import BaseCommand
from django.db import transaction
from django_celery_beat.models import PeriodicTask as DjangoCeleryBeatPeriodicTask
from pipeline.contrib.periodic_task.models import PeriodicTask as PipelinePeriodicTask

from gcloud.clocked_task.models import ClockedTask
from gcloud.constants import CLOCKED_TASK_NOT_STARTED
from gcloud.core.management.commands.sync_config import SOURCE_DB_CONFIG
from gcloud.core.models import Project
from gcloud.periodictask.models import PeriodicTask

logger = logging.getLogger("root")


class Command(BaseCommand):
    help = "通过直连源数据库，关闭指定业务下的符合条件的周期任务和计划任务，并在当前环境开启"

    def add_arguments(self, parser):
        parser.add_argument(
            "--business-ids", type=str, dest="business_ids", required=True, help="业务ID列表，多个用逗号分隔，如：1,2,3"
        )
        parser.add_argument("--dry-run", action="store_true", dest="dry_run", help="模拟运行，不实际执行操作")

    def handle(self, *args, **options):
        business_ids_str = options.get("business_ids")
        dry_run = options.get("dry_run", False)

        source_host = SOURCE_DB_CONFIG.get("host")
        source_port = int(SOURCE_DB_CONFIG.get("port", 3306))
        source_user = SOURCE_DB_CONFIG.get("user")
        source_password = SOURCE_DB_CONFIG.get("password")
        source_db = SOURCE_DB_CONFIG.get("database")

        if not all([source_host, source_user, source_password, source_db]):
            self.stdout.write(self.style.ERROR("源数据库配置不完整，请检查"))
            return

        business_ids_list = [int(biz_id.strip()) for biz_id in business_ids_str.split(",") if biz_id.strip()]
        if not business_ids_list:
            self.stdout.write(self.style.ERROR("业务ID列表不能为空"))
            return

        pt_table = PeriodicTask._meta.db_table
        ppt_table = PipelinePeriodicTask._meta.db_table
        dcbpt_table = DjangoCeleryBeatPeriodicTask._meta.db_table
        ct_table = ClockedTask._meta.db_table
        project_table = Project._meta.db_table

        self.stdout.write("=== 开始连接源数据库 ===")
        try:
            conn = pymysql.connect(
                host=source_host,
                port=source_port,
                user=source_user,
                password=source_password,
                database=source_db,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"连接源数据库失败: {e}"))
            return

        try:
            with conn.cursor() as cursor:
                # 1. 获取 project_ids
                format_strings = ",".join(["%s"] * len(business_ids_list))
                cursor.execute(
                    f"SELECT id FROM {project_table} WHERE bk_biz_id IN ({format_strings})", tuple(business_ids_list)
                )
                project_ids = [row["id"] for row in cursor.fetchall()]

                if not project_ids:
                    self.stdout.write(self.style.WARNING("在源数据库中未找到对应的项目"))
                    return

                # 2. 获取周期任务
                format_strings = ",".join(["%s"] * len(project_ids))
                sql = f"""
                    SELECT pt.id as pt_id, ppt.celery_task_id 
                    FROM {pt_table} pt
                    JOIN {ppt_table} ppt ON pt.task_id = ppt.id
                    JOIN {dcbpt_table} dcbpt ON ppt.celery_task_id = dcbpt.id
                    WHERE pt.project_id IN ({format_strings}) AND dcbpt.enabled = 1
                """
                cursor.execute(sql, tuple(project_ids))
                periodic_tasks = cursor.fetchall()
                periodic_task_ids = [row["pt_id"] for row in periodic_tasks]

                # 3. 获取计划任务
                sql = f"""
                    SELECT ct.clocked_task_id 
                    FROM {ct_table} ct
                    WHERE ct.project_id IN ({format_strings}) AND ct.state = '{CLOCKED_TASK_NOT_STARTED}'
                """
                cursor.execute(sql, tuple(project_ids))
                clocked_tasks = cursor.fetchall()
                clocked_task_ids = [row["clocked_task_id"] for row in clocked_tasks]

                valid_periodic_task_ids = []
                if periodic_task_ids:
                    valid_periodic_task_ids = list(
                        PeriodicTask.objects.filter(id__in=periodic_task_ids).values_list("id", flat=True)
                    )
                    if len(valid_periodic_task_ids) != len(periodic_task_ids):
                        self.stdout.write(self.style.ERROR("周期任务数量不一致，请先确保数据已完全同步。"))
                        return

                valid_clocked_task_ids = []
                if clocked_task_ids:
                    valid_clocked_task_ids = list(
                        ClockedTask.objects.filter(clocked_task_id__in=clocked_task_ids).values_list(
                            "clocked_task_id", flat=True
                        )
                    )
                    if len(valid_clocked_task_ids) != len(clocked_task_ids):
                        self.stdout.write(self.style.ERROR("计划任务数量不一致，请先确保数据已完全同步。"))
                        return

                # 过滤出真正需要关闭的 celery_task_ids
                valid_celery_task_ids = [
                    row["celery_task_id"] for row in periodic_tasks if row["pt_id"] in valid_periodic_task_ids
                ] + valid_clocked_task_ids

                if dry_run:
                    self.stdout.write("=== 模拟运行模式，不执行数据库修改 ===")
                    return

            # 4. 在源数据库中关闭任务
            try:
                conn.begin()
                if valid_celery_task_ids:
                    with conn.cursor() as cursor:
                        format_strings = ",".join(["%s"] * len(valid_celery_task_ids))
                        update_sql = f"UPDATE {dcbpt_table} SET enabled = 0 WHERE id IN ({format_strings})"
                        cursor.execute(update_sql, tuple(valid_celery_task_ids))
                conn.commit()
                if valid_celery_task_ids:
                    self.stdout.write(self.style.SUCCESS(f"✓ 在源数据库中关闭了 {len(valid_celery_task_ids)} 个 celery 任务"))
            except Exception as e:
                conn.rollback()
                raise Exception(f"源数据库更新失败: {e}")

            # 5. 在目标数据库中开启任务
            self.stdout.write("=== 开始在当前环境开启任务 ===")
            try:
                with transaction.atomic():
                    if valid_periodic_task_ids:
                        tasks = PeriodicTask.objects.filter(id__in=valid_periodic_task_ids)
                        for task in tasks:
                            task.set_enabled(True)
                            self.stdout.write(f"✓ 已开启周期任务: ID={task.id}, 名称={task.name}")

                    if valid_clocked_task_ids:
                        DjangoCeleryBeatPeriodicTask.objects.filter(id__in=valid_clocked_task_ids).update(enabled=True)
                        self.stdout.write(f"✓ 已开启计划任务: {len(valid_clocked_task_ids)} 个")

                self.stdout.write(self.style.SUCCESS("任务处理完成"))
            except Exception as e:
                # 发生异常时，Django 事务会自动回滚，我们需要手动回滚源数据库
                self.stdout.write(self.style.WARNING(f"当前环境操作失败，准备回滚源数据库: {e}"))
                try:
                    conn.begin()
                    if valid_celery_task_ids:
                        with conn.cursor() as cursor:
                            format_strings = ",".join(["%s"] * len(valid_celery_task_ids))
                            revert_sql = f"UPDATE {dcbpt_table} SET enabled = 1 WHERE id IN ({format_strings})"
                            cursor.execute(revert_sql, tuple(valid_celery_task_ids))
                    conn.commit()
                    self.stdout.write(self.style.SUCCESS("✓ 源数据库回滚成功"))
                except Exception as revert_e:
                    conn.rollback()
                    self.stdout.write(self.style.ERROR(f"✗ 源数据库回滚失败: {revert_e}"))
                raise e

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"操作失败: {e}"))
        finally:
            conn.close()
