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

from pipeline_plugins.components.collections.sites.open.bk.notify.legacy import NotifyComponent


class BkNotifyLegacyComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        return NotifyComponent

    def cases(self):
        return [
            GET_NOTIFY_RECEIVERS_FAIL_CASE,
            SEND_MSG_FAIL_CASE,
            SEND_WEIXIN_SUCCESS_CASE,
            SEND_EMAIL_SUCCESS_CASE,
            SEND_SMS_SUCCESS_CASE,
            SEND_MULTIPLE_NOTIFY_SUCCESS_CASE,
            SEND_WITH_RECEIVER_INFO_CASE,
            SEND_WITHOUT_RECEIVER_INFO_CASE,
        ]


class MockClient(object):
    def __init__(self, cc_search_business_return=None, cmsi_send_msg_return=None):
        self.api = MagicMock()
        self.api.search_business = MagicMock(return_value=cc_search_business_return)
        self.api.v1_send_weixin = MagicMock(return_value=cmsi_send_msg_return)
        self.api.v1_send_mail = MagicMock(return_value=cmsi_send_msg_return)
        self.api.v1_send_sms = MagicMock(return_value=cmsi_send_msg_return)


GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.bk.notify.legacy.get_client_by_username"
GET_NOTIFY_RECEIVERS = "pipeline_plugins.components.collections.sites.open.bk.notify.legacy.get_notify_receivers"

COMMON_PARENT = {"tenant_id": "system", "executor": "tester", "biz_cc_id": 2}

CC_SEARCH_BUSINESS_FAIL_RETURN = {"result": False, "message": "search business fail"}

CC_SEARCH_BUSINESS_SUCCESS_RETURN = {
    "result": True,
    "data": {
        "count": 1,
        "info": [
            {
                "bk_biz_maintainer": "m1,m2",
                "bk_biz_productor": "p1,p2",
                "bk_biz_developer": "d1,d2",
                "bk_biz_tester": "t1,t2",
            }
        ],
    },
}

CMSI_SEND_MSG_FAIL_RETURN = {"result": False, "message": "send msg fail"}

CMSI_SEND_MSG_SUCCESS_RETURN = {"result": True, "message": "success", "code": 0}

GET_NOTIFY_RECEIVERS_SUCCESS = {"result": True, "message": "success", "data": "tester,a,b,m1,m2,p1,p2"}

GET_NOTIFY_RECEIVERS_FAIL = {"result": False, "message": "get receivers failed", "data": ""}


GET_NOTIFY_RECEIVERS_FAIL_CASE = ComponentTestCase(
    name="get notify receivers fail case",
    inputs={
        "biz_cc_id": 2,
        "bk_notify_type": ["weixin"],
        "bk_receiver_group": ["bk_biz_maintainer", "bk_biz_productor"],
        "bk_more_receiver": "a,b",
        "bk_notify_title": "title",
        "bk_notify_content": "content",
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "get receivers failed"}),
    execute_call_assertion=[],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_NOTIFY_RECEIVERS, return_value=GET_NOTIFY_RECEIVERS_FAIL),
    ],
)


SEND_MSG_FAIL_CASE = ComponentTestCase(
    name="send msg fail case",
    inputs={
        "biz_cc_id": 2,
        "bk_notify_type": ["weixin"],
        "bk_receiver_group": ["bk_biz_maintainer"],
        "bk_more_receiver": "a,b",
        "bk_notify_title": "title",
        "bk_notify_content": "content",
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={"code": 0, "message": "send msg fail"},
    ),
    execute_call_assertion=[],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_NOTIFY_RECEIVERS, return_value=GET_NOTIFY_RECEIVERS_SUCCESS),
        Patcher(
            target=GET_CLIENT_BY_USER,
            return_value=MockClient(
                cc_search_business_return=CC_SEARCH_BUSINESS_SUCCESS_RETURN,
                cmsi_send_msg_return=CMSI_SEND_MSG_FAIL_RETURN,
            ),
        ),
    ],
)

SEND_WEIXIN_SUCCESS_CLIENT = MockClient(
    cc_search_business_return=CC_SEARCH_BUSINESS_SUCCESS_RETURN, cmsi_send_msg_return=CMSI_SEND_MSG_SUCCESS_RETURN
)

SEND_WEIXIN_SUCCESS_CASE = ComponentTestCase(
    name="send weixin success case",
    inputs={
        "biz_cc_id": 2,
        "bk_notify_type": ["weixin"],
        "bk_receiver_group": ["bk_biz_maintainer"],
        "bk_more_receiver": "a,b",
        "bk_notify_title": "title",
        "bk_notify_content": "content",
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs={"code": 0, "message": "success"}),
    execute_call_assertion=[
        CallAssertion(
            func=SEND_WEIXIN_SUCCESS_CLIENT.api.v1_send_weixin,
            calls=[
                Call(
                    {
                        "receiver__username": ["tester", "a", "b", "m1", "m2", "p1", "p2"],
                        "message_data": {
                            "heading": "title",
                            "message": "content",
                        },
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                ),
            ],
        )
    ],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_NOTIFY_RECEIVERS, return_value=GET_NOTIFY_RECEIVERS_SUCCESS),
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEND_WEIXIN_SUCCESS_CLIENT),
    ],
)

