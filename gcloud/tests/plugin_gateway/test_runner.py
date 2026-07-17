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

from unittest.mock import patch

from django.test import TestCase

from gcloud.plugin_gateway.models import PluginGatewayRun
from gcloud.plugin_gateway.services.runner import PluginGatewayRunner


class _RuntimeService:
    def __init__(self):
        self._runtime_attrs = {}

    def setup_runtime_attrs(self, **kwargs):
        self._runtime_attrs.update(kwargs)

    def __getattr__(self, name):
        try:
            return self._runtime_attrs[name]
        except KeyError:
            raise AttributeError()


class _SyncService(_RuntimeService):
    interval = None

    def execute(self, data, parent_data):
        data.set_outputs("echo_operator", parent_data.get_one_of_inputs("operator"))
        data.set_outputs("done", True)
        return True

    def need_schedule(self):
        return False


class _SyncComponent:
    code = "demo_sync"
    version = "legacy"
    bound_service = _SyncService


class _RuntimeAwareService(_RuntimeService):
    interval = None

    def execute(self, data, parent_data):
        self.logger.info("plugin gateway runtime logger is ready")
        data.set_outputs("runtime_id", self.id)
        data.set_outputs("runtime_root_pipeline_id", self.root_pipeline_id)
        return True

    def need_schedule(self):
        return False


class _RuntimeAwareComponent:
    code = "runtime_aware"
    version = "legacy"
    bound_service = _RuntimeAwareService


class _ThirdPartyShellService(_RuntimeService):
    interval = None

    def execute(self, data, parent_data):
        data.set_outputs("plugin_code", data.get_one_of_inputs("plugin_code"))
        data.set_outputs("plugin_version", data.get_one_of_inputs("plugin_version"))
        data.set_outputs("source_key", parent_data.get_one_of_inputs("source_key"))
        data.set_outputs("caller_app_code", parent_data.get_one_of_inputs("caller_app_code"))
        data.set_outputs("open_plugin_run_id", parent_data.get_one_of_inputs("open_plugin_run_id"))
        data.set_outputs("project_id", parent_data.get_one_of_inputs("project_id"))
        return True

    def need_schedule(self):
        return False


class _ThirdPartyShellComponent:
    code = "remote_plugin"
    version = "1.0.0"
    bound_service = _ThirdPartyShellService


class _PollService(_RuntimeService):
    interval = object()

    def execute(self, data, parent_data):
        setattr(self, "__need_schedule__", True)
        return True

    def need_schedule(self):
        return getattr(self, "__need_schedule__", False)

    def schedule(self, data, parent_data, callback_data=None):
        self.logger.info("plugin gateway schedule runtime logger is ready")
        data.set_outputs("polled", True)
        data.set_outputs("trace_id_from_runtime", data.get_one_of_outputs("trace_id"))
        setattr(self, "__schedule_finish__", True)
        return True

    def is_schedule_finished(self):
        return getattr(self, "__schedule_finish__", False)


class _PollComponent:
    code = "demo_poll"
    version = "legacy"
    bound_service = _PollService


