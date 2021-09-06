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

import logging

from django.http.response import JsonResponse
from django.views.decorators.http import require_GET

from pipeline.engine import exceptions, states
from pipeline.engine import api as pipeline_api
from gcloud import err_code
from gcloud.utils.decorators import request_validate
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.validators import StatusValidator

logger = logging.getLogger("root")


@require_GET
@request_validate(StatusValidator)
def root_state(request, project_id):
    instance_id = request.GET.get("instance_id")
    subprocess_id = request.GET.get("subprocess_id")

    if not subprocess_id:
        try:
            task = TaskFlowInstance.objects.get(pk=instance_id, project_id=project_id)
            task_state = task.get_state()
            if "children" in task_state:
                task_state.pop("children")
            ctx = {"result": True, "data": task_state, "message": "", "code": err_code.SUCCESS.code}
            return JsonResponse(ctx)
        except exceptions.InvalidOperationException:
            ctx = {"result": True, "data": {"state": states.READY, "message": "", "code": err_code.SUCCESS.code}}
        except Exception as e:
            message = "taskflow[id=%s] get state error: %s" % (instance_id, e)
            logger.exception(message)
            ctx = {"result": False, "message": message, "data": None, "code": err_code.UNKNOWN_ERROR.code}
        return JsonResponse(ctx)

    # 请求子流程的状态，直接通过pipeline api查询
    try:
        task_status = pipeline_api.get_status_tree(subprocess_id, max_depth=99)
        task_state = TaskFlowInstance.get_state_tree_from_pipeline_status(task_status)
        if "children" in task_state:
            task_state.pop("children")
        ctx = {"result": True, "data": task_state, "message": "", "code": err_code.SUCCESS.code}
    # subprocess pipeline has not executed
    except exceptions.InvalidOperationException:
        ctx = {"result": True, "data": {"state": states.CREATED}, "message": "", "code": err_code.SUCCESS.code}
    except Exception as e:
        message = "taskflow[id=%s] get state error: %s" % (instance_id, e)
        logger.exception(message)
        ctx = {"result": False, "message": message, "data": None, "code": err_code.UNKNOWN_ERROR.code}

    return JsonResponse(ctx)
