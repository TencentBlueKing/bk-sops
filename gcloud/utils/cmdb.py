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

from gcloud.conf import settings

from .thread import ThreadPool

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def batch_request(
    func, params, get_data=lambda x: x["data"]["info"], get_count=lambda x: x["data"]["count"], limit=500
):
    """
    并发请求接口
    :param func: 请求方法
    :param params: 请求参数
    :param get_data: 获取数据函数
    :param get_count: 获取总数函数
    :param limit: 一次请求数量
    :return: 请求结果
    """
    # 请求第一次获取总数
    result = func(page={"start": 0, "limit": 1}, **params)

    if not result["result"]:
        logger.error("[batch_request] {api} count request error, result: {result}".format(api=func.path, result=result))
        return []

    count = get_count(result)
    data = []
    start = 0

    # 根据请求总数并发请求
    pool = ThreadPool()
    params_and_future_list = []
    while start < count:
        request_params = {"page": {"limit": limit, "start": start}}
        request_params.update(params)
        params_and_future_list.append({"params": request_params, "future": pool.apply_async(func, kwds=request_params)})

        start += limit

    pool.close()
    pool.join()

    # 取值
    for params_and_future in params_and_future_list:
        result = params_and_future["future"].get()

        if not result:
            logger.error(
                "[batch_request] {api} request error, params: {params}, result: {result}".format(
                    api=func.__name__, params=params_and_future["params"], result=result
                )
            )
            return []

        data.extend(get_data(result))

    return data


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
    kwargs = {"bk_biz_id": bk_biz_id, "bk_supplier_account": supplier_account, "fields": host_fields or []}

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
    kwargs = {"bk_biz_id": bk_biz_id, "bk_supplier_account": supplier_account, "fields": host_fields or []}

    if ip_list:
        kwargs["host_property_filter"] = {
            "condition": "AND",
            "rules": [{"field": "bk_host_innerip", "operator": "in", "value": ip_list}],
        }

    client = get_client_by_user(username)
    return batch_request(client.cc.list_biz_hosts, kwargs)
