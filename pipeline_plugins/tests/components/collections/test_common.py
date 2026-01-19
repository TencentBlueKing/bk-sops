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

from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.common import HttpRequestService


class HttpRequestServiceTestCase(TestCase):
    """测试 HttpRequestService"""

    def setUp(self):
        self.service = HttpRequestService()
        # 为 service 设置 logger，避免 AttributeError
        self.service.logger = logging.getLogger("test")

    def test_inputs_format(self):
        """测试输入格式定义"""
        inputs = self.service.inputs_format()
        self.assertEqual(len(inputs), 3)

        input_keys = [item.key for item in inputs]
        self.assertIn("bk_http_request_method", input_keys)
        self.assertIn("bk_http_request_url", input_keys)
        self.assertIn("bk_http_request_body", input_keys)

    def test_outputs_format(self):
        """测试输出格式定义"""
        outputs = self.service.outputs_format()
        self.assertEqual(len(outputs), 2)

        output_keys = [item.key for item in outputs]
        self.assertIn("data", output_keys)
        self.assertIn("status_code", output_keys)

    def test_execute_returns_true(self):
        """测试execute方法返回True"""
        data = MagicMock()
        parent_data = MagicMock()
        result = self.service.execute(data, parent_data)
        self.assertTrue(result)

    def test_need_schedule(self):
        """测试需要调度"""
        self.assertTrue(self.service.__need_schedule__)

    @patch("pipeline_plugins.components.collections.common.requests.request")
    def test_schedule_get_request_success(self, mock_request):
        """测试GET请求成功"""
        # 模拟成功的响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": True, "message": "success"}
        mock_request.return_value = mock_response

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key: {
            "bk_http_request_method": "GET",
            "bk_http_request_url": "http://example.com/api",
            "bk_http_request_body": "",
        }.get(key)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None

        result = self.service.schedule(data, parent_data, callback_data=None)

        self.assertTrue(result)
        data.set_outputs.assert_any_call("data", {"result": True, "message": "success"})
        data.set_outputs.assert_any_call("status_code", 200)

    @patch("pipeline_plugins.components.collections.common.requests.request")
    def test_schedule_post_request_success(self, mock_request):
        """测试POST请求成功"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 123}
        mock_request.return_value = mock_response

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key: {
            "bk_http_request_method": "POST",
            "bk_http_request_url": "http://example.com/api",
            "bk_http_request_body": '{"key": "value"}',
        }.get(key)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None

        result = self.service.schedule(data, parent_data, callback_data=None)

        self.assertTrue(result)
        # 验证POST请求带了data和headers
        call_args = mock_request.call_args
        self.assertIn("data", call_args[1])
        self.assertIn("headers", call_args[1])

    @patch("pipeline_plugins.components.collections.common.requests.request")
    def test_schedule_request_exception(self, mock_request):
        """测试请求异常"""
        mock_request.side_effect = Exception("Connection timeout")

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key: {
            "bk_http_request_method": "GET",
            "bk_http_request_url": "http://example.com/timeout",
            "bk_http_request_body": "",
        }.get(key)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None

        result = self.service.schedule(data, parent_data, callback_data=None)

        self.assertFalse(result)
        # 验证设置了错误输出
        calls = [str(call) for call in data.set_outputs.call_args_list]
        self.assertTrue(any("ex_data" in str(call) for call in calls))

    @patch("pipeline_plugins.components.collections.common.requests.request")
    def test_schedule_response_not_json(self, mock_request):
        """测试响应非JSON格式"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.encoding = "utf-8"
        mock_response.content = b"<html>Not JSON</html>"
        mock_response.json.side_effect = ValueError("No JSON object")
        mock_request.return_value = mock_response

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key: {
            "bk_http_request_method": "GET",
            "bk_http_request_url": "http://example.com/html",
            "bk_http_request_body": "",
        }.get(key)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None

        result = self.service.schedule(data, parent_data, callback_data=None)

        self.assertFalse(result)
        data.set_outputs.assert_any_call("status_code", 200)

    @patch("pipeline_plugins.components.collections.common.requests.request")
    def test_schedule_status_code_error(self, mock_request):
        """测试响应状态码错误"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal Server Error"}
        mock_request.return_value = mock_response

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key: {
            "bk_http_request_method": "GET",
            "bk_http_request_url": "http://example.com/error",
            "bk_http_request_body": "",
        }.get(key)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None

        result = self.service.schedule(data, parent_data, callback_data=None)

        self.assertFalse(result)
        data.set_outputs.assert_any_call("status_code", 500)

    def test_getstate(self):
        """测试__getstate__方法"""
        self.service.interval = None
        state = self.service.__getstate__()
        self.assertIsNotNone(state)
