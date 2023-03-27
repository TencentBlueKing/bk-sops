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
    Call,
    CallAssertion,
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    ScheduleAssertion,
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.nodeman.create_task.v4_0 import NodemanCreateTaskComponent


class NodemanCreateTaskComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            INSTALL_SUCCESS_CASE,
            REINSTALL_SUCCESS_CASE,
            INSTALL_FAIL_CASE,
            OPERATE_SUCCESS_CASE,
            OPERATE_FAIL_CASE,
            CHOOSABLE_PARAMS_CASE,
            INSTALL_SUCCESS_CASE_WITH_TTJ,
            MULTI_CLOUD_ID_INSTALL_CASE,
            MULTI_CLOUD_ID_OPERATE_CASE,
        ]

    def component_cls(self):
        return NodemanCreateTaskComponent


class MockClient(object):
    def __init__(
        self,
        install_return=None,
        operate_return=None,
        remove_host=None,
        details_return=None,
        get_job_log_return=None,
        get_rsa_public_key_return=None,
    ):
        self.name = "name"
        self.job_install = MagicMock(return_value=install_return)
        self.job_operate = MagicMock(return_value=operate_return)
        self.remove_host = MagicMock(return_value=remove_host)
        self.job_details = MagicMock(return_value=details_return)
        self.get_job_log = MagicMock(return_value=get_job_log_return)
        self.get_rsa_public_key = MagicMock(return_value=get_rsa_public_key_return)


# mock path
GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.nodeman.create_task.v4_0.BKNodeManClient"
BASE_GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.nodeman.base.BKNodeManClient"

HANDLE_API_ERROR = "pipeline_plugins.components.collections.sites.open.nodeman.base.handle_api_error"
GET_BUSINESS_HOST = "pipeline_plugins.components.collections.sites.open.nodeman.create_task.v4_0.get_business_host"
GET_HOST_ID_BY_INNER_IP = "pipeline_plugins.components.collections.sites.open.nodeman.base.get_host_id_by_inner_ip"
ENCRYPT_AUTH_KEY = "pipeline_plugins.components.collections.sites.open.nodeman.create_task.v4_0.encrypt_auth_key"

# mock clients
CASE_FAIL_CLIENT = MockClient(
    install_return={"result": False, "code": "500", "message": "fail", "data": {"job_id": "1"}},
    operate_return={"result": False, "code": "500", "message": "fail", "data": {"job_id": "1"}},
    remove_host={"result": False, "code": "500", "message": "fail", "data": {}},
    details_return={"result": False, "code": "500", "message": "fail", "data": {}},
)

INSTALL_OR_OPERATE_SUCCESS_CLIENT = MockClient(
    install_return={"result": True, "code": "00", "message": "success", "data": {"job_id": "1"}},
    operate_return={"result": True, "code": "00", "message": "success", "data": {"job_id": "1"}},
    remove_host={"result": True, "code": "00", "message": "success", "data": {}},
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
    get_rsa_public_key_return={
        "message": "",
        "code": 0,
        "data": [
            {
                "content": """-----BEGIN PUBLIC KEY-----
                MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlJ/9Fq0LdVzxXga97bk4
                q69cD0ZjcPGbZUZ6NIRNDa+TzDyhoBKs2vsssX2vEoiUe5oHePY/3g49HwXCHyPj
                iidWzRD2VEGqySkq/q4vXYDBZ+Hi6yf+VjdI+aTgcTTGbPk4LEoiZIbZC0GD93R5
                AYkwL3bQ1OXq2+oYatZ0hSQPKeN+1ZT2gAGC4D+bKp5tgXFqu+zVs6/C5FI7kbxP
                UW/XhgQnsrKVrCH60RCPHiXWfn3ENUo4Z3dndcXA31M283Tupp66yJNKb50OynWo
                Px64VRgYWvvssC8qtnUdVejn5/UFArb2ZOqpA7qcpKXjSl1v//Q8udPzSEjoXd4Y
                HwIDAQAB\n-----END PUBLIC KEY-----""",
                "block_size": 245,
                "name": "DEFAULT",
                "description": "默认RSA密钥",
            }
        ],
        "result": True,
        "request_id": "d474b1688d524662b613c76a78310412",
    },
)

