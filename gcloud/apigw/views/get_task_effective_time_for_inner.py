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
from gcloud.apigw.constants import PROJECT_SCOPE_CMDB_BIZ
from gcloud.apigw.decorators import return_json_response
from gcloud.apigw.views.utils import effective_time_for_task


@login_exempt
@require_GET
@apigw_require
@return_json_response
def get_task_effective_time_for_inner(request, task_id, bk_biz_id):
    """
    统计任务的有效执行时间（排除人工节点及其等待时间，以及失败后等待时间）
    """
    scope = request.GET.get("scope", PROJECT_SCOPE_CMDB_BIZ)
    # 检查是否启用调试模式
    debug_mode = request.GET.get("debug", "0") == "1"
    try:
        return effective_time_for_task(scope, task_id, bk_biz_id, debug_mode)
    except Exception as e:
        return {
            "result": False,
            "message": "calculate effective time failed: {}".format(str(e)),
            "code": err_code.UNKNOWN_ERROR.code,
        }
