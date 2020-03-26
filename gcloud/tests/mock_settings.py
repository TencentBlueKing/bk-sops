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

TEMPLATESCHEME_FILTER = 'pipeline.models.TemplateScheme.objects.filter'

COMMONTEMPLATE_GET = 'gcloud.commons.template.models.CommonTemplate.objects.get'
COMMONTEMPLATE_SELECT_RELATE = 'gcloud.commons.template.models.CommonTemplate.objects.select_related'
COMMONTEMPLATE_IMPORT_TEMPLATES = 'gcloud.commons.template.models.CommonTemplate.objects.import_templates'

TASKFLOW_OBJECTS_FILTER = 'gcloud.taskflow3.models.TaskFlowInstance.objects.filter'
TASKINSTANCE_CREATE_PIPELINE = \
    'gcloud.taskflow3.models.TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes'
TASKINSTANCE_CREATE_PIPELINE_INSTANCE = 'gcloud.taskflow3.models.TaskFlowInstance.objects.create_pipeline_instance'
TASKINSTANCE_CREATE = 'gcloud.taskflow3.models.TaskFlowInstance.objects.create'
TASKINSTANCE_GET = 'gcloud.taskflow3.models.TaskFlowInstance.objects.get'
TASKINSTANCE_FORMAT_STATUS = 'gcloud.taskflow3.models.TaskFlowInstance.format_pipeline_status'
TASKINSTANCE_EXTEN_CLASSIFIED_COUNT = 'gcloud.contrib.analysis.analyse_items.task_flow_instance.dispatch'
TASKINSTANCE_PREVIEW_TREE = 'gcloud.taskflow3.models.TaskFlowInstance.objects.preview_pipeline_tree_exclude_task_nodes'
TASKINSTANCE_OBJECTS_CALLBACK = 'gcloud.taskflow3.models.TaskFlowInstance.objects.callback'
TASKINSTANCE_CALLBACK = 'gcloud.taskflow3.models.TaskFlowInstance.callback'
TASKINSTANCE_HAS_NODE = 'gcloud.taskflow3.models.TaskFlowInstance.has_node'

PERIODIC_TASK_FILTER = 'gcloud.periodictask.models.PeriodicTask.objects.filter'
PERIODIC_TASK_GET = 'gcloud.periodictask.models.PeriodicTask.objects.get'
PERIODIC_TASK_CREATE = 'gcloud.periodictask.models.PeriodicTask.objects.create'
PERIODIC_TASK_PIPELINE_PERIODIC_TASK_CREATE_TASK = 'gcloud.periodictask.models.PipelinePeriodicTask.objects.create_task'

PERIODIC_TASK_HISTORY_CREATE = 'gcloud.periodictask.models.PeriodicTaskHistory.objects.create'

APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE = 'gcloud.apigw.views.create_task.jsonschema.validate'
APIGW_CREATE_TASK_NODE_NAME_HANDLE = 'gcloud.apigw.views.create_task.pipeline_node_name_handle'
APIGW_CREATE_TASK_VALIDATE_WEB_PIPELINE_TREE = 'gcloud.apigw.views.create_task.validate_web_pipeline_tree'
APIGW_CREATE_PERIODIC_TASK_JSON_SCHEMA_VALIDATE = 'gcloud.apigw.views.create_periodic_task.jsonschema.validate'
APIGW_CREATE_PERIODIC_TASK_REPLACE_TEMPLATE_ID = 'gcloud.apigw.views.create_periodic_task.replace_template_id'
APIGW_GET_TASK_STATUS_PIPELINE_API_GET_STATUS_TREE = 'gcloud.apigw.views.get_task_status.pipeline_api.get_status_tree'
APIGW_IMPORT_COMMON_TEMPLATE_READ_ENCODED_TEMPLATE_DATA = 'gcloud.apigw.views.import_common_template.read_encoded_template_data'  # noqa
APIGW_GET_PLUGIN_LIST_COMPONENT_MODEL_FILTER = 'gcloud.apigw.views.get_plugin_list.ComponentModel.objects.filter'
APIGW_GET_PLUGIN_LIST_COMPONENT_LIBRARY_GET_COMPONENT_CLS = 'gcloud.apigw.views.get_plugin_list.ComponentLibrary.get_component_class'  # noqa
APIGW_GET_USER_PROJECT_LIST_GET_USER_BUSINESS_LIST = 'gcloud.apigw.views.get_user_project_list.get_user_business_list'
APIGW_GET_USER_PROJECT_DETAIL_GET_BUSINESS_DETAIL = 'gcloud.apigw.views.get_user_project_detail.get_business_detail'
APIGW_PREVIEW_TASK_TREE_PREVIEW_TEMPLATE_TREE = 'gcloud.apigw.views.preview_task_tree.preview_template_tree'
APIGW_DECORATOR_CHECK_WHITE_LIST = 'gcloud.apigw.decorators.check_white_apps'
APIGW_DECORATOR_GET_USER_MODEL = 'gcloud.apigw.decorators.get_user_model'
APIGW_DECORATOR_BUSINESS_EXIST = 'gcloud.apigw.decorators.business_exist'

MAIN_PACKAGE_SOURCE_GET = 'gcloud.external_plugins.models.main_source.MainPackageSource.objects.get'

ROOT_PACKAGES_CREATE_PACKAGES_FOR_SOURCE = \
    'gcloud.external_plugins.models.sync_base.RootPackage.objects.create_packages_for_source'
ROOT_PACKAGES_DELETE_PACKAGES_IN_SOURCE = \
    'gcloud.external_plugins.models.sync_base.RootPackage.objects.delete_packages_in_source'
ROOT_PACKAGES_PACKAGES_FOR_SOURCE = 'gcloud.external_plugins.models.sync_base.RootPackage.objects.packages_for_source'

GIT_REPO_SOURCE_GET = 'gcloud.external_plugins.models.sync_source.GitRepoSyncSource.objects.get'

CORE_PROJECT_GET_USER_BUSINESS_LIST = 'gcloud.core.project.get_user_business_list'

CORE_MODEL_BUSINESS_UPDATE_OR_CREATE = 'gcloud.core.models.Business.objects.update_or_create'

CORE_MODEL_PROJECT_SYNC_PROJECT = 'gcloud.core.models.Project.objects.sync_project_from_cmdb_business'

CORE_MODEL_USER_DEFAULT_PROJECT_INIT_USER_DEFAULT_PROJECT = \
    'gcloud.core.models.UserDefaultProject.objects.init_user_default_project'

PIPELINE_TEMPLATE_WEB_WRAPPER_UNFOLD_SUBPROCESS = 'pipeline_web.wrapper.PipelineTemplateWebWrapper.unfold_subprocess'

PROJECT_RESOURCE_BATCH_REGISTER_INSTANCE = 'gcloud.core.permissions.project_resource.batch_register_instance'

GCLOUD_CONTRIB_AUTH_BACKEND_UTILS_RESOURCE_ID_FOR = 'gcloud.contrib.auth.backend.utils.resource_id_for'
GCLOUD_CONTRIB_AUTH_BACKEND_UTILS_RESOURCE_ACTIONS_FOR = 'gcloud.contrib.auth.backend.utils.resource_actions_for'
GCLOUD_CONTRIB_AUTH_BACKEND_GET_USER_MODEL = 'gcloud.contrib.auth.backend.get_user_model'
