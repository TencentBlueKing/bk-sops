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
from unittest.mock import call

from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.variables.collections.sites.open.cmdb.var_cmdb_set_module_ip_selector import SetModuleIpSelector

GET_CLIENT_BY_USER = "pipeline_plugins.variables.utils.get_client_by_user"
CC_GET_IPS_INFO_BY_STR = (
    "pipeline_plugins.variables.collections.sites.open.cmdb." "var_cmdb_set_module_ip_selector.cc_get_ips_info_by_str"
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
            get_biz_internal_module_return=None
    ):
        self.cc = MagicMock()
        self.cc.list_biz_hosts_topo = MagicMock(return_value=list_biz_hosts_topo_return)
        self.cc.find_module_with_relation = MagicMock(side_effect=find_module_with_relation_func)
        self.cc.list_biz_hosts = MagicMock(side_effect=list_biz_hosts_func)
        self.cc.search_set = MagicMock(return_value=search_set_return)
        self.cc.list_service_template = MagicMock(return_value=list_service_template_return)
        self.cc.find_module_batch = MagicMock(return_value=find_module_batch_return)
        self.cc.get_biz_internal_module = MagicMock(return_value=get_biz_internal_module_return)


mock_project_obj = MagicMock()
mock_project = MagicMock()
mock_project.objects.get = MagicMock(return_value=mock_project_obj)


def list_biz_hosts_func(*args, **kwargs):
    module_ip_map = {
        3: {"bk_cloud_id": 0, "bk_host_id": 1, "bk_host_innerip": "192.168.1.1", "bk_mac": "", "bk_os_type": None},
        4: {"bk_cloud_id": 0, "bk_host_id": 1, "bk_host_innerip": "192.168.1.2", "bk_mac": "", "bk_os_type": None},
        5: {"bk_cloud_id": 0, "bk_host_id": 1, "bk_host_innerip": "192.168.1.3", "bk_mac": "", "bk_os_type": None},
        61: {"bk_cloud_id": 0, "bk_host_id": 1, "bk_host_innerip": "192.168.40.1", "bk_mac": "", "bk_os_type": None},
        62: {"bk_cloud_id": 0, "bk_host_id": 1, "bk_host_innerip": "192.168.40.2", "bk_mac": "", "bk_os_type": None},
    }
    data = {
        "count": 0,
        "info": [],
    }
    for module_id in kwargs["bk_module_ids"]:
        data["info"].append((module_ip_map[module_id]))
    data["count"] = len(data["info"])
    return {"result": True, "code": 0, "message": "success", "data": data}


def find_module_with_relation_func(*args, **kwargs):
    data = {
        "count": 0,
        "info": []
    }
    if 31 in kwargs["bk_set_ids"] and 61 in kwargs["bk_service_template_ids"]:
        data["info"].append({"bk_module_id": 61})
    if 32 in kwargs["bk_set_ids"] and 62 in kwargs["bk_service_template_ids"]:
        data["info"].append({"bk_module_id": 62})
    data["count"] = len(data["info"])
    return {"result": True, "code": 0, "message": "success", "data": data}


