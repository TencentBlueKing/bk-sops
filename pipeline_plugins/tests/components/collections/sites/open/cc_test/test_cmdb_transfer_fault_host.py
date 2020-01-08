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
    Patcher
)
from pipeline_plugins.components.collections.sites.open.cc import CmdbTransferFaultHostComponent


class CmdbTransferFaultHostComponentTest(TestCase, ComponentTestMixin):

    def cases(self):
        return [
            TRANSFER_SUCCESS_CASE,
            TRANSFER_FAIL_CASE,
            INVALID_IP_CASE
        ]

    def component_cls(self):
        return CmdbTransferFaultHostComponent


class MockClient(object):
    def __init__(self, transfer_host_return=None):
        self.set_bk_api_ver = MagicMock()
        self.cc = MagicMock()
        self.cc.transfer_host_to_faultmodule = MagicMock(return_value=transfer_host_return)


# mock path
GET_CLIENT_BY_USER = 'pipeline_plugins.components.collections.sites.open.cc.get_client_by_user'
GET_IP_BY_REGEX = 'pipeline_plugins.components.utils.common.get_ip_by_regex'
CC_GET_HOST_ID_BY_INNERIP = 'pipeline_plugins.components.collections.sites.open.cc.cc_get_host_id_by_innerip'

# mock client
TRANSFER_SUCCESS_CLIENT = MockClient(
    transfer_host_return={
        "result": True,
        "code": 0,
        "message": "",
        "data": {}
    })

TRANSFER_FAIL_CLIENT = MockClient(
    transfer_host_return={
        "result": False,
        "code": 2,
        "message": "message token",
        "data": {}
    })

TRANSFER_SUCCESS_CASE = ComponentTestCase(
    name='transfer success case',
    inputs={
        'cc_host_ip': '1.1.1.1;2.2.2.2'
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 2,
        'biz_supplier_account': 0
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
        }),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=CC_GET_HOST_ID_BY_INNERIP, calls=[Call('executor_token', 2, ['1.1.1.1', '2.2.2.2'], 0)]),
        CallAssertion(
            func=TRANSFER_SUCCESS_CLIENT.cc.transfer_host_to_faultmodule,
            calls=[Call({
                'bk_biz_id': 2,
                'bk_host_id': [2, 3]
            })])
    ],
    # add patch
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=TRANSFER_SUCCESS_CLIENT),
        Patcher(target=GET_IP_BY_REGEX, return_value=['1.1.1.1', '2.2.2.2']),
        Patcher(target=CC_GET_HOST_ID_BY_INNERIP, return_value={'result': True,
                                                                'data': [2, 3]})]
)

TRANSFER_FAIL_CASE = ComponentTestCase(
    name='transfer fail case',
    inputs={
        'cc_host_ip': '1.1.1.1;2.2.2.2'
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 2,
        'biz_supplier_account': 0
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={'ex_data': u'调用配置平台(CMDB)接口cc.transfer_host_to_fault_module返回失败, '
                            u'params={"bk_biz_id": 2, "bk_host_id": [2, 3]}, error=message token'}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=CC_GET_HOST_ID_BY_INNERIP, calls=[Call('executor_token', 2, ['1.1.1.1', '2.2.2.2'], 0)]),
        CallAssertion(
            func=TRANSFER_FAIL_CLIENT.cc.transfer_host_to_faultmodule,
            calls=[Call({
                'bk_biz_id': 2,
                'bk_host_id': [2, 3]
            })])
    ],
    # add patch
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=TRANSFER_FAIL_CLIENT),
        Patcher(target=GET_IP_BY_REGEX, return_value=['1.1.1.1', '2.2.2.2']),
        Patcher(target=CC_GET_HOST_ID_BY_INNERIP, return_value={'result': True,
                                                                'data': [2, 3]})]
)

INVALID_IP_CASE = ComponentTestCase(
    name='invalid ip case',
    inputs={
        'cc_host_ip': '1.1.1.1;2.2.2.2'
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 2,
        'biz_supplier_account': 0
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            'ex_data': 'invalid ip'
        }),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=CC_GET_HOST_ID_BY_INNERIP, calls=[Call('executor_token', 2, ['1.1.1.1', '2.2.2.2'], 0)]),
    ],
    patchers=[
        Patcher(target=CC_GET_HOST_ID_BY_INNERIP, return_value={'result': False,
                                                                'message': 'invalid ip'}),
    ])
