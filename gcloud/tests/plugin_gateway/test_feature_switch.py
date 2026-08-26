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

import json
from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

from gcloud.plugin_gateway.exceptions import PluginGatewayDisabledError
from gcloud.plugin_gateway.models import PluginGatewayRun, PluginGatewaySourceConfig
from gcloud.plugin_gateway.services.execution import PluginGatewayExecutionService
from gcloud.plugin_gateway.tasks import (
    callback_plugin_gateway_run,
    dispatch_plugin_gateway_run,
    poll_plugin_gateway_run,
    sweep_expired_plugin_gateway_runs,
)
from gcloud.taskflow3.apis.django.v4.node_callback import node_callback
from gcloud.utils import crypto
from pipeline_plugins.components.utils.sites.open.utils import get_node_callback_url


@override_settings(PLUGIN_GATEWAY_ENABLE=False)
class PluginGatewayDisabledTestCase(TestCase):
    """开关关闭时不允许向 open_plugin_* 队列投递任何消息。"""

    def setUp(self):
        PluginGatewaySourceConfig.objects.create(
            source_key="bkflow",
            display_name="BKFlow",
            default_project_id=2001,
            callback_domain_allow_list=["bkflow.example.com"],
            is_enabled=True,
        )
        self.payload = {
            "source_key": "bkflow",
            "plugin_id": "plugin_job_execute",
            "plugin_version": "1.2.0",
            "client_request_id": "task_1_node_1_attempt_1",
            "callback_url": "https://bkflow.example.com/callback",
            "callback_token": "token-001",
            "inputs": {"biz_id": 2},
        }

    def _create_run(self, **overrides):
        defaults = {
            "source_key": "bkflow",
            "plugin_id": "plugin_job_execute",
            "plugin_version": "1.2.0",
            "client_request_id": "task_1_node_1_attempt_1",
            "open_plugin_run_id": "4f3c2b1a0d9e8f7766554433221100aa",
            "callback_url": "https://bkflow.example.com/callback",
            "callback_token": crypto.encrypt("token-001"),
            "run_status": PluginGatewayRun.Status.RUNNING,
            "caller_app_code": "bkflow-app",
            "trigger_payload": {"project_id": 2001},
        }
        defaults.update(overrides)
        return PluginGatewayRun.objects.create(**defaults)

    @patch("gcloud.plugin_gateway.services.execution.dispatch_plugin_gateway_run.apply_async")
    def test_create_run_rejected_without_enqueue(self, mock_dispatch_apply_async):
        with self.assertRaises(PluginGatewayDisabledError):
            PluginGatewayExecutionService.create_run("bkflow-app", self.payload)

        mock_dispatch_apply_async.assert_not_called()
        self.assertFalse(PluginGatewayRun.objects.exists())

    @patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
    def test_sweep_task_does_nothing(self, mock_callback_run):
        self._create_run(execution_expire_at=timezone.now() - timedelta(seconds=1))

        sweep_expired_plugin_gateway_runs()

        mock_callback_run.assert_not_called()

    @patch("gcloud.plugin_gateway.tasks.poll_plugin_gateway_run.apply_async")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayRunner.run_execute")
    def test_dispatch_task_does_not_enqueue_polling(self, mock_run_execute, mock_poll_apply_async):
        run = self._create_run(run_status=PluginGatewayRun.Status.CREATED)

        dispatch_plugin_gateway_run(open_plugin_run_id=run.open_plugin_run_id)

        mock_run_execute.assert_not_called()
        mock_poll_apply_async.assert_not_called()
        run.refresh_from_db()
        self.assertEqual(run.run_status, PluginGatewayRun.Status.CREATED)

    @patch("gcloud.plugin_gateway.tasks.poll_plugin_gateway_run.apply_async")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayRunner.run_schedule")
    def test_polling_task_does_not_enqueue_next_round(self, mock_run_schedule, mock_poll_apply_async):
        run = self._create_run()

        poll_plugin_gateway_run(open_plugin_run_id=run.open_plugin_run_id)

        mock_run_schedule.assert_not_called()
        mock_poll_apply_async.assert_not_called()

    @patch("gcloud.plugin_gateway.tasks.callback_plugin_gateway_run.apply_async")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayRunner.run_schedule")
    def test_callback_task_does_not_enqueue_retry(self, mock_run_schedule, mock_callback_apply_async):
        run = self._create_run()

        callback_plugin_gateway_run(open_plugin_run_id=run.open_plugin_run_id, callback_data={"result": "ok"})

        mock_run_schedule.assert_not_called()
        mock_callback_apply_async.assert_not_called()

    @patch("gcloud.taskflow3.apis.django.v4.node_callback.NodeCommandDispatcher")
    @patch("gcloud.plugin_gateway.tasks.callback_plugin_gateway_run.apply_async")
    def test_node_callback_does_not_route_to_gateway_queue(
        self, mock_callback_apply_async, mock_node_command_dispatcher
    ):
        run = self._create_run(run_status=PluginGatewayRun.Status.WAITING_CALLBACK)
        mock_node_command_dispatcher.return_value.dispatch.return_value = {"result": True, "message": "success"}
        callback_url = get_node_callback_url(
            root_pipeline_id=run.open_plugin_run_id,
            node_id=run.open_plugin_run_id,
            node_version=run.plugin_version,
        )
        request = RequestFactory().post("/", data=json.dumps({"state": "SUCCESS"}), content_type="application/json")

        response = node_callback(request, callback_url.rstrip("/").rsplit("/", 1)[-1])

        self.assertEqual(response.status_code, 200)
        mock_callback_apply_async.assert_not_called()


class PluginGatewayBeatScheduleTestCase(TestCase):
    def test_sweep_beat_schedule_registration_follows_switch(self):
        """关闭时不注册周期任务，避免 beat 持续向无消费者的队列投递消息。"""

        registered = "sweep_expired_plugin_gateway_runs" in settings.CELERYBEAT_SCHEDULE

        self.assertEqual(registered, settings.PLUGIN_GATEWAY_ENABLE)
