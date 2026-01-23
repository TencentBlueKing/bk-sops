# -*- coding: utf-8 -*-
"""
数据库增量同步工具：基于ID记录的增量数据同步
"""

import json
import os

import pymysql
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from pipeline.models import TemplateCurrentVersion

from gcloud.common_template.models import CommonTemplate
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate


class Command(BaseCommand):
    help = "数据库增量同步工具：基于ID记录的增量数据同步"

    def __init__(self):
        super().__init__()
        # 同步状态文件路径
        self.status_file = "sync_status.json"

        self.sync_tables = [
            "core_project",
            "core_business",
            "core_staffgroupset",
            "project_constants_projectconstant",
            "django_celery_beat_crontabschedule",
            "django_celery_beat_intervalschedule",
            "django_celery_beat_clockedschedule",
            "django_celery_beat_periodictask",
            "label_label",
            "label_templatelabelrelation",
            "pipeline_pipelinetemplate",
            "pipeline_pipelineinstance",
            "pipeline_snapshot",
            "pipeline_templateversion",
            "pipeline_templatecurrentversion",
            "pipeline_templaterelationship",
            "pipeline_templatescheme",
            "pipeline_treeinfo",
            "taskflow3_taskflowrelation",
            "taskflow3_taskflowinstance",
            "tasktmpl3_tasktemplate",
            "template_commontemplate",
            "eri_callbackdata",
            "eri_contextoutputs",
            "eri_contextvalue",
            "eri_data",
            "eri_executiondata",
            "eri_executionhistory",
            "eri_logentry",
            "eri_node",
            "eri_process",
            "eri_schedule",
            "eri_state",
            "appmaker_appmaker",
            "clocked_task_clockedtask",
            "collection_collection",
            "function_functiontask",
            "periodictask_periodictask",
            "periodic_task_periodictask",
            "files_fileuploadrecord",
            "files_uploadmodulefiletag",
            "files_uploadticket",
            "operate_record_taskoperaterecord",
            "operate_record_templateoperaterecord",
            "pipeline_web_core_nodeininstance",
            "pipeline_web_core_nodeintemplate",
            "taskflow3_taskcallbackrecord",
            "taskflow3_autoretrynodestrategy",
            "taskflow3_timeoutnodeconfig",
            "periodictask_periodictaskhistory",
            "periodic_task_periodictaskhistory",
        ]

    def add_arguments(self, parser):
        parser.add_argument("--skip-binary", action="store_true", default=False, help="跳过包含二进制数据的记录，默认不跳过")
        parser.add_argument("--dry-run", action="store_true", help="只检查不实际同步")

    def handle(self, *args, **options):
        batch_size = settings.SYNC_INCREMENTAL_BATCH_SIZE
        dry_run = options["dry_run"]

        self.stdout.write("开始增量同步任务...")
        if dry_run:
            self.stdout.write("*** 干运行模式：只检查不实际同步 ***")

        try:
            # 在同步开始前全局禁用外键约束
            with connection.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            self.sync_data(batch_size, dry_run)

            # 同步结束后重新启用外键约束
            with connection.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            self.stdout.write(self.style.SUCCESS("增量同步任务完成！"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"同步失败: {str(e)}"))
            raise

    def sync_data(self, batch_size, dry_run):
        """执行增量数据同步"""
        # 连接源数据库
        try:
            source_conn = pymysql.connect(
                host=settings.SYNC_SOURCE_HOST,
                port=settings.SYNC_SOURCE_PORT,
                user=settings.SYNC_SOURCE_USER,
                password=settings.SYNC_SOURCE_PASSWORD,
                database=settings.SYNC_SOURCE_DATABASE,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
            self.stdout.write("数据库连接成功")
        except Exception as e:
            raise ValueError(f"数据库连接失败: {str(e)}")

        # 加载同步状态
        sync_status = self.load_sync_status()

        # 同步每个表
        for table_name in self.sync_tables:
            self.sync_table(source_conn, table_name, batch_size, sync_status, dry_run)

        # 关闭数据库连接
        source_conn.close()
        # 保存同步状态
        self.save_sync_status(sync_status)

    def sync_table(self, source_conn, table_name, batch_size, sync_status, dry_run):
        """同步单个表的数据"""
        self.stdout.write(f"同步表: {table_name}")

        # 获取上次同步的最后ID
        last_id = sync_status.get(table_name, 0)
        sort_field = self.get_sort_field(table_name)

        # 查询需要同步的数据
        query = f"SELECT * FROM {table_name} WHERE {sort_field} > %s ORDER BY {sort_field} ASC LIMIT %s"

        try:
            with source_conn.cursor() as cursor:
                cursor.execute(query, (last_id, batch_size))
                results = cursor.fetchall()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"查询表 {table_name} 失败: {str(e)}"))
            return

        if not results:
            self.stdout.write(f"表 {table_name} 没有新数据需要同步")
            return

        # 同步数据
        success_count = 0
        max_id = last_id

        for data in results:
            if self.save_record(table_name, data, dry_run):
                success_count += 1
                # 更新最大ID（使用排序字段的值）
                sort_field_value = data.get(sort_field, 0)
                if sort_field_value > max_id:
                    max_id = sort_field_value

        # 更新同步状态
        if not dry_run and max_id > last_id:
            sync_status[table_name] = max_id
            self.stdout.write(f"表 {table_name} 同步完成：{success_count}/{len(results)} 条数据，最后{sort_field}: {max_id}")
        else:
            self.stdout.write(f"表 {table_name} 同步完成：{success_count}/{len(results)} 条数据")

    def get_sort_field(self, table_name):
        """根据表名获取排序字段"""
        # 对于重试表和超时表，使用关联的任务ID进行排序，保持数据一致性
        if table_name == "taskflow3_autoretrynodestrategy":
            return "taskflow_id"
        elif table_name == "taskflow3_timeoutnodeconfig":
            return "task_id"
        else:
            return "id"

    def save_record(self, table_name, data, dry_run):
        """保存单条记录（完全跳过外键约束版本）"""
        try:
            # 根据表名选择对应的模型
            model_class = self.get_model_class(table_name)
            if not model_class:
                self.stdout.write(self.style.WARNING(f"跳过记录：未找到对应的模型类 for {table_name}"))
                return False

            filter_key = self.get_sort_field(table_name)
            record_id = data.get(filter_key)

            filter_kwargs = {filter_key: record_id}
            existing_record = model_class.objects.filter(**filter_kwargs).first()

            # 检查字段是否存在，过滤掉模型中不存在的字段
            valid_data = {}
            removed_fields = []

            # 动态获取目标数据库的表字段
            with connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE {model_class._meta.db_table}")
                table_columns = [row[0] for row in cursor.fetchall()]

            for field, value in data.items():
                if field == "enabled" and table_name == "django_celery_beat_periodictask":
                    value = 0
                if field in table_columns:
                    valid_data[field] = value
                else:
                    removed_fields.append(field)

            if removed_fields:
                self.stdout.write(self.style.WARNING(f"过滤掉不存在的字段: {', '.join(removed_fields)}"))

            if dry_run:
                self.stdout.write(f"[干运行] 将同步记录: {table_name}.{filter_key}={record_id}")
                return True

            with connection.cursor() as cursor:
                if existing_record:
                    # 更新操作 - 为字段名添加反引号转义
                    set_clause = ", ".join([f"`{field}` = %s" for field in valid_data.keys()])
                    values = list(valid_data.values())
                    values.append(record_id)

                    sql = f"UPDATE `{model_class._meta.db_table}` SET {set_clause} WHERE `{filter_key}` = %s"
                    cursor.execute(sql, values)
                else:
                    # 插入操作 - 为字段名添加反引号转义
                    columns = ", ".join([f"`{field}`" for field in valid_data.keys()])
                    placeholders = ", ".join(["%s"] * len(valid_data))
                    values = list(valid_data.values())

                    sql = f"INSERT INTO `{model_class._meta.db_table}` ({columns}) VALUES ({placeholders})"
                    cursor.execute(sql, values)

            return True

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"同步记录失败 {table_name}: {str(e)}"))
            return False

    def get_model_class(self, table_name):
        """根据表名获取对应的Django模型类"""
        from django_celery_beat.models import ClockedSchedule, CrontabSchedule, IntervalSchedule
        from django_celery_beat.models import PeriodicTask as DjangoPeriodicTask
        from pipeline.contrib.periodic_task.models import PeriodicTask, PeriodicTaskHistory
        from pipeline.eri.models import (
            CallbackData,
            ContextOutputs,
            ContextValue,
            Data,
            ExecutionData,
            ExecutionHistory,
            LogEntry,
            Node,
            Process,
            Schedule,
            State,
        )
        from pipeline.models import (
            PipelineInstance,
            PipelineTemplate,
            Snapshot,
            TemplateRelationship,
            TemplateScheme,
            TemplateVersion,
            TreeInfo,
        )

        from files.models import FileUploadRecord, UploadModuleFileTag, UploadTicket
        from gcloud.clocked_task.models import ClockedTask
        from gcloud.contrib.appmaker.models import AppMaker
        from gcloud.contrib.collection.models import Collection
        from gcloud.contrib.function.models import FunctionTask
        from gcloud.contrib.operate_record.models import TaskOperateRecord, TemplateOperateRecord
        from gcloud.core.models import Business, Project, StaffGroupSet
        from gcloud.label.models import Label, TemplateLabelRelation
        from gcloud.periodictask.models import PeriodicTask as SopsPeriodicTask
        from gcloud.periodictask.models import PeriodicTaskHistory as SopsPeriodicTaskHistory
        from gcloud.project_constants.models import ProjectConstant
        from gcloud.taskflow3.models import (
            AutoRetryNodeStrategy,
            TaskCallBackRecord,
            TaskFlowRelation,
            TimeoutNodeConfig,
        )
        from pipeline_web.core.models import NodeInInstance, NodeInTemplate

        # 基础模型映射
        table_model_mapping = {
            "core_project": Project,
            "core_business": Business,
            "core_staffgroupset": StaffGroupSet,
            "taskflow3_taskflowinstance": TaskFlowInstance,
            "tasktmpl3_tasktemplate": TaskTemplate,
            "django_celery_beat_clockedschedule": ClockedSchedule,
            "django_celery_beat_periodictask": DjangoPeriodicTask,
            "django_celery_beat_intervalschedule": IntervalSchedule,
            "django_celery_beat_crontabschedule": CrontabSchedule,
            "eri_callbackdata": CallbackData,
            "eri_contextoutputs": ContextOutputs,
            "eri_contextvalue": ContextValue,
            "eri_data": Data,
            "eri_executiondata": ExecutionData,
            "eri_executionhistory": ExecutionHistory,
            "eri_logentry": LogEntry,
            "eri_node": Node,
            "eri_process": Process,
            "eri_schedule": Schedule,
            "eri_state": State,
            "appmaker_appmaker": AppMaker,
            "clocked_task_clockedtask": ClockedTask,
            "collection_collection": Collection,
            "function_functiontask": FunctionTask,
            "periodictask_periodictask": SopsPeriodicTask,
            "periodictask_periodictaskhistory": SopsPeriodicTaskHistory,
            "periodic_task_periodictask": PeriodicTask,
            "periodic_task_periodictaskhistory": PeriodicTaskHistory,
            "label_label": Label,
            "label_templatelabelrelation": TemplateLabelRelation,
            "operate_record_taskoperaterecord": TaskOperateRecord,
            "operate_record_templateoperaterecord": TemplateOperateRecord,
            "pipeline_pipelinetemplate": PipelineTemplate,
            "pipeline_snapshot": Snapshot,
            "pipeline_treeinfo": TreeInfo,
            "pipeline_pipelineinstance": PipelineInstance,
            "pipeline_templatecurrentversion": TemplateCurrentVersion,
            "pipeline_templaterelationship": TemplateRelationship,
            "pipeline_templatescheme": TemplateScheme,
            "pipeline_templateversion": TemplateVersion,
            "pipeline_web_core_nodeininstance": NodeInInstance,
            "pipeline_web_core_nodeintemplate": NodeInTemplate,
            "project_constants_projectconstant": ProjectConstant,
            "taskflow3_autoretrynodestrategy": AutoRetryNodeStrategy,
            "taskflow3_taskcallbackrecord": TaskCallBackRecord,
            "taskflow3_taskflowrelation": TaskFlowRelation,
            "taskflow3_timeoutnodeconfig": TimeoutNodeConfig,
            "files_fileuploadrecord": FileUploadRecord,
            "files_uploadmodulefiletag": UploadModuleFileTag,
            "files_uploadticket": UploadTicket,
            "template_commontemplate": CommonTemplate,
        }

        return table_model_mapping.get(table_name)

    def load_sync_status(self):
        """加载同步状态"""
        if os.path.exists(self.status_file):
            try:
                with open(self.status_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {}

    def save_sync_status(self, sync_status):
        """保存同步状态"""
        try:
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(sync_status, f, ensure_ascii=False, indent=2)
            self.stdout.write(f"同步状态已保存到: {self.status_file}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"保存同步状态失败: {str(e)}"))
