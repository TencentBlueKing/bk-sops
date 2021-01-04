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
    ScheduleAssertion,
    Call,
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.bk.approve.v1_0 import ApproveComponent


class BkApproveComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        return ApproveComponent

    def cases(self):
        return [
            CREATE_APPROVE_TICKET_FAIL_CASE,
            CREATE_APPROVE_TICKET_SUCCESS_CASE,
        ]


class MockClient(object):
    def __init__(self, create_ticket=None):
        self.create_ticket = MagicMock(return_value=create_ticket)


GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.bk.approve.v1_0.BKItsmClient"
GET_NODE_CALLBACK_URL = "pipeline_plugins.components.collections.sites.open.bk.approve.v1_0.get_node_callback_url"
BK_HANDLE_API_ERROR = "pipeline_plugins.components.collections.sites.open.bk.approve.v1_0.handle_api_error"

COMMON_PARENT = {"executor": "admin", "biz_cc_id": 2, "biz_supplier_account": 0}

CREAT_TICKET_FAIL_RETURN = {"result": False, "message": "create ticket fail"}

CREAT_TICKET_SUCCESS_RETURN = {"message": "success", "code": 0, "data": {"sn": "NO2019090519542603"}, "result": True}

CALLBACK_URL_FAIL_RETURN = {"result": False, "message": "approve reject"}

CALLBACK_URL_SUCCESS_RETURN = {
    "sn": "REQ20200831000005",
    "title": "this is a test",
    "ticket_url": "https://xxx.xx.com",
    "current_status": "FINISHED",
    "updated_by": "admin,hongsong",
    "update_at": "2020-08-31 20:57:22",
    "approve_result": True,
}

CREAT_TICKET_SUCCESS_CLIENT = MockClient(create_ticket=CREAT_TICKET_SUCCESS_RETURN)
CREAT_TICKET_FAIL_RETURN_CLIENT = MockClient(create_ticket=CREAT_TICKET_FAIL_RETURN)

CREAT_TICKET_CALL = {
    "creator": "admin",
    "fields": [
        {"key": "title", "value": "this is a test"},
        {"key": "APPROVER", "value": "tester,tester1"},
        {"key": "APPROVAL_CONTENT", "value": "test content"},
    ],
    "fast_approval": True,
    "meta": {"callback_url": "callback_url"},
}
INPUTS = {
    "bk_verifier": "tester, tester1",
    "bk_approve_title": "this is a test",
    "bk_notify_title": "title",
    "bk_approve_content": "test content",
}

CREATE_APPROVE_TICKET_FAIL_CASE = ComponentTestCase(
    name="create approve ticket fail case",
    inputs=INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "create ticket fail"}),
    execute_call_assertion=[
        CallAssertion(
            func=CREAT_TICKET_FAIL_RETURN_CLIENT.create_ticket,
            calls=[Call(**CREAT_TICKET_CALL)],
        )
    ],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CREAT_TICKET_FAIL_RETURN_CLIENT),
        Patcher(target=BK_HANDLE_API_ERROR, return_value="create ticket fail"),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="callback_url"),
    ],
)

CREATE_APPROVE_TICKET_SUCCESS_CASE = ComponentTestCase(
    name="create approve ticket success case",
    inputs=INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs={"sn": "NO2019090519542603"}),
    execute_call_assertion=[
        CallAssertion(
            func=CREAT_TICKET_SUCCESS_CLIENT.create_ticket,
            calls=[Call(**CREAT_TICKET_CALL)],
        )
    ],
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs={"approve_result": "通过", "sn": "NO2019090519542603"},
        callback_data=CALLBACK_URL_SUCCESS_RETURN,
    ),
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CREAT_TICKET_SUCCESS_CLIENT),
        Patcher(target=BK_HANDLE_API_ERROR, return_value=""),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="callback_url"),
    ],
)
