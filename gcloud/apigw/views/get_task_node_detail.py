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
from django.views.decorators.http import require_GET

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.apigw.views.utils import logger
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskViewInterceptor
from packages.bkoauth.decorators import apigw_required


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskViewInterceptor())
def get_task_node_detail(request, task_id, project_id):
    """
    @summary: 获取节点输入输出
    @param request:
    @param task_id:
    @param project_id:
    @return:
    """
    project = request.project
    try:
        task = TaskFlowInstance.objects.get(id=task_id, project_id=project.id)
    except TaskFlowInstance.DoesNotExist:
        message = (
            "[API] get_task_node_detail task[id={task_id}] "
            "of project[project_id={project_id}, biz_id{biz_id}] does not exist".format(
                task_id=task_id, project_id=project.id, biz_id=project.bk_biz_id
            )
        )
        logger.exception(message)
        return {"result": False, "message": message, "code": err_code.CONTENT_NOT_EXIST.code}

    node_id = request.GET.get("node_id")
    component_code = request.GET.get("component_code")

    try:
        subprocess_stack = json.loads(request.GET.get("subprocess_stack", "[]"))
    except Exception:
        return {
            "result": False,
            "message": "subprocess_stack is not a valid array json",
            "code": err_code.UNKNOWN_ERROR.code,
        }
    result = task.get_node_detail(
        node_id=node_id,
        username=request.user.username,
        component_code=component_code,
        subprocess_stack=subprocess_stack,
        project_id=project_id,
    )
    return result
