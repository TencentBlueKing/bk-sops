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
    Call,
    CallAssertion,
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    Patcher,
)

from pipeline_plugins.components.collections.sites.open.cc import CmdbDeleteHostLockComponent
from pipeline_plugins.tests.components.collections.sites.open.utils.cc_ipv6_mock_utils import (
    CMDB_GET_CLIENT_PATCH,
    create_mock_cmdb_client_with_hosts,
)


class CmdbTransferFaultHostComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        # DELETE_HOST_LOCK_SUCCESS_CASE 加锁成功的测试用例
        # DELETE_HOST_LOCK_FAIL_CASE 加锁失败的测试用例
        return [DELETE_HOST_LOCK_SUCCESS_CASE, DELETE_HOST_LOCK_FAIL_CASE]

    def component_cls(self):
        return CmdbDeleteHostLockComponent


# mock path
GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.cc.host_lock.base.get_client_by_username"
CC_GET_HOST_BY_INNERIP_WITH_IPV6 = (
    "pipeline_plugins.components.collections.sites.open.cc.base.cc_get_host_by_innerip_with_ipv6"
)
CC_GET_HOST_ID_BY_INNERIP = "pipeline_plugins.components.collections.sites.open.cc.base.cc_get_host_id_by_innerip"

# IPv6 场景的 mock 返回值
IPV6_HOST_RESULT = {
    "result": True,
    "data": [
        {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0},
        {"bk_host_id": 2, "bk_host_innerip": "2.2.2.2", "bk_cloud_id": 0},
    ],
}

# 非 IPv6 场景的 mock 返回值
NON_IPV6_HOST_RESULT = {"result": True, "data": ["1", "2"]}

# 使用IPv6适配的CMDB客户端mock
MOCK_CMDB_CLIENT_SUCCESS = create_mock_cmdb_client_with_hosts(
    [
        {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0},
        {"bk_host_id": 2, "bk_host_innerip": "2.2.2.2", "bk_cloud_id": 0},
    ]
)
MOCK_CMDB_CLIENT_SUCCESS.api.delete_host_lock = MagicMock(
    return_value={"result": True, "code": 0, "message": "success", "data": {}}
)

MOCK_CMDB_CLIENT_FAIL = create_mock_cmdb_client_with_hosts(
    [
        {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0},
        {"bk_host_id": 2, "bk_host_innerip": "2.2.2.2", "bk_cloud_id": 0},
    ]
)
MOCK_CMDB_CLIENT_FAIL.api.delete_host_lock = MagicMock(
    return_value={"result": False, "code": 1, "message": "fail", "data": {}}
)

DELETE_HOST_LOCK_SUCCESS_CASE = ComponentTestCase(
    name="delete host lock success case",
    inputs={"cc_host_ip": "1.1.1.1;2.2.2.2"},
    parent_data={
        "tenant_id": "system",
        "executor": "executor_token",
        "biz_cc_id": 2,
        "biz_supplier_account": 0,
        "language": "中文",
    },
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=MOCK_CMDB_CLIENT_SUCCESS.api.delete_host_lock,
            calls=[Call({"id_list": [1, 2]}, headers={"X-Bk-Tenant-Id": "system"})],
        ),
    ],
    # delete patch
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=MOCK_CMDB_CLIENT_SUCCESS),
        Patcher(target=CMDB_GET_CLIENT_PATCH, return_value=MOCK_CMDB_CLIENT_SUCCESS),
        Patcher(target=CC_GET_HOST_BY_INNERIP_WITH_IPV6, return_value=IPV6_HOST_RESULT),
        Patcher(target=CC_GET_HOST_ID_BY_INNERIP, return_value=NON_IPV6_HOST_RESULT),
    ],
)

DELETE_HOST_LOCK_FAIL_CASE = ComponentTestCase(
    name="delete host lock fail case",
    inputs={"cc_host_ip": "1.1.1.1;2.2.2.2"},
    parent_data={
        "tenant_id": "system",
        "executor": "executor_token",
        "biz_cc_id": 2,
        "biz_supplier_account": 0,
        "language": "中文",
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={"ex_data": ('调用配置平台(CMDB)接口cc.delete_host_lock返回失败, error=fail, params={"id_list":[1,2]}')},
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=MOCK_CMDB_CLIENT_FAIL.api.delete_host_lock,
            calls=[Call({"id_list": [1, 2]}, headers={"X-Bk-Tenant-Id": "system"})],
        ),
    ],
    # delete patch
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=MOCK_CMDB_CLIENT_FAIL),
        Patcher(target=CMDB_GET_CLIENT_PATCH, return_value=MOCK_CMDB_CLIENT_FAIL),
        Patcher(target=CC_GET_HOST_BY_INNERIP_WITH_IPV6, return_value=IPV6_HOST_RESULT),
        Patcher(target=CC_GET_HOST_ID_BY_INNERIP, return_value=NON_IPV6_HOST_RESULT),
    ],
)
