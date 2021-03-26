# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

PIPELINE_CORE_GATEWAY_DEFORMAT = "pipeline.core.flow.gateway.deformat_constant_key"
PIPELINE_CORE_CONSTANT_RESOLVE = "pipeline.core.data.expression.ConstantTemplate.resolve_data"

PIPELINE_STATUS_GET = "pipeline.engine.models.Status.objects.get"
PIPELINE_STATUS_FAIL = "pipeline.engine.models.Status.objects.fail"
PIPELINE_STATUS_RAW_FAIL = "pipeline.engine.models.Status.objects.raw_fail"
PIPELINE_STATUS_RETRY = "pipeline.engine.models.Status.objects.retry"
PIPELINE_STATUS_SKIP = "pipeline.engine.models.Status.objects.skip"
PIPELINE_STATUS_FINISH = "pipeline.engine.models.Status.objects.finish"
PIPELINE_STATUS_FILTER = "pipeline.engine.models.Status.objects.filter"
PIPELINE_STATUS_TRANSIT = "pipeline.engine.models.Status.objects.transit"
PIPELINE_STATUS_STATE_FOR = "pipeline.engine.models.Status.objects.state_for"
PIPELINE_STATUS_STATES_FOR = "pipeline.engine.models.Status.objects.states_for"
PIPELINE_STATUS_SELECT_FOR_UPDATE = "pipeline.engine.models.Status.objects.select_for_update"
PIPELINE_STATUS_PREPARE_FOR_PIPELINE = "pipeline.engine.models.Status.objects.prepare_for_pipeline"
PIPELINE_STATUS_RECOVER_FROM_BLOCK = "pipeline.engine.models.Status.objects.recover_from_block"
PIPELINE_STATUS_VERSION_FOR = "pipeline.engine.models.Status.objects.version_for"
PIPELINE_STATUS_BATCH_TRANSIT = "pipeline.engine.models.Status.objects.batch_transit"

PIPELINE_PROCESS_GET = "pipeline.engine.models.PipelineProcess.objects.get"
PIPELINE_PROCESS_FILTER = "pipeline.engine.models.PipelineProcess.objects.filter"
PIPELINE_PROCESS_SELECT_FOR_UPDATE = "pipeline.engine.models.PipelineProcess.objects.select_for_update"
PIPELINE_PROCESS_FORK_CHILD = "pipeline.engine.models.PipelineProcess.objects.fork_child"
PIPELINE_PROCESS_PREPARE_FOR_PIPELINE = "pipeline.engine.models.PipelineProcess.objects.prepare_for_pipeline"
PIPELINE_PROCESS_BATCH_PROCESS_READY = "pipeline.engine.models.PipelineProcess.objects.batch_process_ready"
PIPELINE_PROCESS_PROCESS_READY = "pipeline.engine.models.PipelineProcess.objects.process_ready"
PIPELINE_PROCESS_ADJUST_STATUS = "pipeline.engine.models.PipelineProcess.adjust_status"
PIPELINE_PROCESS_CHILD_PROCESS_READY = "pipeline.engine.models.PipelineProcess.objects.child_process_ready"
PIPELINE_PROCESS_DESTROY = "pipeline.engine.models.PipelineProcess.destroy"
PIPELINE_PROCESS_BLOCKED_BY_FAILURE = "pipeline.engine.models.PipelineProcess.blocked_by_failure_or_suspended"

PIPELINE_SCHEDULE_SERVICE_FILTER = "pipeline.engine.models.ScheduleService.objects.filter"
PIPELINE_SCHEDULE_SERVICE_GET = "pipeline.engine.models.ScheduleService.objects.get"
PIPELINE_SCHEDULE_SERVICE_SET_SCHEDULE = "pipeline.engine.models.ScheduleService.objects.set_schedule"
PIPELINE_SCHEDULE_SCHEDULE_FOR = "pipeline.engine.models.ScheduleService.objects.schedule_for"
PIPELINE_SCHEDULE_DELETE_SCHEDULE = "pipeline.engine.models.ScheduleService.objects.delete_schedule"

