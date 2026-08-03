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
from django.conf import settings
from django.test import RequestFactory, TestCase, override_settings
from mock import MagicMock, patch
from pipeline.contrib.reliable_events.constants import EventStatus, EventType
from pipeline.contrib.reliable_events.models import EngineEventInbox

from gcloud.plugin_gateway.models import PluginGatewayRun
from gcloud.taskflow3.apis.django.v4.node_callback import node_callback
from gcloud.utils import crypto

ROOT_PIPELINE_ID = "root-id"
NODE_ID = "node-id"
NODE_VERSION = "node-version"
DISPATCH_RESULT = {"result": True, "message": "success"}
INBOX_OBJECTS = "pipeline.contrib.reliable_events.models.EngineEventInbox.objects"


class NodeCallbackReliableEventsTestCase(TestCase):
    def setUp(self):
        self.callback_data = {"state": "SUCCESS"}
        self.request = RequestFactory().post("/", data=json.dumps(self.callback_data), content_type="application/json")

    @staticmethod
    def _token(root_pipeline_id=ROOT_PIPELINE_ID, engine_ver=2, node_id=NODE_ID, node_version=NODE_VERSION):
        payload = "{}:{}:{}:{}".format(root_pipeline_id, engine_ver, node_id, node_version)
        return Fernet(settings.CALLBACK_KEY).encrypt(payload.encode("utf-8")).decode()

    @staticmethod
    def _create_event(
        idempotency_key,
        root_pipeline_id="",
        node_id=NODE_ID,
        version=NODE_VERSION,
        event_type=EventType.NODE_CALLBACK,
    ):
        return EngineEventInbox.objects.create(
            event_type=event_type,
            source_type="eri_callbackdata",
            source_id="1",
            idempotency_key=idempotency_key,
            root_pipeline_id=root_pipeline_id,
            node_id=node_id,
            version=version,
            status=EventStatus.PENDING,
        )

    def _call(self, token=None):
        return node_callback(self.request, token or self._token())

    # 用例 1：开关全关（默认）时既不富化，也不能给热路径白加一次 Inbox 查询
    @patch(INBOX_OBJECTS, MagicMock())
    @patch("gcloud.taskflow3.apis.django.v4.node_callback.NodeCommandDispatcher")
    def test_switch_off_no_enrichment_and_no_inbox_query(self, mock_dispatcher):
        mock_dispatcher.return_value.dispatch.return_value = dict(DISPATCH_RESULT)

        response = self._call()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"result": True, "message": "success"})
        self.assertFalse(EngineEventInbox.objects.filter.called)
        self.assertFalse(EngineEventInbox.objects.called)

    # 用例 2：SHADOW 打开 + 库里 root_pipeline_id 存空串（当前引擎侧的真实存储形态）→ 命中
    @override_settings(PIPELINE_RELIABLE_EVENTS_SHADOW_ENABLED=True)
    @patch("gcloud.taskflow3.apis.django.v4.node_callback.NodeCommandDispatcher")
    def test_shadow_enabled_hit_with_empty_root_pipeline_id(self, mock_dispatcher):
        mock_dispatcher.return_value.dispatch.return_value = dict(DISPATCH_RESULT)
        event = self._create_event("callback-empty-root", root_pipeline_id="")

        response = self._call()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {"result": True, "message": "success", "accepted": True, "event_id": event.id},
        )

    # 用例 2b：ACTIVE 打开 + 库里存的是真实 root id（引擎将来回填后的形态）→ 同样命中
    @override_settings(PIPELINE_RELIABLE_EVENTS_ACTIVE_ENABLED=True)
    @patch("gcloud.taskflow3.apis.django.v4.node_callback.NodeCommandDispatcher")
    def test_active_enabled_hit_with_real_root_pipeline_id(self, mock_dispatcher):
        mock_dispatcher.return_value.dispatch.return_value = dict(DISPATCH_RESULT)
        event = self._create_event("callback-real-root", root_pipeline_id=ROOT_PIPELINE_ID)

        response = self._call()

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertIs(body["accepted"], True)
        self.assertEqual(body["event_id"], event.id)

    # 用例 3：开关打开但没有匹配行（事件类型/版本/节点都不匹配）→ 什么都不加，也不报错
    @override_settings(PIPELINE_RELIABLE_EVENTS_SHADOW_ENABLED=True)
    @patch("gcloud.taskflow3.apis.django.v4.node_callback.NodeCommandDispatcher")
    def test_enabled_but_no_matching_event_keeps_response_untouched(self, mock_dispatcher):
        mock_dispatcher.return_value.dispatch.return_value = dict(DISPATCH_RESULT)
        self._create_event("other-event-type", event_type=EventType.SCHEDULE_DUE)
        self._create_event("other-version", version="another-version")
        self._create_event("other-node", node_id="another-node")
        self._create_event("other-root", root_pipeline_id="another-root")

        response = self._call()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"result": True, "message": "success"})

    # 用例 4：Inbox 查询抛异常时必须被吞掉，响应原样返回且仍是 200（不能 500）
    @override_settings(PIPELINE_RELIABLE_EVENTS_SHADOW_ENABLED=True)
    @patch(INBOX_OBJECTS, MagicMock(filter=MagicMock(side_effect=Exception("inbox boom"))))
    @patch("gcloud.taskflow3.apis.django.v4.node_callback.NodeCommandDispatcher")
    def test_inbox_query_exception_is_swallowed(self, mock_dispatcher):
        mock_dispatcher.return_value.dispatch.return_value = dict(DISPATCH_RESULT)

        response = self._call()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"result": True, "message": "success"})

    # 用例 5：命中多条时取 order_by("-id") 的最新一条
    @override_settings(PIPELINE_RELIABLE_EVENTS_SHADOW_ENABLED=True)
    @patch("gcloud.taskflow3.apis.django.v4.node_callback.NodeCommandDispatcher")
    def test_multiple_events_pick_latest(self, mock_dispatcher):
        mock_dispatcher.return_value.dispatch.return_value = dict(DISPATCH_RESULT)
        self._create_event("callback-old", root_pipeline_id="")
        latest = self._create_event("callback-latest", root_pipeline_id=ROOT_PIPELINE_ID)

        response = self._call()

        self.assertEqual(json.loads(response.content)["event_id"], latest.id)

    # 用例 6：富化与 dispatch 成败无关——dispatch 失败时既有 result/message 语义不得被改动，
    # 而 accepted/event_id 表达的是「回调已被可靠记录」，此时照旧附加
    @override_settings(PIPELINE_RELIABLE_EVENTS_SHADOW_ENABLED=True)
    @patch("gcloud.taskflow3.apis.django.v4.node_callback.time.sleep", MagicMock())
    @patch("gcloud.taskflow3.apis.django.v4.node_callback.NodeCommandDispatcher")
    def test_failed_callback_keeps_original_result_semantics(self, mock_dispatcher):
        mock_dispatcher.return_value.dispatch.return_value = {"result": False, "message": "node not found"}
        event = self._create_event("callback-failed", root_pipeline_id="")

        response = self._call()

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertIs(body["result"], False)
        self.assertEqual(body["message"], "node not found")
        self.assertEqual(body.get("event_id"), event.id)
        self.assertIs(body.get("accepted"), True)


