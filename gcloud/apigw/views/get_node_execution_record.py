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
from django.views.decorators.http import require_GET
from rest_framework.exceptions import ValidationError

from gcloud import err_code
from gcloud.analysis_statistics.models import TaskflowExecutedNodeStatistics
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.core.apis.drf.serilaziers import NodeExecutionRecordResponseSerializer, NodeExecutionRecordQuerySerializer
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import FlowViewInterceptor


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(FlowViewInterceptor())
def get_node_execution_record(request, template_id, project_id):
    """
    获取节点最近执行记录
    """
    try:
        params = NodeExecutionRecordQuerySerializer(data=request.GET)
        params.is_valid(raise_exception=True)
        template_node_id = params.data["template_node_id"]

        execution_data = (
            TaskflowExecutedNodeStatistics.objects.filter(
                template_node_id=template_node_id, status=True, is_skip=False, trigger_template_id=template_id
            )
            .order_by("-archived_time")
            .values("archived_time", "elapsed_time")
        )
        execution_total_time = execution_data.count()
        execution_time_data = execution_data[: settings.MAX_RECORDED_NODE_EXECUTION_TIMES]

        node_execution_record_serializer = NodeExecutionRecordResponseSerializer(
            data={"execution_time": execution_time_data, "total": execution_total_time}
        )
        node_execution_record_serializer.is_valid(raise_exception=True)
    except ValidationError as e:
        return {
            "result": False,
            "message": "params is invalid, error: {error}".format(error=e.detail),
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }

    return {
        "result": True,
        "data": node_execution_record_serializer.validated_data,
        "message": "",
        "code": err_code.SUCCESS.code,
    }
