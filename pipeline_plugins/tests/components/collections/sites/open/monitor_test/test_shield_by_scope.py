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
    Patcher
)
from pipeline_plugins.components.collections.sites.open.monitor import AlarmShieldScopeComponent


class AlarmShieldScopeComponentTest(TestCase, ComponentTestMixin):

    def cases(self):
        return [
            ALTER_BILL_FAIL_CASE,
            ALTER_BILL_SUCCESS_CASE,
        ]

    def component_cls(self):
        return AlarmShieldScopeComponent


class MockClient(object):
    def __init__(self, create_shield_result=None):
        self.monitor = MagicMock()
        self.monitor.create_shield = MagicMock(return_value=create_shield_result)


# mock path
GET_CLIENT_BY_USER = 'pipeline_plugins.components.collections.sites.open.monitor.get_client_by_user'

# mock client
CREATE_SHIELD_FAIL_CLIENT = MockClient(
    create_shield_result={
        'result': False,
        'message': 'create shield fail'
    }
)

CREATE_SHIELD_SUCCESS_CLIENT = MockClient(
    create_shield_result={
        'result': True,
        'data': {
            'id': '1',
        },
        'message': 'success'
    }
)

# test case
ALTER_BILL_FAIL_CASE = ComponentTestCase(
    name='create shield fail case',
    inputs={
        'biz_cc_id': 2,
        'bk_alarm_shield_info': {
            'bk_alarm_shield_scope': 'business',
            'bk_alarm_shield_business': 2,
            'bk_alarm_shield_node': ['module_21', 'module_23'],
            'bk_alarm_shield_IP': '10.0.0.1,10.0.0.2'
        },
        'bk_alarm_shield_target': [1, 2, 3],
        'bk_alarm_shield_begin_time': "2019-11-04 00:00:00",
        'bk_alarm_shield_end_time': "2019-11-05 00:00:00",
    },
    parent_data={
        'executor': 'executor',
        'biz_cc_id': 2,
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={'shield_id': '',
                 'message': '调用蓝鲸监控(BK)接口monitor.create_shield返回失败, '
                            'params={"begin_time":"2019-11-04 00:00:00","bk_biz_id":2,"category":"scope",'
                            '"cycle_config":{"begin_time":"","end_time":"","day_list":[],"week_list":[],"type":1},'
                            '"description":"shield by bk_sops",'
                            '"dimension_config":{"scope_type":"biz","metric_id":[1,2,3]},'
                            '"end_time":"2019-11-05 00:00:00","notice_config":{},'
                            '"shield_notice":false,"source":"bk_sops"}, error=create shield fail'}
    ),
    schedule_assertion=None,
    execute_call_assertion=[CallAssertion(
        func=CREATE_SHIELD_FAIL_CLIENT.monitor.create_shield,
        calls=[Call({'begin_time': "2019-11-04 00:00:00",
                     'bk_biz_id': 2,
                     'category': 'scope',
                     'cycle_config': {'begin_time': "", 'end_time': "", 'day_list': [], 'week_list': [], 'type': 1},
                     'description': "shield by bk_sops",
                     'dimension_config': {'scope_type': "biz", "metric_id": [1, 2, 3]},
                     'end_time': "2019-11-05 00:00:00",
                     'notice_config': {},
                     'shield_notice': False,
                     'source': 'bk_sops'})]
    )],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CREATE_SHIELD_FAIL_CLIENT)
    ]
)

ALTER_BILL_SUCCESS_CASE = ComponentTestCase(
    name='create shield success case',
    inputs={
        'biz_cc_id': 2,
        'bk_alarm_shield_info': {
            'bk_alarm_shield_scope': 'business',
            'bk_alarm_shield_business': 2,
            'bk_alarm_shield_node': ['module_21', 'module_23'],
            'bk_alarm_shield_IP': '10.0.0.1,10.0.0.2'
        },
        'bk_alarm_shield_target': [1, 2, 3],
        'bk_alarm_shield_begin_time': "2019-11-04 00:00:00",
        'bk_alarm_shield_end_time': "2019-11-05 00:00:00",
    },
    parent_data={
        'executor': 'executor',
        'biz_cc_id': 2,
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={'shield_id': '1',
                 'message': 'success'}
    ),
    schedule_assertion=None,
    execute_call_assertion=[CallAssertion(
        func=CREATE_SHIELD_SUCCESS_CLIENT.monitor.create_shield,
        calls=[Call({'begin_time': "2019-11-04 00:00:00",
                     'bk_biz_id': 2,
                     'category': 'scope',
                     'cycle_config': {'begin_time': "", 'end_time': "", 'day_list': [], 'week_list': [], 'type': 1},
                     'description': "shield by bk_sops",
                     'dimension_config': {'scope_type': "biz", "metric_id": [1, 2, 3]},
                     'end_time': "2019-11-05 00:00:00",
                     'notice_config': {},
                     'shield_notice': False,
                     'source': 'bk_sops'})]
    )],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CREATE_SHIELD_SUCCESS_CLIENT)
    ]
)
