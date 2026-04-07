# -*- coding: utf-8 -*-
"""
自动计算增量差额并执行同步
"""

import json

import pymysql
from django.core.management import call_command
from django.core.management.base import BaseCommand

from gcloud.core.models import EnvironmentVariables

try:
    from . import sync_config
except ImportError:
    sync_config = None


class Command(BaseCommand):
    help = "自动计算增量差额并执行同步"

    def handle(self, *args, **options):
        if sync_config is None or not sync_config.SOURCE_DB_CONFIG.get("database"):
            self.stdout.write(self.style.ERROR("请检查源环境数据库配置"))
            return

        model_categories = [
            "celery_model_status",
            "pipeline_models_status",
            "taskflow_models_status",
            "eri_models_status",
            "business_models_status",
        ]

        max_diff = 0

        try:
            source_db = sync_config.SOURCE_DB_CONFIG
            source_conn = pymysql.connect(
                host=source_db["host"],
                port=source_db["port"],
                user=source_db["user"],
                password=source_db["password"],
                database=source_db["database"],
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
            self.stdout.write("源数据库连接成功")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"数据库连接失败: {str(e)}"))
            return

        try:
            for category_name in model_categories:
                env_var = EnvironmentVariables.objects.filter(key=category_name).first()
                if not env_var:
                    self.stdout.write(self.style.WARNING(f"未找到分类配置: {category_name}"))
                    continue

                config_data = json.loads(env_var.value)
                for table_name, last_id in config_data.items():
                    sort_field = self.get_sort_field(table_name)

                    query = f"SELECT MAX({sort_field}) as max_id FROM {table_name}"
                    try:
                        with source_conn.cursor() as cursor:
                            cursor.execute(query)
                            result = cursor.fetchone()
                            source_max_id = result.get("max_id") or 0

                            diff = source_max_id - last_id
                            if diff > max_diff:
                                max_diff = diff
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"查询表 {table_name} 失败: {str(e)}"))
        finally:
            source_conn.close()

        self.stdout.write(f"计算得到数据量为: {max_diff}")

        if max_diff > 0:
            self.stdout.write(f"开始执行 sync_incremental_data --batch-size {max_diff}")
            call_command("sync_incremental_data", batch_size=max_diff)
        else:
            self.stdout.write("没有需要同步的新数据")

    def get_sort_field(self, table_name):
        """根据表名获取排序字段"""
        if table_name == "taskflow3_autoretrynodestrategy":
            return "taskflow_id"
        elif table_name == "taskflow3_timeoutnodeconfig":
            return "task_id"
        else:
            return "id"
