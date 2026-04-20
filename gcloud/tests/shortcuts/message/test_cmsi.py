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

import unittest

from bkapi_client_core.apigateway import Operation
from bkapi_client_core.base import OperationGroup

from gcloud.shortcuts.message_cmsi import send_cmsi_message


class FakeCmsiClient:
    def __init__(self):
        self.api = OperationGroup(name="api", manager=self)
        self.requests = []

    def get_client(self):
        return self

    def handle_request(self, operation, context):
        self.requests.append((operation, context))
        return {"result": True, "data": None, "message": "success"}

    def parse_response(self, operation, response):
        return response


class SendCmsiMessageTestCase(unittest.TestCase):
    def test_send_cmsi_message__email_alias_uses_mail_payload(self):
        client = FakeCmsiClient()
        client.api.register("v1_send_mail", Operation(name="v1_send_mail", method="POST", path="/v1/send_mail/"))

        operation_name, payload, result = send_cmsi_message(
            client=client,
            tenant_id="tenant-a",
            msg_type="email",
            receivers="tester1,tester2",
            title="title",
            content="plain content",
            email_content="email content",
        )

        self.assertEqual(operation_name, "v1_send_mail")
        self.assertEqual(
            payload,
            {
                "receiver__username": "tester1,tester2",
                "title": "title",
                "content": "<pre>email content</pre>",
            },
        )
        self.assertEqual(result["result"], True)
        self.assertEqual(len(client.requests), 1)
        operation, context = client.requests[0]
        self.assertEqual(operation.path, "/v1/send_mail/")
        self.assertEqual(context["headers"], {"X-Bk-Tenant-Id": "tenant-a"})

    def test_send_cmsi_message__unknown_msg_type_registers_dynamic_operation(self):
        client = FakeCmsiClient()

        operation_name, payload, result = send_cmsi_message(
            client=client,
            tenant_id="tenant-b",
            msg_type="qy_weixin",
            receivers=["tester1", "tester2"],
            title="title",
            content="content",
        )

        self.assertEqual(operation_name, "v1_send_qy_weixin")
        self.assertEqual(
            payload,
            {
                "receiver__username": ["tester1", "tester2"],
                "title": "title",
                "content": "content",
            },
        )
        self.assertEqual(result["result"], True)
        self.assertEqual(len(client.requests), 1)
        operation, context = client.requests[0]
        self.assertEqual(operation.path, "/v1/send_qy_weixin/")
        self.assertEqual(context["headers"], {"X-Bk-Tenant-Id": "tenant-b"})

    def test_send_cmsi_message__weixin_preserves_message_data_payload(self):
        client = FakeCmsiClient()
        client.api.register("v1_send_weixin", Operation(name="v1_send_weixin", method="POST", path="/v1/send_weixin/"))

        operation_name, payload, result = send_cmsi_message(
            client=client,
            tenant_id="tenant-c",
            msg_type="weixin",
            receivers=["tester1"],
            title="title",
            content="content",
        )

        self.assertEqual(operation_name, "v1_send_weixin")
        self.assertEqual(
            payload,
            {
                "receiver__username": ["tester1"],
                "message_data": {"heading": "title", "message": "content"},
            },
        )
        self.assertEqual(result["result"], True)
        self.assertEqual(len(client.requests), 1)
        operation, context = client.requests[0]
        self.assertEqual(operation.path, "/v1/send_weixin/")
        self.assertEqual(context["headers"], {"X-Bk-Tenant-Id": "tenant-c"})
