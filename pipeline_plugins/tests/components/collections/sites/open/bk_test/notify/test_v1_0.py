# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
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
    ComponentTestMixin,
    ComponentTestCase,
    CallAssertion,
    ExecuteAssertion,
    Call,
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.bk.notify.v1_0 import NotifyComponent


class BkNotifyComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        return NotifyComponent

    def cases(self):
        return [
            GET_NOTIFY_RECEIVERS_FAIL_CASE,
            SEND_MSG_FAIL_CASE,
            SEND_MSG_SUCCESS_CASE,
            SEND_MSG_SUCCESS_RECEIVER_ORDER_CASE
        ]


class MockClient(object):
    def __init__(self, cc_search_business_return=None, cmsi_send_msg_return=None):
        self.cc = MagicMock()
        self.cc.search_business = MagicMock(return_value=cc_search_business_return)
        self.cmsi = MagicMock()
        self.cmsi.send_msg = MagicMock(return_value=cmsi_send_msg_return)


GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.bk.notify.v1_0.get_client_by_user"
HANDLE_API_ERROR = "pipeline_plugins.components.collections.sites.open.bk.notify.v1_0.handle_api_error"
BK_HANDLE_API_ERROR = "pipeline_plugins.components.collections.sites.open.bk.notify.v1_0.bk_handle_api_error"

COMMON_PARENT = {"executor": "admin", "biz_cc_id": 2, "biz_supplier_account": 0}

CC_SEARCH_BUSINESS_FAIL_RETURN = {
    "result": False,
    "message": "search business fail"
}

CC_SEARCH_BUSINESS_SUCCESS_RETURN = {
    "result": True,
    "data": {
        "count": 1,
        "info": [
            {
                "bk_biz_maintainer": "m1,m2",
                "bk_biz_productor": "p1,p2",
                "bk_biz_developer": "d1,d2",
                "bk_biz_tester": "t1,t2"
            }
        ]
    }
}

CMSI_SEND_MSG_FAIL_RETURN = {
    "result": False,
    "message": "send msg fail"
}

CMSI_SEND_MSG_SUCCESS_RETURN = {
    "result": True,
    "message": "success"
}


GET_NOTIFY_RECEIVERS_FAIL_CASE = ComponentTestCase(
    name="get notify receivers fail case",
    inputs={
        "biz_cc_id": 2,
        "bk_notify_type": ["mail", "weixin"],
        "bk_receiver_info": {
            "bk_receiver_group": ["Maintainers", "ProductPm"],
            "bk_more_receiver": "a,b",
        },
        "bk_notify_title": "title",
        "bk_notify_content": "content"
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False,
                                       outputs={"ex_data": "search business fail"}),
    execute_call_assertion=[],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER,
                return_value=MockClient(cc_search_business_return=CC_SEARCH_BUSINESS_FAIL_RETURN)),
        Patcher(target=HANDLE_API_ERROR,
                return_value="search business fail")
    ],
)


SEND_MSG_FAIL_CASE = ComponentTestCase(
    name="send msg fail case",
    inputs={
        "biz_cc_id": 2,
        "bk_notify_type": ["mail", "weixin"],
        "bk_receiver_info": {
            "bk_receiver_group": ["Maintainers", "ProductPm"],
            "bk_more_receiver": "a,b",
        },
        "bk_notify_title": "title",
        "bk_notify_content": "content"
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False,
                                       outputs={"ex_data": "send msg fail;send msg fail;"}),
    execute_call_assertion=[],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER,
                return_value=MockClient(cc_search_business_return=CC_SEARCH_BUSINESS_SUCCESS_RETURN,
                                        cmsi_send_msg_return=CMSI_SEND_MSG_FAIL_RETURN)),
        Patcher(target=BK_HANDLE_API_ERROR,
                return_value="send msg fail")
    ],
)

SEND_MSG_SUCCESS_CLIENT = MockClient(cc_search_business_return=CC_SEARCH_BUSINESS_SUCCESS_RETURN,
                                     cmsi_send_msg_return=CMSI_SEND_MSG_SUCCESS_RETURN)

SEND_MSG_SUCCESS_CASE = ComponentTestCase(
    name="send msg success case",
    inputs={
        "biz_cc_id": 2,
        "bk_notify_type": ["mail", "weixin"],
        "bk_receiver_info": {
            "bk_receiver_group": ["Maintainers", "ProductPm"],
            "bk_more_receiver": "a,b",
        },
        "bk_notify_title": "title",
        "bk_notify_content": "content"
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True,
                                       outputs={}),
    execute_call_assertion=[
        CallAssertion(
            func=SEND_MSG_SUCCESS_CLIENT.cmsi.send_msg,
            calls=[
                Call({
                    "receiver__username": ",".join(sorted(set("b,p1,p2,m1,m2,a".split(",")))),
                    "title": "title",
                    "content": "<pre>content</pre>",
                    "msg_type": "mail"
                }),
                Call({
                    "receiver__username": ",".join(sorted(set("b,p1,p2,m1,m2,a".split(",")))),
                    "title": "title",
                    "content": "content",
                    "msg_type": "weixin"
                })
            ],
        )
    ],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER,
                return_value=SEND_MSG_SUCCESS_CLIENT),
    ],
)


SEND_MSG_SUCCESS_RECEIVER_ORDER_CASE = ComponentTestCase(
    name="send msg success receiver order case",
    inputs={
        "biz_cc_id": 2,
        "bk_notify_type": ["mail", "weixin"],
        "bk_receiver_info": {
            "bk_receiver_group": [],
            "bk_more_receiver": "c,a,b",
        },
        "bk_notify_title": "title",
        "bk_notify_content": "content"
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True,
                                       outputs={}),
    execute_call_assertion=[
        CallAssertion(
            func=SEND_MSG_SUCCESS_CLIENT.cmsi.send_msg,
            calls=[
                Call({
                    "receiver__username": "c,a,b",
                    "title": "title",
                    "content": "<pre>content</pre>",
                    "msg_type": "mail"
                }),
                Call({
                    "receiver__username": "c,a,b",
                    "title": "title",
                    "content": "content",
                    "msg_type": "weixin"
                })
            ],
        )
    ],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER,
                return_value=SEND_MSG_SUCCESS_CLIENT),
    ],
)
