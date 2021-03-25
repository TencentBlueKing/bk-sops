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

from django.utils.translation import ugettext_lazy as _

from api.utils.request import batch_request
from gcloud.conf import settings
from gcloud.core.models import StaffGroupSet
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("root")
logger_celery = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def get_business_host_topo(username, bk_biz_id, supplier_account, host_fields, ip_list=None):
    """获取业务下所有主机信息
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
    client = get_client_by_user(username)
    kwargs = {"bk_biz_id": bk_biz_id, "bk_supplier_account": supplier_account, "fields": list(host_fields or [])}

    if ip_list:
        kwargs["host_property_filter"] = {
            "condition": "AND",
            "rules": [{"field": "bk_host_innerip", "operator": "in", "value": ip_list}],
        }

    result = batch_request(client.cc.list_biz_hosts_topo, kwargs)

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


def get_business_host(username, bk_biz_id, supplier_account, host_fields, ip_list=None):
    """根据主机内网 IP 过滤业务下的主机
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

    if ip_list:
        kwargs["host_property_filter"] = {
            "condition": "AND",
            "rules": [{"field": "bk_host_innerip", "operator": "in", "value": ip_list}],
        }

    client = get_client_by_user(username)
    return batch_request(client.cc.list_biz_hosts, kwargs)


def get_notify_receivers(client, biz_cc_id, supplier_account, receiver_group, more_receiver, logger=None):
    """
    @summary: 根据通知分组和附加通知人获取最终通知人
    @param client: API 客户端
    @param biz_cc_id: 业务CC ID
    @param supplier_account: 租户 ID
    @param receiver_group: 通知分组
    @param more_receiver: 附加通知人
    @param logger: 日志句柄
    @note: 如果 receiver_group 为空，则直接返回 more_receiver；如果 receiver_group 不为空，需要从 CMDB 获取人员信息，人员信息
        无先后顺序
    @return:
    """
    more_receivers = [name.strip() for name in more_receiver.split(",")]
    if not receiver_group:
        result = {"result": True, "message": "success", "data": ",".join(more_receivers)}
        return result

    if logger is None:
        logger = logger_celery
    kwargs = {"bk_supplier_account": supplier_account, "condition": {"bk_biz_id": int(biz_cc_id)}}
    cc_result = client.cc.search_business(kwargs)
    if not cc_result["result"]:
        message = handle_api_error("CMDB", "cc.search_business", kwargs, cc_result)
        logger.error(message)
        result = {"result": False, "message": message, "data": None}
        return result

    biz_count = cc_result["data"]["count"]
    if biz_count != 1:
        logger.error(handle_api_error("CMDB", "cc.search_business", kwargs, cc_result))
        result = {
            "result": False,
            "message": _("从 CMDB 查询到业务不唯一，业务ID:{}, 返回数量: {}".format(biz_cc_id, biz_count)),
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


def get_dynamic_group_host_list(username, bk_biz_id, bk_supplier_account, dynamic_group_id, host_modules_ids):
    """获取动态分组中对应主机列表"""
    client = get_client_by_user(username)
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "bk_supplier_account": bk_supplier_account,
        "id": dynamic_group_id,
        "fields": ["bk_host_innerip", "bk_cloud_id"],
    }
    host_list = batch_request(client.cc.execute_dynamic_group, kwargs, limit=200)
    for host in host_list:
        host["host_modules_id"] = host_modules_ids[host["bk_host_innerip"]]
    return True, {"code": 0, "message": "success", "data": host_list}
