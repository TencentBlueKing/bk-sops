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

from pipeline_plugins.components.collections.gse_kit.job_exec.v1_0 import (
    GsekitJobExecComponent,
    GsekitJobExecService,
    JobStatus,
)


class GsekitJobExecServiceTestCase(TestCase):
    """测试 GsekitJobExecService 类"""

    def setUp(self):
        self.service = GsekitJobExecService()
        # 为 service 设置 logger，避免 AttributeError
        self.service.logger = logging.getLogger("test")
        self.service.finish_schedule = MagicMock()

    def test_inputs_format(self):
        """测试输入格式定义"""
        inputs = self.service.inputs_format()

        self.assertEqual(len(inputs), 9)

        input_keys = [item.key for item in inputs]
        self.assertIn("gsekit_bk_env", input_keys)
        self.assertIn("gsekit_job_object_choices", input_keys)
        self.assertIn("gsekit_job_action_choices", input_keys)
        self.assertIn("gsekit_set", input_keys)
        self.assertIn("gsekit_module", input_keys)
        self.assertIn("gsekit_service_id", input_keys)
        self.assertIn("gsekit_process_name", input_keys)
        self.assertIn("gsekit_process_id", input_keys)
        self.assertIn("gsekit_config_template", input_keys)

    def test_outputs_format(self):
        """测试输出格式定义"""
        outputs = self.service.outputs_format()

        self.assertEqual(len(outputs), 2)

        output_keys = [item.key for item in outputs]
        self.assertIn("gsekit_task_id", output_keys)
        self.assertIn("gsekit_task_page_url", output_keys)

    def test_need_schedule(self):
        """测试需要调度"""
        self.assertTrue(self.service.__need_schedule__)
        self.assertEqual(self.service.interval.interval, 5)

    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.settings")
    def test_execute_configfile_action_success(self, mock_settings, mock_get_client):
        """测试执行配置文件操作成功"""
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.create_job.return_value = {"result": True, "data": {"job_id": "job123"}}
        mock_get_client.return_value = mock_client

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": 2,
            "gsekit_bk_env": "prod",
            "gsekit_job_action_choices": "generate",  # 配置文件相关操作
            "gsekit_set": "set1",
            "gsekit_module": "module1",
            "gsekit_service_id": "service1",
            "gsekit_process_name": "process1",
            "gsekit_process_id": "pid1",
            "gsekit_config_template": ["template1", "template2"],
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {"executor": "admin", "tenant_id": "system"}.get(key)
        parent_data.inputs.biz_cc_id = 2

        result = self.service.execute(data, parent_data)

        self.assertTrue(result)
        data.set_outputs.assert_any_call("gsekit_task_id", "job123")

        # 验证调用了create_job
        mock_client.api.create_job.assert_called_once()
        call_args = mock_client.api.create_job.call_args
        self.assertEqual(call_args[0][0]["job_object"], "configfile")
        self.assertEqual(call_args[0][0]["job_action"], "generate")

    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.settings")
    def test_execute_process_action_success(self, mock_settings, mock_get_client):
        """测试执行进程操作成功"""
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.create_job.return_value = {"result": True, "data": {"job_id": "job456"}}
        mock_get_client.return_value = mock_client

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": 2,
            "gsekit_bk_env": "prod",
            "gsekit_job_action_choices": "restart",  # 进程相关操作
            "gsekit_set": "set1",
            "gsekit_module": "module1",
            "gsekit_service_id": "service1",
            "gsekit_process_name": "process1",
            "gsekit_process_id": "pid1",
            "gsekit_config_template": [],
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {"executor": "admin", "tenant_id": "system"}.get(key)
        parent_data.inputs.biz_cc_id = 2

        result = self.service.execute(data, parent_data)

        self.assertTrue(result)
        data.set_outputs.assert_any_call("gsekit_task_id", "job456")

        # 验证调用了create_job，并且job_object是process
        call_args = mock_client.api.create_job.call_args
        self.assertEqual(call_args[0][0]["job_object"], "process")
        self.assertEqual(call_args[0][0]["job_action"], "restart")

    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.settings")
    def test_execute_create_job_failed(self, mock_settings, mock_get_client):
        """测试创建任务失败"""
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.create_job.return_value = {"result": False, "message": "创建任务失败"}
        mock_get_client.return_value = mock_client

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": 2,
            "gsekit_bk_env": "prod",
            "gsekit_job_action_choices": "restart",
            "gsekit_set": "set1",
            "gsekit_module": "module1",
            "gsekit_service_id": "service1",
            "gsekit_process_name": "process1",
            "gsekit_process_id": "pid1",
            "gsekit_config_template": [],
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {"executor": "admin", "tenant_id": "system"}.get(key)
        parent_data.inputs.biz_cc_id = 2

        result = self.service.execute(data, parent_data)

        self.assertFalse(result)
        # 验证set_outputs被调用了，并且包含错误信息
        self.assertEqual(data.set_outputs.call_count, 1)
        call_args = data.set_outputs.call_args
        self.assertEqual(call_args[0][0], "ex_data")
        self.assertIn("调用gsekit接口gsekit.create_job返回失败", call_args[0][1])

    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.settings")
    def test_schedule_job_succeeded(self, mock_settings, mock_get_client):
        """测试轮询任务状态为成功"""
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.job_status.return_value = {
            "result": True,
            "data": {"job_info": {"status": JobStatus.SUCCEEDED}},
        }
        mock_get_client.return_value = mock_client

        data = MagicMock()
        data.outputs.gsekit_task_id = "job123"
        data.get_one_of_inputs.return_value = 2

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {"executor": "admin", "tenant_id": "system"}.get(key)
        parent_data.inputs.biz_cc_id = 2

        result = self.service.schedule(data, parent_data)

        self.assertTrue(result)
        # 验证调度完成
        self.service.finish_schedule.assert_called_once()

    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.settings")
    def test_schedule_job_running(self, mock_settings, mock_get_client):
        """测试轮询任务状态为运行中"""
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.job_status.return_value = {"result": True, "data": {"job_info": {"status": JobStatus.RUNNING}}}
        mock_get_client.return_value = mock_client

        data = MagicMock()
        data.outputs.gsekit_task_id = "job123"
        data.get_one_of_inputs.return_value = 2

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {"executor": "admin", "tenant_id": "system"}.get(key)
        parent_data.inputs.biz_cc_id = 2

        result = self.service.schedule(data, parent_data)

        self.assertTrue(result)
        # 验证调度未完成，继续等待
        self.service.finish_schedule.assert_not_called()

    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.settings")
    def test_schedule_job_pending(self, mock_settings, mock_get_client):
        """测试轮询任务状态为等待中"""
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.job_status.return_value = {"result": True, "data": {"job_info": {"status": JobStatus.PENDING}}}
        mock_get_client.return_value = mock_client

        data = MagicMock()
        data.outputs.gsekit_task_id = "job123"
        data.get_one_of_inputs.return_value = 2

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {"executor": "admin", "tenant_id": "system"}.get(key)
        parent_data.inputs.biz_cc_id = 2

        result = self.service.schedule(data, parent_data)

        self.assertTrue(result)
        # 验证调度未完成，继续等待
        self.service.finish_schedule.assert_not_called()

    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.settings")
    def test_schedule_job_failed(self, mock_settings, mock_get_client):
        """测试轮询任务状态为失败"""
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.job_status.return_value = {"result": True, "data": {"job_info": {"status": JobStatus.FAILED}}}
        mock_get_client.return_value = mock_client

        data = MagicMock()
        data.outputs.gsekit_task_id = "job123"
        data.get_one_of_inputs.return_value = 2

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {"executor": "admin", "tenant_id": "system"}.get(key)
        parent_data.inputs.biz_cc_id = 2

        result = self.service.schedule(data, parent_data)

        self.assertFalse(result)
        # 验证设置了错误信息
        data.set_outputs.assert_called_once()

    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.settings")
    def test_schedule_job_status_api_failed(self, mock_settings, mock_get_client):
        """测试查询任务状态API调用失败"""
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.job_status.return_value = {"result": False, "message": "查询任务状态失败"}
        mock_get_client.return_value = mock_client

        data = MagicMock()
        data.outputs.gsekit_task_id = "job123"
        data.get_one_of_inputs.return_value = 2

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {"executor": "admin", "tenant_id": "system"}.get(key)
        parent_data.inputs.biz_cc_id = 2

        result = self.service.schedule(data, parent_data)

        self.assertFalse(result)
        # 验证设置了错误信息
        self.assertEqual(data.set_outputs.call_count, 1)
        call_args = data.set_outputs.call_args
        self.assertEqual(call_args[0][0], "ex_data")
        self.assertIn("调用gsekit接口gsekit.check_job_task_status返回失败", call_args[0][1])

    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.settings")
    def test_schedule_job_unexpected_status(self, mock_settings, mock_get_client):
        """测试轮询任务状态为未知状态"""
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.job_status.return_value = {
            "result": True,
            "data": {"job_info": {"status": "unexpected_status"}},
        }
        mock_get_client.return_value = mock_client

        data = MagicMock()
        data.outputs.gsekit_task_id = "job123"
        data.get_one_of_inputs.return_value = 2

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {"executor": "admin", "tenant_id": "system"}.get(key)
        parent_data.inputs.biz_cc_id = 2

        result = self.service.schedule(data, parent_data)

        self.assertFalse(result)
        # 验证设置了错误信息
        data.set_outputs.assert_called_once()


