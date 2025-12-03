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

from django.test import TestCase
from mock import patch

from pipeline_plugins.cmdb_ip_picker.utils import IPPickerHandler
from pipeline_plugins.tests.cmdb_ip_picker.utils.common_settings import MockCMDB, mock_get_client_by_user


class IPPickerHandlerTestCase(TestCase):
    def setUp(self):
        self.tenant_id = "system"
        self.selector = "ip"
        self.username = "username"
        self.bk_biz_id = "bk_biz_id"
        self.bk_supplier_account = "bk_supplier_account"

        mock_get_client_by_user.success = True
        self.patch_client = patch(
            "pipeline_plugins.cmdb_ip_picker.utils.get_client_by_username", mock_get_client_by_user
        )
        self.patch_client.start()
        self.addCleanup(self.patch_client.stop)
        self.patch_cmdb = patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb", MockCMDB)
        self.patch_cmdb.start()
        self.addCleanup(self.patch_cmdb.stop)

    def test__init_default(self):
        expected_property_filters = {
            "host_property_filter": {"condition": "AND", "rules": []},
            "module_property_filter": {"condition": "AND", "rules": []},
            "set_property_filter": {"condition": "AND", "rules": []},
        }

        ip_picker_handler = IPPickerHandler(self.selector, self.username, self.bk_biz_id, self.bk_supplier_account)
        self.assertEqual(ip_picker_handler.property_filters, expected_property_filters)

    def test__inject_condition_params(self):
        filters = [
            {"field": "host", "value": ["1.1.1.1", "2.2.2.2"]},
            {"field": "set", "value": ["set2"]},
            {"field": "set", "value": ["set3"]},
            {"field": "module", "value": ["test1"]},
        ]
        excludes = [{"field": "set", "value": ["set2"]}, {"field": "host", "value": ["3.3.3.3"]}]
        expected_property_filters = {
            "host_property_filter": {
                "condition": "AND",
                "rules": [
                    {"field": "bk_host_innerip", "operator": "in", "value": ["1.1.1.1", "2.2.2.2"]},
                    {"field": "bk_host_innerip", "operator": "not_in", "value": ["3.3.3.3"]},
                ],
            },
            "module_property_filter": {
                "condition": "AND",
                "rules": [
                    {"field": "bk_module_id", "operator": "in", "value": [5, 8]},
                    {"field": "bk_module_id", "operator": "not_in", "value": [5, 6, 7]},
                ],
            },
            "set_property_filter": {"condition": "AND", "rules": []},
        }

        ip_picker_handler = IPPickerHandler(
            self.selector, self.username, self.bk_biz_id, self.bk_supplier_account, filters=filters, excludes=excludes
        )
        self.assertEqual(ip_picker_handler.property_filters, expected_property_filters)

    def test__inject_host_params(self):
        inputted_ips = [
            {
                "bk_host_name": "host1",
                "bk_host_id": 1,
                "agent": 1,
                "cloud": [
                    {
                        "bk_obj_name": "",
                        "id": "0",
                        "bk_obj_id": "plat",
                        "bk_obj_icon": "",
                        "bk_inst_id": 0,
                        "bk_inst_name": "default area",
                    }
                ],
                "bk_host_innerip": "1.1.1.1",
            },
            {
                "bk_host_name": "host2",
                "bk_host_id": 2,
                "agent": 1,
                "cloud": [
                    {
                        "bk_obj_name": "",
                        "id": "0",
                        "bk_obj_id": "plat",
                        "bk_obj_icon": "",
                        "bk_inst_id": 0,
                        "bk_inst_name": "default area",
                    }
                ],
                "bk_host_innerip": "2.2.2.2",
            },
        ]
        expected_property_filters = {
            "host_property_filter": {
                "condition": "AND",
                "rules": [{"field": "bk_host_id", "operator": "in", "value": [1, 2]}],
            },
            "module_property_filter": {"condition": "AND", "rules": []},
            "set_property_filter": {"condition": "AND", "rules": []},
        }

        ip_picker_handler = IPPickerHandler(self.selector, self.username, self.bk_biz_id, self.bk_supplier_account)
        ip_picker_handler._inject_host_params(inputted_ips)
        self.assertEqual(ip_picker_handler.property_filters, expected_property_filters)

    def test__inject_topo_params(self):
        self.selector = "topo"
        topo_list = [
            {"bk_obj_id": "set", "bk_inst_id": 3},
            {"bk_obj_id": "module", "bk_inst_id": 5},
            {"bk_obj_id": "module", "bk_inst_id": 8},
        ]
        expected_property_filters = {
            "host_property_filter": {"condition": "AND", "rules": []},
            "module_property_filter": {
                "condition": "AND",
                "rules": [{"field": "bk_module_id", "operator": "in", "value": [8, 5, 6, 7]}],
            },
            "set_property_filter": {"condition": "AND", "rules": []},
        }

        ip_picker_handler = IPPickerHandler(
            self.tenant_id, self.selector, self.username, self.bk_biz_id, self.bk_supplier_account
        )
        ip_picker_handler._inject_topo_params(topo_list)
        self.assertEqual(ip_picker_handler.property_filters, expected_property_filters)

    def test_format_host_info(self):
        host_info = [
            {"bk_host_innerip": "1.1.1.1", "bk_host_id": 1},
            {"bk_host_id": 2, "bk_host_innerip": "2.2.2.2,3.3.3.3"},
        ]
        expected_host_info = [
            {"bk_host_innerip": "1.1.1.1", "bk_host_id": 1},
            {"bk_host_id": 2, "bk_host_innerip": "2.2.2.2"},
        ]
        formatted_host_info = IPPickerHandler.format_host_info(host_info)
        self.assertEqual(formatted_host_info, expected_host_info)

    def test__fetch_host_ip_with_property_filter(self):
        property_filters = {
            "host_property_filter": {
                "condition": "AND",
                "rules": [{"field": "bk_host_id", "operator": "in", "value": [3]}],
            },
            "module_property_filter": {
                "condition": "AND",
                "rules": [
                    {"field": "bk_module_id", "operator": "not_in", "value": [3, 4, 5]},
                    {"field": "bk_module_id", "operator": "in", "value": [8]},
                ],
            },
            "set_property_filter": {
                "condition": "AND",
                "rules": [
                    {"field": "bk_set_id", "operator": "not_in", "value": [3]},
                    {"field": "bk_set_id", "operator": "in", "value": [4]},
                ],
            },
        }
        expected_result = {
            "result": True,
            "message": "",
            "code": "0",
            "data": [
                {
                    "bk_host_innerip": "3.3.3.3",
                    "bk_host_outerip": "3.3.3.3",
                    "bk_host_name": "3.3.3.3",
                    "bk_host_id": 3,
                    "bk_cloud_id": 0,
                }
            ],
        }
        ip_picker_handler = IPPickerHandler(self.selector, self.username, self.bk_biz_id, self.bk_supplier_account)
        ip_picker_handler.property_filters = property_filters
        result = ip_picker_handler.fetch_host_ip_with_property_filter()
        self.assertEqual(result, expected_result)

    def test__ip_picker_handler(self):
        self.selector = "ip"
        params = {
            "selectors": self.selector,
            "ip": [
                {
                    "bk_host_name": "host1",
                    "bk_host_id": 1,
                    "agent": 1,
                    "cloud": [
                        {
                            "bk_obj_name": "",
                            "id": "0",
                            "bk_obj_id": "plat",
                            "bk_obj_icon": "",
                            "bk_inst_id": 0,
                            "bk_inst_name": "default area",
                        }
                    ],
                    "bk_host_innerip": "1.1.1.1",
                },
                {
                    "bk_host_name": "host2",
                    "bk_host_id": 2,
                    "agent": 1,
                    "cloud": [
                        {
                            "bk_obj_name": "",
                            "id": "0",
                            "bk_obj_id": "plat",
                            "bk_obj_icon": "",
                            "bk_inst_id": 0,
                            "bk_inst_name": "default area",
                        }
                    ],
                    "bk_host_innerip": "2.2.2.2",
                },
            ],
        }
        expected_result = {
            "result": True,
            "data": [
                {
                    "bk_host_innerip": "1.1.1.1",
                    "bk_host_outerip": "1.1.1.1",
                    "bk_host_name": "1.1.1.1",
                    "bk_host_id": 1,
                    "bk_cloud_id": 0,
                },
                {
                    "bk_host_innerip": "2.2.2.2",
                    "bk_host_outerip": "2.2.2.2",
                    "bk_host_name": "2.2.2.2",
                    "bk_host_id": 2,
                    "bk_cloud_id": 0,
                },
            ],
            "message": "",
        }
        ip_picker_handler = IPPickerHandler(
            self.tenant_id, self.selector, self.username, self.bk_biz_id, self.bk_supplier_account
        )
        result = ip_picker_handler.dispatch(params)
        self.assertEqual(result, expected_result)

    def test__topo_picker_handler(self):
        self.selector = "topo"
        params = {
            "selectors": self.selector,
            "topo": [{"bk_obj_id": "set", "bk_inst_id": 3}, {"bk_obj_id": "module", "bk_inst_id": 8}],
        }
        expected_result = {
            "result": True,
            "data": [
                {
                    "bk_host_innerip": "2.2.2.2",
                    "bk_host_outerip": "2.2.2.2",
                    "bk_host_name": "2.2.2.2",
                    "bk_host_id": 2,
                    "bk_cloud_id": 0,
                },
                {
                    "bk_host_innerip": "3.3.3.3",
                    "bk_host_outerip": "3.3.3.3",
                    "bk_host_name": "3.3.3.3",
                    "bk_host_id": 3,
                    "bk_cloud_id": 0,
                },
            ],
            "message": "",
        }
        ip_picker_handler = IPPickerHandler(
            self.tenant_id, self.selector, self.username, self.bk_biz_id, self.bk_supplier_account
        )
        result = ip_picker_handler.dispatch(params)
        self.assertEqual(result, expected_result)

    def test__group_picker_handler(self):
        self.selector = "group"
        params = {
            "selectors": self.selector,
            "group": [{"id": "group1"}, {"id": "group2"}],
        }
        expected_result = {
            "result": True,
            "data": [
                {
                    "bk_host_innerip": "3.3.3.3",
                    "bk_host_outerip": "3.3.3.3",
                    "bk_host_name": "3.3.3.3",
                    "bk_host_id": 3,
                    "bk_cloud_id": 0,
                    "host_modules_id": [8],
                },
            ],
            "message": "",
        }
        ip_picker_handler = IPPickerHandler(
            self.tenant_id,
            self.selector,
            self.username,
            self.bk_biz_id,
            self.bk_supplier_account,
            excludes=[{"field": "host", "value": ["1.1.1.1", "2.2.2.2"]}],
        )
        result = ip_picker_handler.dispatch(params)
        self.assertEqual(result, expected_result)
