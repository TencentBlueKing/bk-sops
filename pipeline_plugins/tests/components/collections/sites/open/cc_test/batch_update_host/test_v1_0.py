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
from pipeline.component_framework.test import ComponentTestCase, ComponentTestMixin, ExecuteAssertion, Patcher

from pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0 import CCBatchUpdateHostComponent
from pipeline_plugins.tests.components.collections.sites.open.utils.cc_ipv6_mock_utils import (
    CC_GET_CLIENT_PATCH,
    CMDB_GET_CLIENT_PATCH,
    MockCMDBClientIPv6,
    create_mock_cmdb_client_with_hosts,
)


class CCBatchUpdateHostComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        return CCBatchUpdateHostComponent

    def cases(self):
        return [INVALID_IP_CASE, CC_HOST_PROP_VALUE_ILLEGAL, BATCH_UPDATE_HOST_SUCCESS, BATCH_UPDATE_HOST_FAIL]


class MockClient(MockCMDBClientIPv6):
    def __init__(self, batch_update_host_return=None):
        super(MockClient, self).__init__()
        self.api.batch_update_host = MagicMock(return_value=batch_update_host_return)


BATCH_UPDATE_HOST_SUCCESS_CLIENT = MockClient(
    batch_update_host_return={"result": True, "code": 0, "message": "success", "data": None}
)

BATCH_UPDATE_HOST_FAIL_CLIENT = MockClient(
    batch_update_host_return={"result": False, "code": 0, "message": "error", "data": None}
)

GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.get_client_by_username"
)
CC_GET_IPS_INFO_BY_STR = (
    "pipeline_plugins.components.collections.sites.open.cc.base.cc_get_host_id_by_innerip_and_cloudid"
)
CC_GET_HOST_BY_INNERIP_WITH_IPV6 = (
    "pipeline_plugins.components.collections.sites.open.cc.base.cc_get_host_by_innerip_with_ipv6"
)
VERIFY_HOST_PROPERTY = (
    "pipeline_plugins.components.collections.sites.open.cc.batch_update_host.v1_0.verify_host_property"
)


def verify_host_property(executor, supplier_account, language, cc_host_property, cc_host_prop_value):
    return True, ""


def verify_host_property_fail(executor, supplier_account, language, cc_host_property, cc_host_prop_value):
    return False, "参数值校验失败，请重试并修改为正确的参数值"


INPUT_DATA = {
    "cc_host_update_method": "auto",
    "cc_host_property_custom": [
        {
            "bk_host_innerip": "1.1.1.1",
            "bk_host_outerip": "",
            "operator": "admin",
            "bk_bak_operator": "admin",
            "bk_sn": "",
            "bk_comment": "test",
            "bk_sla": "",
            "bk_state_name": "",
            "bk_province_name": "",
            "bk_isp_name": "",
            "bk_state": "",
            "x": "",
        }
    ],
    "cc_auto_separator": ",",
}

CC_GET_IPS_INFO_BY_STR_VALUE = {
    "result": True,
    "data": ["111"],
    "invalid_ip": [],
}

# 输入ip不合法案例
INVALID_IP_CASE = ComponentTestCase(
    name="Invalid IP Case",
    inputs=INPUT_DATA,
    parent_data={"tenant_id": "system", "executor": "executor", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={"ex_data": "ip not found in business: 1.1.1.1"},
    ),
    schedule_assertion=None,
    execute_call_assertion=None,
    patchers=[
        Patcher(target=CC_GET_CLIENT_PATCH, return_value=create_mock_cmdb_client_with_hosts([])),
        Patcher(target=CMDB_GET_CLIENT_PATCH, return_value=create_mock_cmdb_client_with_hosts([])),
        Patcher(
            target=CC_GET_HOST_BY_INNERIP_WITH_IPV6,
            return_value={"result": False, "message": "ip not found in business: 1.1.1.1"},
        ),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"result": False, "message": "ip not found in business: 1.1.1.1"},
        ),
    ],
)

# cc_host_prop_value不合法
CC_HOST_PROP_VALUE_ILLEGAL = ComponentTestCase(
    name="cc host prop value illegal",
    inputs=INPUT_DATA,
    parent_data={"tenant_id": "system", "executor": "executor", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "参数值校验失败，请重试并修改为正确的参数值"}),
    schedule_assertion=None,
    execute_call_assertion=None,
    patchers=[
        Patcher(
            target=CC_GET_CLIENT_PATCH,
            return_value=create_mock_cmdb_client_with_hosts(
                [{"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]
            ),
        ),
        Patcher(
            target=CMDB_GET_CLIENT_PATCH,
            return_value=create_mock_cmdb_client_with_hosts(
                [{"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]
            ),
        ),
        Patcher(target=VERIFY_HOST_PROPERTY, side_effect=verify_host_property_fail),
        Patcher(
            target=CC_GET_HOST_BY_INNERIP_WITH_IPV6,
            return_value={"result": True, "data": [{"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]},
        ),
    ],
)

# batch_update_host成功
BATCH_UPDATE_HOST_SUCCESS = ComponentTestCase(
    name="batch update host success",
    inputs=INPUT_DATA,
    parent_data={"tenant_id": "system", "executor": "executor", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=None,
    execute_call_assertion=None,
    patchers=[
        Patcher(
            target=CC_GET_CLIENT_PATCH,
            return_value=create_mock_cmdb_client_with_hosts(
                [{"bk_host_id": 111, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]
            ),
        ),
        Patcher(
            target=CMDB_GET_CLIENT_PATCH,
            return_value=create_mock_cmdb_client_with_hosts(
                [{"bk_host_id": 111, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]
            ),
        ),
        Patcher(target=VERIFY_HOST_PROPERTY, side_effect=verify_host_property),
        Patcher(target=GET_CLIENT_BY_USER, return_value=BATCH_UPDATE_HOST_SUCCESS_CLIENT),
        Patcher(
            target=CC_GET_HOST_BY_INNERIP_WITH_IPV6,
            return_value={
                "result": True,
                "data": [{"bk_host_id": 111, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}],
            },
        ),
    ],
)

# batch_update_host失败
BATCH_UPDATE_HOST_FAIL = ComponentTestCase(
    name="batch update host success",
    inputs=INPUT_DATA,
    parent_data={"tenant_id": "system", "executor": "executor", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "ex_data": (
                "调用配置平台(CMDB)接口cc.batch_update_host返回失败, error=error, "
                'params={"update":[{"bk_host_id":111,"properties":'
                '{"operator":"admin","bk_bak_operator":"admin","bk_comment":"test"}}]}'
            ),
        },
    ),
    schedule_assertion=None,
    execute_call_assertion=None,
    patchers=[
        Patcher(
            target=CC_GET_CLIENT_PATCH,
            return_value=create_mock_cmdb_client_with_hosts(
                [{"bk_host_id": 111, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]
            ),
        ),
        Patcher(
            target=CMDB_GET_CLIENT_PATCH,
            return_value=create_mock_cmdb_client_with_hosts(
                [{"bk_host_id": 111, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]
            ),
        ),
        Patcher(target=VERIFY_HOST_PROPERTY, side_effect=verify_host_property),
        Patcher(target=GET_CLIENT_BY_USER, return_value=BATCH_UPDATE_HOST_FAIL_CLIENT),
        Patcher(
            target=CC_GET_HOST_BY_INNERIP_WITH_IPV6,
            return_value={
                "result": True,
                "data": [{"bk_host_id": 111, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}],
            },
        ),
    ],
)
