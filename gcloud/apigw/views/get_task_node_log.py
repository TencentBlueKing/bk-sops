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
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from gcloud.apigw.decorators import return_json_response
from gcloud.taskflow3.domains.node_log import NodeLogDataSourceFactory
from gcloud.utils.handlers import handle_plain_log

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 30


@login_exempt
@api_view(["GET"])
@apigw_require
@return_json_response
def get_task_node_log(request):
    """
    内部接口，仅限于内部使用
    免去用户登录、iam鉴权等操作
    """
    page = request.query_params.get("page", DEFAULT_PAGE)
    page_size = request.query_params.get("page_size", DEFAULT_PAGE_SIZE)
    node_id = request.query_params.get("node_id")
    version = request.query_params.get("version")
    data_source = NodeLogDataSourceFactory(settings.NODE_LOG_DATA_SOURCE).data_source
    result = data_source.fetch_node_logs(node_id, version, page=page, page_size=page_size)
    if not result["result"]:
        return Response({"result": False, "message": result["message"], "data": None})
    logs, page_info = result["data"]["logs"], result["data"]["page_info"]

    return Response(
        {
            "result": True,
            "message": "success",
            "data": handle_plain_log(logs),
            "page": page_info if page_info else {},
        }
    )
