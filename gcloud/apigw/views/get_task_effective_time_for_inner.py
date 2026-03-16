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


@login_exempt
@api_view(["GET"])
@apigw_require
def get_task_effective_time_for_inner(request, task_id, bk_biz_id):
    """
    统计任务的有效执行时间（排除人工节点及其等待时间，以及失败后等待时间）
    """
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