class GsekitJobExecComponentTestCase(TestCase):
    """测试 GsekitJobExecComponent 类"""

    def test_component_attributes(self):
        """测试组件属性"""
        # Component类不需要实例化，直接测试类属性
        self.assertEqual(GsekitJobExecComponent.name, "执行命令")
        self.assertEqual(GsekitJobExecComponent.code, "gsekit_job_exec")
        self.assertEqual(GsekitJobExecComponent.bound_service, GsekitJobExecService)
        self.assertIsNotNone(GsekitJobExecComponent.form)
        self.assertEqual(GsekitJobExecComponent.version, "1.0")  # 实际版本是1.0不是v1.0


class GsekitJobExecServiceInputsOutputsTestCase(TestCase):
    """测试 GsekitJobExecService 的输入输出格式"""

    def setUp(self):
        self.service = GsekitJobExecService()
        self.service.logger = MagicMock()

    def test_inputs_format(self):
        """测试输入格式定义"""
        inputs = self.service.inputs_format()

        # 验证有输入项
        self.assertIsNotNone(inputs)
        self.assertTrue(len(inputs) > 0)

        # 验证关键输入项存在
        input_keys = [item.key for item in inputs]
        expected_keys = [
            "gsekit_bk_env",
            "gsekit_job_action_choices",
            "gsekit_set",
            "gsekit_module",
            "gsekit_service_id",
            "gsekit_process_name",
            "gsekit_process_id",
            "gsekit_config_template",
        ]

        for key in expected_keys:
            self.assertIn(key, input_keys)

        # 验证输入项格式正确
        for item in inputs:
            self.assertTrue(hasattr(item, "name"))
            self.assertTrue(hasattr(item, "key"))
            self.assertTrue(hasattr(item, "type"))

    def test_outputs_format(self):
        """测试输出格式定义"""
        outputs = self.service.outputs_format()

        # 验证有输出项
        self.assertIsNotNone(outputs)
        self.assertEqual(len(outputs), 2)

        # 验证关键输出项存在
        output_keys = [item.key for item in outputs]
        self.assertIn("gsekit_task_id", output_keys)
        self.assertIn("gsekit_task_page_url", output_keys)

        # 验证输出项格式正确
        for item in outputs:
            self.assertTrue(hasattr(item, "name"))
            self.assertTrue(hasattr(item, "key"))
            self.assertTrue(hasattr(item, "type"))
            self.assertEqual(item.type, "string")

    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.settings")
    def test_execute_with_configfile_generate_action(self, mock_settings, mock_get_client):
        """测试使用配置文件生成操作执行"""
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.create_job.return_value = {"result": True, "data": {"job_id": "job123"}}
        mock_get_client.return_value = mock_client

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": 2,
            "gsekit_bk_env": "prod",
            "gsekit_job_action_choices": "generate",
            "gsekit_set": "set1",
            "gsekit_module": "module1",
            "gsekit_service_id": "service1",
            "gsekit_process_name": "process1",
            "gsekit_process_id": "pid1",
            "gsekit_config_template": ["template1", "template2"],
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {"executor": "admin", "tenant_id": "system"}.get(key)
        parent_data.inputs.biz_cc_id = 2

        result = self.service.execute(data, parent_data)

        self.assertTrue(result)
        # 验证create_job被正确调用，包含config_template_ids
        call_args = mock_client.api.create_job.call_args
        self.assertEqual(call_args[0][0]["job_object"], "configfile")
        self.assertEqual(call_args[0][0]["job_action"], "generate")
        self.assertIn("config_template_ids", call_args[0][0]["extra_data"])

    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.settings")
    def test_execute_with_process_action(self, mock_settings, mock_get_client):
        """测试使用进程操作执行"""
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.create_job.return_value = {"result": True, "data": {"job_id": "job456"}}
        mock_get_client.return_value = mock_client

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": 2,
            "gsekit_bk_env": "prod",
            "gsekit_job_action_choices": "start",  # 进程操作
            "gsekit_set": "set1",
            "gsekit_module": "module1",
            "gsekit_service_id": "service1",
            "gsekit_process_name": "process1",
            "gsekit_process_id": "pid1",
            "gsekit_config_template": [],
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {"executor": "admin", "tenant_id": "system"}.get(key)
        parent_data.inputs.biz_cc_id = 2

        result = self.service.execute(data, parent_data)

        self.assertTrue(result)
        # 验证create_job被正确调用，job_object是process
        call_args = mock_client.api.create_job.call_args
        self.assertEqual(call_args[0][0]["job_object"], "process")
        self.assertEqual(call_args[0][0]["job_action"], "start")

    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.settings")
    def test_schedule_job_status_failed(self, mock_settings, mock_get_client):
        """测试轮询任务状态为失败"""
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.job_status.return_value = {
            "result": True,
            "data": {"status": "failed", "job_info": {"status": "failed"}, "log_url": "http://example.com/log"},
        }
        mock_get_client.return_value = mock_client

        data = MagicMock()
        data.outputs.gsekit_task_id = "job123"
        data.get_one_of_inputs.return_value = 2

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {"executor": "admin", "tenant_id": "system"}.get(key)
        parent_data.inputs.biz_cc_id = 2

        result = self.service.schedule(data, parent_data)

        self.assertFalse(result)
        # 验证设置了错误信息
        data.set_outputs.assert_any_call("ex_data", "Gsekit任务执行异常, 任务状态为 failed")


