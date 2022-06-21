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
    ComponentTestMixin,
    ComponentTestCase,
    CallAssertion,
    ExecuteAssertion,
    Call,
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.monitor.alarm_shield_disable.v1_0 import (
    MonitorAlarmShieldDisableComponent,
)


class MonitorAlarmShieldDisableComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            DISABLE_SHIELD_FAIL_CASE,
            DISABLE_SHIELD_SUCCESS_CASE,
        ]

    def component_cls(self):
        return MonitorAlarmShieldDisableComponent


class MockClient(object):
    def __init__(self, disable_shield_result=None):
        self.disable_shield = MagicMock(return_value=disable_shield_result)

    def __call__(self, *args, **kwargs):
        return self


# mock path
MONITOR_CLIENT = "pipeline_plugins.components.collections.sites.open.monitor.alarm_shield_disable.v1_0.BKMonitorClient"

# mock client
DISABLE_SHIELD_FAIL_CLIENT = MockClient(
    disable_shield_result={"result": False, "message": "disable shield fail", "code": 500}
)

DISABLE_SHIELD_SUCCESS_CLIENT = MockClient(
    disable_shield_result={"result": True, "data": {"id": "1"}, "message": "success", "code": 200}
)

# test case
DISABLE_SHIELD_FAIL_CASE = ComponentTestCase(
    name="disable shield fail case",
    inputs={"bk_alarm_shield_id_input": "1"},
    parent_data={"executor": "executor", "biz_cc_id": 2},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "data": {
                "result": "调用监控平台(Monitor)接口monitor.disable_shield返回失败, " 'params={"id":"1"}, error=disable shield fail'
            },
            "status_code": 500,
        },
    ),
    schedule_assertion=None,
    execute_call_assertion=[CallAssertion(func=DISABLE_SHIELD_FAIL_CLIENT.disable_shield, calls=[Call(**{"id": "1"})])],
    patchers=[Patcher(target=MONITOR_CLIENT, return_value=DISABLE_SHIELD_FAIL_CLIENT)],
)

DISABLE_SHIELD_SUCCESS_CASE = ComponentTestCase(
    name="disable shield success case",
    inputs={"bk_alarm_shield_id_input": "1"},
    parent_data={"executor": "executor", "biz_cc_id": 2},
    execute_assertion=ExecuteAssertion(success=True, outputs={"data": {"result": {"id": "1"}}, "status_code": 200}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=DISABLE_SHIELD_SUCCESS_CLIENT.disable_shield, calls=[Call(**{"id": "1"})])
    ],
    patchers=[Patcher(target=MONITOR_CLIENT, return_value=DISABLE_SHIELD_SUCCESS_CLIENT)],
)
