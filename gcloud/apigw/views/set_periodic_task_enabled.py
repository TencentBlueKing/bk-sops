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

from django.utils.translation import ugettext_lazy as _
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
def set_periodic_task_enabled(request, task_id, project_id):
    project = request.project
    try:
        params = json.loads(request.body)
    except Exception:
        return {"result": False, "message": _("非法请求: 数据错误, 请求不是合法的Json格式"), "code": err_code.REQUEST_PARAM_INVALID.code}

    enabled = params.get("enabled", False)

    try:
        task = PeriodicTask.objects.get(id=task_id, project_id=project.id)
    except PeriodicTask.DoesNotExist:
        return {
            "result": False,
            "message": "task(%s) does not exist" % task_id,
            "code": err_code.CONTENT_NOT_EXIST.code,
        }

    task.set_enabled(enabled)
    return {"result": True, "data": {"enabled": task.enabled}, "code": err_code.SUCCESS.code}
