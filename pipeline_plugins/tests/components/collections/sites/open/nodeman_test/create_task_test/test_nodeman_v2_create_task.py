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

import ujson as json

from django.test import TestCase
from mock import MagicMock

from pipeline.component_framework.test import (
    Call,
    CallAssertion,
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    ScheduleAssertion,
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.nodeman.create_task.v2_0 import NodemanCreateTaskComponent


class NodemanCreateTaskComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            INSTALL_SUCCESS_CASE,
            REINSTALL_SUCCESS_CASE,
            INSTALL_FAIL_CASE,
            OPERATE_SUCCESS_CASE,
            OPERATE_FAIL_CASE,
            REMOVE_SUCCESS_CASE,
        ]

    def component_cls(self):
        return NodemanCreateTaskComponent


class MockClient(object):
    def __init__(self,
                 install_return=None,
                 operate_return=None,
                 remove_host=None,
                 details_return=None,
                 get_job_log_return=None):
        self.name = "name"
        self.nodeman = MagicMock()
        self.nodeman.job_install = MagicMock(return_value=install_return)
        self.nodeman.job_operate = MagicMock(return_value=operate_return)
        self.nodeman.job_operate = MagicMock(return_value=operate_return)
        self.nodeman.remove_host = MagicMock(return_value=remove_host)
        self.nodeman.job_details = MagicMock(return_value=details_return)
        self.nodeman.get_job_log = MagicMock(return_value=get_job_log_return)


# mock path
GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.nodeman.create_task.v2_0.get_client_by_user"
)

HANDLE_API_ERROR = "pipeline_plugins.components.collections.sites.open.nodeman.create_task.v2_0.handle_api_error"
GET_HOST_ID_BY_INNER_IP = \
    "pipeline_plugins.components.collections.sites.open.nodeman.create_task.v2_0.get_host_id_by_inner_ip"

# mock clients
CASE_FAIL_CLIENT = MockClient(
    install_return={
        "result": False,
        "code": "500",
        "message": "fail",
        "data": {"job_id": "1"},
    },
    operate_return={
        "result": False,
        "code": "500",
        "message": "fail",
        "data": {"job_id": "1"},
    },
    remove_host={"result": False, "code": "500", "message": "fail", "data": {}},
    details_return={"result": False, "code": "500", "message": "fail", "data": {}},
)

INSTALL_OR_OPERATE_SUCCESS_CLIENT = MockClient(
    install_return={
        "result": True,
        "code": "00",
        "message": "success",
        "data": {"job_id": "1"},
    },
    operate_return={
        "result": True,
        "code": "00",
        "message": "success",
        "data": {"job_id": "1"},
    },
    remove_host={
        "result": True,
        "code": "00",
        "message": "success",
        "data": {},
    },
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
                "success_count": 1
            },
            "list": [],
        },

    },
)

GET_JOB_LOG_FAIL_DATA = {
    "status": "FAILED",
    "finish_time": "2020-06-04 06:34:49",
    "step": "安装",
    "start_time": "2020-06-04 06:34:22",
    "log": "install failed"
}

DETAILS_FAIL_CLIENT = MockClient(
    install_return={
        "result": True,
        "code": "00",
        "message": "success",
        "data": {"job_id": "1"},
    },
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
                "success_count": 0
            },
            "list": [
                {
                    "status": "FAILED",
                    "instance_id": "host|instance|host|1.1.1.1-0-0",
                    "inner_ip": "1.1.1.1"
                }],
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
                "log": "install failed"
            }
        ],
        "result": True,
    }
)

