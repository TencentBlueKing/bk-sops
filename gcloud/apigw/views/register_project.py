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

import logging

import ujson as json
from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, return_json_response
from gcloud.conf import settings
from gcloud.core.models import Business, EnvironmentVariables, Project

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
def register_project(request):
    """
    第三方系统项目同步注册
    """
    if not request.is_trust:
        return JsonResponse(
            {
                "result": False,
                "message": "you have no permission to call this api.",
                "code": err_code.REQUEST_FORBIDDEN_INVALID.code,
            }
        )
    try:
        params = json.loads(request.body)
        bk_biz_id = int(params.get("bk_biz_id"))
    except Exception:
        return JsonResponse(
            {
                "result": False,
                "message": "should be json format and contain bk_biz_id(int)",
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )

    username = settings.SYSTEM_USE_API_ACCOUNT
    client = get_client_by_user(username)
    biz_kwargs = {
        "bk_supplier_account": EnvironmentVariables.objects.get_var("BKAPP_DEFAULT_SUPPLIER_ACCOUNT", 0),
        "condition": {"bk_biz_id": bk_biz_id},
    }
    biz_result = client.cc.search_business(biz_kwargs)

    if not biz_result["result"] or not biz_result["data"]["info"]:
        message = "[cc.search_business] error: {}, please confirm your bk_biz_id and business data exist".format(
            biz_result
        )
        logger.error("[api register_project]: {}".format(message))
        return JsonResponse({"result": False, "message": message, "code": err_code.UNKNOWN_ERROR.code})

    biz_info = biz_result["data"]["info"][0]
    biz_defaults = {
        "cc_name": biz_info.get("bk_biz_name"),
        "cc_owner": biz_info.get("bk_supplier_account"),
        "cc_company": biz_info.get("bk_supplier_id", 0),
        "time_zone": biz_info.get("time_zone", ""),
        "life_cycle": biz_info.get("life_cycle", ""),
        "status": biz_info.get("bk_data_status", "enable"),
    }

    project_defaults = {
        "name": biz_info.get("bk_biz_name"),
        "time_zone": biz_info.get("time_zone"),
        "creator": username,
        "desc": "",
        "from_cmdb": True,
        "tenant_id": request.app.tenant_id,
    }

    try:
        # 插入后更新Business和Project信息
        Business.objects.update_or_create(cc_id=bk_biz_id, defaults=biz_defaults)
        project, _ = Project.objects.update_or_create(bk_biz_id=bk_biz_id, defaults=project_defaults)
    except Exception as e:
        message = "[api register_project] Error exists when create object: {}".format(e)
        logger.exception(message)
        return JsonResponse({"result": False, "message": message, "code": err_code.UNKNOWN_ERROR.code})

    return JsonResponse(
        {
            "result": True,
            "data": {"project_id": project.id, "project_name": project.name},
            "code": err_code.SUCCESS.code,
        }
    )
