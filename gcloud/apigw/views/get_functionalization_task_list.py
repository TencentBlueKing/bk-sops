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
from django.views.decorators.http import require_GET

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, return_json_response, timezone_inject
from gcloud.apigw.forms.get_functionalization_task_list import GetFunctionalizationTaskListForm
from gcloud.apigw.views.utils import format_function_task_list_data, paginate_list_data
from gcloud.contrib.function.models import FunctionTask
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import FunctionViewInterceptor


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@timezone_inject
@iam_intercept(FunctionViewInterceptor())
def get_functionalization_task_list(request):
    params_validator = GetFunctionalizationTaskListForm(data=request.GET)
    if not params_validator.is_valid():
        return {"result": False, "data": "", "message": params_validator.errors, "code": err_code.VALIDATION_ERROR.code}
    param_mappings = {
        "id_in": "id__in",
        "task_id_in": "task_id__in",
        "status": "status",
        "project_id": "task__project_id",
        "create_time_lte": "create_time__lte",
        "create_time_gte": "create_time__gte",
        "task__project__tenant_id": request.app.tenant_id,
    }
    filter_kwargs = {}
    for param, filter_key in param_mappings.items():
        param_value = params_validator.cleaned_data.get(param)
        if param_value:
            filter_kwargs[filter_key] = param_value

    function_tasks = FunctionTask.objects.select_related("task").filter(**filter_kwargs)
    try:
        function_tasks, count = paginate_list_data(request, function_tasks)
    except Exception as e:
        return {"result": False, "data": "", "message": e, "code": err_code.INVALID_OPERATION.code}
    data = format_function_task_list_data(function_tasks, tz=request.tz)

    response = {"result": True, "data": data, "count": count, "code": err_code.SUCCESS.code}
    return response
