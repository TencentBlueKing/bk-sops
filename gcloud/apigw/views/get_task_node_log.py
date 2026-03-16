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

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, mcp_apigw, project_inject
from gcloud.apigw.views.utils import logger
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskViewInterceptor
from gcloud.taskflow3.domains.node_log import NodeLogDataSourceFactory
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.utils.handlers import handle_plain_log

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 30


def fetch_task_node_log(node_id, version, page=DEFAULT_PAGE, page_size=DEFAULT_PAGE_SIZE):
    """获取节点日志的核心逻辑，供内外接口共用"""
    data_source = NodeLogDataSourceFactory(settings.NODE_LOG_DATA_SOURCE).data_source
    result = data_source.fetch_node_logs(node_id, version, page=page, page_size=page_size)
    if not result["result"]:
        return {"result": False, "message": result["message"], "data": None}
    logs, page_info = result["data"]["logs"], result["data"]["page_info"]
    return {
        "result": True,
        "message": "success",
        "data": handle_plain_log(logs),
        "page": page_info if page_info else {},
    }


@login_exempt
@api_view(["GET"])
@apigw_require
@mcp_apigw()
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskViewInterceptor())
def get_task_node_log(request, task_id, project_id):
    project = request.project
    try:
        TaskFlowInstance.objects.get(id=task_id, project_id=project.id)
    except TaskFlowInstance.DoesNotExist:
        message = (
            "[API] get_task_node_log task[id={task_id}] "
            "of project[project_id={project_id}, biz_id={biz_id}] does not exist".format(
                task_id=task_id, project_id=project.id, biz_id=project.bk_biz_id
            )
        )
        logger.exception(message)
        return Response({"result": False, "message": message, "code": err_code.CONTENT_NOT_EXIST.code})

    node_id = request.GET.get("node_id")
    version = request.GET.get("version")
    page = request.GET.get("page", DEFAULT_PAGE)
    page_size = request.GET.get("page_size", DEFAULT_PAGE_SIZE)

    return Response(fetch_task_node_log(node_id, version, page=page, page_size=page_size))
