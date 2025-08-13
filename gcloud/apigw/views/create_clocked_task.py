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

import ujson as json
from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.exceptions import ValidationError

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.apigw.validators import CreateTaskValidator
from gcloud.apigw.views.utils import logger
from gcloud.clocked_task.models import ClockedTask
from gcloud.clocked_task.serializer import ClockedTaskSerializer
from gcloud.constants import PROJECT
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw.create_clocked_task import CreateClockedTaskInterceptor
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.utils.decorators import request_validate


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@request_validate(CreateTaskValidator)
@iam_intercept(CreateClockedTaskInterceptor())
def create_clocked_task(request, template_id, project_id):
    project = request.project
    request_params = json.loads(request.body)
    logger.info(
        "[API] apigw create_clocked_task info, "
        "template_id: {template_id}, project_id: {project_id}, params: {params}".format(
            template_id=template_id, project_id=project.id, params=request_params
        )
    )

    # 计划任务目前仅支持项目流程模板创建
    try:
        template = TaskTemplate.objects.get(
            pk=template_id, project_id=project.id, is_deleted=False, project__tenant_id=request.user.tenant_id
        )
    except TaskTemplate.DoesNotExist:
        result = {
            "result": False,
            "message": "template[id={template_id}] of project[project_id={project_id} , biz_id{biz_id}] "
            "does not exist".format(
                template_id=template_id,
                project_id=project.id,
                biz_id=project.bk_biz_id,
            ),
            "code": err_code.CONTENT_NOT_EXIST.code,
        }
        return result

    try:
        params = {
            "template_id": template_id,
            "project_id": project.id,
            "template_name": template.name,
            "template_source": PROJECT,
            "task_parameters": {"constants": {}, "template_schemes_id": []},
        }
        params.update(request_params)

        serializer = ClockedTaskSerializer(data=params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
    except ValidationError as e:
        result = {
            "result": False,
            "message": "params is invalid, error: {error}".format(error=e.detail),
            "code": err_code.VALIDATION_ERROR.code,
        }
        return result

    task = ClockedTask.objects.create_task(**validated_data, creator=request.user.username)
    response_serializer = ClockedTaskSerializer(instance=task)
    response_data = response_serializer.data
    response_data.pop("clocked_task_id")

    return {"result": True, "data": response_data, "code": err_code.SUCCESS.code}
