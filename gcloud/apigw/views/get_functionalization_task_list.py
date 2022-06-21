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
from django.views.decorators.http import require_GET

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, timezone_inject, return_json_response
from gcloud.contrib.function.models import FunctionTask
from gcloud.apigw.views.utils import logger, format_function_task_list_data, paginate_list_data
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import FunctionViewInterceptor
from apigw_manager.apigw.decorators import apigw_require


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@timezone_inject
@iam_intercept(FunctionViewInterceptor())
def get_functionalization_task_list(request):
    id_in = request.GET.get("id_in")
    task_id_in = request.GET.get("task_id_in")
    status = request.GET.get("status")
    if id_in:
        try:
            id_in = id_in.split(",")
        except Exception:
            id_in = None
            logger.exception("[API] get_functionalization_task_list id_in[{}] resolve fail, ignore.".format(id_in))
    if task_id_in:
        try:
            task_id_in = task_id_in.split(",")
        except Exception:
            task_id_in = None
            logger.exception(
                "[API] get_functionalization_task_list task_id_in[{}] resolve fail, ignore.".format(task_id_in)
            )

    filter_kwargs = {}
    if status:
        filter_kwargs["status"] = status
    if id_in:
        filter_kwargs["id__in"] = id_in
    if task_id_in:
        filter_kwargs["task__id__in"] = task_id_in

    function_tasks = FunctionTask.objects.select_related("task").filter(**filter_kwargs)
    try:
        function_tasks, count = paginate_list_data(request, function_tasks)
    except Exception as e:
        return {"result": False, "data": "", "message": e, "code": err_code.INVALID_OPERATION.code}
    data = format_function_task_list_data(function_tasks, tz=request.tz)

    response = {"result": True, "data": data, "count": count, "code": err_code.SUCCESS.code}
    return response
