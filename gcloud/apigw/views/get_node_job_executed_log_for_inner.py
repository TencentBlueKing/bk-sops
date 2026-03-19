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

from gcloud.apigw.views.get_node_job_executed_log import fetch_node_job_executed_log


@login_exempt
@api_view(["GET"])
@apigw_require
def get_node_job_executed_log_for_inner(request):
    bk_biz_id = request.query_params.get("bk_biz_id")
    node_id = request.query_params.get("node_id")
    job_scope_type = request.query_params.get("job_scope_type")
    component_code = request.query_params.get("component_code")
    return Response(
        fetch_node_job_executed_log(node_id, bk_biz_id, component_code=component_code, job_scope_type=job_scope_type)
    )
