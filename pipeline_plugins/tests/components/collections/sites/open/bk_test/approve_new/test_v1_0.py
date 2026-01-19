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
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    Patcher,
    ScheduleAssertion,
)

from pipeline_plugins.components.collections.sites.open.bk.approve_new.v1_0 import SpecialApproveComponent


class BkApproveNewComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        return SpecialApproveComponent

    def cases(self):
        return [
            CREATE_TICKET_SUCCESS_CASE,
            CREATE_TICKET_FAIL_CASE,
            SCHEDULE_APPROVE_PASS_CASE,
            SCHEDULE_APPROVE_REJECT_CASE,
            SCHEDULE_APPROVE_REJECT_NOT_BLOCK_CASE,
            SCHEDULE_EXCEPTION_CASE,
        ]


class MockClient(object):
    def __init__(self, create_ticket_return=None):
        self.api = MagicMock()
        self.api.create_ticket = MagicMock(return_value=create_ticket_return)


# Mock paths
GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.bk.approve_new.v1_0.get_client_by_username"
GET_NODE_CALLBACK_URL = "pipeline_plugins.components.collections.sites.open.bk.approve_new.v1_0.get_node_callback_url"
HANDLE_API_ERROR = "pipeline_plugins.components.collections.sites.open.bk.approve_new.v1_0.handle_api_error"
SEND_TASKFLOW_MESSAGE = "pipeline_plugins.components.collections.sites.open.bk.approve_new.v1_0.send_taskflow_message"

# Parent data
COMMON_PARENT = {"executor": "admin", "tenant_id": "default", "biz_cc_id": 1, "task_id": 123}

# Test inputs
BASE_INPUTS = {
    "bk_verifier": "user1,user2,user3",
    "bk_approve_title": "Test Approval",
    "bk_approve_content": "This is a test approval content",
}

BASE_INPUTS_WITH_SPACES = {
    "bk_verifier": "user1 , user2 , user3 ",
    "bk_approve_title": "Test Approval",
    "bk_approve_content": "This is a test approval content",
}

# Test outputs
SUCCESS_OUTPUTS = {"sn": "NO20231201000001", "id": 12345}

# Mock responses
CREATE_TICKET_SUCCESS_RETURN = {
    "result": True,
    "data": {"sn": "NO20231201000001", "id": 12345},
}

CREATE_TICKET_FAIL_RETURN = {"result": False, "message": "create ticket failed"}

# Mock clients
CREATE_TICKET_SUCCESS_CLIENT = MockClient(create_ticket_return=CREATE_TICKET_SUCCESS_RETURN)
CREATE_TICKET_FAIL_CLIENT = MockClient(create_ticket_return=CREATE_TICKET_FAIL_RETURN)

# Test cases
CREATE_TICKET_SUCCESS_CASE = ComponentTestCase(
    name="create ticket success case",
    inputs=BASE_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs=SUCCESS_OUTPUTS),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs={**SUCCESS_OUTPUTS, "approve_result": "通过"},
        callback_data={"ticket": {"approve_result": True}},
        schedule_finished=True,
    ),
    patchers=[
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=CREATE_TICKET_SUCCESS_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="http://callback.url"),
        Patcher(target=SEND_TASKFLOW_MESSAGE, return_value=MagicMock()),
    ],
)

CREATE_TICKET_FAIL_CASE = ComponentTestCase(
    name="create ticket fail case",
    inputs=BASE_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "调用蓝鲸服务(BK)接口itsm.create_ticket返回失败"}),
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=CREATE_TICKET_FAIL_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="http://callback.url"),
        Patcher(target=HANDLE_API_ERROR, return_value="调用蓝鲸服务(BK)接口itsm.create_ticket返回失败"),
    ],
)

SCHEDULE_APPROVE_PASS_CASE = ComponentTestCase(
    name="schedule approve pass case",
    inputs=BASE_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs=SUCCESS_OUTPUTS),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs={**SUCCESS_OUTPUTS, "approve_result": "通过"},
        callback_data={"ticket": {"approve_result": True}},
        schedule_finished=True,
    ),
    patchers=[
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=CREATE_TICKET_SUCCESS_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="http://callback.url"),
        Patcher(target=SEND_TASKFLOW_MESSAGE, return_value=MagicMock()),
    ],
)

SCHEDULE_APPROVE_REJECT_CASE = ComponentTestCase(
    name="schedule approve reject case",
    inputs=BASE_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs=SUCCESS_OUTPUTS),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={**SUCCESS_OUTPUTS, "approve_result": "拒绝"},
        callback_data={"ticket": {"approve_result": False}},
    ),
    patchers=[
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=CREATE_TICKET_SUCCESS_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="http://callback.url"),
        Patcher(target=SEND_TASKFLOW_MESSAGE, return_value=MagicMock()),
    ],
)

SCHEDULE_APPROVE_REJECT_NOT_BLOCK_CASE = ComponentTestCase(
    name="schedule approve reject not block case",
    inputs={**BASE_INPUTS, "rejected_block": False},
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs=SUCCESS_OUTPUTS),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs={**SUCCESS_OUTPUTS, "approve_result": "拒绝"},
        callback_data={"ticket": {"approve_result": False}},
        schedule_finished=True,
    ),
    patchers=[
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=CREATE_TICKET_SUCCESS_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="http://callback.url"),
        Patcher(target=SEND_TASKFLOW_MESSAGE, return_value=MagicMock()),
    ],
)

SCHEDULE_EXCEPTION_CASE = ComponentTestCase(
    name="schedule exception case",
    inputs=BASE_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs=SUCCESS_OUTPUTS),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            **SUCCESS_OUTPUTS,
            "ex_data": "get Special Approve Component result failed: {'invalid': 'data'}, err: 'ticket'",
        },
        callback_data={"invalid": "data"},
    ),
    patchers=[
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=CREATE_TICKET_SUCCESS_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="http://callback.url"),
        Patcher(target=SEND_TASKFLOW_MESSAGE, return_value=MagicMock()),
    ],
)