GET_JOB_LOG_FAIL_DATA = {
    "status": "FAILED",
    "finish_time": "2020-06-04 06:34:49",
    "step": "安装",
    "start_time": "2020-06-04 06:34:22",
    "log": "install failed",
}

DETAILS_FAIL_CLIENT = MockClient(
    install_return={"result": True, "code": "00", "message": "success", "data": {"job_id": "1"}},
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
    get_rsa_public_key_return={
        "message": "",
        "code": 0,
        "data": [
            {
                "content": """-----BEGIN PUBLIC KEY-----
                MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlJ/9Fq0LdVzxXga97bk4
                q69cD0ZjcPGbZUZ6NIRNDa+TzDyhoBKs2vsssX2vEoiUe5oHePY/3g49HwXCHyPj
                iidWzRD2VEGqySkq/q4vXYDBZ+Hi6yf+VjdI+aTgcTTGbPk4LEoiZIbZC0GD93R5
                AYkwL3bQ1OXq2+oYatZ0hSQPKeN+1ZT2gAGC4D+bKp5tgXFqu+zVs6/C5FI7kbxP
                UW/XhgQnsrKVrCH60RCPHiXWfn3ENUo4Z3dndcXA31M283Tupp66yJNKb50OynWo
                Px64VRgYWvvssC8qtnUdVejn5/UFArb2ZOqpA7qcpKXjSl1v//Q8udPzSEjoXd4Y
                HwIDAQAB\n-----END PUBLIC KEY-----""",
                "block_size": 245,
                "name": "DEFAULT",
                "description": "默认RSA密钥",
            }
        ],
        "result": True,
        "request_id": "d474b1688d524662b613c76a78310412",
    },
)

