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

import unittest.mock

from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0 import (
    CCBatchUpdateHostComponent,
    CCBatchUpdateHostService,
    verify_host_property,
)


class VerifyHostPropertyTestCase(TestCase):
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.cc_format_prop_data")
    def test_verify_bk_isp_name_success(self, mock_cc_format_prop_data):
        mock_cc_format_prop_data.return_value = {"result": True, "data": {"电信": "1", "联通": "2"}}

        result, ex_data = verify_host_property("system", "admin", "zh-cn", "bk_isp_name", "电信")

        self.assertTrue(result)
        self.assertEqual(ex_data, "")

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.cc_format_prop_data")
    def test_verify_bk_isp_name_format_fail(self, mock_cc_format_prop_data):
        mock_cc_format_prop_data.return_value = {"result": False, "message": "format error"}

        result, ex_data = verify_host_property("system", "admin", "zh-cn", "bk_isp_name", "电信")

        self.assertFalse(result)
        self.assertEqual(ex_data, "format error")

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.cc_format_prop_data")
    def test_verify_bk_isp_name_invalid_value(self, mock_cc_format_prop_data):
        mock_cc_format_prop_data.return_value = {"result": True, "data": {"电信": "1", "联通": "2"}}

        result, ex_data = verify_host_property("system", "admin", "zh-cn", "bk_isp_name", "移动")

        self.assertFalse(result)
        self.assertIn("移动", ex_data)

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.cc_format_prop_data")
    def test_verify_bk_state_name_success(self, mock_cc_format_prop_data):
        mock_cc_format_prop_data.return_value = {"result": True, "data": {"中国": "1", "美国": "2"}}

        result, ex_data = verify_host_property("system", "admin", "zh-cn", "bk_state_name", "中国")

        self.assertTrue(result)
        self.assertEqual(ex_data, "")

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.cc_format_prop_data")
    def test_verify_bk_state_name_invalid_value(self, mock_cc_format_prop_data):
        mock_cc_format_prop_data.return_value = {"result": True, "data": {"中国": "1", "美国": "2"}}

        result, ex_data = verify_host_property("system", "admin", "zh-cn", "bk_state_name", "日本")

        self.assertFalse(result)
        self.assertIn("日本", ex_data)

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.cc_format_prop_data")
    def test_verify_bk_province_name_success(self, mock_cc_format_prop_data):
        mock_cc_format_prop_data.return_value = {"result": True, "data": {"广东": "1", "北京": "2"}}

        result, ex_data = verify_host_property("system", "admin", "zh-cn", "bk_province_name", "广东")

        self.assertTrue(result)
        self.assertEqual(ex_data, "")

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.cc_format_prop_data")
    def test_verify_bk_province_name_invalid_value(self, mock_cc_format_prop_data):
        mock_cc_format_prop_data.return_value = {"result": True, "data": {"广东": "1", "北京": "2"}}

        result, ex_data = verify_host_property("system", "admin", "zh-cn", "bk_province_name", "上海")

        self.assertFalse(result)
        self.assertIn("上海", ex_data)

    def test_verify_other_property(self):
        # 测试其他属性，直接返回成功
        result, ex_data = verify_host_property("system", "admin", "zh-cn", "bk_host_name", "test_host")

        self.assertTrue(result)
        self.assertEqual(ex_data, "")


