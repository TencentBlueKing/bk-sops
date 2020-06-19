# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
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
from pipeline_plugins.components.collections.sites.open.cc import CmdbAddHostLockComponent


class CmdbTransferFaultHostComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        # ADD_HOST_LOCK_SUCCESS_CASE 加锁成功的测试用例
        # ADD_HOST_LOCK_FAIL_CASE 加锁失败的测试用例
        return [ADD_HOST_LOCK_SUCCESS_CASE, ADD_HOST_LOCK_FAIL_CASE]

    def component_cls(self):
        return CmdbAddHostLockComponent


class MockClient(object):
    def __init__(self, add_host_lock_return=None):
        self.set_bk_api_ver = MagicMock()
        self.cc = MagicMock()
        self.cc.add_host_lock = MagicMock(return_value=add_host_lock_return)


# mock path
GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.cc.host_lock.base.get_client_by_user"
CC_GET_IPS_INFO_BY_STR = "pipeline_plugins.components.collections.sites.open.cc.host_lock.base.cc_get_ips_info_by_str"

# mock client
ADD_HOST_LOCK_SUCCESS_CLIENT = MockClient(
    add_host_lock_return={"result": True, "code": 0, "message": "success", "data": {}}
)

ADD_HOST_LOCK_FAIL_CLIENT = MockClient(add_host_lock_return={"result": False, "code": 1, "message": "fail", "data": {}})

ADD_HOST_LOCK_SUCCESS_CASE = ComponentTestCase(
    name="add host lock success case",
    inputs={"cc_host_ip": "1.1.1.1;2.2.2.2"},
    parent_data={"executor": "executor_token", "biz_cc_id": 2, "biz_supplier_account": 0, "language": "中文"},
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call("executor_token", 2, "1.1.1.1;2.2.2.2")]),
        CallAssertion(
            func=ADD_HOST_LOCK_SUCCESS_CLIENT.cc.add_host_lock, calls=[Call({"id_list": [1, 2]})]
        ),
    ],
    # add patch
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=ADD_HOST_LOCK_SUCCESS_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR,
                return_value={"result": True, "ip_result": [{"HostID": 1}, {"HostID": 2}], "invalid_ip": []}),
    ],
)

ADD_HOST_LOCK_FAIL_CASE = ComponentTestCase(
    name="add host lock fail case",
    inputs={"cc_host_ip": "1.1.1.1;2.2.2.2"},
    parent_data={"executor": "executor_token", "biz_cc_id": 2, "biz_supplier_account": 0, "language": "中文"},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={"ex_data": '调用配置平台(CMDB)接口cc.add_host_lock返回失败, params={"id_list":[1,2]}, error=fail'},
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call("executor_token", 2, "1.1.1.1;2.2.2.2")]),
        CallAssertion(
            func=ADD_HOST_LOCK_FAIL_CLIENT.cc.add_host_lock, calls=[Call({"id_list": [1, 2]})]
        ),
    ],
    # add patch
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=ADD_HOST_LOCK_FAIL_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR,
                return_value={"result": True, "ip_result": [{"HostID": 1}, {"HostID": 2}], "invalid_ip": []}),
    ],
)
