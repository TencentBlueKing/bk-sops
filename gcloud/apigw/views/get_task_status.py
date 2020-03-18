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


from django.http import JsonResponse
from django.views.decorators.http import require_GET

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import api_verify_perms
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.permissions import taskflow_resource
from pipeline.engine import api as pipeline_api
from gcloud.apigw.views.utils import logger

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_perms(
    taskflow_resource,
    [taskflow_resource.actions.view],
    get_kwargs={"task_id": "id", "project_id": "project_id"},
)
def get_task_status(request, task_id, project_id):
    project = request.project
    try:
        task = TaskFlowInstance.objects.get(
            pk=task_id, project_id=project.id, is_deleted=False
        )
        task_status = task.get_status()
        result = {"result": True, "data": task_status, "code": err_code.SUCCESS.code}
        return JsonResponse(result)
    # 请求子流程的状态，直接通过pipeline api查询
    except (ValueError, TaskFlowInstance.DoesNotExist):
        logger.info("task[id=%s] does not exist" % task_id)
    except Exception as e:
        message = "task[id={task_id}] get status error: {error}".format(
            task_id=task_id, error=e
        )
        logger.error(message)
        result = {
            "result": False,
            "message": message,
            "code": err_code.UNKNOW_ERROR.code,
        }
        return JsonResponse(result)

    try:
        task_status = pipeline_api.get_status_tree(task_id, max_depth=99)
        TaskFlowInstance.format_pipeline_status(task_status)
    except Exception as e:
        message = "task[id={task_id}] get status error: {error}".format(
            task_id=task_id, error=e
        )
        logger.error(message)
        result = {
            "result": False,
            "message": message,
            "code": err_code.UNKNOW_ERROR.code,
        }
        return JsonResponse(result)
    result = {"result": True, "data": task_status, "code": err_code.SUCCESS.code}
    return JsonResponse(result)
