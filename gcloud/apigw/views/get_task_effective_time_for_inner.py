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
from rest_framework.decorators import api_view
from rest_framework.response import Response

from gcloud import err_code
from gcloud.analysis_statistics.service import effective_time_for_task
from gcloud.apigw.constants import PROJECT_SCOPE_CMDB_BIZ
from gcloud.apigw.decorators import mark_request_whether_is_trust


@login_exempt
@api_view(["GET"])
@apigw_require
@mark_request_whether_is_trust
def get_task_effective_time_for_inner(request, task_id, bk_biz_id):
    """
    统计任务的有效执行时间（排除人工节点及其等待时间，以及失败后等待时间）

    仅允许处于 APIGW 信任名单（is_trust）的应用调用，避免任意网关应用借此
    绕过用户 IAM 校验跨业务读取任务有效执行时间统计（BAC / 信息泄露）
    """
    if not request.is_trust:
        return Response(
            {
                "result": False,
                "message": "you have no permission to call this api.",
                "code": err_code.REQUEST_FORBIDDEN_INVALID.code,
            }
        )

    scope = request.query_params.get("scope", PROJECT_SCOPE_CMDB_BIZ)
    debug_mode = request.query_params.get("debug", "0") == "1"
    try:
        return Response(effective_time_for_task(scope, task_id, bk_biz_id, debug_mode))
    except Exception as e:
        return Response(
            {
                "result": False,
                "message": "calculate effective time failed: {}".format(str(e)),
                "code": err_code.UNKNOWN_ERROR.code,
            }
        )