PIPELINE_DATA_GET = "pipeline.engine.models.Data.objects.get"
PIPELINE_DATA_FILTER = "pipeline.engine.models.Data.objects.filter"
PIPELINE_DATA_WRITE_NODE_DATA = "pipeline.engine.models.Data.objects.write_node_data"
PIPELINE_DATA_FORCED_FAIL = "pipeline.engine.models.Data.objects.forced_fail"
PIPELINE_DATA_WIRTE_EX_DATA = "pipeline.engine.models.Data.objects.write_ex_data"

PIPELINE_NODE_RELATIONSHIP_BUILD = "pipeline.engine.models.NodeRelationship.objects.build_relationship"
PIPELINE_NODE_RELATIONSHIP_FILTER = "pipeline.engine.models.NodeRelationship.objects.filter"

PIPELINE_CELERYTASK_BIND = "pipeline.engine.models.ProcessCeleryTask.objects.bind"
PIPELINE_CELERYTASK_UNBIND = "pipeline.engine.models.ProcessCeleryTask.objects.unbind"
PIPELINE_CELERYTASK_REVOKE = "pipeline.engine.models.ProcessCeleryTask.objects.revoke"
PIPELINE_CELERYTASK_DESTROY = "pipeline.engine.models.ProcessCeleryTask.objects.destroy"

PIPELINE_NODE_CELERYTASK_DESTROY = "pipeline.engine.models.NodeCeleryTask.objects.destroy"

PIPELINE_FUNCTION_SWITCH_IS_FROZEN = "pipeline.engine.models.FunctionSwitch.objects.is_frozen"

PIPELINE_MODELS_TASK_SERVICE_RUN_PIPELINE = "pipeline.models.task_service.run_pipeline"
PIPELINE_MODELS_POST_PIPELINE_FINISH = "pipeline.models.post_pipeline_finish"
PIPELINE_MODELS_POST_PIPELINE_REVOKE = "pipeline.models.post_pipeline_revoke"

PIPELINE_PIPELINE_INSTANCE_CALCULATE_TREE_INFO = "pipeline.models.PipelineInstance.calculate_tree_info"
PIPELINE_PIPELINE_INSTANCE_IMPORT_STRING = "pipeline.models.import_string"

PIPELINE_PIPELINE_MODEL_GET = "pipeline.engine.models.PipelineModel.objects.get"
PIPELINE_PIPELINE_MODEL_PREPARE_FOR_PIPELINE = "pipeline.engine.models.PipelineModel.objects.prepare_for_pipeline"
PIPELINE_PIPELINE_MODEL_PIPELINE_READY = "pipeline.engine.models.PipelineModel.objects.pipeline_ready"

PIPELINE_SUBPROCESS_RELATIONSHIP_GET_RELATE_PROCESS = (
    "pipeline.engine.models.SubProcessRelationship.objects." "get_relate_process"
)

PIPELINE_HISTORY_GET_HISTORY = "pipeline.engine.models.History.objects.get_histories"
PIPELINE_HISTORY_RECORD = "pipeline.engine.models.History.objects.record"
PIPELINE_HISTORY_LINK_HISTORY = "pipeline.engine.models.LogEntry.objects.link_history"

PIPELINE_ENGINE_API_WORKERS = "pipeline.engine.api.workers"
PIPELINE_ENGINE_API_GET_PROCESS_TO_BE_WAKED = "pipeline.engine.api._get_process_to_be_waked"

PIPELINE_ENGINE_CORE_DATA_DEL_OBJECT = "pipeline.engine.core.data.del_object"
PIPELINE_ENGINE_CORE_DATA_GET_OBJECT = "pipeline.engine.core.data.get_object"
PIPELINE_ENGINE_CORE_DATA_SET_OBJECT = "pipeline.engine.core.data.set_object"

PIPELINE_ENGINE_CORE_API_WORKERS = "pipeline.engine.core.api.workers"

SCHEDULE_GET_SCHEDULE_PARENT_DATA = "pipeline.engine.core.schedule.get_schedule_parent_data"
SCHEDULE_DELETE_PARENT_DATA = "pipeline.engine.core.schedule.delete_parent_data"
SCHEDULE_SET_SCHEDULE_DATA = "pipeline.engine.core.schedule.set_schedule_data"