INSTALL_SUCCESS_CASE = ComponentTestCase(
    name="nodeman v2.0 install task success case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_op_target": {
            "nodeman_bk_cloud_id": "1",
            "nodeman_node_type": "AGENT",
        },
        "nodeman_op_info": {
            "nodeman_ap_id": "1",
            "nodeman_op_type": "INSTALL",
            "nodeman_ip_str": "",
            "nodeman_hosts": [
                {
                    "bk_biz_id": "1",
                    "bk_cloud_id": "1",
                    "inner_ip": "1.1.1.1",
                    "os_type": "LINUX",
                    "port": "22",
                    "account": "test",
                    "auth_type": "PASSWORD",
                    "auth_key": "123",
                    "outer_ip": "1.1.1.1",
                    "login_ip": "1.1.1.1",
                    "data_ip": "1.1.1.1",
                }
            ],
        }
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(success=True, outputs={"job_id": "1"}),
    schedule_assertion=ScheduleAssertion(
        success=True,
        callback_data=None,
        schedule_finished=True,
        outputs={"fail_num": 0, "job_id": "1", "success_num": 1},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.nodeman.job_install,
            calls=[
                Call(
                    {
                        "job_type": "INSTALL_AGENT",
                        "hosts": [
                            {
                                "bk_biz_id": "1",
                                "bk_cloud_id": "1",
                                "inner_ip": "1.1.1.1",
                                "os_type": "LINUX",
                                "port": "22",
                                "account": "test",
                                "auth_type": "PASSWORD",
                                "ap_id": "1",
                                "is_manual": False,  # 不手动操作
                                "peer_exchange_switch_for_agent": 0,  # 不加速
                                "password": "123",
                                "outer_ip": "1.1.1.1",
                                "login_ip": "1.1.1.1",
                                "data_ip": "1.1.1.1",
                            }
                        ],
                    }
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.nodeman.job_details,
            calls=[Call({"job_id": "1"})],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
    ],

)

REINSTALL_SUCCESS_CASE = ComponentTestCase(
    name="nodeman v2.0 reinstall task success case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_op_target": {
            "nodeman_bk_cloud_id": "1",
            "nodeman_node_type": "AGENT",
            "nodeman_ap_id": "1"
        },
        "nodeman_op_info": {
            "nodeman_ap_id": "1",
            "nodeman_op_type": "REINSTALL",
            "nodeman_ip_str": "",
            "nodeman_hosts": [
                {
                    "bk_biz_id": "1",
                    "bk_cloud_id": "1",
                    "inner_ip": "1.1.1.1",
                    "os_type": "LINUX",
                    "port": "22",
                    "account": "test",
                    "auth_type": "PASSWORD",
                    "auth_key": "123",
                    "outer_ip": "1.1.1.1",
                    "login_ip": "1.1.1.1",
                    "data_ip": "1.1.1.1",
                }
            ], }
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(success=True, outputs={"job_id": "1"}),
    schedule_assertion=ScheduleAssertion(
        success=True,
        callback_data=None,
        schedule_finished=True,
        outputs={"fail_num": 0, "job_id": "1", "success_num": 1},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.nodeman.job_install,
            calls=[
                Call(
                    {
                        "job_type": "REINSTALL_AGENT",
                        "hosts": [
                            {
                                "bk_biz_id": "1",
                                "bk_cloud_id": "1",
                                "inner_ip": "1.1.1.1",
                                "os_type": "LINUX",
                                "port": "22",
                                "account": "test",
                                "auth_type": "PASSWORD",
                                "ap_id": "1",
                                "is_manual": False,  # 不手动操作
                                "peer_exchange_switch_for_agent": 0,  # 不加速
                                "password": "123",
                                "outer_ip": "1.1.1.1",
                                "login_ip": "1.1.1.1",
                                "data_ip": "1.1.1.1",
                                "bk_host_id": 1,
                            }
                        ],
                    }
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.nodeman.job_details,
            calls=[Call({"job_id": "1"})],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=GET_HOST_ID_BY_INNER_IP, return_value=[1]),
    ],

)

INSTALL_FAIL_CASE = ComponentTestCase(
    name="nodeman v2.0 install task failed case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_op_target": {
            "nodeman_node_type": "AGENT",
            "nodeman_bk_cloud_id": "1",
        },
        "nodeman_op_info": {
            "nodeman_ap_id": "1",
            "nodeman_op_type": "REINSTALL",
            "nodeman_ip_str": "",
            "nodeman_hosts": [
                {
                    "bk_biz_id": "1",
                    "bk_cloud_id": "1",
                    "inner_ip": "1.1.1.1",
                    "os_type": "LINUX",
                    "port": "22",
                    "account": "test",
                    "auth_type": "PASSWORD",
                    "auth_key": "123",
                    "outer_ip": "1.1.1.1",
                    "login_ip": "1.1.1.1",
                    "data_ip": "1.1.1.1",
                }
            ],
        },

    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(success=True, outputs={'job_id': "1"}),
    execute_call_assertion=[
        CallAssertion(
            func=DETAILS_FAIL_CLIENT.nodeman.job_install,
            calls=[
                Call(
                    {
                        "job_type": "REINSTALL_AGENT",
                        "hosts": [
                            {
                                "bk_biz_id": "1",
                                "bk_cloud_id": "1",
                                "inner_ip": "1.1.1.1",
                                "os_type": "LINUX",
                                "port": "22",
                                "account": "test",
                                "auth_type": "PASSWORD",
                                "ap_id": "1",
                                "is_manual": False,  # 不手动操作
                                "peer_exchange_switch_for_agent": 0,  # 不加速
                                "password": "123",
                                "outer_ip": "1.1.1.1",
                                "login_ip": "1.1.1.1",
                                "data_ip": "1.1.1.1",
                                "bk_host_id": 1,
                            }
                        ],
                    }
                )
            ],
        ),
    ],
    schedule_assertion=ScheduleAssertion(
        success=False,
        callback_data=None,
        schedule_finished=True,
        outputs={
            "job_id": "1",
            "success_num": 0,
            "fail_num": 1,
            "ex_data": "<br>日志信息为：</br><br><b>主机：{fail_host}</b></br><br>日志：</br>{log_info}".format(
                fail_host="1.1.1.1", log_info=json.dumps(GET_JOB_LOG_FAIL_DATA, ensure_ascii=False))
        },
    ),
    schedule_call_assertion=[
        CallAssertion(
            func=DETAILS_FAIL_CLIENT.nodeman.job_details,
            calls=[Call({"job_id": "1"})],
        ),
        CallAssertion(
            func=DETAILS_FAIL_CLIENT.nodeman.get_job_log,
            calls=[Call({
                "job_id": "1",
                "instance_id": "host|instance|host|1.1.1.1-0-0",
            })],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=DETAILS_FAIL_CLIENT),
        Patcher(target=GET_HOST_ID_BY_INNER_IP, return_value=[1]),
        Patcher(target=HANDLE_API_ERROR, return_value="failed"),
    ],

)

OPERATE_SUCCESS_CASE = ComponentTestCase(
    name="nodeman v2.0 operate task success case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_op_target": {
            "nodeman_node_type": "AGENT",
            "nodeman_bk_cloud_id": "1",
        },
        "nodeman_op_info": {
            "nodeman_ap_id": "1",
            "nodeman_op_type": "UPGRADE",
            "nodeman_ip_str": "1.1.1.1",
            "nodeman_hosts": []
        },

    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(success=True, outputs={"job_id": "1"}),
    schedule_assertion=ScheduleAssertion(
        success=True,
        callback_data=None,
        schedule_finished=True,
        outputs={"fail_num": 0, "job_id": "1", "success_num": 1},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.nodeman.job_operate,
            calls=[
                Call(
                    {
                        "job_type": "UPGRADE_AGENT",
                        "bk_biz_id": ["1"],
                        "bk_host_id": [1],
                    }
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.nodeman.job_details,
            calls=[Call({"job_id": "1"})],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=GET_HOST_ID_BY_INNER_IP, return_value=[1]),
    ],

)

OPERATE_FAIL_CASE = ComponentTestCase(
    name="nodeman v2.0 operate task failed case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_op_target": {
            "nodeman_node_type": "AGENT",
            "nodeman_bk_cloud_id": "1",
        },
        "nodeman_op_info": {
            "nodeman_ap_id": "1",
            "nodeman_op_type": "UPGRADE",
            "nodeman_ip_str": "1.1.1.1",
            "nodeman_hosts": []
        },

    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(success=False, outputs={'job_id': '', "ex_data": "failed"}),
    schedule_assertion=[],
    execute_call_assertion=[
        CallAssertion(
            func=CASE_FAIL_CLIENT.nodeman.job_operate,
            calls=[
                Call(
                    {
                        "job_type": "UPGRADE_AGENT",
                        "bk_biz_id": ["1"],
                        "bk_host_id": [1],
                    }
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CASE_FAIL_CLIENT),
        Patcher(target=GET_HOST_ID_BY_INNER_IP, return_value=[1]),
        Patcher(target=HANDLE_API_ERROR, return_value="failed"),
    ],

)
REMOVE_SUCCESS_CASE = ComponentTestCase(
    name="nodeman v2.0 remove host task success case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_op_target": {
            "nodeman_node_type": "AGENT",
            "nodeman_bk_cloud_id": "1",
        },
        "nodeman_op_info": {
            "nodeman_ap_id": "1",
            "nodeman_op_type": "REMOVE",
            "nodeman_ip_str": "1.1.1.1",
            "nodeman_hosts": []
        },

    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(success=True, outputs={"job_id": None}),
    schedule_assertion=ScheduleAssertion(
        success=True,
        callback_data=None,
        schedule_finished=True,
        outputs={"job_id": None},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.nodeman.remove_host,
            calls=[
                Call(
                    {
                        "bk_biz_id": ["1"],
                        "bk_host_id": [1],
                        "is_proxy": False
                    }
                )
            ],
        ),
    ],
    schedule_call_assertion=[],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=GET_HOST_ID_BY_INNER_IP, return_value=[1]),
    ],

)
