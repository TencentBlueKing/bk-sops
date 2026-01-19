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
from mock import MagicMock, patch

from pipeline_plugins.cmdb_ip_picker.utils import (
    IPPickerDataGenerator,
    IPPickerHandler,
    format_condition_dict,
    format_condition_value,
)


class IPPickerDataGeneratorTestCase(TestCase):
    """测试 IPPickerDataGenerator 类"""

    def setUp(self):
        self.tenant_id = "system"
        self.bk_biz_id = 2
        self.username = "test_user"
        self.request_kwargs = {"username": self.username, "bk_biz_id": self.bk_biz_id}
        self.gen_kwargs = {}

    def test_generate_invalid_type(self):
        """测试无效的输入类型"""
        generator = IPPickerDataGenerator(
            self.tenant_id, "invalid_type", "test_data", self.request_kwargs.copy(), self.gen_kwargs, self.bk_biz_id
        )
        result = generator.generate()

        self.assertFalse(result["result"])
        self.assertIn("code", result)
        self.assertIn("message", result)

    @patch("pipeline_plugins.cmdb_ip_picker.utils.batch_request")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_client_by_username")
    def test_generate_group_data_success(self, mock_get_client, mock_batch_request):
        """测试成功生成动态分组数据"""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_batch_request.return_value = [
            {"id": "group1", "name": "分组1", "bk_obj_id": "host"},
            {"id": "group2", "name": "分组2", "bk_obj_id": "host"},
            {"id": "group3", "name": "分组3", "bk_obj_id": "set"},  # 非host类型，应被过滤
        ]

        generator = IPPickerDataGenerator(
            self.tenant_id, "group", "分组1,分组2", self.request_kwargs.copy(), self.gen_kwargs, self.bk_biz_id
        )
        result = generator.generate()

        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["name"], "分组1")

    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.cc_get_ips_info_by_str")
    def test_generate_ip_data_success(self, mock_get_ips, mock_settings):
        """测试成功生成IP数据"""
        mock_settings.ENABLE_IPV6 = False

        mock_get_ips.return_value = {
            "ip_result": [
                {"InnerIP": "10.0.0.1", "HostID": 1, "Source": 0},
                {"InnerIP": "10.0.0.2", "HostID": 2, "Source": 0},
            ],
            "invalid_ip": [],
        }

        generator = IPPickerDataGenerator(
            self.tenant_id, "ip", "10.0.0.1,10.0.0.2", self.request_kwargs.copy(), self.gen_kwargs, self.bk_biz_id
        )
        result = generator.generate()

        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["bk_host_innerip"], "10.0.0.1")

    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.cc_get_ips_info_by_str")
    def test_generate_ip_data_with_invalid_ip(self, mock_get_ips, mock_settings):
        """测试生成IP数据时包含无效IP"""
        mock_settings.ENABLE_IPV6 = False

        mock_get_ips.return_value = {
            "ip_result": [{"InnerIP": "10.0.0.1", "HostID": 1, "Source": 0}],
            "invalid_ip": ["10.0.0.999"],
        }

        generator = IPPickerDataGenerator(
            self.tenant_id, "ip", "10.0.0.1,10.0.0.999", self.request_kwargs.copy(), self.gen_kwargs, self.bk_biz_id
        )
        result = generator.generate()

        self.assertFalse(result["result"])
        self.assertIn("message", result)

    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.cc_get_ips_info_by_str_ipv6")
    def test_generate_ip_data_ipv6_enabled(self, mock_get_ips_ipv6, mock_settings):
        """测试IPv6启用时生成IP数据"""
        mock_settings.ENABLE_IPV6 = True

        mock_get_ips_ipv6.return_value = {
            "ip_result": [{"InnerIP": "fe80::1", "HostID": 1, "Source": 0}],
            "invalid_ip": [],
        }

        generator = IPPickerDataGenerator(
            self.tenant_id, "ip", "fe80::1", self.request_kwargs.copy(), self.gen_kwargs, self.bk_biz_id
        )
        result = generator.generate()

        self.assertTrue(result["result"])
        mock_get_ips_ipv6.assert_called_once()

    def test_generate_topo_data_success(self):
        """测试成功生成拓扑数据"""
        biz_topo_tree = {
            "bk_inst_id": 2,
            "bk_inst_name": "业务1",
            "bk_obj_id": "biz",
            "child": [
                {
                    "bk_inst_id": 3,
                    "bk_inst_name": "集群1",
                    "bk_obj_id": "set",
                    "child": [{"bk_inst_id": 5, "bk_inst_name": "模块1", "bk_obj_id": "module"}],
                }
            ],
        }

        generator = IPPickerDataGenerator(
            self.tenant_id,
            "topo",
            "业务1>集群1>模块1",
            self.request_kwargs.copy(),
            {"biz_topo_tree": biz_topo_tree},
            self.bk_biz_id,
        )
        result = generator.generate()

        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["bk_obj_id"], "module")

    def test_generate_topo_data_with_multiple_paths(self):
        """测试生成包含多个拓扑路径的数据"""
        biz_topo_tree = {
            "bk_inst_id": 2,
            "bk_inst_name": "业务1",
            "bk_obj_id": "biz",
            "child": [
                {
                    "bk_inst_id": 3,
                    "bk_inst_name": "集群1",
                    "bk_obj_id": "set",
                    "child": [
                        {"bk_inst_id": 5, "bk_inst_name": "模块1", "bk_obj_id": "module"},
                        {"bk_inst_id": 6, "bk_inst_name": "模块2", "bk_obj_id": "module"},
                    ],
                },
                {
                    "bk_inst_id": 4,
                    "bk_inst_name": "集群2",
                    "bk_obj_id": "set",
                    "child": [{"bk_inst_id": 7, "bk_inst_name": "模块3", "bk_obj_id": "module"}],
                },
            ],
        }

        generator = IPPickerDataGenerator(
            self.tenant_id,
            "topo",
            "业务1>集群1>模块1,业务1>集群2>模块3",
            self.request_kwargs.copy(),
            {"biz_topo_tree": biz_topo_tree},
            self.bk_biz_id,
        )
        result = generator.generate()

        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 2)

    def test_generate_topo_data_path_not_found(self):
        """测试生成拓扑数据时路径不存在"""
        biz_topo_tree = {"bk_inst_id": 2, "bk_inst_name": "业务1", "bk_obj_id": "biz", "child": []}

        generator = IPPickerDataGenerator(
            self.tenant_id,
            "topo",
            "业务1>不存在的集群>不存在的模块",
            self.request_kwargs.copy(),
            {"biz_topo_tree": biz_topo_tree},
            self.bk_biz_id,
        )

        with self.assertRaises(Exception):
            generator.generate()

    def test_remove_included_topo_path(self):
        """测试去除包含关系的拓扑路径"""
        from pipeline_plugins.cmdb_ip_picker.utils import IPPickerDataGenerator

        # 测试存在包含关系的情况
        path_list = [["业务1", "集群1", "模块1"], ["业务1", "集群1"], ["业务1", "集群2"]]
        result = IPPickerDataGenerator._remove_included_topo_path(path_list)

        # 应该只保留最短路径 ["业务1", "集群1"] 和 ["业务1", "集群2"]
        self.assertEqual(len(result), 2)
        self.assertIn(["业务1", "集群1"], result)
        self.assertIn(["业务1", "集群2"], result)

        # 测试不存在包含关系的情况
        path_list = [["业务1", "集群1"], ["业务1", "集群2"]]
        result = IPPickerDataGenerator._remove_included_topo_path(path_list)
        self.assertEqual(len(result), 2)