ENGINE_ACTIVITY_FAIL_SIGNAL = "pipeline.engine.signals.activity_failed.send"
ENGINE_SIGNAL_TIMEOUT_START_SEND = "pipeline.engine.signals.service_activity_timeout_monitor_start.send"
ENGINE_SIGNAL_TIMEOUT_END_SEND = "pipeline.engine.signals.service_activity_timeout_monitor_end.send"
ENGINE_SIGNAL_ACT_SCHEDULE_FAIL_SEND = "pipeline.engine.signals.service_schedule_fail.send"
ENGINE_SIGNAL_ACT_SCHEDULE_SUCCESS_SEND = "pipeline.engine.signals.service_schedule_success.send"

ENGINE_SIGNAL_NODE_RETRY_READY = "pipeline.engine.signals.node_retry_ready"
ENGINE_SIGNAL_NODE_SKIP_CALL = "pipeline.engine.signals.node_skip_call"

ENGINE_SCHEDULE = "pipeline.engine.core.schedule.schedule"
ENGINE_API_FORCED_FAIL = "pipeline.engine.api.forced_fail"
ENGINE_RUN_LOOP = "pipeline.engine.core.runtime.run_loop"
ENGINE_TASKS_WAKE_UP_APPLY = "pipeline.engine.tasks.wake_up.apply_async"

SIGNAL_VALVE_SEND = "pipeline.django_signal_valve.valve.send"

SUBPROCESS_HYDRATE_NODE_DATA = "pipeline.engine.core.handlers.subprocess.hydrate_node_data"
SUBPROCESS_HYDRATE_DATA = "pipeline.engine.core.handlers.subprocess.hydrate_data"

SERVICE_ACT_HYDRATE_NODE_DATA = "pipeline.engine.core.handlers.service_activity.hydrate_node_data"
SERVICE_ACT_HYDRATE_DATA = "pipeline.engine.core.handlers.service_activity.hydrate_data"

EXG_HYDRATE_NODE_DATA = "pipeline.engine.core.handlers.exclusive_gateway.hydrate_node_data"
EXG_HYDRATE_DATA = "pipeline.engine.core.handlers.exclusive_gateway.hydrate_data"

CPG_HYDRATE_DATA = "pipeline.engine.core.handlers.conditional_parallel.hydrate_data"

ENGINE_HANDLERS_END_EVENT_HANDLE = "pipeline.engine.core.handlers.endevent.base.EndEventHandler.handle"
UTILS_IMPORTER_BASE_EXECUTE_SRC_CODE = "pipeline.utils.importer.base.NonstandardModuleImporter._execute_src_code"
UTILS_IMPORTER_GIT__FETCH_REPO_FILE = "pipeline.utils.importer.git.GitRepoModuleImporter._fetch_repo_file"
UTILS_IMPORTER_GIT__FILE_URL = "pipeline.utils.importer.git.GitRepoModuleImporter._file_url"
UTILS_IMPORTER_GIT_GET_SOURCE = "pipeline.utils.importer.git.GitRepoModuleImporter.get_source"
UTILS_IMPORTER_GIT_GET_FILE = "pipeline.utils.importer.git.GitRepoModuleImporter.get_file"
UTILS_IMPORTER_GIT_IS_PACKAGE = "pipeline.utils.importer.git.GitRepoModuleImporter.is_package"

APPS_SETTINGS = "pipeline.apps.settings"
APPS_SENTINEL = "pipeline.apps.Sentinel"


ENGINE_DATA_API_SETTINGS = "pipeline.engine.core.data.api.settings"
ENGINE_DATA_API_IMPORT_BACKEND = "pipeline.engine.core.data.api._import_backend"
ENGINE_DATA_API_BACKEND = "pipeline.engine.core.data.api._backend"
ENGINE_DATA_API_CANDIDATE_BACKEND = "pipeline.engine.core.data.api._candidate_backend"

ENGINE_HEALTH_ZOMBIE_HEAL_DEFAULT_SETTINGS = "pipeline.engine.health.zombie.heal.default_settings"

DJCELERY_APP_CURRENT_APP_CONNECTION = "celery.current_app.connection"
