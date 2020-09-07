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
from mock import MagicMock, patch

from django.test import TestCase

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
        find_module_with_relation_return=None,
        list_biz_hosts_return=None,
        list_service_template_return=None,
        find_module_batch_return=None,
        cc_get_ips_info_by_str_return=None,
    ):
        self.cc = MagicMock()
        self.cc.list_biz_hosts_topo = MagicMock(return_value=list_biz_hosts_topo_return)
        self.cc.find_module_with_relation = MagicMock(return_value=find_module_with_relation_return)
        self.cc.list_biz_hosts = MagicMock(return_value=list_biz_hosts_return)
        self.cc.search_set = MagicMock(return_value=search_set_return)
        self.cc.list_service_template = MagicMock(return_value=list_service_template_return)
        self.cc.find_module_batch = MagicMock(return_value=find_module_batch_return)
        self.cc_get_ips_info_by_str = MagicMock(return_value=cc_get_ips_info_by_str_return)


mock_project_obj = MagicMock()
mock_project = MagicMock()
mock_project.objects.get = MagicMock(return_value=mock_project_obj)

SELECT_METHOD_SUC_CLIENT = MockClient(
    list_biz_hosts_return={
        "result": True,
        "code": 0,
        "message": "success",
        "data": {
            "count": 2,
            "info": [
                {
                    "bk_cloud_id": 0,
                    "bk_host_id": 1,
                    "bk_host_innerip": "192.168.15.18",
                    "bk_mac": "",
                    "bk_os_type": None,
                },
                {
                    "bk_cloud_id": 0,
                    "bk_host_id": 2,
                    "bk_host_innerip": "192.168.15.4",
                    "bk_mac": "",
                    "bk_os_type": None,
                },
            ],
        },
    },
    list_service_template_return={
        "result": True,
        "code": 0,
        "message": "success",
        "permission": None,
        "data": {"count": 2, "info": [{"id": 51, "name": "test3"}, {"id": 50, "name": "test2"}]},
    },
    search_set_return={
        "result": True,
        "code": 0,
        "message": "",
        "data": {
            "count": 1,
            "info": [
                {"default": 1, "bk_set_id": 30, "bk_set_name": "空闲机池"},
                {"default": 0, "bk_set_id": 31, "bk_set_name": "s1"},
                {"default": 0, "bk_set_id": 32, "bk_set_name": "s2"},
                {"default": 0, "bk_set_id": 33, "bk_set_name": "123"},
                {"default": 0, "bk_set_id": 34, "bk_set_name": "ck_集群"},
                {"default": 0, "bk_set_id": 38, "bk_set_name": "天天飞车"},
                {"default": 0, "bk_set_id": 39, "bk_set_name": "天天飞车"},
            ],
        },
    },
    find_module_with_relation_return={
        "result": True,
        "code": 0,
        "message": "success",
        "data": {"count": 2, "info": [{"bk_module_id": 60}, {"bk_module_id": 61}]},
    },
)
MANUAL_METHOD_SUC_CLIENT = MockClient(
    list_biz_hosts_return={
        "result": True,
        "code": 0,
        "message": "success",
        "data": {
            "count": 2,
            "info": [
                {
                    "bk_cloud_id": 0,
                    "bk_host_id": 1,
                    "bk_host_innerip": "192.168.15.18",
                    "bk_mac": "",
                    "bk_os_type": None,
                },
                {
                    "bk_cloud_id": 0,
                    "bk_host_id": 2,
                    "bk_host_innerip": "192.168.15.4",
                    "bk_mac": "",
                    "bk_os_type": None,
                },
            ],
        },
    },
    list_service_template_return={
        "result": True,
        "code": 0,
        "message": "success",
        "permission": None,
        "data": {"count": 2, "info": [{"id": 51, "name": "test3"}, {"id": 50, "name": "test2"}]},
    },
    search_set_return={
        "result": True,
        "code": 0,
        "message": "",
        "data": {
            "count": 1,
            "info": [
                {"default": 1, "bk_set_id": 30, "bk_set_name": "空闲机池"},
                {"default": 0, "bk_set_id": 31, "bk_set_name": "s1"},
                {"default": 0, "bk_set_id": 32, "bk_set_name": "s2"},
                {"default": 0, "bk_set_id": 33, "bk_set_name": "123"},
                {"default": 0, "bk_set_id": 34, "bk_set_name": "ck_集群"},
                {"default": 0, "bk_set_id": 38, "bk_set_name": "天天飞车"},
                {"default": 0, "bk_set_id": 39, "bk_set_name": "天天飞车"},
            ],
        },
    },
    find_module_with_relation_return={
        "result": True,
        "code": 0,
        "message": "success",
        "data": {"count": 2, "info": [{"bk_module_id": 60}, {"bk_module_id": 61}]},
    },
)
CUSTOM_METHOD_SUC_CLIENT = MockClient(
    list_biz_hosts_return={
        "result": True,
        "code": 0,
        "message": "success",
        "data": {
            "count": 2,
            "info": [
                {
                    "bk_cloud_id": 0,
                    "bk_host_id": 1,
                    "bk_host_innerip": "192.168.15.18",
                    "bk_mac": "",
                    "bk_os_type": None,
                },
                {
                    "bk_cloud_id": 0,
                    "bk_host_id": 2,
                    "bk_host_innerip": "192.168.15.4",
                    "bk_mac": "",
                    "bk_os_type": None,
                },
            ],
        },
    },
    list_service_template_return={
        "result": True,
        "code": 0,
        "message": "success",
        "permission": None,
        "data": {"count": 2, "info": [{"id": 51, "name": "test3"}, {"id": 50, "name": "test2"}]},
    },
    search_set_return={
        "result": True,
        "code": 0,
        "message": "",
        "data": {
            "count": 1,
            "info": [
                {"default": 1, "bk_set_id": 30, "bk_set_name": "空闲机池"},
                {"default": 0, "bk_set_id": 31, "bk_set_name": "s1"},
                {"default": 0, "bk_set_id": 32, "bk_set_name": "s2"},
                {"default": 0, "bk_set_id": 33, "bk_set_name": "123"},
                {"default": 0, "bk_set_id": 34, "bk_set_name": "ck_集群"},
                {"default": 0, "bk_set_id": 38, "bk_set_name": "天天飞车"},
                {"default": 0, "bk_set_id": 39, "bk_set_name": "天天飞车"},
            ],
        },
    },
    find_module_with_relation_return={
        "result": True,
        "code": 0,
        "message": "success",
        "data": {"count": 2, "info": [{"bk_module_id": 60}, {"bk_module_id": 61}]},
    },
    cc_get_ips_info_by_str_return={"result": True, "code": 0, "message": "success", "data": {}},
)
SELECT_METHOD_FAIL_CLIENT = MockClient(
    list_biz_hosts_return={"result": False, "code": 0, "message": "success", "data": {}},
    list_service_template_return={
        "result": True,
        "code": 0,
        "message": "success",
        "permission": None,
        "data": {"count": 2, "info": [{"id": 51, "name": "test3"}, {"id": 50, "name": "test2"}]},
    },
    search_set_return={
        "result": True,
        "code": 0,
        "message": "",
        "data": {
            "count": 1,
            "info": [
                {"default": 1, "bk_set_id": 30, "bk_set_name": "空闲机池"},
                {"default": 0, "bk_set_id": 32, "bk_set_name": "s2"},
                {"default": 0, "bk_set_id": 33, "bk_set_name": "123"},
                {"default": 0, "bk_set_id": 34, "bk_set_name": "ck_集群"},
                {"default": 0, "bk_set_id": 38, "bk_set_name": "天天飞车"},
                {"default": 0, "bk_set_id": 39, "bk_set_name": "天天飞车"},
            ],
        },
    },
    find_module_with_relation_return={
        "result": True,
        "code": 0,
        "message": "success",
        "data": {"count": 2, "info": [{"bk_module_id": 60}, {"bk_module_id": 61}]},
    },
)
MANUAL_METHOD_FAIL_CLIENT = MockClient(
    list_biz_hosts_return={"result": False, "code": 0, "message": "success", "data": {}},
    list_service_template_return={
        "result": True,
        "code": 0,
        "message": "success",
        "permission": None,
        "data": {"count": 2, "info": [{"id": 51, "name": "test3"}, {"id": 50, "name": "test2"}]},
    },
    search_set_return={
        "result": True,
        "code": 0,
        "message": "",
        "data": {
            "count": 1,
            "info": [
                {"default": 1, "bk_set_id": 30, "bk_set_name": "空闲机池"},
                {"default": 0, "bk_set_id": 32, "bk_set_name": "s2"},
                {"default": 0, "bk_set_id": 33, "bk_set_name": "123"},
                {"default": 0, "bk_set_id": 34, "bk_set_name": "ck_集群"},
                {"default": 0, "bk_set_id": 38, "bk_set_name": "天天飞车"},
                {"default": 0, "bk_set_id": 39, "bk_set_name": "天天飞车"},
            ],
        },
    },
    find_module_with_relation_return={
        "result": True,
        "code": 0,
        "message": "success",
        "data": {"count": 2, "info": [{"bk_module_id": 60}, {"bk_module_id": 61}]},
    },
)
CUSTOM_METHOD_FAIL_CLIENT = MockClient(
    list_biz_hosts_return={"result": False, "code": 0, "message": "success", "data": {}},
    list_service_template_return={
        "result": True,
        "code": 0,
        "message": "success",
        "permission": None,
        "data": {"count": 2, "info": [{"id": 51, "name": "test3"}, {"id": 50, "name": "test2"}]},
    },
    search_set_return={
        "result": True,
        "code": 0,
        "message": "",
        "data": {
            "count": 1,
            "info": [
                {"default": 1, "bk_set_id": 30, "bk_set_name": "空闲机池"},
                {"default": 0, "bk_set_id": 32, "bk_set_name": "s2"},
                {"default": 0, "bk_set_id": 33, "bk_set_name": "123"},
                {"default": 0, "bk_set_id": 34, "bk_set_name": "ck_集群"},
                {"default": 0, "bk_set_id": 38, "bk_set_name": "天天飞车"},
                {"default": 0, "bk_set_id": 39, "bk_set_name": "天天飞车"},
            ],
        },
    },
    find_module_with_relation_return={
        "result": True,
        "code": 0,
        "message": "success",
        "data": {"count": 2, "info": [{"bk_module_id": 60}, {"bk_module_id": 61}]},
    },
)

