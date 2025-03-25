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
from cachetools import TTLCache, cached
from django.views.decorators.http import require_GET
from iam import Resource

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.apigw.utils import api_hash_key
from gcloud.apigw.views.utils import logger
from gcloud.core.utils import get_user_business_detail as get_business_detail
from gcloud.iam_auth.conf import PROJECT_ACTIONS, IAMMeta
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.utils import get_resources_allowed_actions_for_user
from gcloud.iam_auth.view_interceptors.apigw import ProjectViewInterceptor


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(ProjectViewInterceptor())
@cached(cache=TTLCache(maxsize=1024, ttl=60), key=api_hash_key)
def get_user_project_detail(request, project_id):
    try:
        biz_detail = get_business_detail(request.user.username, request.project.bk_biz_id, request.app.tenant_id)
    except Exception as e:
        logger.exception("[API] get_user_business_detail call fail: {}".format(e))
        return {
            "result": False,
            "message": "can not get business[{}] detail for user[{}]".format(
                request.project.bk_biz_id, request.user.username
            ),
            "code": err_code.UNKNOWN_ERROR.code,
        }

    project_allowed_actions = get_resources_allowed_actions_for_user(
        username=request.user.username,
        system_id=IAMMeta.SYSTEM_ID,
        actions=PROJECT_ACTIONS,
        resources_list=[
            [
                Resource(
                    IAMMeta.SYSTEM_ID, IAMMeta.PROJECT_RESOURCE, str(request.project.id), {"name": request.project.name}
                )
            ]
        ],
    )

    return {
        "result": True,
        "data": {
            "project_id": request.project.id,
            "project_name": request.project.name,
            "from_cmdb": request.project.from_cmdb,
            "bk_biz_id": biz_detail["bk_biz_id"],
            "bk_biz_name": biz_detail["bk_biz_name"],
            "bk_biz_developer": biz_detail["bk_biz_developer"],
            "bk_biz_maintainer": biz_detail["bk_biz_maintainer"],
            "bk_biz_tester": biz_detail["bk_biz_tester"],
            "bk_biz_productor": biz_detail["bk_biz_productor"],
            "auth_actions": [
                action
                for action, allowed in project_allowed_actions.get(str(request.project.id), {}).items()
                if allowed
            ],
        },
        "code": err_code.SUCCESS.code,
    }