class PluginGatewayRunnerExecuteTestCase(TestCase):
    def _run(self, **overrides):
        defaults = {
            "source_key": "bkflow",
            "plugin_id": "builtin__demo_sync",
            "plugin_version": "legacy",
            "client_request_id": "r1",
            "open_plugin_run_id": "a" * 32,
            "callback_url": "https://bkflow.example.com/callback",
            "callback_token": "token",
            "run_status": PluginGatewayRun.Status.CREATED,
            "caller_app_code": "bkflow-app",
            "trigger_payload": {"inputs": {"k": "v"}},
        }
        defaults.update(overrides)
        return PluginGatewayRun.objects.create(**defaults)

    @patch("gcloud.plugin_gateway.services.runner.ComponentLibrary")
    def test_sync_success(self, mock_lib):
        mock_lib.get_component_class.return_value = _SyncComponent

        result = PluginGatewayRunner.run_execute(
            self._run(),
            {"operator": "zhangsan", "project_id": 10, "bk_biz_id": 2},
        )

        self.assertTrue(result["ok"])
        self.assertFalse(result["need_schedule"])
        self.assertEqual(result["mode"], "sync")
        self.assertFalse(result["finished"])
        self.assertEqual(result["outputs"]["echo_operator"], "zhangsan")
        self.assertTrue(result["outputs"]["done"])

    @patch("gcloud.plugin_gateway.services.runner.ComponentLibrary")
    def test_execute_injects_service_runtime_attrs(self, mock_lib):
        mock_lib.get_component_class.return_value = _RuntimeAwareComponent

        result = PluginGatewayRunner.run_execute(
            self._run(plugin_id="builtin__runtime_aware"),
            {"operator": "zhangsan", "project_id": 10, "bk_biz_id": 2},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["outputs"]["runtime_id"], "a" * 32)
        self.assertEqual(result["outputs"]["runtime_root_pipeline_id"], "a" * 32)

    @patch("gcloud.plugin_gateway.services.runner.ComponentLibrary")
    def test_execute_exception_maps_failed(self, mock_lib):
        class _Boom(_SyncService):
            def execute(self, data, parent_data):
                raise RuntimeError("boom")

        class _BoomComponent(_SyncComponent):
            bound_service = _Boom

        mock_lib.get_component_class.return_value = _BoomComponent

        result = PluginGatewayRunner.run_execute(
            self._run(),
            {"operator": "x", "project_id": 10, "bk_biz_id": 2},
        )

        self.assertFalse(result["ok"])
        self.assertIn("boom", result["error_message"])

    @patch("gcloud.plugin_gateway.services.runner.ComponentLibrary")
    def test_third_party_uses_remote_plugin_shell_and_context(self, mock_lib):
        mock_lib.get_component_class.return_value = _ThirdPartyShellComponent

        result = PluginGatewayRunner.run_execute(
            self._run(plugin_id="bk_plugin_demo", plugin_version="1.1.0"),
            {"operator": "wangwu", "project_id": 10, "bk_biz_id": 2},
        )

        mock_lib.get_component_class.assert_called_once_with("remote_plugin", "1.0.0")
        self.assertTrue(result["ok"])
        self.assertEqual(result["outputs"]["plugin_code"], "bk_plugin_demo")
        self.assertEqual(result["outputs"]["plugin_version"], "1.1.0")
        self.assertEqual(result["outputs"]["source_key"], "bkflow")
        self.assertEqual(result["outputs"]["caller_app_code"], "bkflow-app")
        self.assertEqual(result["outputs"]["open_plugin_run_id"], "a" * 32)
        self.assertEqual(result["outputs"]["project_id"], 10)


class PluginGatewayRunnerScheduleTestCase(TestCase):
    @patch("gcloud.plugin_gateway.services.runner.ComponentLibrary")
    def test_schedule_finishes_with_runtime_outputs(self, mock_lib):
        mock_lib.get_component_class.return_value = _PollComponent
        run = PluginGatewayRun.objects.create(
            source_key="bkflow",
            plugin_id="builtin__demo_poll",
            plugin_version="legacy",
            client_request_id="rp",
            open_plugin_run_id="b" * 32,
            callback_url="https://bkflow.example.com/callback",
            callback_token="token",
            run_status=PluginGatewayRun.Status.RUNNING,
            caller_app_code="bkflow-app",
            trigger_payload={"inputs": {}},
            runtime_outputs={"trace_id": "trace-001"},
        )

        result = PluginGatewayRunner.run_schedule(
            run,
            {"operator": "x", "project_id": 10, "bk_biz_id": 2},
        )

        self.assertTrue(result["ok"])
        self.assertTrue(result["finished"])
        self.assertFalse(result["need_schedule"])
        self.assertEqual(result["mode"], "poll")
        self.assertTrue(result["outputs"]["polled"])
        self.assertEqual(result["outputs"]["trace_id_from_runtime"], "trace-001")
