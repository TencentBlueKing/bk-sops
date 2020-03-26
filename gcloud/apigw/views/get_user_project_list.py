# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
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
from gcloud.core.models import Project
from gcloud.core.utils import get_user_business_list
from gcloud.apigw.views.utils import logger

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
def get_user_project_list(request):
    try:
        biz_list = get_user_business_list(request.user.username)
    except Exception as e:
        logger.exception("[API] get_user_business_list call fail: {}".format(e))
        return JsonResponse(
            {
                "result": False,
                "message": "can not fetch business for user[{}]".format(
                    request.user.username
                ),
                "code": err_code.UNKNOW_ERROR.code,
            }
        )

    biz_id_list = [biz["bk_biz_id"] for biz in biz_list]

    projects = Project.objects.filter(bk_biz_id__in=biz_id_list, is_disable=False)
    data = []

    for proj in projects:
        data.append(
            {"project_id": proj.id, "bk_biz_id": proj.bk_biz_id, "name": proj.name}
        )

    return JsonResponse({"result": True, "data": data, "code": err_code.SUCCESS.code})
