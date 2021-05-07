# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
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
from pipeline_plugins.components.collections.sites.open.cc.update_set_service_status.v1_1 import (
    CCUpdateSetServiceStatusComponent,
)


class CCUpdateWorldStatusComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        return CCUpdateSetServiceStatusComponent

    def cases(self):
        return [
            SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_CASE,
            SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_CASE_WITH_ATTR,
            SEARCH_SET_SUCCESS_UPDATE_SET_FAIL_CASE,
            SEARCH_SET_FAIL_CASE,
        ]


class MockClient(object):
    def __init__(self, search_set_return=None, update_set_return=None):
        self.cc = MagicMock()
        self.cc.search_set = MagicMock(return_value=search_set_return)
        self.cc.update_set = MagicMock(return_value=update_set_return)


GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.cc.update_set_service_status.v1_1.get_client_by_user"
)
CC_GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_user"
BATCH_REQUEST = "pipeline_plugins.components.collections.sites.open.cc.update_set_service_status.v1_1.batch_request"

COMMON_PARENT = {"executor": "admin", "bk_biz_id": 2, "biz_supplier_account": 0}

CC_SEARCH_SET_KWARGS = {
    "bk_biz_id": 2,
    "fields": ["bk_set_id", "bk_set_name"],
    "condition": {"bk_set_name": "set_name"},
    "page": {"start": 0, "limit": 100, "sort": "bk_set_name"},
}

CC_UPDATE_SET_KWARGS = {
    "bk_biz_id": 2,
    "bk_set_id": 2,
    "data": {"bk_service_status": 1},
}

SEARCH_SET_SUCCESS_RESULT = {
    "code": 0,
    "permission": None,
    "result": True,
    "request_id": "c50218c056f3467082b2acbfcc110a73",
    "message": "success",
    "data": {"count": 1, "info": [{"default": 0, "bk_set_id": 45, "bk_set_name": "test1"}]},
}

SEARCH_SET_FAIL_RESULT = {
    "code": 0,
    "permission": None,
    "result": False,
    "request_id": "4a487ef38cf14157a0c3795310bad1a3",
    "message": "fail",
    "data": [],
}

UPDATE_SET_SUCCESS_RESULT = {
    "code": 0,
    "permission": None,
    "result": True,
    "request_id": "4a487ef38cf14157a0c3795310bad1a3",
    "message": "success",
    "data": [],
}

UPDATE_SET_FAIL_RESULT = {
    "code": 0,
    "permission": None,
    "result": False,
    "request_id": "4a487ef38cf14157a0c3795310bad1a3",
    "message": "fail",
    "data": [],
}

SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_INPUT = {"set_list": "test1,2,3", "set_select_method": "name", "set_status": "1"}
SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_INPUT_WITH_ATTR = {
    "set_list": "test1",
    "set_select_method": "custom",
    "set_status": "1",
    "set_attr_id": "bk_set_name",
}

SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_CLIENT = MockClient(
    search_set_return=SEARCH_SET_SUCCESS_RESULT,
    update_set_return=UPDATE_SET_SUCCESS_RESULT,
)

SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_CASE = ComponentTestCase(
    name="success case: all success",
    inputs=SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_INPUT,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=[
        CallAssertion(
            func=SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_CLIENT.cc.search_set, calls=[Call(CC_SEARCH_SET_KWARGS)]
        ),
        CallAssertion(
            func=SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_CLIENT.cc.update_set, calls=[Call(CC_UPDATE_SET_KWARGS)]
        ),
    ],
    execute_call_assertion=[],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_CLIENT),
    ],
)

SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_CASE_WITH_ATTR = ComponentTestCase(
    name="success case: all success",
    inputs=SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_INPUT_WITH_ATTR,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=[
        CallAssertion(
            func=SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_CLIENT.cc.search_set, calls=[Call(CC_SEARCH_SET_KWARGS)]
        ),
        CallAssertion(
            func=SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_CLIENT.cc.update_set, calls=[Call(CC_UPDATE_SET_KWARGS)]
        ),
    ],
    execute_call_assertion=[],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_CLIENT),
    ],
)

SEARCH_SET_SUCCESS_UPDATE_SET_FAIL_CLIENT = MockClient(
    search_set_return=SEARCH_SET_SUCCESS_RESULT,
    update_set_return=UPDATE_SET_FAIL_RESULT,
)

SEARCH_SET_SUCCESS_UPDATE_SET_FAIL_CASE = ComponentTestCase(
    name="fail case: set success update set fail",
    inputs=SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_INPUT,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "ex_data": '调用配置平台(CMDB)接口cc.update_set返回失败, params={"bk_biz_id":2,"bk_supplier_account":0,'
            '"bk_set_id":45,"data":{"bk_service_status":"1"}}, error=fail, request_id=4a487ef38cf14157a0c3795310bad1a3'
        },
    ),
    schedule_assertion=[
        CallAssertion(func=SEARCH_SET_SUCCESS_UPDATE_SET_FAIL_CLIENT.cc.search_set, calls=[Call(CC_SEARCH_SET_KWARGS)]),
        CallAssertion(func=SEARCH_SET_SUCCESS_UPDATE_SET_FAIL_CLIENT.cc.update_set, calls=[Call(CC_UPDATE_SET_KWARGS)]),
    ],
    execute_call_assertion=[],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEARCH_SET_SUCCESS_UPDATE_SET_FAIL_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=SEARCH_SET_SUCCESS_UPDATE_SET_FAIL_CLIENT),
    ],
)

SEARCH_SET_FAIL_CLIENT = MockClient(
    search_set_return=SEARCH_SET_FAIL_RESULT,
    update_set_return=UPDATE_SET_FAIL_RESULT,
)

SEARCH_SET_FAIL_CASE = ComponentTestCase(
    name="fail case: search set fail",
    inputs=SEARCH_SET_SUCCESS_UPDATE_SET_SUCCESS_INPUT,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "batch_request client.cc.search_set error"}),
    schedule_assertion=[
        CallAssertion(func=SEARCH_SET_FAIL_CLIENT.cc.search_set, calls=[Call(CC_SEARCH_SET_KWARGS)]),
        CallAssertion(func=SEARCH_SET_FAIL_CLIENT.cc.update_set, calls=[Call(CC_UPDATE_SET_KWARGS)]),
    ],
    execute_call_assertion=[],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEARCH_SET_FAIL_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=SEARCH_SET_FAIL_CLIENT),
        Patcher(target=BATCH_REQUEST, return_value=[]),
    ],
)