IP_SELECTOR_SELECT_METHOD_SUC_VALUE = {
    "var_ip_method": "select",
    "var_ip_custom_value": "",
    "var_ip_select_value": {"var_set": ["空闲机池", "s1"], "var_module": ["db"], "var_module_name": "ip"},
    "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
    "var_filter_set": "s1,s2",
    "var_filter_module": "ls",
}
IP_SELECTOR_SELECT_METHOD_FAIL_VALUE = {
    "var_ip_method": "select",
    "var_ip_custom_value": "",
    "var_ip_select_value": {"var_set": ["空闲机池", "s1"], "var_module": ["db"], "var_module_name": "ip"},
    "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
    "var_filter_set": "s1,s2",
    "var_filter_module": "ls",
}
IP_SELECTOR_MANUAL_METHOD_SUC_VALUE = {
    "var_ip_method": "manual",
    "var_ip_custom_value": "",
    "var_ip_select_value": {"var_set": ["空闲机池", "s1"], "var_module": ["db"], "var_module_name": "ip"},
    "var_ip_manual_value": {"var_manual_set": "空闲机池,s1", "var_manual_module": "all,db", "var_module_name": ""},
    "var_filter_set": "s1,s2",
    "var_filter_module": "ls",
}
IP_SELECTOR_MANUAL_METHOD_FAIL_VALUE = {
    "var_ip_method": "manual",
    "var_ip_custom_value": "",
    "var_ip_select_value": {"var_set": ["空闲机池", "s1"], "var_module": ["db"], "var_module_name": "ip"},
    "var_ip_manual_value": {"var_manual_set": "空闲机池,s1", "var_manual_module": "all,db", "var_module_name": ""},
    "var_filter_set": "s1,s2",
    "var_filter_module": "ls",
}
IP_SELECTOR_CUSTOM_METHOD_SUC_VALUE = {
    "var_ip_method": "custom",
    "var_ip_custom_value": "192.168.15.18,192.168.15.4",
    "var_ip_select_value": {"var_set": [], "var_module": [], "var_module_name": "ip"},
    "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
    "var_filter_set": "s1,s2",
    "var_filter_module": "ls",
}
IP_SELECTOR_CUSTOM_METHOD_FAIL_VALUE = {
    "var_ip_method": "custom",
    "var_ip_custom_value": "192.168.15.18,192.168.15.4",
    "var_ip_select_value": {"var_set": [], "var_module": [], "var_module_name": "ip"},
    "var_ip_manual_value": {"var_manual_set": "", "var_manual_module": "", "var_module_name": ""},
    "var_filter_set": "s1,s2",
    "var_filter_module": "ls",
}


