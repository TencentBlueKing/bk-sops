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
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE
from iam.exceptions import RawAuthFailedException

from api.utils.request import batch_request
from gcloud.conf import settings
from gcloud.utils import cmdb
from gcloud.utils.data_handler import chunk_data
from gcloud.utils.handlers import handle_api_error
from gcloud.utils.ip import format_sundry_ip
from pipeline_plugins.components.utils.common import batch_execute_func

from .constants import ERROR_CODES, NO_ERROR
from .utils import (
    format_agent_data,
    get_cmdb_topo_tree,
    get_gse_agent_status_ipv6,
    get_modules_id,
    get_modules_of_bk_obj,
    get_objects_of_topo_tree,
)
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username
from packages.bkapi.bk_nodeman.shortcuts import get_client_by_username as get_nodeman_client_by_username

logger = logging.getLogger("root")


def format_agent_ip(data, *args, **kwargs):
    bk_biz_id = kwargs["bk_biz_id"]
    return [
        {
            "host_id": host["bk_host_id"],
            "meta": {"bk_biz_id": bk_biz_id, "scope_type": "biz", "scope_id": bk_biz_id},
        }
        for host in data
    ]


def cmdb_search_topo_tree(request, bk_biz_id, bk_supplier_account=""):
    """
    @summary: 获取 CMDB 上业务的拓扑树，包含空闲机和故障机模块，根节点是业务
    @param request:
    @param bk_biz_id: 业务 CMDB ID
    @param bk_supplier_account: 业务开发商账号
    @return:
    """
    result = get_cmdb_topo_tree(request.user.username, bk_biz_id, bk_supplier_account)
    return JsonResponse(result)