class IPPickerHandlerTestCase(TestCase):
    """测试 IPPickerHandler 类"""

    def setUp(self):
        self.tenant_id = "system"
        self.username = "test_user"
        self.bk_biz_id = 2

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_cmdb_topo_tree")
    def test_init_with_topo_selector(self, mock_get_topo):
        """测试使用topo选择器初始化"""
        mock_get_topo.return_value = {
            "result": True,
            "data": [{"bk_inst_id": 2, "bk_inst_name": "业务1", "bk_obj_id": "biz", "child": []}],
        }

        handler = IPPickerHandler(self.tenant_id, "topo", self.username, self.bk_biz_id)

        self.assertIsNotNone(handler.biz_topo_tree)
        self.assertIsNone(handler.error)

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_cmdb_topo_tree")
    def test_init_with_topo_error(self, mock_get_topo):
        """测试初始化时拓扑树获取失败"""
        mock_get_topo.return_value = {"result": False, "message": "获取拓扑树失败"}

        handler = IPPickerHandler(self.tenant_id, "topo", self.username, self.bk_biz_id)

        self.assertIsNotNone(handler.error)

    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    def test_ip_picker_handler(self, mock_settings, mock_cmdb):
        """测试IP选择器处理"""
        mock_settings.ENABLE_IPV6 = False
        mock_cmdb.get_business_host_topo.return_value = [
            {"host": {"bk_host_id": 1, "bk_host_innerip": "10.0.0.1", "bk_cloud_id": 0}}
        ]

        handler = IPPickerHandler(self.tenant_id, "ip", self.username, self.bk_biz_id)

        inputted_ips = [{"bk_host_id": 1}]
        result = handler.ip_picker_handler(inputted_ips)

        self.assertTrue(result["result"])
        self.assertIn("data", result)

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_cmdb_topo_tree")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    def test_topo_picker_handler(self, mock_settings, mock_cmdb, mock_get_topo):
        """测试拓扑选择器处理"""
        mock_settings.ENABLE_IPV6 = False

        biz_topo_tree = {
            "bk_inst_id": 2,
            "bk_inst_name": "业务1",
            "bk_obj_id": "biz",
            "child": [
                {
                    "bk_inst_id": 3,
                    "bk_inst_name": "集群1",
                    "bk_obj_id": "set",
                    "child": [{"bk_inst_id": 5, "bk_inst_name": "模块1", "bk_obj_id": "module", "bk_module_id": 5}],
                }
            ],
        }

        mock_get_topo.return_value = {"result": True, "data": [biz_topo_tree]}

        mock_cmdb.get_business_host_topo.return_value = [
            {"host": {"bk_host_id": 1, "bk_host_innerip": "10.0.0.1", "bk_cloud_id": 0}},
            {"host": {"bk_host_id": 2, "bk_host_innerip": "10.0.0.2", "bk_cloud_id": 0}},
        ]

        handler = IPPickerHandler(self.tenant_id, "topo", self.username, self.bk_biz_id)

        inputted_topo = [{"bk_obj_id": "module", "bk_inst_id": 5}]
        result = handler.topo_picker_handler(inputted_topo)

        self.assertTrue(result["result"])

    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_dynamic_group_list")
    def test_group_picker_handler_success(self, mock_get_group_list, mock_cmdb):
        """测试动态分组选择器成功处理"""
        mock_get_group_list.return_value = [{"id": "group1", "name": "分组1"}]

        mock_cmdb.get_dynamic_group_host_list.return_value = (
            True,
            {
                "data": [
                    {"bk_host_id": 1, "bk_host_innerip": "10.0.0.1", "bk_cloud_id": 0},
                    {"bk_host_id": 2, "bk_host_innerip": "10.0.0.2", "bk_cloud_id": 0},
                ]
            },
        )

        handler = IPPickerHandler(self.tenant_id, "group", self.username, self.bk_biz_id)

        inputted_group = [{"id": "group1", "name": "分组1"}]
        result = handler.group_picker_handler(inputted_group)

        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 2)

    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_dynamic_group_list")
    def test_group_picker_handler_api_failed(self, mock_get_group_list, mock_cmdb):
        """测试动态分组选择器API调用失败"""
        mock_get_group_list.return_value = [{"id": "group1", "name": "分组1"}]

        mock_cmdb.get_dynamic_group_host_list.return_value = (False, {"code": 500, "message": "API调用失败"})

        handler = IPPickerHandler(self.tenant_id, "group", self.username, self.bk_biz_id)

        inputted_group = [{"id": "group1", "name": "分组1"}]
        result = handler.group_picker_handler(inputted_group)

        self.assertFalse(result["result"])
        self.assertEqual(result["code"], 500)

    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_dynamic_group_list")
    def test_group_picker_handler_with_exception(self, mock_get_group_list, mock_cmdb):
        """测试动态分组选择器获取分组列表异常"""
        mock_get_group_list.side_effect = Exception("获取动态分组列表失败")

        mock_cmdb.get_dynamic_group_host_list.return_value = (
            True,
            {"data": [{"bk_host_id": 1, "bk_host_innerip": "10.0.0.1", "bk_cloud_id": 0}]},
        )

        handler = IPPickerHandler(self.tenant_id, "group", self.username, self.bk_biz_id)

        inputted_group = [{"id": "group1", "name": "分组1"}]
        result = handler.group_picker_handler(inputted_group)

        # 即使获取分组列表失败，仍然应该能处理，只是不做过滤
        self.assertTrue(result["result"])

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_cmdb_topo_tree")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    def test_topo_picker_handler_empty_modules(self, mock_settings, mock_cmdb, mock_get_topo):
        """测试拓扑选择器处理空模块ID"""
        mock_settings.ENABLE_IPV6 = False

        biz_topo_tree = {"bk_inst_id": 2, "bk_inst_name": "业务1", "bk_obj_id": "biz", "child": []}

        mock_get_topo.return_value = {"result": True, "data": [biz_topo_tree]}

        handler = IPPickerHandler(self.tenant_id, "topo", self.username, self.bk_biz_id)

        inputted_topo = [{"bk_obj_id": "set", "bk_inst_id": 999}]
        result = handler.topo_picker_handler(inputted_topo)

        # 没有找到模块时应该返回空列表
        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 0)

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_cmdb_topo_tree")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.extract_ip_from_ip_str")
    def test_init_with_filters_ipv6(self, mock_extract_ip, mock_settings, mock_cmdb, mock_get_topo):
        """测试使用IPv6过滤条件初始化"""
        mock_settings.ENABLE_IPV6 = True
        mock_get_topo.return_value = {
            "result": True,
            "data": [{"bk_inst_id": 2, "bk_inst_name": "业务1", "bk_obj_id": "biz", "child": []}],
        }

        mock_extract_ip.return_value = (
            ["fe80::1"],  # ipv6_list
            ["10.0.0.1"],  # ipv4_list
            [1, 2],  # host_id_list
            [],  # invalid_ip
            [],  # invalid_ip_v6
        )

        filters = [{"field": "host", "value": ["fe80::1", "10.0.0.1", "1", "2"]}]

        handler = IPPickerHandler(self.tenant_id, "ip", self.username, self.bk_biz_id, filters=filters)

        # 验证IPv6条件被正确注入
        host_filter_rules = handler.property_filters["host_property_filter"]["rules"]
        self.assertTrue(len(host_filter_rules) > 0)

    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    def test_format_host_info_with_ipv6(self, mock_settings, mock_cmdb):
        """测试使用IPv6格式化主机信息"""
        mock_settings.ENABLE_IPV6 = True

        host_info = [
            {"bk_host_id": 1, "bk_host_innerip": "", "bk_host_innerip_v6": "fe80::1", "bk_cloud_id": 0},
            {"bk_host_id": 2, "bk_host_innerip": "10.0.0.1", "bk_cloud_id": 0},
        ]

        result = IPPickerHandler.format_host_info(host_info)

        # 第一个主机应该使用IPv6地址
        self.assertEqual(result[0]["bk_host_innerip"], "fe80::1")
        # 第二个主机应该使用IPv4地址
        self.assertEqual(result[1]["bk_host_innerip"], "10.0.0.1")

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_cmdb_topo_tree")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    def test_init_with_excludes(self, mock_settings, mock_cmdb, mock_get_topo):
        """测试使用排除条件初始化"""
        mock_settings.ENABLE_IPV6 = False
        mock_get_topo.return_value = {
            "result": True,
            "data": [
                {
                    "bk_inst_id": 2,
                    "bk_inst_name": "业务1",
                    "bk_obj_id": "biz",
                    "child": [
                        {
                            "bk_inst_id": 3,
                            "bk_inst_name": "集群1",
                            "bk_obj_id": "set",
                            "child": [
                                {"bk_inst_id": 5, "bk_inst_name": "模块1", "bk_obj_id": "module", "bk_module_id": 5}
                            ],
                        }
                    ],
                }
            ],
        }

        excludes = [{"field": "host", "value": ["10.0.0.1"]}, {"field": "set", "value": ["集群1"]}]

        handler = IPPickerHandler(self.tenant_id, "ip", self.username, self.bk_biz_id, excludes=excludes)

        # 验证排除条件被正确注入
        host_filter_rules = handler.property_filters["host_property_filter"]["rules"]
        module_filter_rules = handler.property_filters["module_property_filter"]["rules"]
        self.assertTrue(len(host_filter_rules) > 0)
        self.assertTrue(len(module_filter_rules) > 0)


class UtilityFunctionsTestCase(TestCase):
    """测试工具函数"""

    def test_format_condition_dict(self):
        """测试格式化条件字典"""
        conditions = [
            {"field": "field1", "value": ["value1", "value2"]},
            {"field": "field1", "value": ["value3"]},
            {"field": "field2", "value": ["value4"]},
        ]
        result = format_condition_dict(conditions)
        self.assertIn("field1", result)
        self.assertIn("field2", result)
        self.assertEqual(len(result["field1"]), 3)
        self.assertEqual(len(result["field2"]), 1)

    def test_format_condition_value(self):
        """测试格式化条件值"""
        # 测试列表类型
        result = format_condition_value(["value1", "value2"])
        self.assertEqual(result, ["value1", "value2"])

        # 测试带换行符的字符串
        result = format_condition_value(["value1\nvalue2"])
        self.assertEqual(result, ["value1", "value2"])

        # 测试单个值列表
        result = format_condition_value(["value"])
        self.assertEqual(result, ["value"])
