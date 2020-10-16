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
    Call,
    CallAssertion,
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.cc.cc_set_delete_by_name.v1_0 import CCSetDeleteByNameComponent


class CCSetDeleteByNameComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        return CCSetDeleteByNameComponent

    def cases(self):
        return [INPUT_FAIL_CASE, INPUT_FAIL_NOT_FIND_SETS_CASE, INPUT_SUCCESS_DELETE_SUCCESS_CASE]


class MockClient(object):
    def __init__(self, search_set_return=None, batch_delete_set_return=None):
        self.set_bk_api_ver = MagicMock()
        self.cc = MagicMock()
        self.cc.search_set = MagicMock(return_value=search_set_return)
        self.cc.batch_delete_set = MagicMock(return_value=batch_delete_set_return)


GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.cc.cc_set_delete_by_name.v1_0.get_client_by_user"
)
CC_GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_user"

# 通用client
COMMON_CLIENT = MockClient(
    search_set_return={
        "code": 0,
        "permission": None,
        "result": True,
        "request_id": "cceff7bef1e64533a2a7cf2131bd2cb5",
        "message": "success",
        "data": {"count": 0, "info": [{"default": 0, "bk_set_id": 46}]},
    },
    batch_delete_set_return={
        "code": 0,
        "permission": None,
        "result": True,
        "request_id": "028039a1ed4c41c38596b67e86a2efd4",
        "message": "success",
        "data": None,
    },
)

# 调用 API 的通用参数
CC_SEARCH_SET_KWARGS = {
    "bk_biz_id": 2,
    "fields": ["bk_set_id"],
    "condition": {"bk_set_name": "set_name"},
    "page": {"start": 0, "limit": 100, "sort": "bk_set_name"},
}
CC_BATCH_DELETE_SET_KWARGS = {"bk_biz_id": 2, "delete": {"inst_ids": ["1"]}}

# parent_data
PARENT_DATA = {"executor": "admin", "bk_biz_id": 2}

INPUT_FAIL_CASE = ComponentTestCase(
    name="fail case: input error",
    inputs={"cc_set_name": "测试，test"},
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "存在中文逗号"}),
    schedule_assertion=[],
    execute_call_assertion=[],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=COMMON_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=COMMON_CLIENT),
    ],
)

SEARCH_SET_FAIL_CLIENT = MockClient(
    search_set_return={
        "code": 0,
        "permission": None,
        "result": True,
        "request_id": "cceff7bef1e64533a2a7cf2131bd2cb5",
        "message": "success",
        "data": {"count": 0, "info": []},
    },
)

INPUT_FAIL_NOT_FIND_SETS_CASE = ComponentTestCase(
    name="success case: sets name not fount",
    inputs={"cc_set_name": "测试,test"},
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=[CallAssertion(func=SEARCH_SET_FAIL_CLIENT.cc.search_set, calls=[Call(CC_SEARCH_SET_KWARGS)])],
    execute_call_assertion=[],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=COMMON_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=COMMON_CLIENT),
    ],
)

BATCH_DELETE_SET_FAIL_CLIENT = MockClient(
    search_set_return={
        "code": 0,
        "permission": None,
        "result": True,
        "request_id": "cceff7bef1e64533a2a7cf2131bd2cb5",
        "message": "success",
        "data": {"count": 0, "info": [{"default": 0, "bk_set_id": 46}]},
    },
    batch_delete_set_return={
        "code": 0,
        "permission": None,
        # 'result': False,
        "request_id": "028039a1ed4c41c38596b67e86a2efd4",
        "message": "fail",
        "data": None,
    },
)

INPUT_SUCCESS_DELETE_SUCCESS_CASE = ComponentTestCase(
    name="success case: all success",
    inputs={"cc_set_name": "测试,test"},
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=[
        CallAssertion(func=COMMON_CLIENT.cc.search_set, calls=[Call(CC_SEARCH_SET_KWARGS)]),
        CallAssertion(func=COMMON_CLIENT.cc.batch_delete_set, calls=[Call(CC_SEARCH_SET_KWARGS)]),
    ],
    execute_call_assertion=[],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=COMMON_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=COMMON_CLIENT),
    ],
)
