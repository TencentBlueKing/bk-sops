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
from unittest.mock import call

from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.variables.collections.sites.open.cmdb.var_cmdb_set_module_ip_selector import SetModuleIpSelector

GET_CLIENT_BY_USER = "pipeline_plugins.variables.utils.get_client_by_username"
CC_GET_IPS_INFO_BY_STR = (
    "pipeline_plugins.variables.collections.sites.open.cmdb." "var_cmdb_set_module_ip_selector.cc_get_ips_info_by_str"
)
CC_GET_IPS_INFO_BY_STR_IPV6 = (
    "pipeline_plugins.variables.collections.sites.open.cmdb."
    "var_cmdb_set_module_ip_selector.cc_get_ips_info_by_str_ipv6"
)
CMDB_API_FUNC_PREFIX = "pipeline_plugins.variables.utils"
LIST_BIZ_HOSTS = "{}.list_biz_hosts".format(CMDB_API_FUNC_PREFIX)
FIND_MODULE_WITH_RELATION = "{}.find_module_with_relation".format(CMDB_API_FUNC_PREFIX)
GET_SERVICE_TEMPLATE_LIST = "{}.get_service_template_list".format(CMDB_API_FUNC_PREFIX)
GET_SET_LIST = "{}.get_set_list".format(CMDB_API_FUNC_PREFIX)
GET_MODULE_LIST = "{}.get_module_list".format(CMDB_API_FUNC_PREFIX)


class MockClient(object):
    def __init__(
        self,
        search_set_return=None,
        list_biz_hosts_topo_return=None,
        find_module_with_relation_func=None,
        list_biz_hosts_func=None,
        list_service_template_return=None,
        find_module_batch_return=None,
        get_biz_internal_module_return=None,
    ):
        self.api = MagicMock()
        self.api.list_biz_hosts_topo = MagicMock(return_value=list_biz_hosts_topo_return)
        self.api.find_module_with_relation = MagicMock(side_effect=find_module_with_relation_func)
        self.api.list_biz_hosts = MagicMock(side_effect=list_biz_hosts_func)
        self.api.search_set = MagicMock(return_value=search_set_return)
        self.api.list_service_template = MagicMock(return_value=list_service_template_return)
        self.api.find_module_batch = MagicMock(return_value=find_module_batch_return)
        self.api.get_biz_internal_module = MagicMock(return_value=get_biz_internal_module_return)


mock_project_obj = MagicMock()
mock_project = MagicMock()
mock_project.objects.get = MagicMock(return_value=mock_project_obj)


def list_biz_hosts_func(*args, **kwargs):
    module_ip_map = {
        3: {"bk_cloud_id": 0, "bk_host_id": 3, "bk_host_innerip": "192.168.1.1", "bk_mac": "", "bk_os_type": None},
        4: {"bk_cloud_id": 0, "bk_host_id": 4, "bk_host_innerip": "192.168.1.2", "bk_mac": "", "bk_os_type": None},
        5: {"bk_cloud_id": 0, "bk_host_id": 5, "bk_host_innerip": "192.168.1.3", "bk_mac": "", "bk_os_type": None},
        6: {"bk_cloud_id": 0, "bk_host_id": 6, "bk_host_innerip": "192.168.1.4", "bk_mac": "", "bk_os_type": None},
        61: {"bk_cloud_id": 0, "bk_host_id": 61, "bk_host_innerip": "192.168.40.1", "bk_mac": "", "bk_os_type": None},
        62: {"bk_cloud_id": 0, "bk_host_id": 62, "bk_host_innerip": "192.168.40.2", "bk_mac": "", "bk_os_type": None},
    }
    data = {
        "count": 0,
        "info": [],
    }
    for module_id in args[0]["bk_module_ids"]:
        data["info"].append((module_ip_map[module_id]))
    data["count"] = len(data["info"])
    return {"result": True, "code": 0, "message": "success", "data": data}


def find_module_with_relation_func(*args, **kwargs):
    _kwargs = args[0]
    data = {"count": 0, "info": []}
    # 添加对集群1和db服务模板的匹配
    if 31 in _kwargs["bk_set_ids"] and 61 in _kwargs["bk_service_template_ids"]:
        data["info"].append({"bk_module_id": 61})
    # 添加对集群2和test服务模板的匹配
    if 32 in _kwargs["bk_set_ids"] and 62 in _kwargs["bk_service_template_ids"]:
        data["info"].append({"bk_module_id": 62})
    # 添加对空闲机池的处理
    if 2 in _kwargs["bk_set_ids"]:
        # 根据服务模板ID添加对应的模块
        for template_id in _kwargs["bk_service_template_ids"]:
            if template_id == 3:  # 空闲机
                data["info"].append({"bk_module_id": 3})
            elif template_id == 4:  # 故障机
                data["info"].append({"bk_module_id": 4})
            elif template_id == 5:  # 待回收
                data["info"].append({"bk_module_id": 5})
            elif template_id == 6:  # 自定义空闲机
                data["info"].append({"bk_module_id": 6})
    data["count"] = len(data["info"])
    return {"result": True, "code": 0, "message": "success", "data": data}


