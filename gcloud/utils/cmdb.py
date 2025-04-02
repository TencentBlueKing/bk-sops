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

from django.utils.translation import gettext_lazy as _

from api.utils.request import batch_request
from gcloud.conf import settings
from gcloud.core.models import StaffGroupSet
from gcloud.utils.handlers import handle_api_error
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("root")
logger_celery = logging.getLogger("celery")


def get_business_host_topo(tenant_id, username, bk_biz_id, supplier_account, host_fields,
                           ip_list=None, property_filters=None):
    """获取业务下所有主机信息
    :param tenant_id: 租户ID
    :param username: 请求用户名
    :type username: str
    :param bk_biz_id: 业务 CC ID
    :type bk_biz_id: int
    :param supplier_account: 开发商账号, defaults to 0
    :type supplier_account: int
    :param host_fields: 主机过滤字段
    :type host_fields: list
    :param ip_list: 主机内网 IP 列表
    :type ip_list: list
    :param property_filters: 查询主机时的相关属性过滤条件, 当传递该参数时，ip_list参数生成的过滤条件失效
    :type property_filters: dict
    :return: [
        {
            "host": {
                "bk_host_id": 4,
                "bk_host_innerip": "127.0.0.1",
                "bk_cloud_id": 0,
                ...
            },
            "module": [
                {
                    "bk_module_id": 2,
                    "bk_module_name": "module_name"
                },
                ...
            ],
            "set": [
                {
                    "bk_set_name": "set_name",
                    "bk_set_id": 1
                },
                ...
            ]
        }
    ]
    :rtype: list
    """
    client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)
    kwargs = {"bk_biz_id": bk_biz_id, "bk_supplier_account": supplier_account, "fields": list(host_fields or [])}

    if property_filters is not None:
        kwargs.update(property_filters)
    elif ip_list:
        kwargs["host_property_filter"] = {
            "condition": "AND",
            "rules": [{"field": "bk_host_innerip", "operator": "in", "value": ip_list}],
        }

    result = batch_request(
        client.api.list_biz_hosts_topo,
        kwargs,
        path_params={"bk_biz_id": bk_biz_id},
        headers={"X-Bk-Tenant-Id": tenant_id},
    )

    host_info_list = []
    for host_topo in result:
        host_info = {"host": host_topo["host"], "module": [], "set": []}
        for parent_set in host_topo["topo"]:
            host_info["set"].append({"bk_set_id": parent_set["bk_set_id"], "bk_set_name": parent_set["bk_set_name"]})
            for parent_module in parent_set["module"]:
                host_info["module"].append(
                    {"bk_module_id": parent_module["bk_module_id"], "bk_module_name": parent_module["bk_module_name"]}
                )

        host_info_list.append(host_info)

    return host_info_list


def get_business_host(tenant_id, username, bk_biz_id, supplier_account, host_fields, ip_list=None, bk_cloud_id=None):
    """根据主机内网 IP 过滤业务下的主机
    :param tenant_id: 租户ID
    :param username: 请求用户名
    :type username: str
    :param bk_biz_id: 业务 CC ID
    :type bk_biz_id: int
    :param supplier_account: 开发商账号, defaults to 0
    :type supplier_account: int
    :param host_fields: 主机过滤字段, defaults to None
    :type host_fields: list
    :param ip_list: 主机内网 IP 列表
    :type ip_list: list
    :param bk_cloud_id: IP列表对应的管控区域
    :type bk_cloud_id: int
    :return:
    [
        {
            "bk_cloud_id": 0,
            "bk_host_id": 1,
            "bk_host_innerip": "127.0.0.1",
            "bk_mac": "",
            "bk_os_type": null
        },
        ...
    ]
    :rtype: [type]
    """
    kwargs = {"bk_biz_id": bk_biz_id, "bk_supplier_account": supplier_account, "fields": list(host_fields or [])}

    # 带管控区域的主机数据查询
    if ip_list and bk_cloud_id is not None:
        kwargs["host_property_filter"] = {
            "condition": "AND",
            "rules": [
                {"field": "bk_host_innerip", "operator": "in", "value": ip_list},
                {"field": "bk_cloud_id", "operator": "equal", "value": bk_cloud_id},
            ],
        }
    elif ip_list:
        kwargs["host_property_filter"] = {
            "condition": "AND",
            "rules": [{"field": "bk_host_innerip", "operator": "in", "value": ip_list}],
        }

    client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)
    return batch_request(
        client.api.list_biz_hosts,
        kwargs,
        path_params={"bk_biz_id": bk_biz_id},
        headers={"X-Bk-Tenant-Id": tenant_id},
    )