INSTALL_SUCCESS_CASE = ComponentTestCase(
    name="nodeman v4.0 install task success case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_op_info": {
            "nodeman_op_type": "INSTALL",
            "nodeman_node_type": "AGENT",
            "nodeman_other_hosts": [],
            "nodeman_hosts": [
                {
                    "bk_biz_id": "1",
                    "nodeman_ap_id": "1",
                    "nodeman_bk_cloud_id": "1",
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
    execute_assertion=ExecuteAssertion(success=True, outputs={"job_id": "1"}),
    schedule_assertion=ScheduleAssertion(
        success=True,
        callback_data=None,
        schedule_finished=True,
        outputs={"fail_num": 0, "job_id": "1", "success_num": 1},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.job_install,
            calls=[
                Call(
                    **{
                        "job_type": "INSTALL_AGENT",
                        "is_install_latest_plugins": True,
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
                                "peer_exchange_switch_for_agent": 1,  # 不加速
                                "password": "encrypt_auth_key",
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
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.job_details,
            calls=[Call(**{"job_id": "1"})],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=ENCRYPT_AUTH_KEY, return_value="encrypt_auth_key"),
    ],
)

REINSTALL_SUCCESS_CASE = ComponentTestCase(
    name="nodeman v4.0 reinstall task success case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_op_info": {
            "nodeman_op_type": "REINSTALL",
            "nodeman_node_type": "AGENT",
            "nodeman_hosts": [
                {
                    "bk_biz_id": "1",
                    "nodeman_bk_cloud_id": "1",
                    "nodeman_ap_id": "1",
                    "inner_ip": "1.1.1.1",
                    "os_type": "LINUX",
                    "port": "22",
                    "account": "test",
                    "auth_type": "PASSWORD",
                    "auth_key": "123",
                    "outer_ip": "1.1.1.1",
                    "login_ip": "1.1.1.1",
                    "data_ip": "1.1.1.1",
                },
                {
                    "bk_biz_id": "1",
                    "nodeman_bk_cloud_id": "1",
                    "nodeman_ap_id": "1",
                    "inner_ip": "2.2.2.2,3.3.3.3",
                    "os_type": "LINUX",
                    "port": "22",
                    "account": "test",
                    "auth_type": "PASSWORD",
                    "auth_key": "123",
                    "outer_ip": "4.4.4.4,5.5.5.5",
                    "login_ip": "6.6.6.6,7.7.7.7",
                    "data_ip": "8.8.8.8,9.9.9.9",
                },
            ],
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
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.job_install,
            calls=[
                Call(
                    **{
                        "job_type": "REINSTALL_AGENT",
                        "is_install_latest_plugins": True,
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
                                "peer_exchange_switch_for_agent": 1,  # 不加速
                                "password": "encrypt_auth_key",
                                "outer_ip": "1.1.1.1",
                                "login_ip": "1.1.1.1",
                                "data_ip": "1.1.1.1",
                                "bk_host_id": 1,
                            },
                            {
                                "bk_biz_id": "1",
                                "bk_cloud_id": "1",
                                "inner_ip": "2.2.2.2",
                                "os_type": "LINUX",
                                "port": "22",
                                "account": "test",
                                "auth_type": "PASSWORD",
                                "ap_id": "1",
                                "is_manual": False,  # 不手动操作
                                "peer_exchange_switch_for_agent": 1,  # 不加速
                                "password": "encrypt_auth_key",
                                "outer_ip": "4.4.4.4",
                                "login_ip": "6.6.6.6",
                                "data_ip": "8.8.8.8",
                                "bk_host_id": 2,
                            },
                            {
                                "bk_biz_id": "1",
                                "bk_cloud_id": "1",
                                "inner_ip": "3.3.3.3",
                                "os_type": "LINUX",
                                "port": "22",
                                "account": "test",
                                "auth_type": "PASSWORD",
                                "ap_id": "1",
                                "is_manual": False,  # 不手动操作
                                "peer_exchange_switch_for_agent": 1,  # 不加速
                                "password": "encrypt_auth_key",
                                "outer_ip": "5.5.5.5",
                                "login_ip": "7.7.7.7",
                                "data_ip": "9.9.9.9",
                                "bk_host_id": 3,
                            },
                        ],
                    }
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.job_details,
            calls=[Call(**{"job_id": "1"})],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(
            target=GET_BUSINESS_HOST,
            return_value=[
                {"bk_host_innerip": "1.1.1.1", "bk_host_id": 1},
                {"bk_host_innerip": "2.2.2.2", "bk_host_id": 2},
                {"bk_host_innerip": "3.3.3.3", "bk_host_id": 3},
            ],
        ),
        Patcher(target=ENCRYPT_AUTH_KEY, return_value="encrypt_auth_key"),
    ],
)

INSTALL_FAIL_CASE = ComponentTestCase(
    name="nodeman v4.0 install task failed case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_op_info": {
            "nodeman_op_type": "REINSTALL",
            "nodeman_node_type": "AGENT",
            "nodeman_ip_str": "",
            "nodeman_hosts": [
                {
                    "nodeman_ap_id": "1",
                    "bk_biz_id": "1",
                    "nodeman_bk_cloud_id": "1",
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
    execute_assertion=ExecuteAssertion(success=True, outputs={"job_id": "1"}),
    execute_call_assertion=[
        CallAssertion(
            func=DETAILS_FAIL_CLIENT.job_install,
            calls=[
                Call(
                    **{
                        "job_type": "REINSTALL_AGENT",
                        "is_install_latest_plugins": True,
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
                                "peer_exchange_switch_for_agent": 1,  # 不加速
                                "password": "encrypt_auth_key",
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
            "ex_data": "<br>操作失败主机日志信息：</br><br><b>主机：1.1.1.1</b></br><br>错误日志：</br>安装\ninstall failed",
        },
    ),
    schedule_call_assertion=[
        CallAssertion(
            func=DETAILS_FAIL_CLIENT.job_details,
            calls=[Call(**{"job_id": "1"})],
        ),
        CallAssertion(
            func=DETAILS_FAIL_CLIENT.get_job_log,
            calls=[Call(**{"job_id": "1", "instance_id": "host|instance|host|1.1.1.1-0-0"})],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=DETAILS_FAIL_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=DETAILS_FAIL_CLIENT),
        Patcher(target=GET_BUSINESS_HOST, return_value=[{"bk_host_innerip": "1.1.1.1", "bk_host_id": 1}]),
        Patcher(target=HANDLE_API_ERROR, return_value="failed"),
        Patcher(target=ENCRYPT_AUTH_KEY, return_value="encrypt_auth_key"),
    ],
)

OPERATE_SUCCESS_CASE = ComponentTestCase(
    name="nodeman v4.0 operate task success case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_op_info": {
            "nodeman_node_type": "AGENT",
            "nodeman_op_type": "UPGRADE",
            "nodeman_other_hosts": [{"nodeman_bk_cloud_id": "1", "nodeman_ip_str": "1.1.1.1"}],
            "nodeman_hosts": [],
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
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.job_operate,
            calls=[Call(**{"job_type": "UPGRADE_AGENT", "bk_biz_id": ["1"], "bk_host_id": [1]})],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.job_details,
            calls=[Call(**{"job_id": "1"})],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=GET_HOST_ID_BY_INNER_IP, return_value={"1.1.1.1": 1}),
        Patcher(target=GET_BUSINESS_HOST, return_value=[{"bk_host_innerip": "1.1.1.1", "bk_host_id": 1}]),
    ],
)

OPERATE_FAIL_CASE = ComponentTestCase(
    name="nodeman v4.0 operate task failed case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_node_type": "AGENT",
        "nodeman_op_info": {
            "nodeman_op_type": "UPGRADE",
            "nodeman_node_type": "AGENT",
            "nodeman_other_hosts": [{"nodeman_bk_cloud_id": "1", "nodeman_ip_str": "1.1.1.1"}],
            "nodeman_hosts": [],
        },
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(success=False, outputs={"job_id": "", "ex_data": "failed"}),
    schedule_assertion=[],
    execute_call_assertion=[
        CallAssertion(
            func=CASE_FAIL_CLIENT.job_operate,
            calls=[Call(**{"job_type": "UPGRADE_AGENT", "bk_biz_id": ["1"], "bk_host_id": [1]})],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CASE_FAIL_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=CASE_FAIL_CLIENT),
        Patcher(target=GET_HOST_ID_BY_INNER_IP, return_value={"1.1.1.1": 1}),
        Patcher(target=GET_BUSINESS_HOST, return_value=[{"bk_host_innerip": "1.1.1.1", "bk_host_id": 1}]),
        Patcher(target=HANDLE_API_ERROR, return_value="failed"),
    ],
)

CHOOSABLE_PARAMS_CASE = ComponentTestCase(
    name="nodeman v4.0 choosable params case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_node_type": "AGENT",
        "nodeman_op_info": {
            "nodeman_op_type": "REINSTALL",
            "nodeman_node_type": "AGENT",
            "nodeman_other_hosts": [],
            "nodeman_hosts": [
                {
                    "bk_biz_id": "1",
                    "nodeman_ap_id": "1",
                    "nodeman_bk_cloud_id": "1",
                    "inner_ip": "1.1.1.1,2.2.2.2",
                    "os_type": "LINUX",
                    "port": "22",
                    "account": "test",
                    "auth_type": "PASSWORD",
                    "auth_key": "123",
                    "outer_ip": "3.3.3.3,4.4.4.4",
                    "login_ip": "5.5.5.5,6.6.6.6",
                    "data_ip": "7.7.7.7,8.8.8.8",
                },
                {
                    "bk_biz_id": "1",
                    "nodeman_ap_id": "1",
                    "nodeman_bk_cloud_id": "1",
                    "inner_ip": "127.0.0.1",
                    "os_type": "LINUX",
                    "port": "22",
                    "account": "test",
                    "auth_type": "PASSWORD",
                    "auth_key": "123",
                    "outer_ip": "3.3.3.3",
                    "login_ip": "5.5.5.5",
                    "data_ip": "7.7.7.7",
                },
                {
                    "bk_biz_id": "1",
                    "nodeman_ap_id": "1",
                    "nodeman_bk_cloud_id": "1",
                    "inner_ip": "127.0.0.2",
                    "os_type": "LINUX",
                    "port": "22",
                    "account": "test",
                    "auth_type": "PASSWORD",
                    "auth_key": "123",
                    "outer_ip": "",
                    "login_ip": "",
                    "data_ip": "7.7.7.7",
                },
            ],
        },
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(success=True, outputs={"job_id": "1"}),
    execute_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.job_install,
            calls=[
                Call(
                    **{
                        "job_type": "REINSTALL_AGENT",
                        "is_install_latest_plugins": True,
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
                                "peer_exchange_switch_for_agent": 1,  # 不加速
                                "password": "encrypt_auth_key",
                                "outer_ip": "3.3.3.3",
                                "login_ip": "5.5.5.5",
                                "data_ip": "7.7.7.7",
                                "bk_host_id": 1,
                            },
                            {
                                "bk_biz_id": "1",
                                "bk_cloud_id": "1",
                                "inner_ip": "2.2.2.2",
                                "os_type": "LINUX",
                                "port": "22",
                                "account": "test",
                                "auth_type": "PASSWORD",
                                "ap_id": "1",
                                "is_manual": False,  # 不手动操作
                                "peer_exchange_switch_for_agent": 1,  # 不加速
                                "password": "encrypt_auth_key",
                                "outer_ip": "4.4.4.4",
                                "login_ip": "6.6.6.6",
                                "data_ip": "8.8.8.8",
                                "bk_host_id": 1,
                            },
                            {
                                "bk_biz_id": "1",
                                "bk_cloud_id": "1",
                                "inner_ip": "127.0.0.1",
                                "os_type": "LINUX",
                                "port": "22",
                                "account": "test",
                                "auth_type": "PASSWORD",
                                "ap_id": "1",
                                "is_manual": False,  # 不手动操作
                                "peer_exchange_switch_for_agent": 1,  # 不加速
                                "password": "encrypt_auth_key",
                                "outer_ip": "3.3.3.3",
                                "login_ip": "5.5.5.5",
                                "data_ip": "7.7.7.7",
                                "bk_host_id": 1,
                            },
                            {
                                "bk_biz_id": "1",
                                "bk_cloud_id": "1",
                                "inner_ip": "127.0.0.2",
                                "os_type": "LINUX",
                                "port": "22",
                                "account": "test",
                                "auth_type": "PASSWORD",
                                "ap_id": "1",
                                "is_manual": False,  # 不手动操作
                                "peer_exchange_switch_for_agent": 1,  # 不加速
                                "password": "encrypt_auth_key",
                                "data_ip": "7.7.7.7",
                                "bk_host_id": 1,
                            },
                        ],
                    }
                )
            ],
        ),
    ],
    schedule_assertion=[],
    schedule_call_assertion=[],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(
            target=GET_BUSINESS_HOST,
            return_value=[
                {"bk_host_innerip": "1.1.1.1", "bk_host_id": 1},
                {"bk_host_innerip": "2.2.2.2", "bk_host_id": 1},
                {"bk_host_innerip": "127.0.0.1", "bk_host_id": 1},
                {"bk_host_innerip": "127.0.0.2", "bk_host_id": 1},
            ],
        ),
        Patcher(target=ENCRYPT_AUTH_KEY, return_value="encrypt_auth_key"),
    ],
)

INSTALL_SUCCESS_CASE_WITH_TTJ = ComponentTestCase(
    name="nodeman v4.0 install task with tjj success case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_node_type": "AGENT",
        "nodeman_ticket": {"nodeman_tjj_ticket": "xxxxx"},
        "nodeman_op_info": {
            "nodeman_op_type": "INSTALL",
            "nodeman_node_type": "AGENT",
            "nodeman_ip_str": "",
            "nodeman_hosts": [
                {
                    "bk_biz_id": "1",
                    "nodeman_ap_id": "1",
                    "nodeman_bk_cloud_id": "1",
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
    execute_assertion=ExecuteAssertion(success=True, outputs={"job_id": "1"}),
    schedule_assertion=ScheduleAssertion(
        success=True,
        callback_data=None,
        schedule_finished=True,
        outputs={"fail_num": 0, "job_id": "1", "success_num": 1},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.job_install,
            calls=[
                Call(
                    **{
                        "job_type": "INSTALL_AGENT",
                        "is_install_latest_plugins": True,
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
                                "peer_exchange_switch_for_agent": 1,  # 不加速
                                "password": "encrypt_auth_key",
                                "outer_ip": "1.1.1.1",
                                "login_ip": "1.1.1.1",
                                "data_ip": "1.1.1.1",
                            }
                        ],
                        "tcoa_ticket": "xxxxx",
                    }
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.job_details,
            calls=[Call(**{"job_id": "1"})],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=ENCRYPT_AUTH_KEY, return_value="encrypt_auth_key"),
    ],
)

MULTI_CLOUD_ID_OPERATE_CASE = ComponentTestCase(
    name="nodeman v4.0 multi cloud_id operate task success case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_op_info": {
            "nodeman_op_type": "UPGRADE",
            "nodeman_node_type": "AGENT",
            "nodeman_other_hosts": [
                {"nodeman_bk_cloud_id": "1", "nodeman_ip_str": "1.1.1.1"},
                {"nodeman_bk_cloud_id": "2", "nodeman_ip_str": "2.2.2.2"},
            ],
            "nodeman_hosts": [],
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
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.job_operate,
            calls=[Call(**{"job_type": "UPGRADE_AGENT", "bk_biz_id": ["1"], "bk_host_id": [1, 2]})],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.job_details,
            calls=[Call(**{"job_id": "1"})],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=GET_HOST_ID_BY_INNER_IP, side_effect=[{"1.1.1.1": 1}, {"2.2.2.2": 2}]),
        Patcher(
            target=GET_BUSINESS_HOST,
            side_effect=[
                {"bk_host_innerip": "1.1.1.1", "bk_host_id": "1"},
                {"bk_host_innerip": "2.2.2.2", "bk_host_id": "1"},
            ],
        ),
    ],
)

MULTI_CLOUD_ID_INSTALL_CASE = ComponentTestCase(
    name="nodeman v4.0 install task success case",
    inputs={
        "bk_biz_id": "1",
        "nodeman_node_type": "AGENT",
        "nodeman_op_info": {
            "nodeman_op_type": "INSTALL",
            "nodeman_node_type": "AGENT",
            "nodeman_other_hosts": [],
            "nodeman_hosts": [
                {
                    "nodeman_ap_id": "1",
                    "nodeman_bk_cloud_id": "1",
                    "inner_ip": "1.1.1.1",
                    "os_type": "LINUX",
                    "port": "22",
                    "account": "test",
                    "auth_type": "PASSWORD",
                    "auth_key": "123",
                    "outer_ip": "1.1.1.1",
                    "login_ip": "1.1.1.1",
                    "data_ip": "1.1.1.1",
                },
                {
                    "nodeman_ap_id": "2",
                    "nodeman_bk_cloud_id": "2",
                    "inner_ip": "2.2.2.2",
                    "os_type": "LINUX",
                    "port": "22",
                    "account": "test",
                    "auth_type": "PASSWORD",
                    "auth_key": "123",
                    "outer_ip": "2.2.2.2",
                    "login_ip": "2.2.2.2",
                    "data_ip": "2.2.2.2",
                },
            ],
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
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.job_install,
            calls=[
                Call(
                    **{
                        "job_type": "INSTALL_AGENT",
                        "is_install_latest_plugins": True,
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
                                "peer_exchange_switch_for_agent": 1,  # 不加速
                                "password": "encrypt_auth_key",
                                "outer_ip": "1.1.1.1",
                                "login_ip": "1.1.1.1",
                                "data_ip": "1.1.1.1",
                            },
                            {
                                "bk_biz_id": "1",
                                "bk_cloud_id": "2",
                                "inner_ip": "2.2.2.2",
                                "os_type": "LINUX",
                                "port": "22",
                                "account": "test",
                                "auth_type": "PASSWORD",
                                "ap_id": "2",
                                "is_manual": False,  # 不手动操作
                                "peer_exchange_switch_for_agent": 1,  # 不加速
                                "password": "encrypt_auth_key",
                                "outer_ip": "2.2.2.2",
                                "login_ip": "2.2.2.2",
                                "data_ip": "2.2.2.2",
                            },
                        ],
                    }
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=INSTALL_OR_OPERATE_SUCCESS_CLIENT.job_details,
            calls=[Call(**{"job_id": "1"})],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=INSTALL_OR_OPERATE_SUCCESS_CLIENT),
        Patcher(target=ENCRYPT_AUTH_KEY, return_value="encrypt_auth_key"),
    ],
)
