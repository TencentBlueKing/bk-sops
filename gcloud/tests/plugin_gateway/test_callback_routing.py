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
from unittest.mock import patch

from cryptography.fernet import Fernet
from django.conf import settings
from django.test import RequestFactory, TestCase, override_settings

from gcloud.plugin_gateway.models import PluginGatewayRun
from gcloud.taskflow3.apis.django.v4.node_callback import node_callback
from gcloud.utils import crypto
from pipeline_plugins.components.utils.sites.open.utils import get_node_callback_url


@override_settings(PLUGIN_GATEWAY_ENABLE=True)
class PluginGatewayCallbackRoutingTestCase(TestCase):
    def setUp(self):
        self.run = PluginGatewayRun.objects.create(
            source_key="bkflow",
            plugin_id="danny-test-plugi",
            plugin_version="1.0.2",
            client_request_id="task-1-node-1",
            open_plugin_run_id="36c446392af844909adc447d4a2717b5",
            callback_url="https://bkflow.example.com/callback",
            callback_token=crypto.encrypt("callback-token"),
            run_status=PluginGatewayRun.Status.WAITING_CALLBACK,
            caller_app_code="bkflow",
            trigger_payload={},
        )
        self.callback_data = {"state": "SUCCESS"}

    def _callback_token(self):
        callback_url = get_node_callback_url(
            root_pipeline_id=self.run.open_plugin_run_id,
            node_id=self.run.open_plugin_run_id,
            node_version=self.run.plugin_version,
        )
        return callback_url.rstrip("/").rsplit("/", 1)[-1]

    @staticmethod
    def _engine_callback_token():
        return Fernet(settings.CALLBACK_KEY).encrypt(b"root-id:2:node-id:node-version").decode()

    @patch("gcloud.taskflow3.apis.django.v4.node_callback.NodeCommandDispatcher")
    @patch("gcloud.plugin_gateway.tasks.callback_plugin_gateway_run.apply_async")
    def test_plugin_gateway_run_callback_routes_to_gateway_task(
        self, mock_callback_apply_async, mock_node_command_dispatcher
    ):
        mock_node_command_dispatcher.return_value.dispatch.return_value = {
            "result": True,
            "message": "success",
        }
        request = RequestFactory().post(
            "/",
            data=json.dumps(self.callback_data),
            content_type="application/json",
        )

        response = node_callback(request, self._callback_token())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"result": True, "message": "success"})
        mock_callback_apply_async.assert_called_once_with(
            kwargs={
                "open_plugin_run_id": self.run.open_plugin_run_id,
                "callback_data": self.callback_data,
            },
            queue="open_plugin_callback",
        )
        mock_node_command_dispatcher.assert_not_called()

    @patch("gcloud.taskflow3.apis.django.v4.node_callback.NodeCommandDispatcher")
    @patch("gcloud.plugin_gateway.tasks.callback_plugin_gateway_run.apply_async")
    def test_normal_node_callback_still_routes_to_engine(self, mock_callback_apply_async, mock_node_command_dispatcher):
        mock_node_command_dispatcher.return_value.dispatch.return_value = {
            "result": True,
            "message": "success",
        }
        request = RequestFactory().post(
            "/",
            data=json.dumps(self.callback_data),
            content_type="application/json",
        )

        response = node_callback(request, self._engine_callback_token())

        self.assertEqual(response.status_code, 200)
        mock_node_command_dispatcher.assert_called_once_with(
            engine_ver=2,
            node_id="node-id",
            taskflow_id=None,
        )
        mock_node_command_dispatcher.return_value.dispatch.assert_called_once_with(
            command="callback",
            operator="",
            version="node-version",
            data=self.callback_data,
        )
        mock_callback_apply_async.assert_not_called()