def cc_get_ips_info_by_str_func(tenant_id, username, biz_cc_id, ip_str, use_cache=True):
    """Mock function for cc_get_ips_info_by_str"""
    # Map IPs to their host IDs to match list_biz_hosts_func
    ip_to_host_id = {
        "192.168.1.1": 3,
        "192.168.1.2": 4,
        "192.168.1.3": 5,
        "192.168.1.4": 6,
        "192.168.40.1": 61,
        "192.168.40.2": 62,
        "192.168.15.4": 999,  # This IP doesn't belong to any module
    }

    ip_list = ip_str.split(",")
    ip_result = []
    for ip in ip_list:
        ip_result.append(
            {
                "InnerIP": ip,
                "Source": 0,
                "HostID": ip_to_host_id.get(ip, 999),  # Default to 999 for unknown IPs
                "Sets": [],
                "Modules": [],
            }
        )
    return {"result": True, "ip_result": ip_result, "ip_count": len(ip_result), "invalid_ip": []}


def list_biz_hosts_topo_return(*args, **kwargs):

    return {"result": True, "code": 0, "message": "success", "data": {}}


def list_biz_hosts_topo_return(*args, **kwargs):

    return {"result": True, "code": 0, "message": "success", "data": {}}


class VarCmdbSetModuleIpSelectorTestCase(TestCase):
    """
        set-module-ip topo层级构造
        [{
        "bk_biz_id": 1,
        "info": [
            {
                "bk_set_id": 2,
                "bk_set_name": "空闲机池",
                "info": [
                    {
                        "bk_module_id": 3,
                        "bk_module_name": "空闲机",
                        "host": ["192.168.1.1"]
                    },
                    {
                        "bk_module_id": 4,
                        "bk_module_name": "故障机",
                        "host": ["192.168.1.2"]
                    },
                    {
                        "bk_module_id": 5,
                        "bk_module_name": "待回收",
                        "host": ["192.168.1.3"]
                    },
                    {
                        "bk_module_id": 6,
                        "bk_module_name": "自定义空闲机",
                        "host": ["192.168.1.4"]
                    },
                ]
            },
            {
                "bk_set_id": 31,
                "bk_set_name": "集群1",
                "info": [
                    {
                        "bk_module_id": 61,
                        "bk_module_name": "test1",
                        "host": ["192.168.40.1"]
                    },
                ]
            },
            {
                "bk_set_id": 32,
                "bk_set_name": "集群2",
                "info": [
                    {
                        "bk_module_id": 62,
                        "bk_module_name": "test2",
                        "host": ["192.168.40.2"]
                    },
                ]
            },
        ]
    }]
    """

    def setUp(self):
        self.supplier_account = "supplier_account_token"

        self.project_patcher = patch(
            "pipeline_plugins.variables.collections.sites.open.cmdb.var_cmdb_set_module_ip_selector.Project",
            mock_project,
        )
        self.get_business_host_return = [
            {"bk_host_innerip": "1.1.1.1", "bk_cloud_id": 1, "bk_attr": 1},
            {"bk_host_innerip": "1.1.1.2", "bk_cloud_id": 2, "bk_attr": 2},
            {"bk_host_innerip": "1.1.1.3", "bk_attr": 3},
        ]
        self.bk_biz_id = 1
        mock_project_obj.bk_biz_id = self.bk_biz_id

        self.cc_get_ips_info_by_str_patcher = patch(
            CC_GET_IPS_INFO_BY_STR, MagicMock(side_effect=cc_get_ips_info_by_str_func)
        )
        self.cc_get_ips_info_by_str_patcher.start()

        # Add IPv6 mock
        self.cc_get_ips_info_by_str_ipv6_patcher = patch(
            CC_GET_IPS_INFO_BY_STR_IPV6, MagicMock(side_effect=cc_get_ips_info_by_str_func)
        )
        self.cc_get_ips_info_by_str_ipv6_patcher.start()

        self.pipeline_data = {"executor": "admin", "biz_cc_id": 123, "project_id": 1, "tenant_id": "system"}

        self.client = patch(
            GET_CLIENT_BY_USER,
            MagicMock(
                return_value=MockClient(
                    list_biz_hosts_func=list_biz_hosts_func,
                    list_service_template_return={
                        "result": True,
                        "code": 0,
                        "message": "success",
                        "permission": None,
                        "data": {"count": 2, "info": [{"id": 62, "name": "test"}, {"id": 61, "name": "db"}]},
                    },
                    search_set_return={
                        "result": True,
                        "code": 0,
                        "message": "",
                        "data": {
                            "count": 3,
                            "info": [
                                {"default": 0, "bk_set_id": 2, "bk_set_name": "空闲机池"},
                                {"default": 0, "bk_set_id": 31, "bk_set_name": "集群1"},
                                {"default": 0, "bk_set_id": 32, "bk_set_name": "集群2"},
                            ],
                        },
                    },
                    find_module_with_relation_func=find_module_with_relation_func,
                    get_biz_internal_module_return={
                        "result": True,
                        "code": 0,
                        "message": "success",
                        "data": {
                            "bk_set_id": 2,
                            "bk_set_name": "空闲机池",
                            "module": [
                                {"bk_module_id": 3, "bk_module_name": "空闲机"},
                                {"bk_module_id": 4, "bk_module_name": "故障机"},
                                {"bk_module_id": 5, "bk_module_name": "待回收"},
                                {"bk_module_id": 6, "bk_module_name": "自定义空闲机"},
                            ],
                        },
                    },
                    find_module_batch_return={
                        "result": True,
                        "message": "find module batch success",
                        "data": [{"bk_module_id": 1111, "ip": "1.1.1.1"}, {"bk_module_id": 2222, "ip": "2.2.2.2"}],
                    },
                )
            ),
        )
        self.client.start()
        self.client2 = patch(
            "gcloud.utils.cmdb.get_client_by_username",
            MagicMock(
                return_value=MockClient(
                    list_biz_hosts_topo_return={
                        "result": True,
                        "code": 0,
                        "message": "success",
                        "data": {
                            "count": 2,
                            "info": [
                                {
                                    "host": {
                                        "bk_cloud_id": 0,
                                        "bk_host_innerip": "192.168.40.1",
                                        "bk_host_innerip_v6": "3f2a:7c1d:9e4b:058c:217d:6b3f:895a:4e0c",
                                    },
                                    "topo": [
                                        {
                                            "bk_set_id": 11,
                                            "bk_set_name": "集群1",
                                            "module": [{"bk_module_id": 56, "bk_module_name": "m1"}],
                                        }
                                    ],
                                },
                                {
                                    "host": {
                                        "bk_cloud_id": 0,
                                        "bk_host_innerip": "192.168.15.4",
                                        "bk_host_innerip_v6": "3f2a:7c1d:9e4b:058c:217d:6b3f:895a:4e0c",
                                    },
                                    "topo": [
                                        {
                                            "bk_set_id": 11,
                                            "bk_set_name": "集群1",
                                            "module": [{"bk_module_id": 56, "bk_module_name": "m1"}],
                                        }
                                    ],
                                },
                            ],
                        },
                    },
                    list_biz_hosts_func=list_biz_hosts_func,
                    list_service_template_return={
                        "result": True,
                        "code": 0,
                        "message": "success",
                        "permission": None,
                        "data": {"count": 2, "info": [{"id": 62, "name": "test"}, {"id": 61, "name": "db"}]},
                    },
                    search_set_return={
                        "result": True,
                        "code": 0,
                        "message": "",
                        "data": {
                            "count": 3,
                            "info": [
                                {"default": 0, "bk_set_id": 2, "bk_set_name": "空闲机池"},
                                {"default": 0, "bk_set_id": 31, "bk_set_name": "集群1"},
                                {"default": 0, "bk_set_id": 32, "bk_set_name": "集群2"},
                            ],
                        },
                    },
                    find_module_with_relation_func=find_module_with_relation_func,
                    get_biz_internal_module_return={
                        "result": True,
                        "code": 0,
                        "message": "success",
                        "data": {
                            "bk_set_id": 2,
                            "bk_set_name": "空闲机池",
                            "module": [
                                {"bk_module_id": 3, "bk_module_name": "空闲机"},
                                {"bk_module_id": 4, "bk_module_name": "故障机"},
                                {"bk_module_id": 5, "bk_module_name": "待回收"},
                                {"bk_module_id": 6, "bk_module_name": "自定义空闲机"},
                            ],
                        },
                    },
                    find_module_batch_return={
                        "result": True,
                        "message": "find module batch success",
                        "data": [{"bk_module_id": 1111, "ip": "1.1.1.1"}, {"bk_module_id": 2222, "ip": "2.2.2.2"}],
                    },
                )
            ),
        )
        self.client2.start()
        self.project_patcher.start()

        # Mock get_service_template_list with correct structure
        self.get_service_template_list_patcher = patch(
            GET_SERVICE_TEMPLATE_LIST,
            MagicMock(
                return_value=[
                    {"id": 62, "name": "test"},
                    {"id": 61, "name": "db"},
                    {"id": 3, "name": "空闲机"},
                    {"id": 4, "name": "故障机"},
                    {"id": 5, "name": "待回收"},
                    {"id": 6, "name": "自定义空闲机"},
                ]
            ),
        )
        self.get_service_template_list_patcher.start()

        self.get_set_list_patcher = patch(
            GET_SET_LIST,
            MagicMock(
                return_value=[
                    {"bk_set_id": 2, "bk_set_name": "空闲机池"},
                    {"bk_set_id": 31, "bk_set_name": "集群1"},
                    {"bk_set_id": 32, "bk_set_name": "集群2"},
                ]
            ),
        )
        self.get_set_list_patcher.start()

        def mock_list_biz_hosts(tenant_id, username, bk_biz_id, kwargs):
            print(f"DEBUG: list_biz_hosts called with kwargs={kwargs}")
            result = []
            for module_id in kwargs["bk_module_ids"]:
                if module_id == 61:
                    result.append({"bk_host_innerip": "192.168.40.1"})
                elif module_id == 62:
                    result.append({"bk_host_innerip": "192.168.40.2"})
                elif module_id == 3:
                    result.append({"bk_host_innerip": "192.168.1.1"})
                elif module_id == 4:
                    result.append({"bk_host_innerip": "192.168.1.2"})
                elif module_id == 5:
                    result.append({"bk_host_innerip": "192.168.1.3"})
                elif module_id == 6:
                    result.append({"bk_host_innerip": "192.168.1.4"})
            print(f"DEBUG: list_biz_hosts returning {result}")
            return result

        self.list_biz_hosts_patcher = patch(LIST_BIZ_HOSTS, MagicMock(side_effect=mock_list_biz_hosts))
        self.list_biz_hosts_patcher.start()

        def mock_find_module_with_relation(tenant_id, bk_biz_id, username, set_ids, service_template_ids, fields):
            print(
                f"DEBUG: find_module_with_relation called with set_ids={set_ids}, "
                f"service_template_ids={service_template_ids}"
            )
            result = []
            if 31 in set_ids and 61 in service_template_ids:
                result.append({"bk_module_id": 61})
            if 32 in set_ids and 62 in service_template_ids:
                result.append({"bk_module_id": 62})
            print(f"DEBUG: find_module_with_relation returning {result}")
            return result

        self.find_module_with_relation_patcher = patch(
            FIND_MODULE_WITH_RELATION, MagicMock(side_effect=mock_find_module_with_relation)
        )
        self.find_module_with_relation_patcher.start()

        # Mock get_service_template_list_by_names
        def mock_get_service_template_list_by_names(names, template_list):
            return [t for t in template_list if t["name"] in names]

        self.get_service_template_list_by_names_patcher = patch(
            "pipeline_plugins.variables.utils.get_service_template_list_by_names",
            MagicMock(side_effect=mock_get_service_template_list_by_names),
        )
        self.get_service_template_list_by_names_patcher.start()

        # Mock get_list_by_selected_names
        def mock_get_list_by_selected_names(names, item_list):
            if isinstance(names, str):
                names = [names]
            return [item for item in item_list if item.get("bk_set_name") in names]

        self.get_list_by_selected_names_patcher = patch(
            "pipeline_plugins.variables.utils.get_list_by_selected_names",
            MagicMock(side_effect=mock_get_list_by_selected_names),
        )
        self.get_list_by_selected_names_patcher.start()

        # Mock get_biz_internal_module
        self.get_biz_internal_module_patcher = patch(
            "pipeline_plugins.variables.utils.get_biz_internal_module",
            MagicMock(
                return_value={
                    "result": True,
                    "data": [
                        {"id": 3, "name": "空闲机"},
                        {"id": 4, "name": "故障机"},
                        {"id": 5, "name": "待回收"},
                        {"id": 6, "name": "自定义空闲机"},
                    ],
                }
            ),
        )
        self.get_biz_internal_module_patcher.start()

    def tearDown(self):
        self.client.stop()
        self.client2.stop()
        self.cc_get_ips_info_by_str_patcher.stop()
        self.cc_get_ips_info_by_str_ipv6_patcher.stop()
        self.project_patcher.stop()
        self.get_service_template_list_patcher.stop()
        self.get_set_list_patcher.stop()
        self.list_biz_hosts_patcher.stop()
        self.find_module_with_relation_patcher.stop()
        self.get_service_template_list_by_names_patcher.stop()
        self.get_biz_internal_module_patcher.stop()
        self.get_list_by_selected_names_patcher.stop()

    def test_select_method_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["集群1"], "var_module": ["db"], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "db",
            },
            name="test_select_method_success_case",
            context={},
        )
        self.assertEqual(set("192.168.40.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "page": {"start": 0, "limit": 1},
                                "bk_biz_id": 1,
                                "bk_service_template_ids": [61],
                                "bk_set_ids": [31],
                                "fields": ["bk_module_id"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "page": {"limit": 500, "start": 0},
                                "bk_biz_id": 1,
                                "bk_service_template_ids": [61],
                                "bk_set_ids": [31],
                                "fields": ["bk_module_id"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "page": {"start": 0, "limit": 1},
                                "bk_biz_id": 1,
                                "bk_module_ids": [61],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "page": {"limit": 500, "start": 0},
                                "bk_biz_id": 1,
                                "bk_module_ids": [61],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_ip_selector_select_method_suc_no_filter_has_filter_set_modulue_success_case(
        self, mock_get_client_by_user_return=None
    ):  # noqa
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {
                    "var_set": ["空闲机池", "集群1"],
                    "var_module": ["空闲机", "db"],
                    "var_module_name": "ip",
                },
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "空闲机池",
                "var_filter_module": "",
            },
            name="test_ip_selector_select_method_suc_no_filter_has_filter_set_modulue_success_case",
            context={},
        )
        self.assertEqual(set("192.168.1.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {"func": self.client.new().api.find_module_with_relation, "calls": []},
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "page": {"start": 0, "limit": 1},
                                "bk_biz_id": 1,
                                "bk_module_ids": [3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "page": {"limit": 500, "start": 0},
                                "bk_biz_id": 1,
                                "bk_module_ids": [3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_ip_selector_select_method_suc_has_filter_set_module_success_case(
        self, mock_get_client_by_user_return=None
    ):  # noqa
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {
                    "var_set": ["空闲机池", "集群1"],
                    "var_module": ["空闲机", "db"],
                    "var_module_name": "ip",
                },
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "空闲机池",
                "var_filter_module": "空闲机",
            },
            name="test_ip_selector_select_method_suc_has_filter_set_module_success_case",
            context={},
        )
        self.assertEqual(set("192.168.1.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {"func": self.client.new().api.find_module_with_relation, "calls": []},
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "page": {"start": 0, "limit": 1},
                                "bk_biz_id": 1,
                                "bk_module_ids": [3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "page": {"limit": 500, "start": 0},
                                "bk_biz_id": 1,
                                "bk_module_ids": [3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_ip_selector_select_method_suc_has_filter_other_set_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {
                    "var_set": ["空闲机池", "集群1"],
                    "var_module": ["空闲机", "db"],
                    "var_module_name": "ip",
                },
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,空闲机池",
                "var_filter_module": "",
            },
            name="test_ip_selector_select_method_suc_has_filter_other_set_success_case",
            context={},
        )
        self.assertEqual(set("192.168.40.1,192.168.1.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_service_template_ids": [61, 3],
                                "bk_set_ids": [31],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_service_template_ids": [61, 3],
                                "bk_set_ids": [31],
                                "fields": ["bk_module_id"],
                                "page": {"limit": 500, "start": 0},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "page": {"start": 0, "limit": 1},
                                "bk_biz_id": 1,
                                "bk_module_ids": [61, 3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "page": {"limit": 500, "start": 0},
                                "bk_biz_id": 1,
                                "bk_module_ids": [61, 3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_ip_selector_select_method_suc_has_filter_other_set_module_success_case(
        self, mock_get_client_by_user_return=None
    ):  # noqa
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {
                    "var_set": ["空闲机池", "集群1"],
                    "var_module": ["空闲机", "db"],
                    "var_module_name": "ip",
                },
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,空闲机池",
                "var_filter_module": "空闲机",
            },
            name="test_ip_selector_select_method_suc_has_filter_other_set_module_success_case",
            context={},
        )
        self.assertEqual(set("192.168.1.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_service_template_ids": [3],
                                "bk_set_ids": [31],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        )
                    ],
                },
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "page": {"start": 0, "limit": 1},
                                "bk_biz_id": 1,
                                "bk_module_ids": [3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "page": {"limit": 500, "start": 0},
                                "bk_biz_id": 1,
                                "bk_module_ids": [3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_ip_selector_select_method_suc_no_filter_no_modulue_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["db"], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "",
                "var_filter_module": "",
            },
            name="test_ip_selector_select_method_suc_no_filter_no_modulue_success_case",
            context={},
        )
        self.assertEqual(set("192.168.40.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_service_template_ids": [61],
                                "bk_set_ids": [31],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_service_template_ids": [61],
                                "bk_set_ids": [31],
                                "fields": ["bk_module_id"],
                                "page": {"limit": 500, "start": 0},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "page": {"start": 0, "limit": 1},
                                "bk_biz_id": 1,
                                "bk_module_ids": [61],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "page": {"limit": 500, "start": 0},
                                "bk_biz_id": 1,
                                "bk_module_ids": [61],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_ip_selector_select_method_suc_no_filter_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {
                    "var_set": ["空闲机池", "集群1"],
                    "var_module": ["空闲机", "db"],
                    "var_module_name": "ip",
                },
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "",
                "var_filter_module": "",
            },
            name="test_ip_selector_select_method_suc_no_filter_success_case",
            context={},
        )
        self.assertEqual(set("192.168.40.1,192.168.1.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_service_template_ids": [61, 3],
                                "bk_set_ids": [31],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_service_template_ids": [61, 3],
                                "bk_set_ids": [31],
                                "fields": ["bk_module_id"],
                                "page": {"limit": 500, "start": 0},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "page": {"start": 0, "limit": 1},
                                "bk_biz_id": 1,
                                "bk_module_ids": [61, 3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "page": {"limit": 500, "start": 0},
                                "bk_biz_id": 1,
                                "bk_module_ids": [61, 3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_ip_selector_select_method_no_inner_module_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {
                    "var_set": ["空闲机", "集群1"],
                    "var_module": ["空闲机", "db"],
                    "var_module_name": "ip",
                },
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "ls",
            },
            name="test_ip_selector_select_method_no_inner_module_success_case",
            context={},
        )
        self.assertEqual(set("".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [],
                },
                {"func": self.client.new().api.list_biz_hosts, "calls": []},
            ]
        )

    def test_ip_selector_select_method_all_select_set_success__case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["all"], "var_module": ["空闲机", "db"], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "空闲机",
            },
            name="test_ip_selector_select_method_all_select_set_success__case",
            context={},
        )
        self.assertEqual(set("".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_service_template_ids": [3],
                                "bk_set_ids": [31, 32],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        )
                    ],
                },
                {"func": self.client.new().api.list_biz_hosts, "calls": []},
            ]
        )

    def test_ip_selector_select_method_all_select_set_module_fail_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["all"], "var_module": ["all"], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "空闲机",
            },
            name="test_ip_selector_select_method_all_select_set_module_success__case",
            context={},
        )
        self.assertEqual(set("".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {"func": self.client.new().api.find_module_with_relation, "calls": []},
                {"func": self.client.new().api.list_biz_hosts, "calls": []},
            ]
        )

    def test_ip_selector_select_method_all_select_set_module_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["all"], "var_module": ["all"], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "空闲机池,集群2",
                "var_filter_module": "空闲机",
            },
            name="test_ip_selector_select_method_all_select_set_module_success__case",
            context={},
        )
        self.assertEqual(set("192.168.1.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_service_template_ids": [3],
                                "bk_set_ids": [32],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        )
                    ],
                },
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                                "page": {"start": 0, "limit": 500},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_ip_selector_select_method_all_select_module_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["集群1"], "var_module": ["all"], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "空闲机",
            },
            name="test_ip_selector_select_method_all_select_module_success_case",
            context={},
        )
        self.assertEqual(set("".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_service_template_ids": [3],
                                "bk_set_ids": [31],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        )
                    ],
                },
                {"func": self.client.new().api.list_biz_hosts, "calls": []},
            ]
        )

    def test_select_method_get_ip_fail_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["db"], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "ls",
            },
            name="test_select_method_get_ip_fail_case",
            context={},
        )
        self.assertEqual(set("".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [],
                },
                {"func": self.client.new().api.list_biz_hosts, "calls": []},
            ]
        )

    def test_manual_method_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "manual",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["db"], "var_module_name": "ip"},
                "var_ip_manual_value": {
                    "var_manual_set": "空闲机,集群1",
                    "var_manual_module": "all,db",
                    "var_module_name": "",
                },
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "ls",
            },
            name="test_manual_method_success_case",
            context={},
        )
        self.assertEqual(set("".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [],
                },
                {"func": self.client.new().api.list_biz_hosts, "calls": []},
            ]
        )

    def test_manual_method_all_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "manual",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": [], "var_module": [], "var_module_name": ""},
                "var_ip_manual_value": {"var_manual_set": "集群1", "var_manual_module": "all", "var_module_name": ""},
                "var_filter_set": "",
                "var_filter_module": "",
            },
            name="test_manual_method_success_case",
            context={},
        )
        self.assertEqual(set("192.168.40.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_service_template_ids": [62, 61, 3, 4, 5, 6],
                                "bk_set_ids": [31],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_service_template_ids": [62, 61, 3, 4, 5, 6],
                                "bk_set_ids": [31],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 500},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [61],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [61],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                                "page": {"start": 0, "limit": 500},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_manual_method_invalid_module_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "manual",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": [], "var_module": [], "var_module_name": ""},
                "var_ip_manual_value": {
                    "var_manual_set": "集群1",
                    "var_manual_module": "not_exist",
                    "var_module_name": "",
                },
                "var_filter_set": "",
                "var_filter_module": "",
            },
            name="test_manual_method_success_case",
            context={},
        )
        self.assertEqual(set([""]), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {"func": self.client.new().api.find_module_with_relation, "calls": []},
                {"func": self.client.new().api.list_biz_hosts, "calls": []},
            ]
        )

    def test_manual_method_fail_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "manual",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["db"], "var_module_name": "ip"},
                "var_ip_manual_value": {
                    "var_manual_set": "空闲机,集群1",
                    "var_manual_module": "all,db",
                    "var_module_name": "",
                },
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "ls",
            },
            name="test_manual_method_success_case",
            context={},
        )
        self.assertEqual(set("".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [],
                },
                {"func": self.client.new().api.list_biz_hosts, "calls": []},
            ]
        )

    def test_custom_method_success_case(self, mock_get_client_by_user_return=None):
        # set_module_ip_selector = SetModuleIpSelector(
        #     pipeline_data=self.pipeline_data,
        #     value={
        #         "var_ip_method": "manual",
        #         "var_ip_custom_value": "",
        #         "var_ip_select_value": {"var_set": [], "var_module": [], "var_module_name": ""},
        #         "var_ip_manual_value": {"var_manual_set": "集群1", "var_manual_module": "all", "var_module_name": ""},
        #         "var_filter_set": "",
        #         "var_filter_module": "",
        #     },
        #     name="test_manual_method_success_case",
        #     context={},
        # )
        # self.assertEqual(set("192.168.40.1".split(",")), set(set_module_ip_selector.get_value().split(",")))

        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "custom",
                "var_ip_custom_value": "192.168.40.1,192.168.15.4",
                "var_ip_select_value": {"var_set": [], "var_module": [], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "db",
            },
            name="test_custom_method_success_case",
            context={},
        )
        self.assertEqual(set("192.168.40.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [],
                },
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [61],
                                "fields": ["bk_host_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [61],
                                "fields": ["bk_host_id"],
                                "page": {"start": 0, "limit": 500},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_custom_method_fail_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "custom",
                "var_ip_custom_value": "192.168.40.1,192.168.15.4",
                "var_ip_select_value": {"var_set": [], "var_module": [], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "ls",
            },
            name="test_manual_method_success_case",
            context={},
        )
        self.assertEqual(set("".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [],
                },
                {"func": self.client.new().api.list_biz_hosts, "calls": []},
            ]
        )

    def test_custom_method_biz_input_inner_set_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "custom",
                "var_ip_custom_value": "192.168.40.1,192.168.40.2,192.168.1.1",
                "var_ip_select_value": {"var_set": [], "var_module": [], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "空闲机池,集群2",
                "var_filter_module": "test,空闲机",
            },
            name="test_custom_method_biz_innerip_success_case",
            context={},
        )
        self.assertEqual(set("192.168.40.2,192.168.1.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_set_ids": [32],
                                "bk_service_template_ids": [62, 3],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_set_ids": [32],
                                "bk_service_template_ids": [62, 3],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 500},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [62, 3],
                                "fields": ["bk_host_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [62, 3],
                                "fields": ["bk_host_id"],
                                "page": {"start": 0, "limit": 500},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_custom_method_biz_input_inner_module_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "custom",
                "var_ip_custom_value": "192.168.40.2,192.168.1.1",
                "var_ip_select_value": {"var_set": [], "var_module": [], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "",
                "var_filter_module": "空闲机",
            },
            name="test_custom_method_biz_input_inner_module_success_case",
            context={},
        )
        self.assertEqual(set("192.168.1.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_set_ids": [31, 32],
                                "bk_service_template_ids": [3],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        )
                    ],
                },
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [3],
                                # "bk_supplier_account": "supplier_account_token",
                                "fields": ["bk_host_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [3],
                                # "bk_supplier_account": "supplier_account_token",
                                "fields": ["bk_host_id"],
                                "page": {"start": 0, "limit": 500},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_select_method_biz_input_inner_module_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["空闲机"], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "db,空闲机",
            },
            name="test_select_method_biz_innerip_success_case",
            context={},
        )
        self.assertEqual(set("".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_set_ids": [31],
                                "bk_service_template_ids": [3],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        )
                    ],
                },
                {"func": self.client.new().api.list_biz_hosts, "calls": []},
            ]
        )

    def test_select_method_biz_input_inner_set_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["空闲机"], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "空闲机池,集群2",
                "var_filter_module": "空闲机",
            },
            name="test_select_method_biz_input_inner_set_success_case",
            context={},
        )
        self.assertEqual(set("192.168.1.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {"func": self.client.new().api.find_module_with_relation, "calls": []},
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                                "page": {"start": 0, "limit": 500},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_select_method_no_filter_set_module_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["空闲机"], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "",
                "var_filter_module": "",
            },
            name="test_select_method_no_filter_set_module_success_case",
            context={},
        )
        self.assertEqual(set("192.168.1.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_set_ids": [31],
                                "bk_service_template_ids": [3],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        )
                    ],
                },
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [3],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                                "page": {"start": 0, "limit": 500},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_select_method_no_filter_set_module_select_module_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["all"], "var_module_name": ""},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "",
                "var_filter_module": "",
            },
            name="test_select_method_no_filter_set_module_select_module_success_case",
            context={},
        )
        self.assertEqual(
            "192.168.40.1,192.168.1.1,192.168.1.2,192.168.1.3,192.168.1.4", set_module_ip_selector.get_value()
        )
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_set_ids": [31],
                                "bk_service_template_ids": [62, 61, 3, 4, 5, 6],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_set_ids": [31],
                                "bk_service_template_ids": [62, 61, 3, 4, 5, 6],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 500},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [61, 3, 4, 5, 6],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [61, 3, 4, 5, 6],
                                "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
                                "page": {"start": 0, "limit": 500},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_select_method_inner_service_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["集群1"], "var_module": ["all"], "var_module_name": ""},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "",
                "var_filter_module": "待回收",
            },
            name="test_select_method_inner_service_success_case",
            context={},
        )
        self.assertEqual(set("".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_set_ids": [31],
                                "bk_service_template_ids": [5],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        )
                    ],
                },
                {"func": self.client.new().api.list_biz_hosts, "calls": []},
            ]
        )

    def test_select_method_filter_set_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["集群1"], "var_module": ["all"], "var_module_name": ""},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "空闲机池",
                "var_filter_module": "",
            },
            name="test_select_method_inner_service_success_case",
            context={},
        )
        self.assertEqual(set("".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {"func": self.client.new().api.find_module_with_relation, "calls": []},
                {"func": self.client.new().api.list_biz_hosts, "calls": []},
            ]
        )

    def test_custom_inputs_custom_internal_module_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "custom",
                "var_ip_custom_value": "192.168.1.4",
                "var_ip_select_value": {"var_set": [], "var_module": [], "var_module_name": ""},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "",
                "var_filter_module": "",
            },
            name="test_custom_inputs_custom_internal_module_case",
            context={},
        )
        self.assertEqual(set("192.168.1.4".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_set_ids": [31, 32],
                                "bk_service_template_ids": [62, 61, 3, 4, 5, 6],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_set_ids": [31, 32],
                                "bk_service_template_ids": [62, 61, 3, 4, 5, 6],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 500},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
                {
                    "func": self.client.new().api.list_biz_hosts,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [61, 62, 3, 4, 5, 6],
                                "fields": ["bk_host_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_module_ids": [61, 62, 3, 4, 5, 6],
                                "fields": ["bk_host_id"],
                                "page": {"start": 0, "limit": 500},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        ),
                    ],
                },
            ]
        )

    def test_ip_selector_manual_method_all_select_set_internal_module__case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "manual",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": [], "var_module": [], "var_module_name": ""},
                "var_ip_manual_value": {"var_manual_set": "all", "var_manual_module": "空闲机", "var_module_name": ""},
                "var_filter_set": "",
                "var_filter_module": "",
            },
            name="test_ip_selector_manual_method_all_select_set_success__case",
            context={},
        )
        self.assertEqual(set("192.168.1.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_set_ids": [31, 32],
                                "bk_service_template_ids": [3],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        )
                    ],
                },
                {"func": self.client.new().api.list_biz_hosts, "calls": []},
            ]
        )

    def test_ip_selector_manual_method_all_select_set_module__case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "manual",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": [], "var_module": [], "var_module_name": ""},
                "var_ip_manual_value": {"var_manual_set": "all", "var_manual_module": "db", "var_module_name": ""},
                "var_filter_set": "",
                "var_filter_module": "",
            },
            name="test_ip_selector_manual_method_all_select_set_module__case",
            context={},
        )
        self.assertEqual(set("192.168.40.1".split(",")), set(set_module_ip_selector.get_value().split(",")))
        call_assert(
            [
                {
                    "func": self.client.new().api.find_module_with_relation,
                    "calls": [
                        call(
                            {
                                "bk_biz_id": 1,
                                "bk_set_ids": [31, 32],
                                "bk_service_template_ids": [61],
                                "fields": ["bk_module_id"],
                                "page": {"start": 0, "limit": 1},
                            },
                            path_params={"bk_biz_id": 1},
                            headers={"X-Bk-Tenant-Id": "system"},
                        )
                    ],
                },
                {"func": self.client.new().api.list_biz_hosts, "calls": []},
            ]
        )


def call_assert(calls_list):
    for call_item in calls_list:
        call_item["func"].assert_has_calls(calls=call_item["calls"])
