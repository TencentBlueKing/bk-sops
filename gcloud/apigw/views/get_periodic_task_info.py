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
from gcloud.apigw.decorators import mark_request_whether_is_trust, return_json_response
from gcloud.apigw.decorators import project_inject
from gcloud.periodictask.models import PeriodicTask
from gcloud.apigw.views.utils import info_data_from_period_task
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import GetPeriodicTaskInfoInterceptor
from apigw_manager.apigw.decorators import apigw_require
from gcloud.apigw.serializers import IncludeTaskSerializer


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(GetPeriodicTaskInfoInterceptor())
def get_periodic_task_info(request, task_id, project_id):
    serializer = IncludeTaskSerializer(data=request.GET)
    if not serializer.is_valid():
        return {"result": False, "message": serializer.errors, "code": err_code.REQUEST_PARAM_INVALID.code}
    include_edit_info = serializer.validated_data["include_edit_info"]
    project = request.project
    try:
        task = PeriodicTask.objects.get(id=task_id, project_id=project.id)
    except PeriodicTask.DoesNotExist:
        return {
            "result": False,
            "message": "task(%s) does not exist" % task_id,
            "code": err_code.CONTENT_NOT_EXIST.code,
        }

    data = info_data_from_period_task(task, include_edit_info=include_edit_info)
    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