class PluginGatewayBranchNotEnrichedTestCase(TestCase):
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

    # 用例 7：插件网关路由分支是 open plugin 的路径，不是引擎节点回调，不得被富化
    @override_settings(PIPELINE_RELIABLE_EVENTS_SHADOW_ENABLED=True)
    @patch("gcloud.plugin_gateway.tasks.callback_plugin_gateway_run.apply_async", MagicMock())
    @patch("gcloud.taskflow3.apis.django.v4.node_callback.NodeCommandDispatcher")
    def test_plugin_gateway_branch_not_enriched(self, mock_dispatcher):
        run_id = self.run.open_plugin_run_id
        EngineEventInbox.objects.create(
            event_type=EventType.NODE_CALLBACK,
            idempotency_key="gateway-run-event",
            root_pipeline_id="",
            node_id=run_id,
            version=self.run.plugin_version,
            status=EventStatus.PENDING,
        )
        payload = "{}:2:{}:{}".format(run_id, run_id, self.run.plugin_version)
        token = Fernet(settings.CALLBACK_KEY).encrypt(payload.encode("utf-8")).decode()
        request = RequestFactory().post("/", data=json.dumps(self.callback_data), content_type="application/json")

        response = node_callback(request, token)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"result": True, "message": "success"})
        mock_dispatcher.assert_not_called()
