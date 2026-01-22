# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from apigw_manager.apigw.decorators import apigw_require
from bamboo_engine import states as bamboo_engine_states
from blueapps.account.decorators import login_exempt
from cachetools import TTLCache
from django.views.decorators.http import require_GET

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, mcp_apigw, project_inject, return_json_response
from gcloud.apigw.utils import BucketTTLCache, api_bucket_and_key, bucket_cached
from gcloud.apigw.views.utils import logger
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskViewInterceptor
from gcloud.taskflow3.domains.dispatchers import TaskCommandDispatcher
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.utils import add_node_name_to_status_tree, extract_nodes_by_statuses, get_failed_nodes_info


def cache_decisioner(key, value):
    if not value["result"]:
        return False

    if value["data"]["state"] == "CREATED":
        return False

    return True


@login_exempt
@require_GET
@apigw_require
@mcp_apigw()
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskViewInterceptor())
@bucket_cached(
    BucketTTLCache(TTLCache, {"maxsize": 1024, "ttl": 10}, decisioner=cache_decisioner),
    bucket_and_key_func=api_bucket_and_key,
)
def get_task_status(request, task_id, project_id):
    project = request.project
    subprocess_id = request.GET.get("subprocess_id")
    with_ex_data = request.GET.get("with_ex_data")
    with_failed_node_info = request.GET.get("with_failed_node_info")
    with_auto_retry_status = request.GET.get("with_auto_retry_status")

    try:
        task = TaskFlowInstance.objects.get(pk=task_id, project_id=project.id, is_deleted=False)
    except Exception as e:
        message = "task[id={task_id}] get status error: {error}".format(task_id=task_id, error=e)
        logger.exception(message)
        return {
            "result": False,
            "message": message,
            "code": err_code.UNKNOWN_ERROR.code,
        }

    dispatcher = TaskCommandDispatcher(
        engine_ver=task.engine_ver,
        taskflow_id=task.id,
        pipeline_instance=task.pipeline_instance,
        project_id=project.id,
    )
    result = dispatcher.get_task_status(subprocess_id=subprocess_id, with_ex_data=with_ex_data)
    if not result["result"]:
        return result

    # add node name
    if "name" not in result["data"]:
        try:
            add_node_name_to_status_tree(task.pipeline_instance.execution_data, result["data"].get("children", {}))
        except Exception as e:
            message = "task[id={task_id}] add node name error: {error}".format(task_id=task_id, error=e)
            logger.exception(message)
            return {
                "result": False,
                "message": message,
                "code": err_code.UNKNOWN_ERROR.code,
            }

    if with_failed_node_info or with_auto_retry_status:
        try:
            status_tree, root_pipeline_id = result["data"], result["data"]["id"]
            failed_node_ids = extract_nodes_by_statuses(status_tree, statuses=[bamboo_engine_states.FAILED])
            failed_node_info = get_failed_nodes_info(root_pipeline_id, failed_node_ids)
            if with_failed_node_info:
                result["data"]["failed_node_info"] = failed_node_info
            if with_auto_retry_status:
                auto_retry_waiting_nodes = [
                    node_id
                    for node_id, failed_info in failed_node_info.items()
                    if "max_auto_retry_times" in failed_info
                    and failed_info["auto_retry_times"] < failed_info["max_auto_retry_times"]
                ]
                result["data"]["auto_retry_status"] = {
                    "exist_auto_retry_nodes": True if len(auto_retry_waiting_nodes) else False,
                    "auto_retry_nodes": auto_retry_waiting_nodes,
                }
        except Exception as e:
            logger.error(
                "task[id={task_id}] extract failed node info error, get_task_status result: {result}".format(
                    task_id=task_id, result=result
                )
            )
            message = "task[id={task_id}] extract failed node info error: {error}".format(task_id=task_id, error=e)
            logger.exception(message)
            return {
                "result": False,
                "message": message,
                "code": err_code.UNKNOWN_ERROR.code,
            }

    result["data"]["name"] = task.name

    return result