def cc_get_ips_info_by_str_func(*args, **kwargs):
    ip_list = args[2].split(",")
    data = {"ip_result": []}
    for ip in ip_list:
        data["ip_result"].append({"InnerIP": ip, "Source": 0})
    return data


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

        self.supplier_account_for_project_patcher = patch(
            "pipeline_plugins.variables.collections.sites.open.cmdb.var_cmdb_set_module_ip_selector."
            "supplier_account_for_project",
            MagicMock(return_value=self.supplier_account),
        )

        self.cc_get_ips_info_by_str_patcher = patch(
            CC_GET_IPS_INFO_BY_STR, MagicMock(side_effect=cc_get_ips_info_by_str_func)
        )
        self.cc_get_ips_info_by_str_patcher.start()

        self.pipeline_data = {"executor": "admin", "biz_cc_id": 123, "project_id": 1}

        self.client = patch(GET_CLIENT_BY_USER, MagicMock(return_value=MockClient(
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
                        {
                            "bk_module_id": 3,
                            "bk_module_name": "空闲机"
                        },
                        {
                            "bk_module_id": 4,
                            "bk_module_name": "故障机"
                        },
                        {
                            "bk_module_id": 5,
                            "bk_module_name": "待回收"
                        }
                    ]
                }
            }
        )))
        self.client.start()
        self.project_patcher.start()
        self.supplier_account_for_project_patcher.start()

    def tearDown(self):
        self.client.stop()
        self.cc_get_ips_info_by_str_patcher.stop()
        self.project_patcher.stop()
        self.supplier_account_for_project_patcher.stop()

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
        self.assertEqual('192.168.40.1', set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[61], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_service_template_ids=[61], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'limit': 500, 'start': 0})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[61], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[61], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]

            }
        ])

    def test_ip_selector_select_method_suc_no_filter_has_filter_set_modulue_success_case(self, mock_get_client_by_user_return=None): # noqa
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["空闲机", "db"],
                                        "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "空闲机池",
                "var_filter_module": "",
            },
            name="test_ip_selector_select_method_suc_no_filter_has_filter_set_modulue_success_case",
            context={},
        )
        self.assertEqual('192.168.1.1', set_module_ip_selector.get_value())
        call_assert([
            {
                "func":
                    self.client.new().cc.find_module_with_relation,
                "calls": []
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]
            }
        ])

    def test_ip_selector_select_method_suc_has_filter_set_module_success_case(self,
                                                                              mock_get_client_by_user_return=None): # noqa
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["空闲机", "db"],
                                        "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "空闲机池",
                "var_filter_module": "空闲机",
            },
            name="test_ip_selector_select_method_suc_has_filter_set_module_success_case",
            context={},
        )
        self.assertEqual("192.168.1.1", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": []
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]
            }
        ])

    def test_ip_selector_select_method_suc_has_filter_other_set_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["空闲机", "db"],
                                        "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,空闲机池",
                "var_filter_module": "",
            },
            name="test_ip_selector_select_method_suc_has_filter_other_set_success_case",
            context={},
        )
        self.assertEqual("192.168.40.1,192.168.1.1", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[61, 3], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_service_template_ids=[61, 3], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'limit': 500, 'start': 0})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[61, 3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[61, 3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]
            }
        ])

    def test_ip_selector_select_method_suc_has_filter_other_set_module_success_case(self,
                                                                                    mock_get_client_by_user_return=None): # noqa
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["空闲机", "db"],
                                        "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,空闲机池",
                "var_filter_module": "空闲机",
            },
            name="test_ip_selector_select_method_suc_has_filter_other_set_module_success_case",
            context={},
        )
        self.assertEqual("192.168.1.1", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[3], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]
            }
        ])

    def test_ip_selector_select_method_suc_no_filter_no_modulue_success_case(self,
                                                                             mock_get_client_by_user_return=None):
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
        self.assertEqual("192.168.40.1", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[61], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_service_template_ids=[61], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'limit': 500, 'start': 0})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[61], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[61], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]

            }
        ])

    def test_ip_selector_select_method_suc_no_filter_success_case(self,
                                                                  mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["空闲机", "db"],
                                        "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "",
                "var_filter_module": "",
            },
            name="test_ip_selector_select_method_suc_no_filter_success_case",
            context={},
        )
        self.assertEqual("192.168.40.1,192.168.1.1", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[61, 3], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_service_template_ids=[61, 3], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'limit': 500, 'start': 0})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[61, 3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[61, 3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]
            }
        ])

    def test_ip_selector_select_method_no_inner_module_success_case(self,
                                                                    mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机", "集群1"], "var_module": ["空闲机", "db"],
                                        "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "ls",
            },
            name="test_ip_selector_select_method_no_inner_module_success_case",
            context={},
        )
        self.assertEqual("", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": []
            }
        ])

    def test_ip_selector_select_method_all_select_set_success__case(self,
                                                                    mock_get_client_by_user_return=None):
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
        self.assertEqual("", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[3], bk_set_ids=[31, 32], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": []
            }
        ])

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
        self.assertEqual("", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": []
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": []
            }
        ])

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
        self.assertEqual("192.168.1.1", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[3], bk_set_ids=[32], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]
            }
        ])

    def test_ip_selector_select_method_all_select_module_success_case(self,
                                                                      mock_get_client_by_user_return=None):
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
        self.assertEqual("", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[3], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": []
            }
        ])

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
        self.assertEqual("", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": []
            }
        ])

    def test_manual_method_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "manual",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["db"], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "空闲机,集群1", "var_manual_module": "all,db",
                                        "var_module_name": ""},
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "ls",
            },
            name="test_manual_method_success_case",
            context={},
        )
        self.assertEqual("", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": []
            }
        ])

    def test_manual_method_all_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "manual",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": [], "var_module": [], "var_module_name": ""},
                "var_ip_manual_value": {"var_manual_set": "集群1", "var_manual_module": "all",
                                        "var_module_name": ""},
                "var_filter_set": "",
                "var_filter_module": "",
            },
            name="test_manual_method_success_case",
            context={},
        )
        self.assertEqual("192.168.40.1", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[62, 61, 3, 4, 5], bk_set_ids=[31],
                               fields=['bk_module_id'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_service_template_ids=[62, 61, 3, 4, 5], bk_set_ids=[31],
                               fields=['bk_module_id'], page={'limit': 500, 'start': 0})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[61], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[61], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]
            }
        ])

    def test_manual_method_fail_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "manual",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["db"], "var_module_name": "ip"},
                "var_ip_manual_value": {"var_manual_set": "空闲机,集群1", "var_manual_module": "all,db",
                                        "var_module_name": ""},
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "ls",
            },
            name="test_manual_method_success_case",
            context={},
        )
        self.assertEqual("", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": []
            }
        ])

    def test_custom_method_success_case(self, mock_get_client_by_user_return=None):
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
        self.assertEqual("192.168.40.1", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[61], bk_set_ids=[31, 32], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_service_template_ids=[61], bk_set_ids=[31, 32], fields=['bk_module_id'],
                               page={'limit': 500, 'start': 0})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[61], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[61], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]
            }
        ])

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
        self.assertEqual("", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[], bk_set_ids=[31, 32], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": []
            }
        ])

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
        self.assertEqual("192.168.40.2,192.168.1.1", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[62, 3], bk_set_ids=[32], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_service_template_ids=[62, 3], bk_set_ids=[32], fields=['bk_module_id'],
                               page={'limit': 500, 'start': 0})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[62, 3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[62, 3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]
            }
        ])

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
        self.assertEqual("192.168.1.1", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[3], bk_set_ids=[31, 32], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]
            }
        ])

    def test_select_method_biz_input_inner_module_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["空闲机"], "var_module_name": "ip,空闲机"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "集群1,集群2",
                "var_filter_module": "db,空闲机",
            }
            ,
            name="test_select_method_biz_innerip_success_case",
            context={},
        )
        self.assertEqual("", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[3], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": []
            }
        ])

    def test_select_method_biz_input_inner_set_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["空闲机"], "var_module_name": "ip,空闲机"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "空闲机池,集群2",
                "var_filter_module": "空闲机",
            },
            name="test_select_method_biz_input_inner_set_success_case",
            context={},
        )
        self.assertEqual("192.168.1.1", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": []
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]
            }
        ])

    def test_select_method_no_filter_set_module_success_case(self, mock_get_client_by_user_return=None):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value={
                "var_ip_method": "select",
                "var_ip_custom_value": "",
                "var_ip_select_value": {"var_set": ["空闲机池", "集群1"], "var_module": ["空闲机"], "var_module_name": "ip,空闲机"},
                "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
                "var_filter_set": "",
                "var_filter_module": "",
            },
            name="test_select_method_no_filter_set_module_success_case",
            context={},
        )
        self.assertEqual("192.168.1.1", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[3], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[3], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]
            }
        ])

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
        self.assertEqual("192.168.40.1,192.168.1.1,192.168.1.2,192.168.1.3", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[62, 61, 3, 4, 5], bk_set_ids=[31],
                               fields=['bk_module_id'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_service_template_ids=[62, 61, 3, 4, 5], bk_set_ids=[31],
                               fields=['bk_module_id'], page={'limit': 500, 'start': 0})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": [call(bk_biz_id=1, bk_module_ids=[61, 3, 4, 5], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'start': 0, 'limit': 1}),
                          call(bk_biz_id=1, bk_module_ids=[61, 3, 4, 5], bk_supplier_account='supplier_account_token',
                               fields=['bk_host_innerip'], page={'limit': 500, 'start': 0})]
            }
        ])

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
        self.assertEqual("", set_module_ip_selector.get_value())
        call_assert([
            {
                "func": self.client.new().cc.find_module_with_relation,
                "calls": [call(bk_biz_id=1, bk_service_template_ids=[5], bk_set_ids=[31], fields=['bk_module_id'],
                               page={'start': 0, 'limit': 1})]
            },
            {
                "func": self.client.new().cc.list_biz_hosts,
                "calls": []
            }
        ])


def call_assert(calls_list):
    for call_item in calls_list:
        call_item["func"].assert_has_calls(calls=call_item["calls"])
