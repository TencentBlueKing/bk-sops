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


import ujson as json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import api_verify_proj_perms
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.contrib.analysis.analyse_items import task_flow_instance
from gcloud.core.permissions import project_resource
from gcloud.apigw.views.utils import logger

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_proj_perms([project_resource.actions.view])
def query_task_count(request, project_id):
    """
    @summary: 按照不同维度统计业务任务总数
    @param request:
    @param project_id:
    @return:
    """
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse(
            {
                "result": False,
                "message": "invalid json format",
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )
    project = request.project
    conditions = params.get("conditions", {})
    group_by = params.get("group_by")
    if not isinstance(conditions, dict):
        message = (
            "query_task_list params conditions[%s] are invalid dict data" % conditions
        )
        logger.error(message)
        return JsonResponse(
            {
                "result": False,
                "message": message,
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )
    if group_by not in ["category", "create_method", "flow_type", "status"]:
        message = "query_task_list params group_by[%s] is invalid" % group_by
        logger.error(message)
        return JsonResponse(
            {
                "result": False,
                "message": message,
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )

    filters = {"project_id": project.id, "is_deleted": False}
    filters.update(conditions)
    success, content = task_flow_instance.dispatch(group_by, filters)
    if not success:
        return JsonResponse(
            {"result": False, "message": content, "code": err_code.UNKNOW_ERROR.code}
        )
    return JsonResponse(
        {"result": True, "data": content, "code": err_code.SUCCESS.code}
    )
