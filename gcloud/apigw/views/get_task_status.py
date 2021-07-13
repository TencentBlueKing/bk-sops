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
from cachetools import TTLCache
from django.views.decorators.http import require_GET

from blueapps.account.decorators import login_exempt
from gcloud.apigw.utils import bucket_cached, BucketTTLCache, api_bucket_and_key

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.domains.dispatchers import TaskCommandDispatcher
from gcloud.taskflow3.utils import add_node_name_to_status_tree
from gcloud.apigw.views.utils import logger
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskViewInterceptor
from packages.bkoauth.decorators import apigw_required


def cache_decisioner(key, value):
    if not value["result"]:
        return False

    if value["data"]["state"] == "CREATED":
        return False

    return True


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskViewInterceptor())
@bucket_cached(
    BucketTTLCache(TTLCache, {"maxsize": 1024, "ttl": 60}, decisioner=cache_decisioner),
    bucket_and_key_func=api_bucket_and_key,
)
def get_task_status(request, task_id, project_id):
    project = request.project
    subprocess_id = request.GET.get("subprocess_id")
    with_ex_data = request.GET.get("with_ex_data")

    try:
        task = TaskFlowInstance.objects.get(pk=task_id, project_id=project.id, is_deleted=False)
    except Exception as e:
        message = "task[id={task_id}] get status error: {error}".format(task_id=task_id, error=e)
        logger.error(message)
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
        add_node_name_to_status_tree(task.pipeline_instance.execution_data, result["data"].get("children", {}))
    result["data"]["name"] = task.name

    return result
