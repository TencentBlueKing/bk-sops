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
from blueapps.account.decorators import login_exempt
from django.db.models import Value
from django.views.decorators.http import require_GET

from gcloud import err_code
from gcloud.apigw.decorators import (
    mark_request_whether_is_trust,
    project_inject,
    return_json_response,
    timezone_inject,
    validate_project_access,
)
from gcloud.apigw.forms import GetTaskListForm
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import ProjectViewInterceptor
from gcloud.taskflow3.models import TaskFlowInstance


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@validate_project_access
@timezone_inject
@iam_intercept(ProjectViewInterceptor())
def get_task_count(request, project_id):
    project = request.project
    params_validator = GetTaskListForm(data=request.GET)
    if not params_validator.is_valid():
        return {"result": False, "data": "", "message": params_validator.errors, "code": err_code.VALIDATION_ERROR.code}
    param_mappings = {
        "keyword": "pipeline_instance__name__contains",
        "is_started": "pipeline_instance__is_started",
        "is_finished": "pipeline_instance__is_finished",
        "executor": "pipeline_instance__executor",
        "create_method": "create_method",
        "template_id": "template_id",
    }
    filter_kwargs = dict(is_deleted=Value(0), project_id=project.id)
    for param, filter_key in param_mappings.items():
        if param in request.GET:
            filter_kwargs[filter_key] = params_validator.cleaned_data[param]

    tasks = TaskFlowInstance.objects.select_related("pipeline_instance").filter(**filter_kwargs)

    try:
        count = tasks.count()
    except Exception as e:
        return {"result": False, "data": "", "message": e, "code": err_code.INVALID_OPERATION.code}

    response = {
        "result": True,
        "data": {"count": count},
        "code": err_code.SUCCESS.code,
    }
    return response
