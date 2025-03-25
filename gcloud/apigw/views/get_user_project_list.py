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
from gcloud.apigw.decorators import mark_request_whether_is_trust, return_json_response
from gcloud.apigw.views.utils import logger
from gcloud.iam_auth.utils import get_user_projects


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
def get_user_project_list(request):
    try:
        projects = get_user_projects(request.user.username, request.user.tenant_id)
    except Exception as e:
        logger.exception("[API] get_user_project_list call fail: {}".format(e))
        return {
            "result": False,
            "message": "can not fetch project for user[{}]".format(request.user.username),
            "code": err_code.UNKNOWN_ERROR.code,
        }

    data = [
        {"project_id": proj.id, "bk_biz_id": proj.bk_biz_id, "name": proj.name}
        for proj in projects
        if not proj.is_disable
    ]

    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
