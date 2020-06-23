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

from gcloud.utils import cmdb
from gcloud.conf import settings

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def cc_get_inner_ip_by_module_id(username, biz_cc_id, module_id_list, supplier_account=0, host_fields=None):
    """根据模块列表过滤业务下主机

    :param username: 请求用户名
    :type username: str
    :param biz_cc_id: 业务 CC ID
    :type biz_cc_id: int
    :param module_id_list: 过滤模块 ID 列表
    :type module_id_list: list[int]
    :param supplier_account: 开发商账号, defaults to 0
    :type supplier_account: int, optional
    :param host_fields: 主机过滤字段, defaults to None
    :type host_fields: list[str], optional
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
    host_info_list = cmdb.get_business_host_topo(username, biz_cc_id, supplier_account, host_fields)

    # filter host
    filtered = []
    target_modules = {int(mid) for mid in module_id_list}
    for host_info in host_info_list:
        parent_module_id_set = {m["bk_module_id"] for m in host_info["module"]}
        if target_modules.intersection(parent_module_id_set):
            filtered.append(host_info)

    return filtered


def cc_format_module_hosts(username, biz_cc_id, module_id_list, supplier_account, data_format, host_fields):
    """根据指定格式返回主机列表

    :param username: 请求用户名
    :type username: str
    :param biz_cc_id: 业务 CC ID
    :type biz_cc_id: int
    :param module_id_list: 过滤模块 ID 列表
    :type module_id_list: list[int]
    :param supplier_account: 开发商账号, defaults to 0
    :type supplier_account: int, optional
    :param data_format: 数据格式, tree or ip
    :type data_format: str
    :param host_fields: 主机过滤字段, defaults to None
    :type host_fields: list[str], optional
    :return: tree: {
        "module_3": [
            {"id": "127.0.0.1", "label": "127.0.0.1"},
            ....
        ]
    }
            ip: [
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
    :rtype: dict(tree) or list(ip)
    """

    module_host_list = cc_get_inner_ip_by_module_id(username, biz_cc_id, module_id_list, supplier_account, host_fields)
    if data_format == "tree":
        module_host_dict = {}
        for item in module_host_list:
            for mod in item["module"]:
                if mod["bk_module_id"] in module_id_list:
                    module_host_dict.setdefault("module_%s" % mod["bk_module_id"], []).append(
                        {
                            "id": "%s_%s" % (mod["bk_module_id"], item["host"]["bk_host_innerip"]),
                            "label": item["host"]["bk_host_innerip"],
                        }
                    )

        return module_host_dict
    else:
        return module_host_list
