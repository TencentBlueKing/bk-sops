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

from gcloud.apigw.views.get_task_plugin_log import fetch_task_plugin_log
from plugin_service.api_decorators import validate_params
from plugin_service.serializers import LogQuerySerializer


@login_exempt
@api_view(["GET"])
@apigw_require
@validate_params(LogQuerySerializer)
def get_task_plugin_log_for_inner(request):
    """
    内部接口，仅限于内部使用
    免去用户登录、iam鉴权等操作
    """
    trace_id = request.validated_data.get("trace_id")
    scroll_id = request.validated_data.get("scroll_id")
    plugin_code = request.validated_data.get("plugin_code")
    return Response(fetch_task_plugin_log(plugin_code, trace_id, scroll_id))