class GsekitJobExecServiceEdgeCasesTestCase(TestCase):
    """测试 GsekitJobExecService 的边缘情况"""

    def setUp(self):
        self.service = GsekitJobExecService()
        self.service.logger = MagicMock()

    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.settings")
    def test_execute_with_release_action(self, mock_settings, mock_get_client):
        """测试使用release操作执行"""
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.create_job.return_value = {"result": True, "data": {"job_id": "job789"}}
        mock_get_client.return_value = mock_client

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": 2,
            "gsekit_bk_env": "prod",
            "gsekit_job_action_choices": "release",
            "gsekit_set": "set1",
            "gsekit_module": "module1",
            "gsekit_service_id": "service1",
            "gsekit_process_name": "process1",
            "gsekit_process_id": "pid1",
            "gsekit_config_template": ["template1"],
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {"executor": "admin", "tenant_id": "system"}.get(key)
        parent_data.inputs.biz_cc_id = 2

        result = self.service.execute(data, parent_data)

        self.assertTrue(result)
        call_args = mock_client.api.create_job.call_args
        self.assertEqual(call_args[0][0]["job_object"], "configfile")

    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.gse_kit.job_exec.v1_0.settings")
    def test_execute_with_diff_action(self, mock_settings, mock_get_client):
        """测试使用diff操作执行"""
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.create_job.return_value = {"result": True, "data": {"job_id": "job999"}}
        mock_get_client.return_value = mock_client

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": 2,
            "gsekit_bk_env": "prod",
            "gsekit_job_action_choices": "diff",
            "gsekit_set": "set1",
            "gsekit_module": "module1",
            "gsekit_service_id": "service1",
            "gsekit_process_name": "process1",
            "gsekit_process_id": "pid1",
            "gsekit_config_template": ["template1"],
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {"executor": "admin", "tenant_id": "system"}.get(key)
        parent_data.inputs.biz_cc_id = 2

        result = self.service.execute(data, parent_data)

        self.assertTrue(result)
        call_args = mock_client.api.create_job.call_args
        self.assertEqual(call_args[0][0]["job_object"], "configfile")
