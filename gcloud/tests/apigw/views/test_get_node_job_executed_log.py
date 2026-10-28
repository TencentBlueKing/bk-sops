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

from django.test import SimpleTestCase
from mock import MagicMock, patch

from gcloud.apigw.views.get_node_job_executed_log import fetch_node_job_executed_log
from gcloud.constants import JobBizScopeType
from gcloud.exceptions import APIError


class FetchNodeJobExecutedLogTest(SimpleTestCase):
    """get_node_job_executed_log 接口核心逻辑的回归测试"""

    def _mock_settings(self, mock_settings):
        mock_settings.SYSTEM_USE_API_ACCOUNT = "system"
        mock_settings.ESB_GET_CLIENT_BY_USER = MagicMock(return_value=MagicMock())

    @patch("gcloud.apigw.views.get_node_job_executed_log.get_job_instance_log")
    @patch("gcloud.apigw.views.get_node_job_executed_log.settings")
    def test_biz_plugin_prefers_inputs_biz_cc_id(self, mock_settings, mock_get_log):
        self._mock_settings(mock_settings)
        mock_get_log.return_value = {"result": True, "data": "log", "matched_target_ip": False}

        execution_data = MagicMock()
        execution_data.inputs = {"biz_cc_id": 5}
        execution_data.outputs = {"job_inst_id": 1}

        result = fetch_node_job_executed_log(
            "node1", "999", component_code="job_fast_execute_script", execution_data=execution_data
        )
        self.assertTrue(result["result"])
        args = mock_get_log.call_args[0]
        # (client, logger, job_instance_id, bk_biz_id, target_ip, job_scope_type)
        self.assertEqual(args[3], 5)
        self.assertEqual(args[5], JobBizScopeType.BIZ.value)

    @patch("gcloud.apigw.views.get_node_job_executed_log.has_biz_set", MagicMock(return_value=True))
    @patch("gcloud.apigw.views.get_node_job_executed_log.get_job_instance_log")
    @patch("gcloud.apigw.views.get_node_job_executed_log.settings")
    def test_all_biz_plugin_uses_all_biz_cc_id(self, mock_settings, mock_get_log):
        self._mock_settings(mock_settings)
        mock_get_log.return_value = {"result": True, "data": "log", "matched_target_ip": False}

        execution_data = MagicMock()
        execution_data.inputs = {"all_biz_cc_id": 99}
        execution_data.outputs = {"job_inst_id": 1}

        result = fetch_node_job_executed_log(
            "node1", "999", component_code="all_biz_execute_job_plan", execution_data=execution_data
        )
        self.assertTrue(result["result"])
        args = mock_get_log.call_args[0]
        self.assertEqual(args[3], 99)
        self.assertEqual(args[5], JobBizScopeType.BIZ_SET.value)

    @patch("gcloud.apigw.views.get_node_job_executed_log.get_job_instance_log")
    @patch("gcloud.apigw.views.get_node_job_executed_log.settings")
    def test_multi_instance_iterates_all_instances(self, mock_settings, mock_get_log):
        self._mock_settings(mock_settings)
        mock_get_log.return_value = {"result": True, "data": "log", "matched_target_ip": False}

        execution_data = MagicMock()
        execution_data.inputs = {}
        execution_data.outputs = {"job_instance_id_list": [1, 2]}

        result = fetch_node_job_executed_log(
            "node1", "999", component_code="job_fast_push_file", execution_data=execution_data
        )
        self.assertTrue(result["result"])
        self.assertEqual(mock_get_log.call_count, 2)

    @patch("gcloud.apigw.views.get_node_job_executed_log.get_job_instance_log")
    @patch("gcloud.apigw.views.get_node_job_executed_log.settings")
    def test_legacy_plugin_falls_back_to_job_inst_id(self, mock_settings, mock_get_log):
        """旧版本插件（legacy、v1.0）只输出 job_inst_id，应兼容为单实例查询"""
        self._mock_settings(mock_settings)
        mock_get_log.return_value = {"result": True, "data": "log", "matched_target_ip": False}

        execution_data = MagicMock()
        execution_data.inputs = {}
        execution_data.outputs = {"job_inst_id": 123}

        result = fetch_node_job_executed_log(
            "node1", "999", component_code="job_fast_push_file", execution_data=execution_data
        )
        self.assertTrue(result["result"])
        mock_get_log.assert_called_once()
        self.assertEqual(mock_get_log.call_args[0][2], 123)

    @patch("gcloud.apigw.views.get_node_job_executed_log.get_job_instance_log")
    @patch("gcloud.apigw.views.get_node_job_executed_log.settings")
    def test_target_ip_not_matched_returns_failure(self, mock_settings, mock_get_log):
        """传了 target_ip 但所有作业实例都没有命中，应报错而不是返回空日志"""
        self._mock_settings(mock_settings)
        mock_get_log.return_value = {"result": True, "data": "", "matched_target_ip": False}

        execution_data = MagicMock()
        execution_data.inputs = {}
        execution_data.outputs = {"job_instance_id_list": [1, 2]}

        result = fetch_node_job_executed_log(
            "node1",
            "999",
            target_ip="1.1.1.1",
            component_code="job_fast_push_file",
            execution_data=execution_data,
        )
        self.assertFalse(result["result"])
        self.assertIn("1.1.1.1", result["message"])

    @patch("gcloud.apigw.views.get_node_job_executed_log.get_job_instance_log")
    @patch("gcloud.apigw.views.get_node_job_executed_log.settings")
    def test_target_ip_matched_returns_success(self, mock_settings, mock_get_log):
        self._mock_settings(mock_settings)
        mock_get_log.return_value = {"result": True, "data": "log", "matched_target_ip": True}

        execution_data = MagicMock()
        execution_data.inputs = {}
        execution_data.outputs = {"job_instance_id_list": [1]}

        result = fetch_node_job_executed_log(
            "node1",
            "999",
            target_ip="1.1.1.1",
            component_code="job_fast_push_file",
            execution_data=execution_data,
        )
        self.assertTrue(result["result"])
        self.assertEqual(result["logs"], "log")

    @patch("gcloud.apigw.views.get_node_job_executed_log.has_biz_set")
    @patch("gcloud.apigw.views.get_node_job_executed_log.get_job_instance_log")
    @patch("gcloud.apigw.views.get_node_job_executed_log.settings")
    def test_has_biz_set_api_error_returns_failure(self, mock_settings, mock_get_log, mock_has_biz_set):
        """CC 查询失败时应转换为可识别的接口错误，而不是直接抛异常"""
        self._mock_settings(mock_settings)
        mock_has_biz_set.side_effect = APIError(system="cc", api="list_business_set", message="cc error")

        execution_data = MagicMock()
        execution_data.inputs = {"all_biz_cc_id": 99}
        execution_data.outputs = {"job_inst_id": 1}

        result = fetch_node_job_executed_log(
            "node1", "999", component_code="all_biz_execute_job_plan", execution_data=execution_data
        )
        self.assertFalse(result["result"])
        self.assertIn("get biz set info failed", result["message"])
        mock_get_log.assert_not_called()

    @patch("gcloud.apigw.views.get_node_job_executed_log.get_job_instance_log")
    @patch("gcloud.apigw.views.get_node_job_executed_log.settings")
    def test_unknown_component_code(self, mock_settings, mock_get_log):
        self._mock_settings(mock_settings)

        execution_data = MagicMock()
        execution_data.inputs = {}
        execution_data.outputs = {"job_inst_id": 1}

        result = fetch_node_job_executed_log(
            "node1", "999", component_code="unknown_code", execution_data=execution_data
        )
        self.assertFalse(result["result"])
        self.assertEqual(result["message"], "component code not found: unknown_code")
        mock_get_log.assert_not_called()
