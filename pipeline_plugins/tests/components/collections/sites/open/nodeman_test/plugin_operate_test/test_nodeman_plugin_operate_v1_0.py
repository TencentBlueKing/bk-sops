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
from django.conf import settings
from django.test import TestCase
from mock import MagicMock
from pipeline.component_framework.test import (
    Call,
    CallAssertion,
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    Patcher,
    ScheduleAssertion,
)

from pipeline_plugins.components.collections.sites.open.nodeman.plugin_operate.v1_0 import (
    NodemanPluginOperateComponent,
)


class NodemanPluginOperateComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            OPERATE_SUCCESS_CASE,
            OPERATE_FAIL_CASE,
        ]

    def component_cls(self):
        return NodemanPluginOperateComponent


class MockClient(object):
    def __init__(self, plugin_operate=None, details_return=None, get_job_log_return=None):
        self.plugin_operate = MagicMock(return_value=plugin_operate)
        self.job_details = MagicMock(return_value=details_return)
        self.get_job_log = MagicMock(return_value=get_job_log_return)


# mock path
GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.nodeman.base.BKNodeManClient"
GET_CLIENT_BY_USER_BASE = "pipeline_plugins.components.collections.sites.open.nodeman.base.BKNodeManClient"

HANDLE_API_ERROR = "pipeline_plugins.components.collections.sites.open.nodeman.base.handle_api_error"
GET_HOST_ID_BY_INNER_IP = (
    "pipeline_plugins.components.collections.sites.open.nodeman.ip_v6_base.get_host_id_by_inner_ip"
)

# mock clients
CASE_FAIL_CLIENT = MockClient(
    plugin_operate={"result": False, "code": "500", "message": "fail", "data": {"job_id": "1"}},
    details_return={"result": False, "code": "500", "message": "fail", "data": {}},
)

INSTALL_OR_OPERATE_SUCCESS_CLIENT = MockClient(
    plugin_operate={"result": True, "code": "00", "message": "success", "data": {"plugin": "1"}},
    details_return={
        "result": True,
        "code": "00",
        "message": "success",
        "data": {
            "status": "SUCCESS",
            "statistics": {
                "failed_count": 0,
                "filter_count": 0,
                "running_count": 0,
                "total_count": 1,
                "pending_count": 0,
                "success_count": 1,
            },
            "list": [],
        },
    },
)


DETAILS_FAIL_CLIENT = MockClient(
    plugin_operate={"result": True, "code": "00", "message": "success", "data": {"job_id": "1"}},
    details_return={
        "result": True,
        "code": "00",
        "message": "success",
        "data": {
            "status": "FAILED",
            "statistics": {
                "failed_count": 1,
                "filter_count": 0,
                "running_count": 0,
                "total_count": 1,
                "pending_count": 0,
                "success_count": 0,
            },
            "list": [{"status": "FAILED", "instance_id": "host|instance|host|1.1.1.1-0-0", "inner_ip": "1.1.1.1"}],
        },
    },
    get_job_log_return={
        "message": "",
        "code": 0,
        "data": [
            {
                "status": "FAILED",
                "finish_time": "2020-06-04 06:34:49",
                "step": "安装",
                "start_time": "2020-06-04 06:34:22",
                "log": "install failed",
            }
        ],
        "result": True,
    },
)


OPERATE_SUCCESS_CASE = ComponentTestCase(
    name="nodeman v1.0 operate plugin success case",
    inputs={
        "biz_cc_id": "1",
        "nodeman_plugin_operate": {
            "nodeman_op_type": "MAIN_INSTALL_PLUGIN",
            "nodeman_plugin": "plugin",
            "nodeman_plugin_version": "plugin_version",
            "install_config": ["keep_config"],
        },
        "nodeman_host_info": {
            "nodeman_host_input_type": "host_ip",
            "nodeman_bk_cloud_id": "0",
            "nodeman_host_ip": "1.1.1.1",
        },
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_url": ["{}/#/task-history/1/log/host|instance|host|1".format(settings.BK_NODEMAN_HOST)],
            "job_id": "1",
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        callback_data=None,
        schedule_finished=True,
        outputs={
            "job_url": ["{}/#/task-history/1/log/host|instance|host|1".format(settings.BK_NODEMAN_HOST)],
            "job_id": "1",
            "success_num": 1,
            "fail_num": 0,
        },
    ),
    execute_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.plugin_operate,
            calls=[
                Call(
                    {
                        "job_type": "MAIN_INSTALL_PLUGIN",
                        "bk_biz_id": ["1"],
                        "bk_host_id": [1],
                        "plugin_params": {"name": "plugin", "version": "plugin_version", "keep_config": 1},
                    }
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.job_details, calls=[Call(**{"job_id": "1"})]),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=GET_CLIENT_BY_USER_BASE, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=GET_HOST_ID_BY_INNER_IP, return_value={"1.1.1.1": 1}),
    ],
)

OPERATE_FAIL_CASE = ComponentTestCase(
    name="nodeman v1.0 operate plugin failed case",
    inputs={
        "biz_cc_id": "1",
        "nodeman_plugin_operate": {
            "nodeman_op_type": "MAIN_INSTALL_PLUGIN",
            "nodeman_plugin": "plugin",
            "nodeman_plugin_version": "plugin_version",
            "install_config": ["keep_config"],
        },
        "nodeman_host_info": {
            "nodeman_host_input_type": "host_ip",
            "nodeman_bk_cloud_id": "0",
            "nodeman_host_ip": "1.1.1.1",
        },
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "failed"}),
    schedule_assertion=[],
    execute_call_assertion=[
        CallAssertion(
            func=CASE_FAIL_CLIENT.plugin_operate,
            calls=[
                Call(
                    {
                        "job_type": "MAIN_INSTALL_PLUGIN",
                        "bk_biz_id": ["1"],
                        "bk_host_id": [1],
                        "plugin_params": {"name": "plugin", "version": "plugin_version", "keep_config": 1},
                    }
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CASE_FAIL_CLIENT),
        Patcher(target=GET_CLIENT_BY_USER_BASE, return_value=CASE_FAIL_CLIENT),
        Patcher(target=GET_HOST_ID_BY_INNER_IP, return_value={"1.1.1.1": 1}),
        Patcher(target=HANDLE_API_ERROR, return_value="failed"),
    ],
)
