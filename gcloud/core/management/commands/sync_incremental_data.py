# -*- coding: utf-8 -*-
"""
数据库增量同步工具：基于ID记录的增量数据同步
"""
import json
import os
import time

import pymysql
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from gcloud.core.models import EnvironmentVariables

# 导入数据库配置文件
try:
    from . import sync_config
except ImportError:
    # 如果sync_config不存在，使用默认配置
    sync_config = None


class Command(BaseCommand):
    help = "数据库增量同步工具：基于ID记录的增量数据同步"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="只检查不实际同步")
        parser.add_argument("--batch-size", type=int, default=100, help="每次同步的记录数")

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        dry_run = options["dry_run"]

        lock_key = "sync_incremental_data_lock"
        # 加锁，防止同时多次执行，超时时间设置为1小时
        # 增加重试逻辑，最多重试6次，每次间隔10秒
        max_retries = int(os.getenv("MAX_RETRIES", 6))
        retry_interval = int(os.getenv("RETRY_INTERVAL", 10))
        lock_acquired = False

        for attempt in range(max_retries):
            if settings.redis_inst.set(lock_key, 1, nx=True, ex=3600):
                lock_acquired = True
                break
            self.stdout.write(self.style.WARNING(f"尝试获取锁失败，等待 {retry_interval} 秒后重试 ({attempt + 1}/{max_retries})..."))
            time.sleep(retry_interval)

        if not lock_acquired:
            return

        try:
            self.stdout.write("开始增量同步任务...")
            if dry_run:
                self.stdout.write("*** 干运行模式：只检查不实际同步 ***")

            if sync_config is None or not sync_config.SOURCE_DB_CONFIG.get("database"):
                self.stdout.write(self.style.ERROR("请检查源环境数据库配置"))
                return

            try:
                # 在同步开始前全局禁用外键约束
                with connection.cursor() as cursor:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                # 连接源数据库
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
                    self.stdout.write("数据库连接成功")
                except Exception as e:
                    raise ValueError(f"数据库连接失败: {str(e)}")

                self.sync_data(source_conn, batch_size, dry_run)
                # 关闭数据库连接
                source_conn.close()

                self.stdout.write(self.style.SUCCESS("增量同步任务完成！"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"同步失败: {str(e)}"))
                raise
            finally:
                # 同步结束后重新启用外键约束
                with connection.cursor() as cursor:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        finally:
            # 处理完成删除锁
            settings.redis_inst.delete(lock_key)

    def sync_data(self, source_conn, batch_size, dry_run):
        """执行增量数据同步 - 按分类同步，每个分类完成后立即更新数据库状态"""

        # 定义分类配置
        model_categories = [
            "celery_model_status",
            "pipeline_models_status",
            "taskflow_models_status",
            "eri_models_status",
            "business_models_status",
        ]

        # 按分类进行同步
        for category_name in model_categories:
            self.stdout.write(f"=== 处理分类: {category_name} ===")

            # 加载该分类的同步配置
            category_config = self.load_category_config_from_db(category_name)
            if not category_config:
                self.stdout.write(self.style.WARNING(f"分类 {category_name} 没有同步配置，跳过"))
                continue

            # 同步该分类下的所有模型
            category_updated = False
            updated_config = category_config.copy()

            for table_name in updated_config.keys():
                last_id = category_config.get(table_name, 0)
                # 同步表并获取同步过程中达到的最大ID
                new_max_id = self.sync_table(source_conn, table_name, batch_size, last_id, dry_run)

                # 如果表有更新，记录新的最大ID
                if not dry_run and new_max_id > last_id:
                    updated_config[table_name] = new_max_id
                    category_updated = True

            # 更新该分类的同步状态
            if category_updated and not dry_run:
                self.update_category_status_in_db(category_name, updated_config)
                self.stdout.write(f"分类 {category_name} 同步完成并已更新数据库状态")
            else:
                self.stdout.write(f"分类 {category_name} 同步完成")

    def sync_table(self, source_conn, table_name, batch_size, last_id, dry_run):
        """同步单个表的数据，返回同步过程中达到的最大ID（如果没有新数据返回last_id）"""
        self.stdout.write(f"同步表: {table_name}")

        sort_field = self.get_sort_field(table_name)
        # 查询需要同步的数据
        query = f"SELECT * FROM {table_name} WHERE {sort_field} > %s ORDER BY {sort_field} ASC LIMIT %s"
        try:
            with source_conn.cursor() as cursor:
                cursor.execute(query, (last_id, batch_size))
                results = cursor.fetchall()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"查询表 {table_name} 失败: {str(e)}"))
            return last_id

        if not results:
            self.stdout.write(f"表 {table_name} 没有新数据需要同步")
            return last_id

        # 同步数据
        max_id = last_id

        success_count = self.batch_save_records(table_name, results, dry_run)

        if success_count > 0:
            last_record_value = results[-1].get(sort_field, 0)
            if last_record_value > max_id:
                max_id = last_record_value

        if not dry_run and max_id > last_id:
            self.stdout.write(f"表 {table_name} 同步完成：{success_count}/{len(results)} 条数据，最后{sort_field}: {max_id}")
            return max_id
        else:
            self.stdout.write(f"表 {table_name} 同步完成：{success_count}/{len(results)} 条数据")
            return last_id

    def load_category_config_from_db(self, category_key):
        """从数据库加载指定分类的同步配置"""
        try:
            env_var = EnvironmentVariables.objects.filter(key=category_key).first()
            if env_var:
                config_data = json.loads(env_var.value)
                self.stdout.write(f"加载分类配置: {category_key} - {len(config_data)} 个模型")
                return config_data
            else:
                self.stdout.write(self.style.WARNING(f"未找到分类配置: {category_key}"))
                return {}
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"加载分类配置 {category_key} 失败: {str(e)}"))
            return {}

    def update_category_status_in_db(self, category_name, config_data):
        """更新数据库中指定分类的同步状态"""
        try:
            env_var = EnvironmentVariables.objects.filter(key=category_name).first()
            if env_var:
                env_var.value = json.dumps(config_data, ensure_ascii=False, indent=2)
                env_var.save()
                self.stdout.write(f"更新分类状态: {category_name}")
            else:
                # 如果不存在则创建
                EnvironmentVariables.objects.create(
                    key=category_name,
                    name=f"{category_name} 最大ID数据",
                    value=json.dumps(config_data, ensure_ascii=False, indent=2),
                )
                self.stdout.write(f"创建分类状态: {category_name}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"更新分类状态 {category_name} 失败: {str(e)}"))

    def get_sort_field(self, table_name):
        """根据表名获取排序字段"""
        # 对于重试表和超时表，使用关联的任务ID进行排序，保持数据一致性
        if table_name == "taskflow3_autoretrynodestrategy":
            return "taskflow_id"
        elif table_name == "taskflow3_timeoutnodeconfig":
            return "task_id"
        else:
            return "id"

    def batch_save_records(self, table_name, results, dry_run):
        """批量保存记录（完全跳过外键约束版本）"""
        if not results:
            return 0

        try:
            processed_results = []
            for data in results:
                valid_data = data.copy()
                # 特殊字段处理
                if "enabled" in valid_data and table_name == "django_celery_beat_periodictask":
                    valid_data["enabled"] = 0

                # 特殊处理：为template_commontemplate表添加tenant_id默认值
                if table_name == "template_commontemplate" and "tenant_id" not in valid_data:
                    valid_data["tenant_id"] = sync_config.TENANT_CONFIG.get("tenant_id", "tencent")

                # 特殊处理：为clocked_task_clockedtask表添加timezone默认值
                if table_name == "clocked_task_clockedtask" and "timezone" not in valid_data:
                    valid_data["timezone"] = "Asia/Shanghai"

                processed_results.append(valid_data)

            if dry_run:
                self.stdout.write(f"[运行] 将批量同步 {len(processed_results)} 条记录到表: {table_name}")
                return len(processed_results)

            # 假设所有记录的字段相同，取第一条记录的字段作为列名
            first_record = processed_results[0]
            columns = ", ".join([f"`{field}`" for field in first_record.keys()])
            placeholders = ", ".join(["%s"] * len(first_record))

            sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"

            # 提取所有记录的值，注意顺序必须与first_record.keys()一致
            keys = list(first_record.keys())
            values_list = [tuple(record[k] for k in keys) for record in processed_results]

            with connection.cursor() as cursor:
                cursor.executemany(sql, values_list)
            return len(processed_results)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"批量同步记录失败 {table_name}: {str(e)}"))
            return 0
