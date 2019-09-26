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

from pipeline.component_framework.test import (Call, CallAssertion,
                                               ComponentTestCase,
                                               ComponentTestMixin,
                                               ExecuteAssertion, Patcher)
from pipeline_plugins.components.collections.sites.open.nodeman import NodemanCreateTaskComponent


class NodemanCreateTaskComponentTest(TestCase, ComponentTestMixin):

    def cases(self):
        return [
            CREATE_TASK_SUCCESS_CASE,
            CREATE_TASK_FAIL_CASE
        ]

    def component_cls(self):
        return NodemanCreateTaskComponent


class MockClient(object):
    def __init__(self, create_task_return):
        self.name = 'name'
        self.nodeman = MagicMock()
        self.nodeman.create_task = MagicMock(return_value=create_task_return)


# mock path
GET_CLIENT_BY_USER = 'pipeline_plugins.components.collections.sites.open.nodeman.get_client_by_user'
NODEMAN_RSA_ENCRYPT = 'pipeline_plugins.components.collections.sites.open.nodeman.nodeman_rsa_encrypt'

# mock clients
CREATE_TASK_FAIL_CLIENT = MockClient(
    create_task_return={
        'result': False,
        'code': "500",
        'message': 'fail',
        'data': {
            'hosts': [{
                'job_id': "1"
            }]
        }
    }
)
CREATE_TASK_SUCCESS_CLIENT = MockClient(
    create_task_return={
        'result': True,
        'code': "00",
        'message': 'success',
        'data': {
            'hosts': [{
                'job_id': "1"
            }]
        }
    }
)

CREATE_TASK_SUCCESS_CASE = ComponentTestCase(
    name='nodeman create task success case',
    inputs={
        'biz_cc_id': '1',
        'nodeman_bk_cloud_id': '1',
        'nodeman_node_type': 'AGENT',
        'nodeman_op_type': 'INSTALL',
        'nodeman_hosts': [
            {
                'conn_ips': '1.1.1.1',
                'login_ip': '1.1.1.1',
                'data_ip': '1.1.1.1',
                'cascade_ip': '1.1.1.1',
                'os_type': 'LINUX',
                'has_cygwin': False,
                'port': '22',
                'account': 'test',
                'auth_type': 'PASSWORD',
                'password': '123',
                'key': ''
            }
        ]
    },
    parent_data={
        'executor': 'tester',
        'biz_cc_id': "1"
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={'job_id': '1'}
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CREATE_TASK_SUCCESS_CLIENT.nodeman.create_task,
            calls=[Call({
                'bk_biz_id': '1',
                'bk_cloud_id': '1',
                'node_type': 'AGENT',
                'op_type': 'INSTALL',
                'creator': 'tester',
                'hosts': [
                    {
                        'conn_ips': '1.1.1.1',
                        'login_ip': '1.1.1.1',
                        'data_ip': '1.1.1.1',
                        'cascade_ip': '1.1.1.1',
                        'os_type': 'LINUX',
                        'has_cygwin': False,
                        'port': '22',
                        'account': 'test',
                        'auth_type': 'PASSWORD',
                        'password': '123',
                        'key': ''
                    }
                ]
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CREATE_TASK_SUCCESS_CLIENT),
        Patcher(target=NODEMAN_RSA_ENCRYPT, return_value="123")
    ]
)

CREATE_TASK_FAIL_CASE = ComponentTestCase(
    name='nodeman create task fail case',
    inputs={
        'biz_cc_id': '1',
        'nodeman_bk_cloud_id': '1',
        'nodeman_node_type': 'AGENT',
        'nodeman_op_type': 'INSTALL',
        'nodeman_hosts': [
            {
                'conn_ips': '1.1.1.1',
                'login_ip': '1.1.1.1',
                'data_ip': '1.1.1.1',
                'cascade_ip': '1.1.1.1',
                'os_type': 'LINUX',
                'has_cygwin': False,
                'port': '22',
                'account': 'test',
                'auth_type': 'PASSWORD',
                'password': '123',
                'key': ''
            }
        ]
    },
    parent_data={
        'executor': 'tester',
        'biz_cc_id': "1"
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={'ex_data': u'create agent install task failed: fail'}
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CREATE_TASK_FAIL_CLIENT.nodeman.create_task,
            calls=[Call({
                'bk_biz_id': '1',
                'bk_cloud_id': '1',
                'node_type': 'AGENT',
                'op_type': 'INSTALL',
                'creator': 'tester',
                'hosts': [
                    {
                        'conn_ips': '1.1.1.1',
                        'login_ip': '1.1.1.1',
                        'data_ip': '1.1.1.1',
                        'cascade_ip': '1.1.1.1',
                        'os_type': 'LINUX',
                        'has_cygwin': False,
                        'port': '22',
                        'account': 'test',
                        'auth_type': 'PASSWORD',
                        'password': '123',
                        'key': ''
                    }
                ]
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CREATE_TASK_FAIL_CLIENT),
        Patcher(target=NODEMAN_RSA_ENCRYPT, return_value="123")
    ]
)