class CCBatchUpdateHostServiceTestCase(TestCase):
    def setUp(self):
        self.service = CCBatchUpdateHostService()
        self.service.logger = MagicMock()

    def test_inputs_format(self):
        inputs = self.service.inputs_format()
        self.assertEqual(len(inputs), 3)
        self.assertEqual(inputs[0].key, "cc_host_update_method")
        self.assertEqual(inputs[1].key, "cc_host_property_custom")
        self.assertEqual(inputs[2].key, "gcs_template_break_line")

    def test_outputs_format(self):
        outputs = self.service.outputs_format()
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0].key, "invalid_ip")

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.verify_host_property")
    def test_execute_manual_mode_success(self, mock_verify_host_property, mock_get_client):
        # 准备mock数据
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "biz_cc_id": 2,
                "language": "zh-cn",
            }.get(x, default)
        )

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "cc_host_update_method": "manual",
                "cc_host_property_custom": [
                    {
                        "bk_host_innerip": "192.168.1.1",
                        "bk_host_name": "test_host",
                    }
                ],
                "cc_auto_separator": ",",
            }.get(x, default)
        )

        # mock client
        mock_client = MagicMock()
        mock_client.api.batch_update_host = MagicMock(return_value={"result": True})
        mock_get_client.return_value = mock_client

        # mock verify_host_property
        mock_verify_host_property.return_value = (True, "")

        # mock get_host_list_with_cloud_id
        with patch.object(self.service, "get_host_list_with_cloud_id", return_value={"result": True, "data": ["100"]}):
            # 执行
            result = self.service.execute(data, parent_data)

        # 断言
        self.assertTrue(result)

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.chunk_table_data")
    def test_execute_auto_mode_chunk_fail(self, mock_chunk_table_data, mock_get_client):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "biz_cc_id": 2,
                "language": "zh-cn",
            }.get(x, default)
        )

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "cc_host_update_method": "auto",
                "cc_host_property_custom": [{"field": "value1,value2"}],
                "cc_auto_separator": ",",
            }.get(x, default)
        )

        # mock chunk_table_data 返回失败
        mock_chunk_table_data.return_value = {"result": False, "message": "chunk failed"}

        # 执行
        result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.get_client_by_username")
    def test_execute_get_host_list_fail(self, mock_get_client):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "biz_cc_id": 2,
                "language": "zh-cn",
            }.get(x, default)
        )

        data = MagicMock()
        data.outputs = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "cc_host_update_method": "manual",
                "cc_host_property_custom": [
                    {
                        "bk_host_innerip": "192.168.1.1",
                        "bk_host_name": "test_host",
                    }
                ],
                "cc_auto_separator": ",",
            }.get(x, default)
        )

        # mock get_host_list_with_cloud_id 返回失败
        with patch.object(
            self.service, "get_host_list_with_cloud_id", return_value={"result": False, "message": "host not found"}
        ):
            # 执行
            result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.verify_host_property")
    def test_execute_verify_host_property_fail(self, mock_verify_host_property, mock_get_client):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "biz_cc_id": 2,
                "language": "zh-cn",
            }.get(x, default)
        )

        data = MagicMock()
        data.outputs = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "cc_host_update_method": "manual",
                "cc_host_property_custom": [
                    {
                        "bk_host_innerip": "192.168.1.1",
                        "bk_isp_name": "移动",
                    }
                ],
                "cc_auto_separator": ",",
            }.get(x, default)
        )

        # mock verify_host_property 返回失败
        mock_verify_host_property.return_value = (False, "invalid isp name")

        # mock get_host_list_with_cloud_id
        with patch.object(self.service, "get_host_list_with_cloud_id", return_value={"result": True, "data": ["100"]}):
            # 执行
            result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.verify_host_property")
    def test_execute_batch_update_host_fail(self, mock_verify_host_property, mock_get_client):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "biz_cc_id": 2,
                "language": "zh-cn",
            }.get(x, default)
        )

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "cc_host_update_method": "manual",
                "cc_host_property_custom": [
                    {
                        "bk_host_innerip": "192.168.1.1",
                        "bk_host_name": "test_host",
                    }
                ],
                "cc_auto_separator": ",",
            }.get(x, default)
        )

        # mock client
        mock_client = MagicMock()
        mock_client.api.batch_update_host = MagicMock(return_value={"result": False, "message": "update failed"})
        mock_get_client.return_value = mock_client

        # mock verify_host_property
        mock_verify_host_property.return_value = (True, "")

        # mock get_host_list_with_cloud_id
        with patch.object(self.service, "get_host_list_with_cloud_id", return_value={"result": True, "data": ["100"]}):
            # 执行
            result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", unittest.mock.ANY)

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.verify_host_property")
    def test_execute_with_empty_property_value(self, mock_verify_host_property, mock_get_client):
        # 测试属性值为空的情况，应该被过滤掉
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "biz_cc_id": 2,
                "language": "zh-cn",
            }.get(x, default)
        )

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "cc_host_update_method": "manual",
                "cc_host_property_custom": [
                    {
                        "bk_host_innerip": "192.168.1.1",
                        "bk_host_name": "test_host",
                        "bk_comment": "",  # 空值应该被过滤
                    }
                ],
                "cc_auto_separator": ",",
            }.get(x, default)
        )

        # mock client
        mock_client = MagicMock()
        mock_client.api.batch_update_host = MagicMock(return_value={"result": True})
        mock_get_client.return_value = mock_client

        # mock verify_host_property
        mock_verify_host_property.return_value = (True, "")

        # mock get_host_list_with_cloud_id
        with patch.object(self.service, "get_host_list_with_cloud_id", return_value={"result": True, "data": ["100"]}):
            # 执行
            result = self.service.execute(data, parent_data)

        # 断言
        self.assertTrue(result)
        # 验证 batch_update_host 被调用，且 properties 中没有空值
        call_args = mock_client.api.batch_update_host.call_args
        properties = call_args[0][0]["update"][0]["properties"]
        self.assertIn("bk_host_name", properties)
        self.assertNotIn("bk_comment", properties)


class CCBatchUpdateHostComponentTestCase(TestCase):
    def test_component_code(self):
        component = CCBatchUpdateHostComponent
        self.assertEqual(component.code, "cc_batch_update_host")
        self.assertEqual(component.bound_service, CCBatchUpdateHostService)
