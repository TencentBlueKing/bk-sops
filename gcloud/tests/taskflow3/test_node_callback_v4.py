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

from cryptography.fernet import Fernet
from django.test import RequestFactory, SimpleTestCase
from mock import MagicMock, patch

from gcloud.taskflow3.apis.django.v4.node_callback import node_callback


class NodeCallbackV4LogTestCase(SimpleTestCase):
    def test_callback_log_does_not_expose_token_or_payload_values(self):
        callback_key = Fernet.generate_key()
        token = Fernet(callback_key).encrypt(b"2:node_id:node_version").decode()
        secret_value = "do-not-write-this-value-to-log"
        request = RequestFactory().post(
            "/taskflow/api/v4/nodes/callback/{}/".format(token),
            data=json.dumps({"job_instance_id": 1, "status": 3, "secret": secret_value}),
            content_type="application/json",
        )
        dispatcher = MagicMock()
        dispatcher.dispatch.return_value = {"result": True, "message": "success", "code": 0}
        trace_context = MagicMock()

        with self.settings(CALLBACK_KEY=callback_key):
            with patch("gcloud.taskflow3.apis.django.v4.node_callback.NodeCommandDispatcher", return_value=dispatcher):
                with patch("gcloud.taskflow3.apis.django.v4.node_callback.start_trace", return_value=trace_context):
                    with self.assertLogs("root", level="INFO") as captured:
                        response = node_callback(request, token)

        logs = "\n".join(captured.output)
        self.assertEqual(response.status_code, 200)
        self.assertIn("outcome=received", logs)
        self.assertIn("node_id=node_id", logs)
        self.assertIn("node_version=node_version", logs)
        self.assertIn("payload_keys=['job_instance_id', 'secret', 'status']", logs)
        self.assertNotIn(token, logs)
        self.assertNotIn(secret_value, logs)
