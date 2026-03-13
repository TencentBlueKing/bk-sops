import json
import logging

from django.core.management.base import BaseCommand
from django.db import connection

from gcloud.core.models import EnvironmentVariables

logger = logging.getLogger("root")


class Command(BaseCommand):
    help = "同步数据库模型的最大ID到环境变量表（按分类存储）"

    def add_arguments(self, parser):
        """添加命令行参数"""
        parser.add_argument("--dry_run", action="store_true", help="模拟运行模式，不实际执行更新")

    def get_sort_field(self, table_name):
        """根据表名获取排序字段"""
        # 对于重试表和超时表，使用关联的任务ID进行排序，保持数据一致性
        if table_name == "taskflow3_autoretrynodestrategy":
            return "taskflow_id"
        elif table_name == "taskflow3_timeoutnodeconfig":
            return "task_id"
        else:
            return "id"

    def get_model_max_id(self, model_name):
        """获取指定模型的最大ID"""
        try:
            with connection.cursor() as cursor:
                # 根据表名获取对应的排序字段
                table_name = model_name
                sort_field = self.get_sort_field(table_name)
                cursor.execute(f"SELECT {sort_field} FROM {table_name} ORDER BY {sort_field} DESC LIMIT 1")
                result = cursor.fetchone()
                return result[0] if result and result[0] is not None else 0
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"查询模型 {model_name} 的最大ID失败: {e}"))
            return None

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        self.stdout.write("开始同步数据库模型的最大ID到环境变量表（按分类存储）")

        if dry_run:
            self.stdout.write("=== 模拟运行模式 ===")
            return

        # 定义模型分类
        model_categories = {
            "celery_model_status": {
                "name": "Celery Beat 相关模型",
                "models": [
                    "django_celery_beat_clockedschedule",
                    "django_celery_beat_crontabschedule",
                    "django_celery_beat_periodictask",
                ],
            },
            "pipeline_models_status": {
                "name": "Pipeline 相关模型",
                "models": [
                    "pipeline_pipelinetemplate",
                    "pipeline_pipelineinstance",
                    "pipeline_snapshot",
                    "pipeline_templateversion",
                    "pipeline_templatecurrentversion",
                    "pipeline_templaterelationship",
                    "pipeline_templatescheme",
                    "pipeline_treeinfo",
                ],
            },
            "taskflow_models_status": {
                "name": "Taskflow 相关模型",
                "models": [
                    "taskflow3_taskflowinstance",
                    "tasktmpl3_tasktemplate",
                    "taskflow3_autoretrynodestrategy",
                    "taskflow3_timeoutnodeconfig",
                ],
            },
            "eri_models_status": {
                "name": "ERI 执行引擎模型",
                "models": [
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
                ],
            },
            "business_models_status": {
                "name": "其他业务模型",
                "models": [
                    "periodictask_periodictask",
                    "periodic_task_periodictask",
                    "files_fileuploadrecord",
                    "files_uploadticket",
                    "operate_record_taskoperaterecord",
                    "operate_record_templateoperaterecord",
                    "pipeline_web_core_nodeininstance",
                    "pipeline_web_core_nodeintemplate",
                    "periodictask_periodictaskhistory",
                    "periodic_task_periodictaskhistory",
                    "core_staffgroupset",
                    "project_constants_projectconstant",
                    "label_label",
                    "label_templatelabelrelation",
                    "appmaker_appmaker",
                    "clocked_task_clockedtask",
                    "collection_collection",
                    "function_functiontask",
                ],
            },
        }

        for category_key, category_info in model_categories.items():
            self.stdout.write(f"处理分类: {category_info['name']}")

            # 检查是否已经存在该环境变量
            existing_var = EnvironmentVariables.objects.filter(key=category_key).first()

            # 收集该分类下所有模型的最大ID
            category_data = {}
            category_success = True

            for table_name in category_info["models"]:
                max_id = self.get_model_max_id(table_name)

                if max_id is None:
                    self.stdout.write(self.style.WARNING(f"  模型 {table_name} 查询失败"))
                    category_success = False
                    continue

                category_data[table_name] = max_id
                self.stdout.write(f"  模型 {table_name}: 最大ID = {max_id}")

            if not category_success:
                self.stdout.write(self.style.WARNING(f"分类 {category_info['name']} 部分模型查询失败，跳过该分类"))
                continue

            # 将数据转换为JSON格式
            json_data = json.dumps(category_data, ensure_ascii=False, indent=2)
            try:
                # 创建或更新环境变量
                if existing_var:
                    existing_var.value = json_data
                    existing_var.name = f"{category_info['name']} 最大ID数据"
                    existing_var.save()
                    self.stdout.write(f"更新环境变量: {category_key}")
                else:
                    EnvironmentVariables.objects.create(
                        key=category_key, name=f"{category_info['name']} 最大ID数据", value=json_data
                    )
                    self.stdout.write(f"创建环境变量: {category_key}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"保存环境变量 {category_key} 失败: {e}"))
                logger.error(f"保存环境变量 {category_key} 失败: {e}")

        self.stdout.write(self.style.SUCCESS("同步完成"))
