# -*- coding: utf-8 -*-
"""
数据库增量同步工具：基于ID记录的增量数据同步
"""

import json

import pymysql
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection

from gcloud.core.models import EnvironmentVariables


class Command(BaseCommand):
    help = "数据库增量同步工具：基于ID记录的增量数据同步"

    def __init__(self):
        super().__init__()
        # 同步状态文件路径
        self.status_file = "sync_status.json"

    def add_arguments(self, parser):
        parser.add_argument("--skip-binary", action="store_true", default=False, help="跳过包含二进制数据的记录，默认不跳过")
        parser.add_argument("--dry-run", action="store_true", help="只检查不实际同步")
        parser.add_argument("--batch-size", type=int, default=100, help="每次同步的记录数")
        parser.add_argument("--host", type=str, help="源数据库主机")
        parser.add_argument("--port", type=int, help="源数据库端口")
        parser.add_argument("--user", type=str, help="源数据库用户名")
        parser.add_argument("--password", type=str, help="源数据库密码")
        parser.add_argument("--database", type=str, help="源数据库名称")
        parser.add_argument("--tenant_id", type=str, help="租户ID")

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        dry_run = options["dry_run"]

        self.stdout.write("开始增量同步任务...")
        if dry_run:
            self.stdout.write("*** 干运行模式：只检查不实际同步 ***")

        try:
            # 在同步开始前全局禁用外键约束
            with connection.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            # 连接源数据库
            try:
                source_conn = pymysql.connect(
                    host=options["host"],
                    port=options["port"],
                    user=options["user"],
                    password=options["password"],
                    database=options["database"],
                    charset="utf8mb4",
                    cursorclass=pymysql.cursors.DictCursor,
                )
                self.stdout.write("数据库连接成功")
            except Exception as e:
                raise ValueError(f"数据库连接失败: {str(e)}")

            self.sync_data(source_conn, batch_size, dry_run)
            # 关闭数据库连接
            source_conn.close()

            # 同步结束后重新启用外键约束
            with connection.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            self.stdout.write(self.style.SUCCESS("增量同步任务完成！"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"同步失败: {str(e)}"))
            raise

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
        success_count = 0
        max_id = last_id

        for data in results:
            if self.save_record(table_name, data, dry_run):
                success_count += 1
                # 更新最大ID（使用排序字段的值）
                sort_field_value = data.get(sort_field, 0)
                if sort_field_value > max_id:
                    max_id = sort_field_value

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
                self.stdout.write(f"[运行] 将同步记录: {table_name}.{filter_key}={record_id}")
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

        # 基础模型映射
        table_model_mapping = {
            "core_project": apps.get_model("core", "Project"),
            "core_business": apps.get_model("core", "Business"),
            "core_staffgroupset": apps.get_model("core", "StaffGroupSet"),
            "taskflow3_taskflowinstance": apps.get_model("taskflow3", "TaskFlowInstance"),
            "tasktmpl3_tasktemplate": apps.get_model("tasktmpl3", "TaskTemplate"),
            "django_celery_beat_clockedschedule": apps.get_model("django_celery_beat", "ClockedSchedule"),
            "django_celery_beat_periodictask": apps.get_model("django_celery_beat", "PeriodicTask"),
            "django_celery_beat_intervalschedule": apps.get_model("django_celery_beat", "IntervalSchedule"),
            "django_celery_beat_crontabschedule": apps.get_model("django_celery_beat", "CrontabSchedule"),
            "eri_callbackdata": apps.get_model("eri", "CallbackData"),
            "eri_contextoutputs": apps.get_model("eri", "ContextOutputs"),
            "eri_contextvalue": apps.get_model("eri", "ContextValue"),
            "eri_data": apps.get_model("eri", "Data"),
            "eri_executiondata": apps.get_model("eri", "ExecutionData"),
            "eri_executionhistory": apps.get_model("eri", "ExecutionHistory"),
            "eri_logentry": apps.get_model("eri", "LogEntry"),
            "eri_node": apps.get_model("eri", "Node"),
            "eri_process": apps.get_model("eri", "Process"),
            "eri_schedule": apps.get_model("eri", "Schedule"),
            "eri_state": apps.get_model("eri", "State"),
            "appmaker_appmaker": apps.get_model("appmaker", "AppMaker"),
            "clocked_task_clockedtask": apps.get_model("clocked_task", "ClockedTask"),
            "collection_collection": apps.get_model("collection", "Collection"),
            "function_functiontask": apps.get_model("function", "FunctionTask"),
            "periodictask_periodictask": apps.get_model("periodictask", "PeriodicTask"),
            "periodictask_periodictaskhistory": apps.get_model("periodictask", "PeriodicTaskHistory"),
            "periodic_task_periodictask": apps.get_model("periodic_task", "PeriodicTask"),
            "periodic_task_periodictaskhistory": apps.get_model("periodic_task", "PeriodicTaskHistory"),
            "label_label": apps.get_model("label", "Label"),
            "label_templatelabelrelation": apps.get_model("label", "TemplateLabelRelation"),
            "operate_record_taskoperaterecord": apps.get_model("operate_record", "TaskOperateRecord"),
            "operate_record_templateoperaterecord": apps.get_model("operate_record", "TemplateOperateRecord"),
            "pipeline_pipelinetemplate": apps.get_model("pipeline", "PipelineTemplate"),
            "pipeline_snapshot": apps.get_model("pipeline", "Snapshot"),
            "pipeline_treeinfo": apps.get_model("pipeline", "TreeInfo"),
            "pipeline_pipelineinstance": apps.get_model("pipeline", "PipelineInstance"),
            "pipeline_templatecurrentversion": apps.get_model("pipeline", "TemplateCurrentVersion"),
            "pipeline_templaterelationship": apps.get_model("pipeline", "TemplateRelationship"),
            "pipeline_templatescheme": apps.get_model("pipeline", "TemplateScheme"),
            "pipeline_templateversion": apps.get_model("pipeline", "TemplateVersion"),
            "pipeline_web_core_nodeininstance": apps.get_model("pipeline_web_core", "NodeInInstance"),
            "pipeline_web_core_nodeintemplate": apps.get_model("pipeline_web_core", "NodeInTemplate"),
            "project_constants_projectconstant": apps.get_model("project_constants", "ProjectConstant"),
            "taskflow3_autoretrynodestrategy": apps.get_model("taskflow3", "AutoRetryNodeStrategy"),
            "taskflow3_taskcallbackrecord": apps.get_model("taskflow3", "TaskCallBackRecord"),
            "taskflow3_taskflowrelation": apps.get_model("taskflow3", "TaskFlowRelation"),
            "taskflow3_timeoutnodeconfig": apps.get_model("taskflow3", "TimeoutNodeConfig"),
            "files_fileuploadrecord": apps.get_model("files", "FileUploadRecord"),
            "files_uploadmodulefiletag": apps.get_model("files", "UploadModuleFileTag"),
            "files_uploadticket": apps.get_model("files", "UploadTicket"),
            "template_commontemplate": apps.get_model("template", "CommonTemplate"),
        }

        return table_model_mapping.get(table_name)
