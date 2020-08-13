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
import logging

from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def nodeman_get_cloud_area(request):
    client = get_client_by_user(request.user.username)
    cloud_area_result = client.nodeman.cloud_list()
    if not cloud_area_result["result"]:
        message = handle_api_error(_("节点管理(NODEMAN)"), "nodeman.cloud_list", {}, cloud_area_result)
        logger.error(message)
        return JsonResponse(
            {"result": cloud_area_result["result"], "code": cloud_area_result.get("code", "-1"), "message": message}
        )

    data = cloud_area_result["data"]

    result = [{"text": cloud["bk_cloud_name"], "value": cloud["bk_cloud_id"]} for cloud in data]

    cloud_area_result["data"] = result
    return JsonResponse(cloud_area_result)


def nodeman_get_ap_list(request):
    client = get_client_by_user(request.user.username)
    ap_list = client.nodeman.ap_list()
    if not ap_list["result"]:
        message = handle_api_error(_("节点管理(NODEMAN)"), "nodeman.ap_list", {}, ap_list)
        logger.error(message)
        return JsonResponse({"result": ap_list["result"], "code": ap_list.get("code", "-1"), "message": message})

    data = ap_list["data"]

    result = [{"text": ap["name"], "value": ap["id"]} for ap in data]

    ap_list["data"] = result
    return JsonResponse(ap_list)


nodeman_urlpatterns = [
    url(r"^nodeman_get_cloud_area/$", nodeman_get_cloud_area),
    url(r"^nodeman_get_ap_list/$", nodeman_get_ap_list),
]
