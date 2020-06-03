# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


from django.http import JsonResponse
from django.views.decorators.http import require_GET

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.core.utils import get_user_business_detail as get_business_detail
from gcloud.apigw.views.utils import logger
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import ProjectViewInterceptor

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
@iam_intercept(ProjectViewInterceptor())
def get_user_project_detail(request, project_id):
    try:
        biz_detail = get_business_detail(request.user.username, request.project.bk_biz_id)
    except Exception as e:
        logger.exception("[API] get_user_business_detail call fail: {}".format(e))
        return JsonResponse(
            {
                "result": False,
                "message": "can not get business[{}] detail for user[{}]".format(
                    request.user.username, request.project.bk_biz_id
                ),
                "code": err_code.UNKNOW_ERROR.code,
            }
        )

    return JsonResponse(
        {
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
            },
            "code": err_code.SUCCESS.code,
        }
    )
