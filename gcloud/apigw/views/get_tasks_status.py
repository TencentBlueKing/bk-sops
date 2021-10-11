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

import ujson as json
from cachetools import cached, TTLCache

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.utils import api_hash_key
from gcloud.utils.dates import format_datetime
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.domains.dispatchers import TaskCommandDispatcher
from gcloud.taskflow3.utils import add_node_name_to_status_tree
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import ProjectViewInterceptor
from packages.bkoauth.decorators import apigw_required


@csrf_exempt
@login_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@iam_intercept(ProjectViewInterceptor())
@cached(cache=TTLCache(maxsize=1024, ttl=10), key=api_hash_key)
def get_tasks_status(request, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return {
            "result": False,
            "message": "request body is not a valid json",
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }

    task_ids = params.get("task_id_list", [])
    if not isinstance(task_ids, list):
        return {"result": False, "message": "task_id_list must be a list", "code": err_code.REQUEST_PARAM_INVALID.code}
    include_children_status = params.get("include_children_status", False)

    tasks = TaskFlowInstance.objects.filter(id__in=task_ids, project__id=request.project.id)

    data = []
    for task in tasks:
        dispatcher = TaskCommandDispatcher(
            engine_ver=task.engine_ver,
            taskflow_id=task.id,
            pipeline_instance=task.pipeline_instance,
            project_id=project_id,
        )
        result = dispatcher.get_task_status()
        if not result["result"]:
            return result

        status = result["data"]
        if not include_children_status and "children" in status:
            status.pop("children")

        if "name" not in status:
            add_node_name_to_status_tree(task.pipeline_instance.execution_data, status.get("children", {}))
        status["name"] = task.name

        data.append(
            {
                "id": task.id,
                "name": task.name,
                "status": status,
                "flow_type": task.flow_type,
                "current_flow": task.current_flow,
                "is_deleted": task.is_deleted,
                "create_time": format_datetime(task.create_time),
                "start_time": format_datetime(task.start_time),
                "finish_time": format_datetime(task.finish_time),
                "url": task.url,
            }
        )

    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
