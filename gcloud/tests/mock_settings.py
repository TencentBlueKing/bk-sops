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

TASKTEMPLATE_SELECT_RELATE = 'gcloud.tasktmpl3.models.TaskTemplate.objects.select_related'
TASKTEMPLATE_GET = 'gcloud.tasktmpl3.models.TaskTemplate.objects.get'

COMMONTEMPLATE_SELECT_RELATE = 'gcloud.commons.template.models.CommonTemplate.objects.select_related'

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

APIGW_BIZ_PERM_DECORATOR = 'gcloud.apigw.decorators.api_check_user_perm_of_business'
APIGW_TASK_PERM_DECORATOR = 'gcloud.apigw.decorators.api_check_user_perm_of_task'
APIGW_VIEW_JSON_SCHEMA_VALIDATE = 'gcloud.apigw.views.jsonschema.validate'
APIGW_VIEW_PIPELINE_API_GET_STATUS_TREE = 'gcloud.apigw.views.pipeline_api.get_status_tree'
APIGW_DECORATOR_CHECK_WHITE_LIST = 'gcloud.apigw.decorators.check_white_apps'
APIGW_DECORATOR_GET_USER_MODEL = 'gcloud.apigw.decorators.get_user_model'
APIGW_DECORATOR_PREPARE_USER_BUSINESS = 'gcloud.apigw.decorators.prepare_user_business'
APIGW_DECORATOR_BUSINESS_EXIST = 'gcloud.apigw.decorators.business_exist'
