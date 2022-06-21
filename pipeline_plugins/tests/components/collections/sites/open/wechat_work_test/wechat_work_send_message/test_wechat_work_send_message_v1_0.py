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

from django.test import TestCase
from mock import MagicMock

from pipeline.component_framework.test import (
    Call,
    CallAssertion,
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.wechat_work.wechat_work_send_message.v1_0 import (
    WechatWorkSendMessageComponent,
)  # noqa


class WechatWorkSendMessageComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            WEBHOOK_NOT_CONFIG_CASE,
            EMPTY_CHAT_ID_CASE,
            INVALID_CHAT_ID_CASE,
            WEBHOOK_CALL_ERR_CASE,
            WEBHOOK_CALL_RESP_NOT_OK_CASE,
            SUCCESS_CASE,
        ]

    def component_cls(self):
        return WechatWorkSendMessageComponent


# mock paths
ENVIRONMENT_VAIRABLES_GET = "pipeline_plugins.components.collections.sites.open.wechat_work.wechat_work_send_message.v1_0.EnvironmentVariables.objects.get_var"  # noqa
REQUESTS_POST = (
    "pipeline_plugins.components.collections.sites.open.wechat_work.wechat_work_send_message.v1_0.requests.post"  # noqa
)

# test  cases

WEBHOOK_NOT_CONFIG_CASE = ComponentTestCase(
    name="webhook not config test case",
    inputs={
        "wechat_work_chat_id": "@all",
        "message_content": "haha",
        "wechat_work_mentioned_members": "",
        "msgtype": "text",
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(
        success=False, outputs={"ex_data": "WechatWork send message URL is not config, contact admin please"}
    ),
    schedule_assertion=None,
    patchers=[Patcher(target=ENVIRONMENT_VAIRABLES_GET, return_value=None)],
)

EMPTY_CHAT_ID_CASE = ComponentTestCase(
    name="empty chat id case",
    inputs={
        "wechat_work_chat_id": "",
        "message_content": "haha",
        "wechat_work_mentioned_members": "",
        "msgtype": "text",
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "会话 ID 不能为空"}),
    schedule_assertion=None,
    patchers=[Patcher(target=ENVIRONMENT_VAIRABLES_GET, return_value="test_url")],
)

INVALID_CHAT_ID_CASE = ComponentTestCase(
    name="invalid chat id case",
    inputs={
        "wechat_work_chat_id": "@all",
        "message_content": "haha",
        "wechat_work_mentioned_members": "",
        "msgtype": "text",
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "无效的会话 ID: @all"}),
    schedule_assertion=None,
    patchers=[Patcher(target=ENVIRONMENT_VAIRABLES_GET, return_value="test_url")],
)

WEBHOOK_CALL_ERR_CASE = ComponentTestCase(
    name="web hook call err case",
    inputs={
        "wechat_work_chat_id": "11111111111111111111111111111111\n22222222222222222222222222222222",  # noqa
        "message_content": "haha",
        "wechat_work_mentioned_members": "",
        "msgtype": "text",
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "企业微信发送消息请求失败，详细信息: exc_token"}),
    schedule_assertion=None,
    patchers=[
        Patcher(target=ENVIRONMENT_VAIRABLES_GET, return_value="test_url"),
        Patcher(target=REQUESTS_POST, side_effect=MagicMock(side_effect=Exception("exc_token"))),
    ],
)

WEBHOOK_CALL_RESP_NOT_OK_RESP = MagicMock()
WEBHOOK_CALL_RESP_NOT_OK_RESP.ok = False
WEBHOOK_CALL_RESP_NOT_OK_RESP.status_code = 500
WEBHOOK_CALL_RESP_NOT_OK_RESP.content = "content_token"

WEBHOOK_CALL_RESP_NOT_OK_CASE = ComponentTestCase(
    name="web hook resp not ok case",
    inputs={
        "wechat_work_chat_id": "11111111111111111111111111111111\n22222222222222222222222222222222",  # noqa
        "message_content": "haha",
        "wechat_work_mentioned_members": "",
        "msgtype": "text",
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "企业微信发送消息请求失败，状态码: 500, 响应: content_token"}),
    schedule_assertion=None,
    patchers=[
        Patcher(target=ENVIRONMENT_VAIRABLES_GET, return_value="test_url"),
        Patcher(target=REQUESTS_POST, side_effect=MagicMock(return_value=WEBHOOK_CALL_RESP_NOT_OK_RESP)),
    ],
)

SUCCESS_RESP = MagicMock()
SUCCESS_RESP.ok = True
SUCCESS_RESP.status_code = 200
SUCCESS_RESP.content = "content_token"
SUCCESS_REQUEST_POST = MagicMock(return_value=SUCCESS_RESP)


SUCCESS_CASE = ComponentTestCase(
    name="success case",
    inputs={
        "wechat_work_chat_id": "11111111111111111111111111111111\n22222222222222222222222222222222",  # noqa
        "message_content": "haha",
        "wechat_work_mentioned_members": "m1,m2",
        "msgtype": "text",
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=SUCCESS_REQUEST_POST,
            calls=[
                Call(
                    url="test_url",
                    json={
                        "chatid": "11111111111111111111111111111111|22222222222222222222222222222222",  # noqa
                        "msgtype": "text",
                        "text": {"content": "haha", "mentioned_list": ["m1", "m2"]},
                    },
                    timeout=5,
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=ENVIRONMENT_VAIRABLES_GET, return_value="test_url"),
        Patcher(target=REQUESTS_POST, side_effect=SUCCESS_REQUEST_POST),
    ],
)
