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

import datetime
import logging

import pytz
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.controller import PauseService, SleepTimerService


class PauseServiceTestCase(TestCase):
    """测试 PauseService"""

    def setUp(self):
        self.service = PauseService()
        # 为 service 设置 logger，避免 AttributeError
        self.service.logger = logging.getLogger("test")

    def test_inputs_format(self):
        """测试输入格式"""
        inputs = self.service.inputs_format()
        self.assertEqual(len(inputs), 1)
        self.assertEqual(inputs[0].key, "description")

    def test_outputs_format(self):
        """测试输出格式"""
        outputs = self.service.outputs_format()
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0].key, "callback_data")

    @patch("pipeline_plugins.components.collections.controller.send_taskflow_message")
    def test_execute_success(self, mock_send_message):
        """测试execute成功"""
        data = MagicMock()
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = 123

        result = self.service.execute(data, parent_data)

        self.assertTrue(result)
        parent_data.get_one_of_inputs.assert_called_once_with("task_id")
        mock_send_message.delay.assert_called_once()

    def test_schedule_without_callback(self):
        """测试schedule没有回调数据"""
        data = MagicMock()
        parent_data = MagicMock()

        result = self.service.schedule(data, parent_data, callback_data=None)

        self.assertTrue(result)

    def test_schedule_with_callback(self):
        """测试schedule有回调数据"""
        data = MagicMock()
        parent_data = MagicMock()
        callback_data = {"key": "value"}

        result = self.service.schedule(data, parent_data, callback_data=callback_data)

        self.assertTrue(result)
        self.assertEqual(data.outputs.callback_data, callback_data)


class SleepTimerServiceTestCase(TestCase):
    """测试 SleepTimerService"""

    def setUp(self):
        self.service = SleepTimerService()
        # 为 service 设置 logger，避免 AttributeError
        self.service.logger = logging.getLogger("test")

    def test_inputs_format(self):
        """测试输入格式"""
        inputs = self.service.inputs_format()
        self.assertEqual(len(inputs), 2)

        input_keys = [item.key for item in inputs]
        self.assertIn("bk_timing", input_keys)
        self.assertIn("force_check", input_keys)

    def test_outputs_format(self):
        """测试输出格式"""
        outputs = self.service.outputs_format()
        self.assertEqual(len(outputs), 0)

    def test_date_regex(self):
        """测试日期正则表达式"""
        # 有效的日期时间格式
        self.assertIsNotNone(self.service.date_regex.match("2025-12-09 10:30:45"))
        self.assertIsNotNone(self.service.date_regex.match("2025-01-01 00:00:00"))
        self.assertIsNotNone(self.service.date_regex.match("2025-12-31 23:59:59"))

        # 无效的日期时间格式
        self.assertIsNone(self.service.date_regex.match("2025-12-09"))
        self.assertIsNone(self.service.date_regex.match("10:30:45"))
        self.assertIsNone(self.service.date_regex.match("invalid"))

    def test_seconds_regex(self):
        """测试秒数正则表达式"""
        # 有效的秒数格式
        self.assertIsNotNone(self.service.seconds_regex.match("3600"))
        self.assertIsNotNone(self.service.seconds_regex.match("0"))
        self.assertIsNotNone(self.service.seconds_regex.match("999999"))

        # 无效的秒数格式
        self.assertIsNone(self.service.seconds_regex.match("-100"))
        self.assertIsNone(self.service.seconds_regex.match("3.14"))
        self.assertIsNone(self.service.seconds_regex.match("abc"))

    @patch("pipeline_plugins.components.collections.controller.Project")
    def test_execute_with_seconds_success(self, mock_project):
        """测试使用秒数格式执行成功"""
        # 模拟 Project 对象
        mock_project_instance = MagicMock()
        mock_project_instance.time_zone = "Asia/Shanghai"
        mock_project.objects.get.return_value = mock_project_instance

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {"bk_timing": "3600", "force_check": True}.get(
            key, default
        )

        parent_data = MagicMock()
        parent_data.inputs.project_id = 1
        parent_data.get_one_of_inputs.return_value = None

        result = self.service.execute(data, parent_data)

        self.assertTrue(result)
        self.assertIsNotNone(data.outputs.timing_time)
        self.assertIsNotNone(data.outputs.business_tz)

    @patch("pipeline_plugins.components.collections.controller.Project")
    def test_execute_with_invalid_format(self, mock_project):
        """测试使用无效格式失败"""
        # 模拟 Project 对象
        mock_project_instance = MagicMock()
        mock_project_instance.time_zone = "Asia/Shanghai"
        mock_project.objects.get.return_value = mock_project_instance

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "bk_timing": "invalid_format",
            "force_check": True,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.inputs.project_id = 1
        parent_data.get_one_of_inputs.return_value = None

        result = self.service.execute(data, parent_data)

        self.assertFalse(result)
        data.set_outputs.assert_called_once()

    def test_schedule_time_passed(self):
        """测试定时时间已过，应该完成调度"""
        data = MagicMock()
        past_time = datetime.datetime.now(pytz.timezone("Asia/Shanghai")) - datetime.timedelta(seconds=10)
        data.outputs.timing_time = past_time
        data.outputs.business_tz = pytz.timezone("Asia/Shanghai")

        parent_data = MagicMock()

        # Mock finish_schedule 方法
        self.service.finish_schedule = MagicMock()

        result = self.service.schedule(data, parent_data, callback_data=None)

        self.assertTrue(result)
        # 验证调度完成
        self.service.finish_schedule.assert_called_once()

    def test_schedule_time_not_yet(self):
        """测试定时时间未到，应该继续等待"""
        data = MagicMock()
        future_time = datetime.datetime.now(pytz.timezone("Asia/Shanghai")) + datetime.timedelta(seconds=60)
        data.outputs.timing_time = future_time
        data.outputs.business_tz = pytz.timezone("Asia/Shanghai")

        parent_data = MagicMock()

        result = self.service.schedule(data, parent_data, callback_data=None)

        self.assertTrue(result)