def cmdb_search_host(request, bk_biz_id, bk_supplier_account="", bk_supplier_id=0):
    """
    @summary: 获取 CMDB 上业务的 IP 列表，以及 agent 状态等信息
    @param request:
    @param bk_biz_id: 业务 CMDB ID
    @param bk_supplier_account: 业务开发商账号
    @param bk_supplier_id: 业务开发商ID
    @params fields: list 查询字段，默认只返回 bk_host_innerip、bk_host_name、bk_host_id, 可以查询主机的任意字段，也可以查询
                set、module、cloud、agent等信息
    @return:
    """
    tenant_id = request.user.tenant_id
    default_host_fields = ["bk_host_id", "bk_host_name", "bk_cloud_id", "bk_host_innerip"]
    if settings.ENABLE_IPV6 or settings.ENABLE_GSE_V2:
        # IPV6环境下或者开启了GSE 2.0 版本
        default_host_fields.append("bk_agent_id")
    fields = set(default_host_fields + json.loads(request.GET.get("fields", "[]")))
    client = get_client_by_username(request.user.username, stage=settings.BK_APIGW_STAGE_NAME)

    topo_modules_id = set()

    # get filter module id
    if request.GET.get("topo", None):
        topo = json.loads(request.GET.get("topo"))
        topo_result = get_cmdb_topo_tree(tenant_id, request.user.username, bk_biz_id, bk_supplier_account)
        if not topo_result["result"]:
            return JsonResponse(topo_result)

        biz_topo_tree = topo_result["data"][0]
        topo_dict = {}
        for tp in topo:
            topo_dict.setdefault(tp["bk_obj_id"], []).append(int(tp["bk_inst_id"]))
        topo_objects = get_objects_of_topo_tree(biz_topo_tree, topo_dict)
        topo_modules = []

        for obj in topo_objects:
            topo_modules += get_modules_of_bk_obj(obj)
        topo_modules_id = set(get_modules_id(topo_modules))

    cloud_area_result = client.api.search_cloud_area({}, headers={"X-Bk-Tenant-Id": tenant_id})
    if not cloud_area_result["result"]:
        message = handle_api_error(_("配置平台(CMDB)"), "cc.search_cloud_area", {}, cloud_area_result)
        result = {"result": False, "code": ERROR_CODES.API_GSE_ERROR, "message": message}
        return JsonResponse(result)

    raw_host_info_list = cmdb.get_business_host_topo(tenant_id, request.user.username, bk_biz_id, bk_supplier_account,
                                                     fields)

    # map cloud_area_id to cloud_area
    cloud_area_dict = {}
    for cloud_area in cloud_area_result["data"]["info"]:
        cloud_area_dict[cloud_area["bk_cloud_id"]] = cloud_area

    # module filtered
    host_info_list = []
    if topo_modules_id:
        for host_info in raw_host_info_list:
            parent_module_id_set = {m["bk_module_id"] for m in host_info["module"]}
            if topo_modules_id.intersection(parent_module_id_set):
                host_info_list.append(host_info)
    else:
        host_info_list = raw_host_info_list

    data = []

    if host_info_list:
        for host in host_info_list:
            host_detail = {field: host["host"][field] for field in fields if field in host["host"]}
            host_detail["bk_host_innerip"] = format_sundry_ip(host_detail["bk_host_innerip"])
            if "set" in fields:
                host_detail["set"] = host["set"]
            if "module" in fields:
                host_detail["module"] = host["module"]
            if "cloud" in fields or "agent" in fields:
                cloud_id = host["host"].get("bk_cloud_id")
                host_detail["cloud"] = [
                    {"id": str(cloud_id), "bk_inst_name": cloud_area_dict.get(cloud_id, {}).get("bk_cloud_name", "")}
                ]
            data.append(host_detail)

        if "agent" in fields:
            if settings.ENABLE_IPV6 or settings.ENABLE_GSE_V2:
                # 开启IPV6将会调用网关进行查询
                bk_agent_id_list = []
                for host in data:
                    bk_agent_id = host.get("bk_agent_id")
                    # 如果bk_agent_id=空
                    if not bk_agent_id:
                        if not host["bk_host_innerip"]:
                            # 如果既没有如果bk_agent_id，又没有ipv4地址，说明这个主机石台没有安装agent的ipv6主机，忽略，不再查询agent状态
                            continue
                        bk_agent_id = "{}:{}".format(host["bk_cloud_id"], host["bk_host_innerip"])
                    bk_agent_id_list.append(bk_agent_id)

                try:
                    agent_id_status_map = get_gse_agent_status_ipv6(bk_agent_id_list)
                except Exception as e:
                    result = {"result": False, "code": ERROR_CODES.API_GSE_ERROR, "message": e}
                    return JsonResponse(result)

                for host in data:
                    bk_agent_id = host.get("bk_agent_id")
                    # 如果bk_agent_id = 空
                    if not bk_agent_id:
                        if not host["bk_host_innerip"]:
                            # 如果既没有如果bk_agent_id，又没有ipv4地址，说明这个主机石台没有安装agent的ipv6主机，忽略，不再查询agent状态, 直接重置为未知
                            host["agent"] = -1
                            continue
                        bk_agent_id = "{}:{}".format(host["bk_cloud_id"], host["bk_host_innerip"])
                    host["agent"] = agent_id_status_map.get(bk_agent_id, -1)
            else:
                nodeman_client = get_nodeman_client_by_username(request.user.username)
                host_list = chunk_data(data, 1000, format_agent_ip, bk_biz_id=bk_biz_id)
                agent_kwargs = [
                    {
                        "data": {"all_scope": True, "host_list": host},
                        "headers": {"X-Bk-Tenant-Id": request.user.tenant_id},
                    } for host in host_list
                ]
                results = batch_execute_func(nodeman_client.api.ipchooser_host_details, agent_kwargs,
                                             interval_enabled=True)

                agent_data = []
                for result in results:
                    agent_result = result["result"]
                    if not agent_result["result"]:
                        message = handle_api_error(
                            _("节点管理(nodeman)"), "nodeman.get_ipchooser_host_details", agent_kwargs, agent_result
                        )
                        result = {"result": False, "code": ERROR_CODES.API_GSE_ERROR, "message": message}
                        return JsonResponse(result)
                    agent_data.extend(agent_result["data"])
                agent_data = format_agent_data(agent_data)
                for host in data:
                    # agent在线状态，0为不在线，1为在线，-1为未知
                    agent_info = agent_data.get(
                        "{cloud}:{ip}".format(cloud=host["bk_cloud_id"], ip=host["bk_host_innerip"]), {}
                    )
                    host["agent"] = agent_info.get("bk_agent_alive", -1)

        # search host lock status
        if request.GET.get("search_host_lock", None):
            bk_host_id_list = [host_detail["bk_host_id"] for host_detail in data]
            host_lock_status_result = client.api.search_host_lock(
                {"id_list": bk_host_id_list},
                headers={"X-Bk-Tenant-Id": tenant_id},
            )
            if not host_lock_status_result["result"]:
                message = handle_api_error(_("配置平台(CMDB)"), "cc.search_host_lock", {}, host_lock_status_result)
                result = {"result": False, "code": ERROR_CODES.API_GSE_ERROR, "message": message}
                return JsonResponse(result)
            host_lock_status_data = {int(k): v for k, v in host_lock_status_result["data"].items()}
            for host_detail in data:
                host_lock_status = host_lock_status_data.get(host_detail["bk_host_id"])
                if host_lock_status is not None:
                    host_detail["bk_host_lock_status"] = host_lock_status
    result = {"result": True, "code": NO_ERROR, "data": data}
    return JsonResponse(result)


