# -*- coding: utf-8 -*-
"""
项目流程资源覆盖更新工具：
按业务 ID（CMDB bk_biz_id）将源环境中该业务下的项目流程（TaskTemplate）覆盖更新到当前环境。

更新范围（只更新部分字段）：
1. pipeline_pipelinetemplate:
       name, description, editor, edit_time, snapshot_id, has_subprocess, is_deleted
2. pipeline_templatecurrentversion:
       current_version
3. tasktmpl3_tasktemplate:
       category, notify_type, notify_receivers, time_out, is_deleted,
       executor_proxy, default_flow_type, ai_notify_type, ai_notify_group
"""
import pymysql
from django.core.management.base import BaseCommand
from django.db import connection, transaction

try:
    from . import sync_config
except ImportError:
    sync_config = None


PIPELINE_TEMPLATE_UPDATE_FIELDS = [
    "name",
    "description",
    "editor",
    "edit_time",
    "snapshot_id",
    "has_subprocess",
    "is_deleted",
]

TASK_TEMPLATE_UPDATE_FIELDS = [
    "executor_proxy",
    "default_flow_type",
    "category",
    "notify_type",
    "notify_receivers",
    "time_out",
    "is_deleted",
    "ai_notify_type",
    "ai_notify_group",
]


class Command(BaseCommand):
    help = "按业务 ID 覆盖更新项目流程资源（TaskTemplate）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--biz-id",
            type=int,
            required=True,
            help="CMDB 业务 ID（对应 core_project.bk_biz_id），仅更新该业务下的流程",
        )
        parser.add_argument("--dry-run", action="store_true", help="只检查不实际更新")

    def handle(self, *args, **options):
        biz_id = options["biz_id"]
        dry_run = options["dry_run"]

        self.stdout.write(f"开始更新业务 bk_biz_id={biz_id} 下的项目流程...")
        if dry_run:
            self.stdout.write("*** 干运行模式：只检查不实际更新 ***")

        if sync_config is None or not sync_config.SOURCE_DB_CONFIG.get("database"):
            self.stdout.write(self.style.ERROR("请检查源环境数据库配置"))
            return

        source_conn = None
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            # 连接源数据库
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

            self.do_update(source_conn, biz_id, dry_run)

            self.stdout.write(self.style.SUCCESS("项目流程资源覆盖更新任务完成！"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"覆盖更新失败: {str(e)}"))
            raise
        finally:
            if source_conn is not None:
                source_conn.close()
            with connection.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    # ------------------------------------------------------------------
    # 核心流程
    # ------------------------------------------------------------------
    def do_update(self, source_conn, biz_id, dry_run):
        """循环目标环境中该业务下已存在的流程，从源端拉取最新数据覆盖更新"""

        # 1. 在目标端通过 bk_biz_id 查找 project_id
        project_ids = self.fetch_local_project_ids(biz_id)
        if not project_ids:
            self.stdout.write(self.style.WARNING(f"目标端找不到 bk_biz_id={biz_id} 对应的项目"))
            return
        self.stdout.write(f"目标端找到 {len(project_ids)} 个项目: {project_ids}")

        # 2. 从目标端拉取这些项目下所有已存在的 tasktmpl3_tasktemplate
        local_task_templates = self.fetch_local_task_templates(project_ids)
        if not local_task_templates:
            self.stdout.write(self.style.WARNING(f"目标端 bk_biz_id={biz_id} 下没有任何项目流程，请先执行全量同步"))
            return
        self.stdout.write(f"目标端共找到 {len(local_task_templates)} 个项目流程，开始从源端拉取最新数据覆盖更新")

        # 3. 从源端拉取对应的 pipeline_template 和 task_template 最新数据
        pipeline_template_ids = [t["pipeline_template_id"] for t in local_task_templates]
        source_pipeline_templates = self.fetch_pipeline_templates(source_conn, pipeline_template_ids)
        source_task_templates = self.fetch_task_templates_by_pipeline_ids(source_conn, pipeline_template_ids)

        # 4. 逐条覆盖更新
        success, skipped = 0, 0
        for local_task_row in local_task_templates:
            template_id = local_task_row["pipeline_template_id"]

            source_pipeline_row = source_pipeline_templates.get(template_id)
            source_task_row = source_task_templates.get(template_id)

            if source_pipeline_row is None:
                self.stdout.write(self.style.WARNING(f"[跳过] 源端无 pipeline_template={template_id}，可能已在源端删除"))
                skipped += 1
                continue

            ok = self.update_one(local_task_row, source_pipeline_row, source_task_row, dry_run)
            if ok:
                success += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(f"处理完成：成功 {success} 个，跳过 {skipped} 个"))

    # ------------------------------------------------------------------
    # 目标端数据查询
    # ------------------------------------------------------------------
    def fetch_local_project_ids(self, bk_biz_id):
        """从目标端 core_project 表根据 bk_biz_id 查找 project_id，返回 id 列表"""
        sql = "SELECT id FROM core_project WHERE bk_biz_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(sql, (bk_biz_id,))
            return [row[0] for row in cursor.fetchall()]

    def _fetchall_dict(self, cursor):
        """将 cursor 的 tuple 结果转为 dict 列表（兼容 Django 默认游标）"""
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def fetch_local_task_templates(self, project_ids):
        """从目标端 tasktmpl3_tasktemplate 表拉取指定项目下的所有流程，返回 dict 列表"""
        if not project_ids:
            return []
        placeholders = ", ".join(["%s"] * len(project_ids))
        sql = f"SELECT * FROM tasktmpl3_tasktemplate WHERE project_id IN ({placeholders})"
        with connection.cursor() as cursor:
            cursor.execute(sql, project_ids)
            return self._fetchall_dict(cursor)

    # ------------------------------------------------------------------
    # 源端数据抓取
    # ------------------------------------------------------------------

    def fetch_task_templates_by_pipeline_ids(self, source_conn, pipeline_template_ids):
        """从源端拉取指定 pipeline_template_id 对应的 tasktmpl3_tasktemplate 记录"""
        if not pipeline_template_ids:
            return {}
        placeholders = ", ".join(["%s"] * len(pipeline_template_ids))
        sql = f"SELECT * FROM tasktmpl3_tasktemplate WHERE pipeline_template_id IN ({placeholders})"
        with source_conn.cursor() as cursor:
            cursor.execute(sql, pipeline_template_ids)
            return {row["pipeline_template_id"]: row for row in cursor.fetchall()}

    def fetch_pipeline_templates(self, source_conn, template_ids):
        if not template_ids:
            return {}
        placeholders = ", ".join(["%s"] * len(template_ids))
        sql = f"SELECT * FROM pipeline_pipelinetemplate WHERE template_id IN ({placeholders})"
        with source_conn.cursor() as cursor:
            cursor.execute(sql, template_ids)
            return {row["template_id"]: row for row in cursor.fetchall()}

    # ------------------------------------------------------------------
    # 写入目标库
    # ------------------------------------------------------------------
    def update_one(self, local_task_row, source_pipeline_row, source_task_row, dry_run):
        """用源端最新数据覆盖更新目标端记录

        :param local_task_row: 目标端已有的 tasktmpl3_tasktemplate 记录（含 id、pipeline_template_id）
        :param source_pipeline_row: 源端 pipeline_pipelinetemplate 最新记录
        :param source_task_row: 源端 tasktmpl3_tasktemplate 最新记录
        """
        template_id = local_task_row["pipeline_template_id"]
        local_task_id = local_task_row["id"]

        if dry_run:
            self.stdout.write(f"[dry-run] 将更新 template_id={template_id} (name={source_pipeline_row.get('name')})")
            return True

        try:
            with transaction.atomic():
                self._update_pipeline_template(source_pipeline_row)
                self._update_task_template(local_task_id, source_task_row)
            self.stdout.write(f"[ok] 已更新 template_id={template_id} (name={source_pipeline_row.get('name')})")
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[失败] template_id={template_id}: {str(e)}"))
            return False

    def _update_pipeline_template(self, row):
        set_clause = ", ".join([f"`{f}` = %s" for f in PIPELINE_TEMPLATE_UPDATE_FIELDS])
        values = [row.get(f) for f in PIPELINE_TEMPLATE_UPDATE_FIELDS]
        values.append(row["template_id"])
        sql = f"UPDATE `pipeline_pipelinetemplate` SET {set_clause} WHERE `template_id` = %s"
        with connection.cursor() as cursor:
            cursor.execute(sql, values)

    def _update_task_template(self, local_task_id, source_row):
        set_clause = ", ".join([f"`{f}` = %s" for f in TASK_TEMPLATE_UPDATE_FIELDS])
        values = [source_row.get(f) for f in TASK_TEMPLATE_UPDATE_FIELDS]
        values.append(local_task_id)
        sql = f"UPDATE `tasktmpl3_tasktemplate` SET {set_clause} WHERE `id` = %s"
        with connection.cursor() as cursor:
            cursor.execute(sql, values)
