# -*- coding: utf-8 -*-
"""
项目流程资源覆盖更新工具：
按业务 ID（CMDB bk_biz_id）将源环境中该业务下的项目流程（TaskTemplate）覆盖更新到当前环境。

更新范围（只更新部分字段）：
1. pipeline_pipelinetemplate:
       name, description, editor, edit_time, snapshot_id, has_subprocess, is_deleted
2. pipeline_templatecurrentversion:
       current_version（同步为 pipeline_pipelinetemplate.snapshot.md5sum）
3. tasktmpl3_tasktemplate:
       category, notify_type, notify_receivers, time_out, is_deleted,
       executor_proxy, default_flow_type, ai_notify_type, ai_notify_group

注意：pipeline_snapshot 的同步由其他脚本负责，本脚本假设目标端已存在对应的 snapshot 记录。

执行模式：
  采用两阶段执行模式：
  阶段一（校验阶段）：生成待更新清单，校验所有依赖（如 snapshot 是否存在）
  阶段二（执行阶段）：校验全部通过后，再统一执行更新
  任一校验失败都会终止执行，保证数据一致性。
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

    # ------------------------------------------------------------------
    # 核心流程：两阶段执行
    # ------------------------------------------------------------------
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

            # 阶段一：校验并生成更新计划
            self.stdout.write(self.style.WARNING("=" * 60))
            self.stdout.write(self.style.WARNING("阶段一：校验依赖并生成待更新清单..."))
            self.stdout.write(self.style.WARNING("=" * 60))
            update_plan = self._validate_and_build_update_plan(source_conn, biz_id)

            if not update_plan:
                self.stdout.write(self.style.WARNING("没有需要更新的流程，退出"))
                return

            # 显示更新计划
            self.stdout.write(self.style.WARNING("=" * 60))
            self.stdout.write(self.style.SUCCESS(f"校验通过！共 {len(update_plan)} 个流程待更新："))
            for item in update_plan:
                self.stdout.write(f"  - template_id={item['template_id']}, name={item['name']}")
            self.stdout.write(self.style.WARNING("=" * 60))

            if dry_run:
                self.stdout.write(self.style.SUCCESS("[dry-run] 校验通过，跳过实际更新"))
                return

            # 阶段二：统一执行更新
            self.stdout.write(self.style.WARNING("阶段二：统一执行更新..."))
            self.stdout.write(self.style.WARNING("=" * 60))
            self._execute_update_plan(update_plan)

            self.stdout.write(self.style.SUCCESS("=" * 60))
            self.stdout.write(self.style.SUCCESS("项目流程资源覆盖更新任务完成！"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"覆盖更新失败: {str(e)}"))
            import traceback

            self.stdout.write(self.style.ERROR(traceback.format_exc()))
            raise
        finally:
            if source_conn is not None:
                source_conn.close()

    # ------------------------------------------------------------------
    # 阶段一：校验并生成更新计划
    # ------------------------------------------------------------------
    def _validate_and_build_update_plan(self, source_conn, biz_id):
        """校验依赖并生成待更新清单

        返回更新计划列表，每个元素包含：
        - template_id: 模板ID
        - name: 模板名称
        - local_task_id: 目标端 task_template 的 id
        - source_pipeline_row: 源端 pipeline_template 数据
        - source_task_row: 源端 task_template 数据
        - snapshot_id: 引用的 snapshot_id

        任一校验失败都会抛出异常终止执行。
        """

        # 1. 在目标端通过 bk_biz_id 查找 project_id
        project_ids = self.fetch_local_project_ids(biz_id)
        if not project_ids:
            raise ValueError(f"目标端找不到 bk_biz_id={biz_id} 对应的项目")
        self.stdout.write(f"[校验] 目标端找到 {len(project_ids)} 个项目: {project_ids}")

        # 2. 从目标端拉取这些项目下所有已存在的 tasktmpl3_tasktemplate
        local_task_templates = self.fetch_local_task_templates(project_ids)
        if not local_task_templates:
            raise ValueError(f"目标端 bk_biz_id={biz_id} 下没有任何项目流程，请先执行全量同步")
        self.stdout.write(f"[校验] 目标端共找到 {len(local_task_templates)} 个项目流程")

        # 3. 从源端拉取对应的 pipeline_template 和 task_template 最新数据
        pipeline_template_ids = [t["pipeline_template_id"] for t in local_task_templates]
        source_pipeline_templates = self.fetch_pipeline_templates(source_conn, pipeline_template_ids)
        source_task_templates = self.fetch_task_templates_by_pipeline_ids(source_conn, pipeline_template_ids)

        # 4. 校验源端数据完整性，并收集所有需要校验的 snapshot_id
        self.stdout.write("[校验] 开始校验源端数据完整性和依赖...")
        update_plan = []
        all_snapshot_ids = set()

        for local_task_row in local_task_templates:
            template_id = local_task_row["pipeline_template_id"]

            source_pipeline_row = source_pipeline_templates.get(template_id)
            if source_pipeline_row is None:
                raise ValueError(f"校验失败：源端无 pipeline_template={template_id}，" f"目标端存在但该流程可能在源端已被删除，请手动处理")

            source_task_row = source_task_templates.get(template_id)
            # source_task_row 允许为 None，使用源端 pipeline_template 的字段即可

            snapshot_id = source_pipeline_row.get("snapshot_id")
            if snapshot_id is None:
                raise ValueError(f"校验失败：template_id={template_id} 的 snapshot_id 为 NULL")

            # 收集需要校验的 snapshot_id
            all_snapshot_ids.add(snapshot_id)

            update_plan.append(
                {
                    "template_id": template_id,
                    "name": source_pipeline_row.get("name", ""),
                    "local_task_id": local_task_row["id"],
                    "source_pipeline_row": source_pipeline_row,
                    "source_task_row": source_task_row,
                    "snapshot_id": snapshot_id,
                }
            )

        self.stdout.write(f"[校验] 数据完整性校验通过，共 {len(update_plan)} 个流程待更新")

        # 5. 批量校验目标端 snapshot 是否存在
        self.stdout.write(f"[校验] 开始校验目标端 snapshot 依赖（共 {len(all_snapshot_ids)} 个）...")
        self._validate_snapshots_exist(all_snapshot_ids)

        self.stdout.write(self.style.SUCCESS("[校验] 所有依赖校验通过"))
        return update_plan

    def _validate_snapshots_exist(self, snapshot_ids):
        """批量校验目标端是否存在所有需要的 snapshot

        任一缺失则抛出异常，终止执行。
        """
        if not snapshot_ids:
            return

        placeholders = ", ".join(["%s"] * len(snapshot_ids))
        sql = f"SELECT id FROM pipeline_snapshot WHERE id IN ({placeholders})"
        with connection.cursor() as cursor:
            cursor.execute(sql, list(snapshot_ids))
            existing_ids = {row[0] for row in cursor.fetchall()}

        missing_ids = snapshot_ids - existing_ids
        if missing_ids:
            raise ValueError(f"校验失败：目标端缺失 {len(missing_ids)} 个 snapshot 记录：{missing_ids}")

    # ------------------------------------------------------------------
    # 阶段二：统一执行更新
    # ------------------------------------------------------------------
    def _execute_update_plan(self, update_plan):
        """统一执行更新计划

        所有更新操作在同一个事务中完成，任一失败则全部回滚。
        """
        try:
            with transaction.atomic():
                success = 0
                for item in update_plan:
                    template_id = item["template_id"]
                    name = item["name"]
                    local_task_id = item["local_task_id"]
                    source_pipeline_row = item["source_pipeline_row"]
                    source_task_row = item["source_task_row"]
                    snapshot_id = item["snapshot_id"]

                    self._update_pipeline_template(source_pipeline_row)
                    self._update_template_current_version(template_id, snapshot_id)
                    self._update_task_template(local_task_id, source_task_row)
                    success += 1
                    self.stdout.write(f"[ok] 已更新 template_id={template_id} (name={name})")

                self.stdout.write(self.style.SUCCESS(f"更新完成：成功 {success}/{len(update_plan)} 个"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"更新失败，所有操作已回滚: {str(e)}"))
            raise

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
        sql = f"SELECT * FROM tasktmpl3_tasktemplate WHERE project_id IN ({placeholders}) AND id < 500000"
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
    def _update_pipeline_template(self, row):
        set_clause = ", ".join([f"`{f}` = %s" for f in PIPELINE_TEMPLATE_UPDATE_FIELDS])
        values = [row.get(f) for f in PIPELINE_TEMPLATE_UPDATE_FIELDS]
        values.append(row["template_id"])
        sql = f"UPDATE `pipeline_pipelinetemplate` SET {set_clause} WHERE `template_id` = %s"
        with connection.cursor() as cursor:
            cursor.execute(sql, values)

    def _update_template_current_version(self, template_id, snapshot_id):
        """更新 pipeline_templatecurrentversion 表，将 current_version 设为对应 snapshot 的 md5sum

        逻辑与 Django TemplateCurrentVersionManager.update_current_version 一致：
        - 先查 snapshot 的 md5sum
        - 再用 update_or_create 语义更新 pipeline_templatecurrentversion
        """
        # 查询 snapshot 的 md5sum
        sql_get_md5 = "SELECT md5sum FROM pipeline_snapshot WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(sql_get_md5, (snapshot_id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"snapshot_id={snapshot_id} 在目标端不存在，请先同步 snapshot 数据")
            current_version = row[0]

        # update_or_create 语义
        sql_select = "SELECT id FROM pipeline_templatecurrentversion WHERE template_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(sql_select, (template_id,))
            exists = cursor.fetchone()

        if exists:
            sql_update = "UPDATE pipeline_templatecurrentversion " "SET current_version = %s " "WHERE template_id = %s"
            with connection.cursor() as cursor:
                cursor.execute(sql_update, (current_version, template_id))
        else:
            sql_insert = "INSERT INTO pipeline_templatecurrentversion (template_id, current_version) " "VALUES (%s, %s)"
            with connection.cursor() as cursor:
                cursor.execute(sql_insert, (template_id, current_version))

    def _update_task_template(self, local_task_id, source_row):
        set_clause = ", ".join([f"`{f}` = %s" for f in TASK_TEMPLATE_UPDATE_FIELDS])
        values = [source_row.get(f) for f in TASK_TEMPLATE_UPDATE_FIELDS]
        values.append(local_task_id)
        sql = f"UPDATE `tasktmpl3_tasktemplate` SET {set_clause} WHERE `id` = %s"
        with connection.cursor() as cursor:
            cursor.execute(sql, values)
