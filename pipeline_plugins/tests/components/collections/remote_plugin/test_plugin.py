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
    ExecuteAssertion,
    ScheduleAssertion,
    Patcher,
)
from pipeline_plugins.components.collections.remote_plugin.v1_0_0 import RemotePluginComponent, State


class RemotePluginComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        # return the component class which should be tested
        return RemotePluginComponent

    def cases(self):
        # return your component test cases here
        return [
            EXECUTE_SUCCESS_CASE,
            EXECUTE_AND_SCHEDULE_SUCCESS_CASE,
            EXECUTE_FAIL_CASE,
            INVOKE_API_FAIL_CASE,
            SCHEDULE_FAIL_CASE,
        ]


class MockPluginClient(object):
    def __init__(self, invoke_result=None, get_schedule_result=None, get_detail_result=None):
        self.invoke = MagicMock(return_value=invoke_result)
        self.get_schedule = MagicMock(return_value=get_schedule_result)
        self.get_detail = MagicMock(return_value=get_detail_result)


# mock path
PLUGIN_SERVICE_API_CLIENT = "pipeline_plugins.components.collections.remote_plugin.v1_0_0.PluginServiceApiClient"

# parent_data
PARENT_DATA = {"executor": "executor", "biz_cc_id": 1}

# INPUTS
BASE_INPUTS = {"plugin_code": "code", "plugin_version": "version"}

# OUTPUTS
BASE_OUTPUTS = {"output": "output"}
INVOKE_FAIL_EX_DATA_OUTPUTS = {"ex_data": "[remote plugin service invoke] error: ex_data, trace_id: trace_id"}
STATE_FAIL_EX_DATA_OUTPUTS = {"ex_data": "state fail"}
SCHEDULE_FAIL_EX_DATA_OUTPUTS = {"ex_data": "please check the logs for the reason of task failure."}
TRACE_ID_OUTPUTS = {"trace_id": "trace_id"}

# mock clients
ONLY_EXECUTE_AND_SUCCESS_CLIENT = MockPluginClient(
    invoke_result=(True, {**TRACE_ID_OUTPUTS, "state": State.SUCCESS, "outputs": BASE_OUTPUTS}),
    get_detail_result={"result": True, "data": {"context_inputs": {"properties": {}}}},
)

EXECUTE_AND_SCHEDULE_SUCCESS_CLIENT = MockPluginClient(
    invoke_result=(True, {**TRACE_ID_OUTPUTS, "state": State.POLL, "outputs": {}}),
    get_schedule_result=(True, {"state": State.SUCCESS, "outputs": BASE_OUTPUTS}),
    get_detail_result={"result": True, "data": {"context_inputs": {"properties": {}}}},
)

EXECUTE_AND_SCHEDULE_SUCCESS_CALLBACK_CLIENT = MockPluginClient(
    invoke_result=(True, {**TRACE_ID_OUTPUTS, "state": State.CALLBACK, "outputs": {}}),
    get_schedule_result=(True, {"state": State.SUCCESS, "outputs": BASE_OUTPUTS}),
    get_detail_result={"result": True, "data": {"context_inputs": {"properties": {}}}},
)

INVOKE_API_FAIL_CLIENT = MockPluginClient(
    invoke_result=(False, {**TRACE_ID_OUTPUTS, "message": "ex_data"}),
    get_detail_result={"result": True, "data": {"context_inputs": {"properties": {}}}},
)

EXECUTE_FAIL_CLIENT = MockPluginClient(
    invoke_result=(True, {**TRACE_ID_OUTPUTS, "state": State.FAIL, "err": "state fail"}),
    get_detail_result={"result": True, "data": {"context_inputs": {"properties": {}}}},
)

SCHEDULE_FAIL_CLIENT = MockPluginClient(
    invoke_result=(True, {**TRACE_ID_OUTPUTS, "state": State.POLL, "outputs": {}}),
    get_schedule_result=(True, {"state": State.FAIL, "outputs": BASE_OUTPUTS}),
    get_detail_result={"result": True, "data": {"context_inputs": {"properties": {}}}},
)

# only execute success
EXECUTE_SUCCESS_CASE = ComponentTestCase(
    name="Only need execute and success case",
    inputs=BASE_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs={**TRACE_ID_OUTPUTS, **BASE_OUTPUTS}),
    schedule_assertion=None,
    patchers=[Patcher(target=PLUGIN_SERVICE_API_CLIENT, return_value=ONLY_EXECUTE_AND_SUCCESS_CLIENT)],
)

# both execute and schedule success
EXECUTE_AND_SCHEDULE_SUCCESS_CASE = ComponentTestCase(
    name="Both execute and schedule success case",
    inputs=BASE_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs={**TRACE_ID_OUTPUTS}),
    schedule_assertion=ScheduleAssertion(
        success=True, outputs={**TRACE_ID_OUTPUTS, **BASE_OUTPUTS}, callback_data={}, schedule_finished=True
    ),
    patchers=[Patcher(target=PLUGIN_SERVICE_API_CLIENT, return_value=EXECUTE_AND_SCHEDULE_SUCCESS_CLIENT)],
)

# execute fail because invoke api fail
INVOKE_API_FAIL_CASE = ComponentTestCase(
    name="execute fail because invoke api fail",
    inputs=BASE_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=False, outputs={**INVOKE_FAIL_EX_DATA_OUTPUTS}),
    schedule_assertion=None,
    patchers=[Patcher(target=PLUGIN_SERVICE_API_CLIENT, return_value=INVOKE_API_FAIL_CLIENT)],
)

# execute fail because state fail
EXECUTE_FAIL_CASE = ComponentTestCase(
    name="execute fail because state fail",
    inputs=BASE_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=False, outputs={**TRACE_ID_OUTPUTS, **STATE_FAIL_EX_DATA_OUTPUTS}),
    schedule_assertion=None,
    patchers=[Patcher(target=PLUGIN_SERVICE_API_CLIENT, return_value=EXECUTE_FAIL_CLIENT)],
)

# schedule fail
SCHEDULE_FAIL_CASE = ComponentTestCase(
    name="schedule fail",
    inputs=BASE_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs={**TRACE_ID_OUTPUTS}),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={**TRACE_ID_OUTPUTS, **SCHEDULE_FAIL_EX_DATA_OUTPUTS, **BASE_OUTPUTS},
        callback_data={},
    ),
    patchers=[Patcher(target=PLUGIN_SERVICE_API_CLIENT, return_value=SCHEDULE_FAIL_CLIENT)],
)

# [plugin callback]both execute and schedule success
EXECUTE_AND_SCHEDULE_SUCCESS_CASE = ComponentTestCase(
    name="[plugin callback]both execute and schedule success",
    inputs=BASE_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs={**TRACE_ID_OUTPUTS}),
    schedule_assertion=ScheduleAssertion(
        success=True, outputs={**TRACE_ID_OUTPUTS, **BASE_OUTPUTS}, callback_data={}, schedule_finished=True
    ),
    patchers=[Patcher(target=PLUGIN_SERVICE_API_CLIENT, return_value=EXECUTE_AND_SCHEDULE_SUCCESS_CALLBACK_CLIENT)],
)
