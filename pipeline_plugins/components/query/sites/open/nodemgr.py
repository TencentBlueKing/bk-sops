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

import env
import ujson as json
from django.conf.urls import url
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from api.collections.nodemgr import BKNodemgrClient
from gcloud.iam_auth.utils import check_and_raise_raw_auth_fail_exception
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("root")

NODEMGR_DEFAULT_LOGIN_INFO = {
    "linux": {
        "user": "root",
        "port": 22
    },
    "windows": {
        "user": "Administrator",
        "port": 445
    },
    "darwin": {
        "user": "root",
        "port": 22
    }
}


def get_login_info():
    try:
        return json.loads(env.BK_NODEMGR_DEFAULT_LOGIN_INFO)
    except Exception:
        return NODEMGR_DEFAULT_LOGIN_INFO


def nodemgr_get_networkarea(request):
    client = BKNodemgrClient(username=request.user.username)

    result = []
    offset = 0
    limit = 1000
    while True:
        response = client.networkarea_list(offset=offset, limit=limit)

        if response.get("code", -1) != 0:
            message = handle_api_error(_("节点管理(NODEMGR)"), "nodemgr.networkarea_list", {}, response)
            logger.error(message)
            check_and_raise_raw_auth_fail_exception(response, message)

            return JsonResponse({"result": False, "code": response.get("code", -1), "message": message})

        items = response["data"]["items"]
        result.extend([{
            "text": f"[{item['bk_networkarea_id']}] {item['bk_networkarea_name']}",
            "value": item["bk_networkarea_id"],
            "id": item["bk_networkarea_id"]} for item in items])

        if len(items) < limit:
            break
        offset += limit

    result = sorted(result, key=lambda x: x["id"])

    return JsonResponse({"result": True, "data": result})


def nodemgr_get_networkunit(request, networkarea_id: int):
    client = BKNodemgrClient(username=request.user.username)

    result = []
    offset = 0
    limit = 1000
    while True:
        response = client.networkunit_list(networkarea_id=int(networkarea_id), offset=offset, limit=limit)

        if response.get("code", -1) != 0:
            message = handle_api_error(_("节点管理(NODEMGR)"), "nodemgr.networkunit_list", {}, response)
            logger.error(message)
            check_and_raise_raw_auth_fail_exception(response, message)

            return JsonResponse({"result": False, "code": response.get("code", -1), "message": message})

        items = response["data"]["items"]
        result.extend([{
            "text": f"[{item['bk_networkunit_id']}] {item['bk_networkunit_name']}",
            "value": item["bk_networkunit_id"],
            "id": item["bk_networkunit_id"]} for item in items])

        if len(items) < limit:
            break
        offset += limit

    result = sorted(result, key=lambda x: x["id"])

    return JsonResponse({"result": True, "data": result})


def nodemgr_get_os_type(request, node_role: str):
    client = BKNodemgrClient(username=request.user.username)

    response = client.package_distinct(node_role=node_role)
    if response.get("code", -1) != 0:
        message = handle_api_error(_("节点管理(NODEMGR)"), "nodemgr.package_distinct", {}, response)
        logger.error(message)
        check_and_raise_raw_auth_fail_exception(response, message)

        return JsonResponse({"result": False, "code": response.get("code", -1), "message": message})

    items = response["data"]["os_type"]
    result = [{"text": item, "value": item, "default_info": get_login_info().get(item, {})} for item in items]

    return JsonResponse({"result": True, "data": result})


def nodemgr_get_release_version(request, node_role: str):
    client = BKNodemgrClient(username=request.user.username)

    version_set = set()
    offset = 0
    limit = 1000
    while True:
        response = client.package_list(node_role=node_role, offset=offset, limit=limit)
        if response.get("code", -1) != 0:
            message = handle_api_error(_("节点管理(NODEMGR)"), "nodemgr.package_list", {}, response)
            logger.error(message)
            check_and_raise_raw_auth_fail_exception(response, message)

            return JsonResponse({"result": False, "code": response.get("code", -1), "message": message})

        items = response["data"]["items"]
        for item in items:
            version_set.add(item["version"])

        if len(items) < limit:
            break
        offset += limit

    result = [{"text": version, "value": version} for version in version_set]
    result = sorted(result, key=lambda x: x["value"], reverse=True)

    return JsonResponse({"result": True, "data": result})


def nodemgr_get_plugin(request, biz_id: int):
    client = BKNodemgrClient(username=request.user.username)

    result = []
    offset = 0
    limit = 500
    while True:
        response = client.plugin_list(biz_id=[int(biz_id)], offset=offset, limit=limit)
        if response.get("code", -1) != 0:
            message = handle_api_error(_("节点管理(NODEMGR)"), "nodemgr.plugin_list", {}, response)
            logger.error(message)
            check_and_raise_raw_auth_fail_exception(response, message)

            return JsonResponse({"result": False, "code": response.get("code", -1), "message": message})

        items = response["data"]["items"]
        for item in items:
            result.append({
                "text": item["name"],
                "value": item["name"],
                "data": item,
            })

        if len(items) < limit:
            break
        offset += limit

    return JsonResponse({"result": True, "data": result})


def nodemgr_get_plugin_version(request, plugin_pkg_name: str):
    client = BKNodemgrClient(username=request.user.username)

    version_set = set()
    offset = 0
    limit = 1000
    while True:
        response = client.package_list(node_role="plugin", offset=offset, limit=limit, plugin_pkg_name=plugin_pkg_name)
        if response.get("code", -1) != 0:
            message = handle_api_error(_("节点管理(NODEMGR)"), "nodemgr.plugin_list", {}, response)
            logger.error(message)
            check_and_raise_raw_auth_fail_exception(response, message)

            return JsonResponse({"result": False, "code": response.get("code", -1), "message": message})

        items = response["data"]["items"]
        for item in items:
            version_set.add(item["version"])

        if len(items) < limit:
            break
        offset += limit

    result = [{"text": version, "value": version} for version in version_set]
    result = sorted(result, key=lambda x: x["value"], reverse=True)

    return JsonResponse({"result": True, "data": result})


nodemgr_urlpatterns = [
    url(r"^nodemgr_get_networkarea/$", nodemgr_get_networkarea),
    url(r"^nodemgr_get_networkunit/(?P<networkarea_id>\w+)/$", nodemgr_get_networkunit),
    url(r"^nodemgr_get_os_type/(?P<node_role>\w+)/$", nodemgr_get_os_type),
    url(r"^nodemgr_get_release_version/(?P<node_role>\w+)/$", nodemgr_get_release_version),
    url(r"^nodemgr_get_plugin/(?P<biz_id>\d+)/$", nodemgr_get_plugin),
    url(r"^nodemgr_get_plugin_version/(?P<plugin_pkg_name>.+)/$", nodemgr_get_plugin_version),
]