def get_business_set_host(tenant_id, username, supplier_account, host_fields, ip_list=None,
                          filter_field="bk_host_innerip"):
    """根据主机内网 IP 过滤业务下的主机
    :param tenant_id: 租户ID
    :param username: 请求用户名
    :type username: str
    :param supplier_account: 开发商账号, defaults to 0
    :type supplier_account: int
    :param host_fields: 主机过滤字段, defaults to None
    :type host_fields: list
    :param ip_list: 主机内网 IP 列表
    :type ip_list: list
    :param filter_field: 过滤字段
    :type filter_field: str
    :return:
    [
        {
            "bk_cloud_id": 0,
            "bk_host_id": 1,
            "bk_host_innerip": "127.0.0.1",
            "bk_mac": "",
            "bk_os_type": null
        },
        ...
    ]
    """
    kwargs = {
        "bk_supplier_account": supplier_account,
        "fields": list(host_fields or []),
        "host_property_filter": {
            "condition": "AND",
            "rules": [{"field": filter_field, "operator": "in", "value": ip_list or []}],
        },
    }

    client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)
    return batch_request(
        client.api.list_hosts_without_biz,
        kwargs,
        headers={"X-Bk-Tenant-Id": tenant_id},
    )


def get_business_host_ipv6(tenant_id, username, bk_biz_id, supplier_account, host_fields, ip_list=None,
                           bk_cloud_id=None):
    """
    根据主机内网 IP 过滤业务下的主机, 主要查询ip_v6
    :param tenant_id: 租户ID
    :param username: 请求用户名
    :type username: str
    :param bk_biz_id: 业务 CC ID
    :type bk_biz_id: int
    :param supplier_account: 开发商账号, defaults to 0
    :type supplier_account: int
    :param host_fields: 主机过滤字段, defaults to None
    :type host_fields: list
    :param ip_list: 主机内网 IP 列表
    :type ip_list: list
    :param bk_cloud_id: IP列表对应的管控区域
    :type bk_cloud_id: int
    :return:
    [
        {
            "bk_cloud_id": 0,
            "bk_host_id": 1,
            "bk_host_innerip": "127.0.0.1",
            "bk_mac": "",
            "bk_os_type": null
        },
        ...
    ]
    :rtype: [type]
    """
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "bk_supplier_account": supplier_account,
        "fields": list(host_fields or []),
        "host_property_filter": {
            "condition": "AND",
            "rules": [{"field": "bk_host_innerip_v6", "operator": "in", "value": ip_list}],
        },
    }
    if bk_cloud_id is not None:
        kwargs["host_property_filter"]["rules"].append(
            {"field": "bk_cloud_id", "operator": "equal", "value": bk_cloud_id}
        )

    client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)
    return batch_request(
        client.api.list_biz_hosts,
        kwargs,
        path_params={"bk_biz_id": bk_biz_id},
        headers={"X-Bk-Tenant-Id": tenant_id},
    )


def get_business_set_host_ipv6(tenant_id, username, supplier_account, host_fields, ip_list=None):
    """
    根据主机内网 IP 过滤业务集下的主机, 主要查询ip_v6
    :param tenant_id: 租户ID
    :param username: 请求用户名
    :type username: str
    :param bk_biz_id: 业务 CC ID
    :type bk_biz_id: int
    :param supplier_account: 开发商账号, defaults to 0
    :type supplier_account: int
    :param host_fields: 主机过滤字段, defaults to None
    :type host_fields: list
    :param ip_list: 主机内网 IP 列表
    :type ip_list: list
    :param bk_cloud_id: IP列表对应的管控区域
    :type bk_cloud_id: int
    :return:
    [
        {
            "bk_cloud_id": 0,
            "bk_host_id": 1,
            "bk_host_innerip": "127.0.0.1",
            "bk_mac": "",
            "bk_os_type": null
        },
        ...
    ]
    :rtype: [type]
    @param bk_biz_ids:
    """
    kwargs = {
        "bk_supplier_account": supplier_account,
        "fields": list(host_fields or []),
        "host_property_filter": {
            "condition": "AND",
            "rules": [{"field": "bk_host_innerip_v6", "operator": "in", "value": ip_list}],
        },
    }

    client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)
    return batch_request(
        client.api.list_hosts_without_biz,
        kwargs,
        headers={"X-Bk-Tenant-Id": tenant_id}
    )


