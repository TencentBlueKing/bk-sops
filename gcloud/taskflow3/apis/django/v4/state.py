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

import logging

from django.http.response import JsonResponse
from django.views.decorators.http import require_GET

from gcloud import err_code
from gcloud.taskflow3.apis.django.validators import StatusValidator
from gcloud.taskflow3.domains.dispatchers import TaskCommandDispatcher
from gcloud.utils.decorators import request_validate
from gcloud.taskflow3.models import TaskFlowInstance

logger = logging.getLogger("root")


@require_GET
@request_validate(StatusValidator)
def root_state(request, project_id):
    instance_id = request.GET.get("instance_id")
    subprocess_id = request.GET.get("subprocess_id")

    try:
        task = TaskFlowInstance.objects.get(pk=instance_id, project_id=project_id, is_deleted=False)
    except Exception as e:
        message = "task[id={task_id}] get status error: {error}".format(task_id=instance_id, error=e)
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
        project_id=project_id,
    )

    result = dispatcher.get_task_status(subprocess_id=subprocess_id)
    if not result["result"]:
        return JsonResponse(result)

    result["data"] = {"state": result["data"]["state"]}
    return JsonResponse(result)
