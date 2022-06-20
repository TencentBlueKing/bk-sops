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
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, return_json_response
from gcloud.apigw.decorators import project_inject
from gcloud.periodictask.models import PeriodicTask
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import PeriodicTaskEditInterceptor
from apigw_manager.apigw.decorators import apigw_require


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(PeriodicTaskEditInterceptor())
def modify_cron_for_periodic_task(request, task_id, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return {"result": False, "message": "invalid json format", "code": err_code.REQUEST_PARAM_INVALID.code}

    project = request.project
    cron = params.get("cron", {})
    tz = project.time_zone

    try:
        task = PeriodicTask.objects.get(id=task_id, project_id=project.id)
    except PeriodicTask.DoesNotExist:
        return {
            "result": False,
            "message": "task(%s) does not exist" % task_id,
            "code": err_code.CONTENT_NOT_EXIST.code,
        }

    try:
        task.modify_cron(cron, tz)
    except Exception as e:
        return {"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code}

    return {"result": True, "data": {"cron": task.cron}, "code": err_code.SUCCESS.code}