def get_notify_receivers(tenant_id, username, biz_cc_id, supplier_account, receiver_group, more_receiver, logger=None):
    """
    @summary: 根据通知分组和附加通知人获取最终通知人
    @param tenant_id: 租户ID
    @param username: 请求用户名
    @param biz_cc_id: 业务CC ID
    @param supplier_account: 租户 ID
    @param receiver_group: 通知分组
    @param more_receiver: 附加通知人
    @param logger: 日志句柄
    @note: 如果 receiver_group 为空，则直接返回 more_receiver；如果 receiver_group 不为空，需要从 CMDB 获取人员信息，人员信息
        无先后顺序
    @return:
    """
    client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)
    more_receivers = [name.strip() for name in more_receiver.split(",")]
    if not receiver_group:
        result = {"result": True, "message": "success", "data": ",".join(more_receivers)}
        return result

    if logger is None:
        logger = logger_celery
    kwargs = {"bk_supplier_account": supplier_account, "condition": {"bk_biz_id": int(biz_cc_id)}}
    cc_result = client.api.search_business(
        kwargs,
        path_params={"bk_supplier_account": supplier_account},
        headers={"X-Bk-Tenant-Id": tenant_id},
    )
    if not cc_result["result"]:
        message = handle_api_error("CMDB", "cc.search_business", kwargs, cc_result)
        logger.error(message)
        result = {"result": False, "message": message, "data": None}
        return result

    biz_count = cc_result["data"]["count"]
    if biz_count != 1:
        logger.error(handle_api_error("CMDB", "cc.search_business", kwargs, cc_result))
        message = _(
            f"业务人员信息查询失败: 从[配置平台]中查询业务[ID: {biz_cc_id}] 人员信息失败, 请检查业务存在以及拥有访问权限 | get_notify_receivers"
        )
        logger.error(message)
        result = {
            "result": False,
            "message": message,
            "data": None,
        }
        return result

    biz_data = cc_result["data"]["info"][0]
    staff_groups = []
    receivers = []

    if isinstance(receiver_group, str):
        receiver_group = receiver_group.split(",")

    for group in receiver_group:
        # 原通知分组
        if group in biz_data:
            if biz_data[group]:
                receivers.extend(biz_data[group].split(","))
        # 自定义人员分组
        else:
            staff_groups.append(group)
    staff_groups = StaffGroupSet.objects.filter(is_deleted=False, id__in=staff_groups).values_list("members", flat=True)
    for group in staff_groups:
        receivers.extend(group.split(","))

    if more_receiver:
        receivers.extend(more_receivers)

    result = {"result": True, "message": "success", "data": ",".join(sorted(set(receivers)))}
    return result


def get_dynamic_group_list(tenant_id, username, bk_biz_id, bk_supplier_account):
    """获取业务下的所有动态分组列表"""
    client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)
    kwargs = {"bk_biz_id": bk_biz_id, "bk_supplier_account": bk_supplier_account}
    result = batch_request(
        client.api.search_dynamic_group,
        kwargs,
        limit=200,
        check_iam_auth_fail=True,
        path_params={"bk_biz_id": bk_biz_id},
        headers={"X-Bk-Tenant-Id": tenant_id},
    )

    dynamic_groups = [{"id": dynamic_group["id"]} for dynamic_group in result if dynamic_group["bk_obj_id"] == "host"]
    return dynamic_groups


def get_dynamic_group_host_list(tenant_id, username, bk_biz_id, bk_supplier_account, dynamic_group_id):
    """获取动态分组中对应主机列表"""
    client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)
    fields = ["bk_host_innerip", "bk_cloud_id", "bk_host_id"]
    if settings.ENABLE_IPV6:
        fields.append("bk_host_innerip_v6")
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "bk_supplier_account": bk_supplier_account,
        "id": dynamic_group_id,
        "fields": fields,
    }
    host_list = batch_request(
        client.api.execute_dynamic_group,
        kwargs,
        limit=200,
        path_params={"bk_biz_id": bk_biz_id},
        headers={"X-Bk-Tenant-Id": tenant_id},
    )
    return True, {"code": 0, "message": "success", "data": host_list}


def get_business_host_by_hosts_ids(tenant_id, username, bk_biz_id, supplier_account, host_fields, host_id_list=None):
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "bk_supplier_account": supplier_account,
        "fields": list(host_fields or []),
        "host_property_filter": {
            "condition": "AND",
            "rules": [{"field": "bk_host_id", "operator": "in", "value": host_id_list}],
        },
    }

    client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)
    return batch_request(
        client.api.list_biz_hosts,
        kwargs,
        path_params={"bk_biz_id": bk_biz_id},
        headers={"X-Bk-Tenant-Id": tenant_id},
    )
