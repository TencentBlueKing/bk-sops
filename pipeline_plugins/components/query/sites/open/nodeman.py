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
import os

from django.conf.urls import url
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from api.collections.nodeman import BKNodeManClient
from gcloud.iam_auth.utils import check_and_raise_raw_auth_fail_exception
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("root")

BKAPP_NODEMAN_SUPPORT_TJJ = os.environ.get("BKAPP_NODEMAN_SUPPORT_TJJ", "False") == "True"


def nodeman_get_cloud_area(request):
    client = BKNodeManClient(username=request.user.username)
    cloud_area_result = client.cloud_list()
    if not cloud_area_result["result"]:
        message = handle_api_error(_("节点管理(NODEMAN)"), "nodeman.cloud_list", {}, cloud_area_result)
        logger.error(message)
        check_and_raise_raw_auth_fail_exception(cloud_area_result, message)
        return JsonResponse(
            {"result": cloud_area_result["result"], "code": cloud_area_result.get("code", "-1"), "message": message}
        )

    data = cloud_area_result["data"]

    result = [{"text": cloud["bk_cloud_name"], "value": cloud["bk_cloud_id"]} for cloud in data]

    cloud_area_result["data"] = result
    return JsonResponse(cloud_area_result)


def nodeman_get_ap_list(request):
    client = BKNodeManClient(username=request.user.username)
    ap_list = client.ap_list()
    if not ap_list["result"]:
        message = handle_api_error(_("节点管理(NODEMAN)"), "nodeman.ap_list", {}, ap_list)
        logger.error(message)
        return JsonResponse({"result": ap_list["result"], "code": ap_list.get("code", "-1"), "message": message})

    data = ap_list["data"]

    result = [{"text": ap["name"], "value": ap["id"]} for ap in data]

    ap_list["data"] = result
    return JsonResponse(ap_list)


def nodeman_get_plugin_list(request, category):
    """获取插件列表"""
    client = BKNodeManClient(username=request.user.username)
    plugin_list = client.plugin_process(category)

    if not plugin_list["result"]:
        message = handle_api_error(_("节点管理(NODEMAN)"), "nodeman.plugin_process", {}, plugin_list)
        logger.error(message)
        check_and_raise_raw_auth_fail_exception(plugin_list, message)
        return JsonResponse(
            {"result": plugin_list["result"], "code": plugin_list.get("code", "-1"), "message": message}
        )

    data = plugin_list["data"]

    result = [{"text": ap["name"], "value": ap["name"]} for ap in data]
    plugin_list["data"] = result
    return JsonResponse(plugin_list)


def nodeman_get_plugin_version(request, plugin, os_type):
    """根据系统获取插件版本"""
    client = BKNodeManClient(username=request.user.username)
    kwargs = {"name": plugin, "os": os_type.upper()}
    plugin_version_list = client.plugin_package(**kwargs)

    if not plugin_version_list["result"]:
        message = handle_api_error(_("节点管理(NODEMAN)"), "nodeman.plugin_package", {}, plugin_version_list)
        logger.error(message)
        check_and_raise_raw_auth_fail_exception(plugin_version_list, message)
        return JsonResponse(
            {"result": plugin_version_list["result"], "code": plugin_version_list.get("code", "-1"), "message": message}
        )

    data = plugin_version_list["data"]

    result = [{"text": version["version"], "value": version["version"]} for version in data]

    plugin_version_list["data"] = result
    return JsonResponse(plugin_version_list)


def nodeman_is_support_tjj(request):
    """
    获取当前环境下的节点管理是否支持铁将军认证
    @param request:
    @return:
    """
    return JsonResponse({"result": True, "message": "success", "code": 0, "data": BKAPP_NODEMAN_SUPPORT_TJJ})


def nodeman_get_install_channel(request, cloud_id: int):
    client = BKNodeManClient(username=request.user.username)
    install_channel_result = client.install_channel()

    if not install_channel_result["result"]:
        message = handle_api_error(_("节点管理(NODEMAN)"), "nodeman.install_channel", {}, install_channel_result)
        logger.error(message)
        check_and_raise_raw_auth_fail_exception(install_channel_result, message)
        return JsonResponse(
            {
                "result": install_channel_result["result"],
                "code": install_channel_result.get("code", "-1"),
                "message": message,
            }
        )

    data = install_channel_result["data"]
    result = [
        {"text": channel["name"], "value": channel["id"]} for channel in data if channel["bk_cloud_id"] == int(cloud_id)
    ]
    install_channel_result["data"] = result
    return JsonResponse(install_channel_result)


nodeman_urlpatterns = [
    url(r"^nodeman_get_cloud_area/$", nodeman_get_cloud_area),
    url(r"^nodeman_get_ap_list/$", nodeman_get_ap_list),
    url(r"^nodeman_is_support_tjj/$", nodeman_is_support_tjj),
    url(r"^nodeman_get_plugin_list/(?P<category>\w+)/$", nodeman_get_plugin_list),
    url(r"^nodeman_get_plugin_version/(?P<plugin>[\w-]+)/(?P<os_type>\w+)/$", nodeman_get_plugin_version),
    url(r"^nodeman_get_install_channel/(?P<cloud_id>\w+)/$", nodeman_get_install_channel),
]