class VarCmdbSetModuleIpSelectorTestCase(TestCase):
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

        self.pipeline_data = {"executor": "admin", "biz_cc_id": 123, "project_id": 1}

        self.project_patcher.start()
        self.supplier_account_for_project_patcher.start()

        self.select_method_success_return = "192.168.15.18,192.168.15.4"
        self.select_method_get_ip_fail_return = ""
        self.manual_method_success_return = "192.168.15.18,192.168.15.4"
        self.manual_method_fail_return = ""
        self.custom_method_success_return = "192.168.15.18,192.168.15.4"
        self.custom_method_fail_return = ""

    def tearDown(self):
        self.project_patcher.stop()
        self.supplier_account_for_project_patcher.stop()

    @patch(GET_CLIENT_BY_USER, return_value=SELECT_METHOD_SUC_CLIENT)
    def test_select_method_success_case(self, mock_get_client_by_user_return):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value=IP_SELECTOR_SELECT_METHOD_SUC_VALUE,
            name="test_select_method_success_case",
            context={},
        )
        self.assertEqual(self.select_method_success_return, set_module_ip_selector.get_value())

    @patch(GET_CLIENT_BY_USER, return_value=SELECT_METHOD_FAIL_CLIENT)
    def test_select_method_get_ip_fail_case(self, mock_get_client_by_user_return):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value=IP_SELECTOR_SELECT_METHOD_FAIL_VALUE,
            name="test_select_method_get_ip_fail_case",
            context={},
        )
        self.assertEqual(self.select_method_get_ip_fail_return, set_module_ip_selector.get_value())

    @patch(GET_CLIENT_BY_USER, return_value=MANUAL_METHOD_SUC_CLIENT)
    def test_manual_method_success_case(self, mock_get_client_by_user_return):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value=IP_SELECTOR_MANUAL_METHOD_SUC_VALUE,
            name="test_manual_method_success_case",
            context={},
        )
        self.assertEqual(self.manual_method_success_return, set_module_ip_selector.get_value())

    @patch(GET_CLIENT_BY_USER, return_value=MANUAL_METHOD_FAIL_CLIENT)
    def test_manual_method_fail_case(self, mock_get_client_by_user_return):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value=IP_SELECTOR_MANUAL_METHOD_FAIL_VALUE,
            name="test_manual_method_success_case",
            context={},
        )
        self.assertEqual(self.manual_method_fail_return, set_module_ip_selector.get_value())

    @patch(GET_CLIENT_BY_USER, return_value=CUSTOM_METHOD_SUC_CLIENT)
    def test_custom_method_success_case(self, mock_get_client_by_user_return):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value=IP_SELECTOR_MANUAL_METHOD_SUC_VALUE,
            name="test_custom_method_success_case",
            context={},
        )
        self.assertEqual(self.custom_method_success_return, set_module_ip_selector.get_value())

    @patch(GET_CLIENT_BY_USER, return_value=CUSTOM_METHOD_FAIL_CLIENT)
    def test_custom_method_fail_case(self, mock_get_client_by_user_return):
        set_module_ip_selector = SetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value=IP_SELECTOR_CUSTOM_METHOD_FAIL_VALUE,
            name="test_manual_method_success_case",
            context={},
        )
        self.assertEqual(self.custom_method_fail_return, set_module_ip_selector.get_value())
