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
from django.db import connection

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
        """根据 bk_biz_id 拉取源端该业务的所有流程，逐条覆盖更新"""

        # 1. 在源端通过 bk_biz_id 查找 project_id
        project_ids = self.fetch_project_ids(source_conn, biz_id)
        if not project_ids:
            self.stdout.write(self.style.WARNING(f"源端找不到 bk_biz_id={biz_id} 对应的项目"))
            return
        self.stdout.write(f"源端找到 {len(project_ids)} 个项目: {project_ids}")

        # 2. 拉取这些项目下的所有 tasktmpl3_tasktemplate
        task_templates = self.fetch_task_templates_by_projects(source_conn, project_ids)
        if not task_templates:
            self.stdout.write(self.style.WARNING(f"源端 bk_biz_id={biz_id} 下没有任何项目流程"))
            return
        self.stdout.write(f"源端共找到 {len(task_templates)} 个项目流程")

        # 3. 拉取关联的 pipeline_template 和 current_version
        pipeline_template_ids = [t["pipeline_template_id"] for t in task_templates]
        pipeline_templates = self.fetch_pipeline_templates(source_conn, pipeline_template_ids)

        # 4. 逐条覆盖
        success, skipped = 0, 0
        for task_row in task_templates:
            template_id = task_row["pipeline_template_id"]
            pipeline_row = pipeline_templates.get(template_id)

            if pipeline_row is None:
                self.stdout.write(
                    self.style.WARNING(f"[跳过] 源端无 pipeline_template={template_id}（task_template id={task_row['id']}）")
                )
                skipped += 1
                continue

            ok = self.update_one(task_row, pipeline_row, dry_run)
            if ok:
                success += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(f"处理完成：成功 {success} 个，跳过 {skipped} 个"))

    # ------------------------------------------------------------------
    # 源端数据抓取
    # ------------------------------------------------------------------
    def fetch_project_ids(self, source_conn, bk_biz_id):
        sql = "SELECT id FROM core_project WHERE bk_biz_id = %s"
        with source_conn.cursor() as cursor:
            cursor.execute(sql, (bk_biz_id,))
            return [row["id"] for row in cursor.fetchall()]

    def fetch_task_templates_by_projects(self, source_conn, project_ids):
        if not project_ids:
            return []
        placeholders = ", ".join(["%s"] * len(project_ids))
        sql = f"SELECT * FROM tasktmpl3_tasktemplate WHERE project_id IN ({placeholders})"
        with source_conn.cursor() as cursor:
            cursor.execute(sql, project_ids)
            return list(cursor.fetchall())

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
    def update_one(self, task_row, pipeline_row, dry_run):
        template_id = pipeline_row["template_id"]

        # 校验目标库是否已存在该流程（不存在则跳过，由全量同步处理新增）
        if not self._exists(
            "SELECT 1 FROM pipeline_pipelinetemplate WHERE template_id = %s",
            (template_id,),
        ):
            self.stdout.write(self.style.WARNING(f"[跳过] 目标库无 pipeline_template={template_id}，留待全量同步处理"))
            return False

        # 校验目标库 task_template 是否存在
        if not self._exists(
            "SELECT 1 FROM tasktmpl3_tasktemplate WHERE id = %s",
            (task_row["id"],),
        ):
            self.stdout.write(self.style.WARNING(f"[跳过] 目标库无 tasktmpl3_tasktemplate id={task_row['id']}，留待全量同步处理"))
            return False

        if dry_run:
            self.stdout.write(f"[dry-run] 将更新 template_id={template_id} (name={pipeline_row.get('name')})")
            return True

        try:
            self._update_pipeline_template(pipeline_row)
            self._update_task_template(task_row)
            self.stdout.write(f"[ok] 已更新 template_id={template_id} (name={pipeline_row.get('name')})")
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

    def _update_task_template(self, row):
        set_clause = ", ".join([f"`{f}` = %s" for f in TASK_TEMPLATE_UPDATE_FIELDS])
        values = [row.get(f) for f in TASK_TEMPLATE_UPDATE_FIELDS]
        values.append(row["id"])
        sql = f"UPDATE `tasktmpl3_tasktemplate` SET {set_clause} WHERE `id` = %s"
        with connection.cursor() as cursor:
            cursor.execute(sql, values)

    def _exists(self, sql, params):
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone() is not None
