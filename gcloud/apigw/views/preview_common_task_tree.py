# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


import ujson as json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.constants import COMMON
from gcloud.taskflow3.models import preview_template_tree
from gcloud.apigw.views.utils import logger
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import CommonFlowViewInterceptor
from packages.bkoauth.decorators import apigw_required


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@iam_intercept(CommonFlowViewInterceptor())
def preview_common_task_tree(request, project_id, template_id):
    try:
        req_data = json.loads(request.body)
    except Exception:
        return {
            "result": False,
            "message": "request body is not a valid json",
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }

    version = req_data.get("version")
    exclude_task_nodes_id = req_data.get("exclude_task_nodes_id", [])

    if not isinstance(exclude_task_nodes_id, list):
        return {
            "result": False,
            "message": "invalid exclude_task_nodes_id",
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }

    try:
        data = preview_template_tree(request.project.id, COMMON, template_id, version, exclude_task_nodes_id)
    except Exception as e:
        logger.exception("[API] preview_common_task_tree fail: {}".format(e))
        return {
            "result": False,
            "message": "preview_common_task_tree fail: {}".format(e),
            "code": err_code.UNKNOWN_ERROR.code,
        }

    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