def cmdb_get_mainline_object_topo(request, bk_biz_id, bk_supplier_account=""):
    """
    @summary: 获取配置平台业务拓扑模型
    @param request:
    @param bk_biz_id:
    @param bk_supplier_account:
    @return:
    """
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "bk_supplier_account": bk_supplier_account,
    }
    client = get_client_by_username(request.user.username, stage=settings.BK_APIGW_STAGE_NAME)
    cc_result = client.api.get_mainline_object_topo(kwargs, headers={"X-Bk-Tenant-Id": request.user.tenant_id})
    if not cc_result["result"]:
        message = handle_api_error(_("配置平台(CMDB)"), "cc.get_mainline_object_topo", kwargs, cc_result)
        if cc_result.get("code", 0) == HTTP_AUTH_FORBIDDEN_CODE:
            logger.warning(message)
            raise RawAuthFailedException(permissions=cc_result.get("permission", []))

        return JsonResponse({"result": cc_result["result"], "code": cc_result["code"], "message": message})
    data = cc_result["data"]
    for bk_obj in data:
        if bk_obj["bk_obj_id"] == "host":
            bk_obj["bk_obj_name"] = "IP"
    result = {"result": cc_result["result"], "code": cc_result["code"], "data": cc_result["data"]}
    return JsonResponse(result)


def cmdb_search_dynamic_group(request, bk_biz_id, bk_supplier_account=""):
    """
    @summary: 查询动态分组列表
    @param request:
    @param bk_biz_id:
    @param bk_supplier_account:
    @return:
    """
    client = get_client_by_username(request.user.username, stage=settings.BK_APIGW_STAGE_NAME)
    kwargs = {"bk_biz_id": bk_biz_id, "bk_supplier_account": bk_supplier_account}
    result = batch_request(
        client.api.search_dynamic_group,
        kwargs,
        limit=200,
        check_iam_auth_fail=True,
        path_params={"bk_biz_id": bk_biz_id},
        headers={"X-Bk-Tenant-Id": request.user.tenant_id},
    )

    dynamic_groups = []
    for dynamic_group in result:
        if dynamic_group["bk_obj_id"] == "host":
            dynamic_groups.append(
                {"id": dynamic_group["id"], "name": dynamic_group["name"], "create_user": dynamic_group["create_user"]}
            )
    return JsonResponse({"result": True, "data": {"count": len(dynamic_groups), "info": dynamic_groups}})
