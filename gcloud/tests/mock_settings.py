# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

BUSINESS_GET = 'gcloud.core.models.Business.objects.get'

PROJECT_GET = 'gcloud.core.models.Project.objects.get'
PROJECT_FILTER = 'gcloud.core.models.Project.objects.filter'

TASKTEMPLATE_SELECT_RELATE = 'gcloud.tasktmpl3.models.TaskTemplate.objects.select_related'
TASKTEMPLATE_GET = 'gcloud.tasktmpl3.models.TaskTemplate.objects.get'
TASKTEMPLATE_CREATE_PIPELINE_TEMPLATE = 'gcloud.tasktmpl3.models.TaskTemplate.objects.create_pipeline_template'
TASKTEMPLATE_MODEL = 'gcloud.tasktmpl3.models.TaskTemplate.objects.model'

COMMONTEMPLATE_SELECT_RELATE = 'gcloud.commons.template.models.CommonTemplate.objects.select_related'
COMMONTEMPLATE_IMPORT_TEMPLATES = 'gcloud.commons.template.models.CommonTemplate.objects.import_templates'

TASKINSTANCE_CREATE_PIPELINE = \
    'gcloud.taskflow3.models.TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes'
TASKINSTANCE_CREATE = 'gcloud.taskflow3.models.TaskFlowInstance.objects.create'
TASKINSTANCE_GET = 'gcloud.taskflow3.models.TaskFlowInstance.objects.get'
TASKINSTANCE_FORMAT_STATUS = 'gcloud.taskflow3.models.TaskFlowInstance.format_pipeline_status'
TASKINSTANCE_EXTEN_CLASSIFIED_COUNT = 'gcloud.taskflow3.models.TaskFlowInstance.objects.extend_classified_count'
TASKINSTANCE_PREVIEW_TREE = 'gcloud.taskflow3.models.TaskFlowInstance.objects.preview_pipeline_tree_exclude_task_nodes'
TASKINSTANCE_OBJECTS_CALLBACK = 'gcloud.taskflow3.models.TaskFlowInstance.objects.callback'
TASKINSTANCE_CALLBACK = 'gcloud.taskflow3.models.TaskFlowInstance.callback'
TASKINSTANCE_HAS_NODE = 'gcloud.taskflow3.models.TaskFlowInstance.has_node'

PERIODIC_TASK_FILTER = 'gcloud.periodictask.models.PeriodicTask.objects.filter'
PERIODIC_TASK_GET = 'gcloud.periodictask.models.PeriodicTask.objects.get'
PERIODIC_TASK_CREATE = 'gcloud.periodictask.models.PeriodicTask.objects.create'
PERIODIC_TASK_PIPELINE_PERIODIC_TASK_CREATE_TASK = 'gcloud.periodictask.models.PipelinePeriodicTask.objects.create_task'

PERIODIC_TASK_HISTORY_CREATE = 'gcloud.periodictask.models.PeriodicTaskHistory.objects.create'

APIGW_BIZ_PERM_DECORATOR = 'gcloud.apigw.decorators.api_check_user_perm_of_business'
APIGW_TASK_PERM_DECORATOR = 'gcloud.apigw.decorators.api_check_user_perm_of_task'
APIGW_VIEW_JSON_SCHEMA_VALIDATE = 'gcloud.apigw.views.jsonschema.validate'
APIGW_VIEW_PIPELINE_API_GET_STATUS_TREE = 'gcloud.apigw.views.pipeline_api.get_status_tree'
APIGW_DECORATOR_CHECK_WHITE_LIST = 'gcloud.apigw.decorators.check_white_apps'
APIGW_DECORATOR_GET_USER_MODEL = 'gcloud.apigw.decorators.get_user_model'
APIGW_DECORATOR_BUSINESS_EXIST = 'gcloud.apigw.decorators.business_exist'
APIGW_READ_TEMPLATE_DATA_FILE = 'gcloud.apigw.views.read_template_data_file'
APIGW_REPLACE_TEMPLATE_ID = 'gcloud.apigw.views.replace_template_id'

CORE_PROJECT_GET_USER_BUSINESS_LIST = 'gcloud.core.project.get_user_business_list'

CORE_MODEL_BUSINESS_UPDATE_OR_CREATE = 'gcloud.core.models.Business.objects.update_or_create'

CORE_MODEL_PROJECT_SYNC_PROJECT = 'gcloud.core.models.Project.objects.sync_project_from_cmdb_business'

CORE_MODEL_USER_DEFAULT_PROJECT_INIT_USER_DEFAULT_PROJECT = \
    'gcloud.core.models.UserDefaultProject.objects.init_user_default_project'

PIPELINE_TEMPLATE_WEB_WRAPPER_UNFOLD_SUBPROCESS = 'pipeline_web.wrapper.PipelineTemplateWebWrapper.unfold_subprocess'

PROJECT_RESOURCE_BATCH_REGISTER_INSTANCE = 'gcloud.core.permissions.project_resource.batch_register_instance'