SEND_EMAIL_SUCCESS_CASE = ComponentTestCase(
    name="send email success case",
    inputs={
        "biz_cc_id": 2,
        "bk_notify_type": ["email"],
        "bk_receiver_group": ["bk_biz_maintainer"],
        "bk_more_receiver": "a,b",
        "bk_notify_title": "title",
        "bk_notify_content": "content",
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs={"code": 0, "message": "success"}),
    execute_call_assertion=[
        CallAssertion(
            func=SEND_WEIXIN_SUCCESS_CLIENT.api.v1_send_mail,
            calls=[
                Call(
                    {
                        "receiver__username": ["tester", "a", "b", "m1", "m2", "p1", "p2"],
                        "title": "title",
                        "content": "<pre>content</pre>",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                ),
            ],
        )
    ],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_NOTIFY_RECEIVERS, return_value=GET_NOTIFY_RECEIVERS_SUCCESS),
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEND_WEIXIN_SUCCESS_CLIENT),
    ],
)

SEND_SMS_SUCCESS_CASE = ComponentTestCase(
    name="send sms success case",
    inputs={
        "biz_cc_id": 2,
        "bk_notify_type": ["sms"],
        "bk_receiver_group": ["bk_biz_maintainer"],
        "bk_more_receiver": "a,b",
        "bk_notify_title": "title",
        "bk_notify_content": "content",
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs={"code": 0, "message": "success"}),
    execute_call_assertion=[
        CallAssertion(
            func=SEND_WEIXIN_SUCCESS_CLIENT.api.v1_send_sms,
            calls=[
                Call(
                    {
                        "receiver__username": ["tester", "a", "b", "m1", "m2", "p1", "p2"],
                        "content": "《蓝鲸作业平台》通知 title: content 该信息如非本人订阅，请忽略本短信。",
                        "is_content_base64": False,
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                ),
            ],
        )
    ],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_NOTIFY_RECEIVERS, return_value=GET_NOTIFY_RECEIVERS_SUCCESS),
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEND_WEIXIN_SUCCESS_CLIENT),
    ],
)

SEND_MULTIPLE_NOTIFY_SUCCESS_CASE = ComponentTestCase(
    name="send multiple notify types success case",
    inputs={
        "biz_cc_id": 2,
        "bk_notify_type": ["weixin", "email", "sms"],
        "bk_receiver_group": ["bk_biz_maintainer"],
        "bk_more_receiver": "a,b",
        "bk_notify_title": "title",
        "bk_notify_content": "content",
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs={"code": 0, "message": "success"}),
    execute_call_assertion=[],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_NOTIFY_RECEIVERS, return_value=GET_NOTIFY_RECEIVERS_SUCCESS),
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEND_WEIXIN_SUCCESS_CLIENT),
    ],
)


class MockClientWithException(object):
    def __init__(self):
        self.api = MagicMock()
        self.api.v1_send_weixin = MagicMock(side_effect=Exception("Network error"))


SEND_MSG_EXCEPTION_CASE = ComponentTestCase(
    name="send msg exception case",
    inputs={
        "biz_cc_id": 2,
        "bk_notify_type": ["weixin"],
        "bk_receiver_group": ["bk_biz_maintainer"],
        "bk_more_receiver": "a,b",
        "bk_notify_title": "title",
        "bk_notify_content": "content",
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={"ex_data": "消息发送失败"},
    ),
    execute_call_assertion=[],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_NOTIFY_RECEIVERS, return_value=GET_NOTIFY_RECEIVERS_SUCCESS),
        Patcher(target=GET_CLIENT_BY_USER, return_value=MockClientWithException()),
    ],
)

SEND_WITH_RECEIVER_INFO_CASE = ComponentTestCase(
    name="send with receiver_info case (legacy format)",
    inputs={
        "biz_cc_id": 2,
        "bk_notify_type": ["weixin"],
        "bk_receiver_info": {"bk_receiver_group": ["Maintainers", "ProductPm"], "bk_more_receiver": "a,b"},
        "bk_notify_title": "title",
        "bk_notify_content": "content",
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs={"code": 0, "message": "success"}),
    execute_call_assertion=[],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_NOTIFY_RECEIVERS, return_value=GET_NOTIFY_RECEIVERS_SUCCESS),
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEND_WEIXIN_SUCCESS_CLIENT),
    ],
)

SEND_WITHOUT_RECEIVER_INFO_CASE = ComponentTestCase(
    name="send without receiver_info case (new format)",
    inputs={
        "biz_cc_id": 2,
        "bk_notify_type": ["weixin"],
        "bk_receiver_group": ["bk_biz_maintainer", "bk_biz_productor"],
        "bk_more_receiver": "a,b",
        "bk_notify_title": "title",
        "bk_notify_content": "content",
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs={"code": 0, "message": "success"}),
    execute_call_assertion=[],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_NOTIFY_RECEIVERS, return_value=GET_NOTIFY_RECEIVERS_SUCCESS),
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEND_WEIXIN_SUCCESS_CLIENT),
    ],
)
