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
    ScheduleAssertion,
    Call,
    Patcher
)
from pipeline_plugins.components.collections.sites.open.job import JobExecuteTaskComponent


class JobExecuteTaskComponentTest(TestCase, ComponentTestMixin):

    def cases(self):
        return [
            EXECUTE_JOB_FAIL_CASE,
            INVALID_CALLBACK_DATA_CASE,
            JOB_EXECUTE_NOT_SUCCESS_CASE,
            GET_GLOBAL_VAR_FAIL_CASE,
            EXECUTE_SUCCESS_CASE,
            INVALID_IP_CASE
        ]

    def component_cls(self):
        return JobExecuteTaskComponent


class MockClient(object):
    def __init__(self, execute_job_return, get_global_var_return=None):
        self.set_bk_api_ver = MagicMock()
        self.job = MagicMock()
        self.job.execute_job = MagicMock(return_value=execute_job_return)
        self.job.get_job_instance_global_var_value = MagicMock(return_value=get_global_var_return)


# mock path
GET_CLIENT_BY_USER = 'pipeline_plugins.components.collections.sites.open.job.get_client_by_user'
CC_GET_IPS_INFO_BY_STR = 'pipeline_plugins.components.collections.sites.open.job.cc_get_ips_info_by_str'
GET_NODE_CALLBACK_URL = 'pipeline_plugins.components.collections.sites.open.job.get_node_callback_url'
GET_JOB_INSTANCE_URL = 'pipeline_plugins.components.collections.sites.open.job.get_job_instance_url'

# mock clients
EXECUTE_JOB_CALL_FAIL_CLIENT = MockClient(execute_job_return={
    'result': False,
    'message': 'message token'
})
INVALID_CALLBACK_DATA_CLIENT = MockClient(execute_job_return={
    'result': True,
    'data': {
        'job_instance_id': 56789,
        'job_instance_name': 'job_name_token'
    }})
JOB_EXECUTE_NOT_SUCCESS_CLIENT = MockClient(
    execute_job_return={
        'result': True,
        'data': {
            'job_instance_id': 56789,
            'job_instance_name': 'job_name_token'
        }})
GET_GLOBAL_VAR_CALL_FAIL_CLIENT = MockClient(
    execute_job_return={
        'result': True,
        'data': {
            'job_instance_id': 56789,
            'job_instance_name': 'job_name_token'
        }},
    get_global_var_return={
        'result': False,
        'message': 'global var message token'
    })
EXECUTE_SUCCESS_CLIENT = MockClient(
    execute_job_return={
        'result': True,
        'data': {
            'job_instance_id': 56789,
            'job_instance_name': 'job_name_token'
        }},
    get_global_var_return={
        'result': True,
        'data': {
            'job_instance_var_values': [
                {'step_instance_var_values': [
                    {'category': 1, 'name': 'key_1', 'value': 'new_value_1'},
                    {'category': 1, 'name': 'key_2', 'value': 'new_value_2'}
                ]}
            ]
        }
    })

# test cases
EXECUTE_JOB_FAIL_CASE = ComponentTestCase(
    name='execute_job call failed case',
    inputs={
        'job_global_var': [
            {'type': 1, 'name': 'key_1', 'value': 'value_1'},
            {'type': 1, 'name': 'key_2', 'value': 'value_2'},
            {'type': 2, 'name': 'key_3', 'value': '1.1.1.1,2.2.2.2'}
        ],
        'job_task_id': 12345
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={'ex_data': 'message token'}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call(username='executor_token',
                                                               biz_cc_id=1,
                                                               ip_str='1.1.1.1,2.2.2.2',
                                                               use_cache=False)]),
        CallAssertion(
            func=EXECUTE_JOB_CALL_FAIL_CLIENT.job.execute_job,
            calls=[Call({
                'bk_biz_id': 1,
                'bk_job_id': 12345,
                'global_vars': [
                    {'name': 'key_1', 'value': 'value_1'},
                    {'name': 'key_2', 'value': 'value_2'},
                    {'name': 'key_3', 'ip_list': [{'ip': '1.1.1.1', 'bk_cloud_id': 1},
                                                  {'ip': '2.2.2.2', 'bk_cloud_id': 1}]}
                ],
                'bk_callback_url': 'url_token'
            })])
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_JOB_CALL_FAIL_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={
            'ip_result': [
                {'InnerIP': '1.1.1.1', 'Source': 1},
                {'InnerIP': '2.2.2.2', 'Source': 1},
            ]
        }),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value='url_token')
    ])

INVALID_CALLBACK_DATA_CASE = ComponentTestCase(
    name='invalid callback case',
    inputs={
        'job_global_var': [
            {'type': 1, 'name': 'key_1', 'value': 'value_1'},
            {'type': 1, 'name': 'key_2', 'value': 'value_2'},
            {'type': 2, 'name': 'key_3', 'value': '1.1.1.1,2.2.2.2'}
        ],
        'job_task_id': 12345
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': INVALID_CALLBACK_DATA_CLIENT
        }),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': INVALID_CALLBACK_DATA_CLIENT,
            'ex_data': 'invalid callback_data, '
                       'job_instance_id: None, status: None'
        },
        callback_data={}),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username='executor_token',
                        biz_cc_id=1,
                        ip_str='1.1.1.1,2.2.2.2',
                        use_cache=False)]),
        CallAssertion(
            func=INVALID_CALLBACK_DATA_CLIENT.job.execute_job,
            calls=[Call({
                'bk_biz_id': 1,
                'bk_job_id': 12345,
                'global_vars': [
                    {'name': 'key_1', 'value': 'value_1'},
                    {'name': 'key_2', 'value': 'value_2'},
                    {'name': 'key_3',
                     'ip_list': [{'ip': '1.1.1.1', 'bk_cloud_id': 1},
                                 {'ip': '2.2.2.2', 'bk_cloud_id': 1}]}
                ],
                'bk_callback_url': 'url_token'
            })])
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INVALID_CALLBACK_DATA_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={
            'ip_result': [
                {'InnerIP': '1.1.1.1', 'Source': 1},
                {'InnerIP': '2.2.2.2', 'Source': 1},
            ]}),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value='url_token'),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value='instance_url_token'),
    ])

JOB_EXECUTE_NOT_SUCCESS_CASE = ComponentTestCase(
    name='job execute not success case',
    inputs={
        'job_global_var': [
            {'type': 1, 'name': 'key_1', 'value': 'value_1'},
            {'type': 1, 'name': 'key_2', 'value': 'value_2'},
            {'type': 2, 'name': 'key_3', 'value': '1.1.1.1,2.2.2.2'}
        ],
        'job_task_id': 12345
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': JOB_EXECUTE_NOT_SUCCESS_CLIENT
        }),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': JOB_EXECUTE_NOT_SUCCESS_CLIENT,
            'ex_data': {
                'exception_msg': u"任务执行失败，<a href='%s' target='_blank'>"
                                 u"前往作业平台(JOB)查看详情</a>" % 'instance_url_token',
                'task_inst_id': 56789,
                'show_ip_log': True
            }
        },
        callback_data={
            'job_instance_id': 56789,
            'status': 1
        }),
    execute_call_assertion=[
        CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call(
            username='executor_token',
            biz_cc_id=1,
            ip_str='1.1.1.1,2.2.2.2',
            use_cache=False)]),
        CallAssertion(
            func=JOB_EXECUTE_NOT_SUCCESS_CLIENT.job.execute_job,
            calls=[Call({
                'bk_biz_id': 1,
                'bk_job_id': 12345,
                'global_vars': [
                    {'name': 'key_1', 'value': 'value_1'},
                    {'name': 'key_2', 'value': 'value_2'},
                    {'name': 'key_3', 'ip_list': [{'ip': '1.1.1.1', 'bk_cloud_id': 1},
                                                  {'ip': '2.2.2.2', 'bk_cloud_id': 1}]}
                ],
                'bk_callback_url': 'url_token'
            })])
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=JOB_EXECUTE_NOT_SUCCESS_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={
            'ip_result': [
                {'InnerIP': '1.1.1.1', 'Source': 1},
                {'InnerIP': '2.2.2.2', 'Source': 1},
            ]
        }),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value='url_token'),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value='instance_url_token'),
    ])

GET_GLOBAL_VAR_FAIL_CASE = ComponentTestCase(
    name='get global var fail case',
    inputs={
        'job_global_var': [
            {'type': 1, 'name': 'key_1', 'value': 'value_1'},
            {'type': 1, 'name': 'key_2', 'value': 'value_2'},
            {'type': 2, 'name': 'key_3', 'value': '1.1.1.1,2.2.2.2'}
        ],
        'job_task_id': 12345
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': GET_GLOBAL_VAR_CALL_FAIL_CLIENT
        }),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': GET_GLOBAL_VAR_CALL_FAIL_CLIENT,
            'ex_data': 'global var message token'
        },
        callback_data={
            'job_instance_id': 56789,
            'status': 3
        }),
    execute_call_assertion=[
        CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call(
            username='executor_token',
            biz_cc_id=1,
            ip_str='1.1.1.1,2.2.2.2',
            use_cache=False)]),
        CallAssertion(
            func=GET_GLOBAL_VAR_CALL_FAIL_CLIENT.job.execute_job,
            calls=[Call({
                'bk_biz_id': 1,
                'bk_job_id': 12345,
                'global_vars': [
                    {'name': 'key_1', 'value': 'value_1'},
                    {'name': 'key_2', 'value': 'value_2'},
                    {'name': 'key_3', 'ip_list': [{'ip': '1.1.1.1', 'bk_cloud_id': 1},
                                                  {'ip': '2.2.2.2', 'bk_cloud_id': 1}]}
                ],
                'bk_callback_url': 'url_token'
            })])
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=GET_GLOBAL_VAR_CALL_FAIL_CLIENT.job.get_job_instance_global_var_value,
            calls=[Call({
                'bk_biz_id': 1,
                'job_instance_id': 56789
            })]
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=GET_GLOBAL_VAR_CALL_FAIL_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={
            'ip_result': [
                {'InnerIP': '1.1.1.1', 'Source': 1},
                {'InnerIP': '2.2.2.2', 'Source': 1},
            ]
        }),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value='url_token'),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value='instance_url_token'),
    ])

EXECUTE_SUCCESS_CASE = ComponentTestCase(
    name='execute success case',
    inputs={
        'job_global_var': [
            {'type': 1, 'name': 'key_1', 'value': 'value_1'},
            {'type': 1, 'name': 'key_2', 'value': 'value_2'},
            {'type': 2, 'name': 'key_3', 'value': '1.1.1.1,2.2.2.2'}
        ],
        'job_task_id': 12345
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': EXECUTE_SUCCESS_CLIENT
        }),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': EXECUTE_SUCCESS_CLIENT,
            'key_1': 'new_value_1',
            'key_2': 'new_value_2'
        },
        callback_data={
            'job_instance_id': 56789,
            'status': 3
        }),
    execute_call_assertion=[
        CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call(
            username='executor_token',
            biz_cc_id=1,
            ip_str='1.1.1.1,2.2.2.2',
            use_cache=False)]),
        CallAssertion(
            func=EXECUTE_SUCCESS_CLIENT.job.execute_job,
            calls=[Call({
                'bk_biz_id': 1,
                'bk_job_id': 12345,
                'global_vars': [
                    {'name': 'key_1', 'value': 'value_1'},
                    {'name': 'key_2', 'value': 'value_2'},
                    {'name': 'key_3', 'ip_list': [{'ip': '1.1.1.1', 'bk_cloud_id': 1},
                                                  {'ip': '2.2.2.2', 'bk_cloud_id': 1}]}
                ],
                'bk_callback_url': 'url_token'
            })])
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=EXECUTE_SUCCESS_CLIENT.job.get_job_instance_global_var_value,
            calls=[Call({
                'bk_biz_id': 1,
                'job_instance_id': 56789
            })]
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_SUCCESS_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={
            'ip_result': [
                {'InnerIP': '1.1.1.1', 'Source': 1},
                {'InnerIP': '2.2.2.2', 'Source': 1},
            ]
        }),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value='url_token'),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value='instance_url_token'),
    ])

INVALID_IP_CASE = ComponentTestCase(
    name='invalid ip case',
    inputs={
        'job_global_var': [
            {'type': 1, 'name': 'key_1', 'value': 'value_1'},
            {'type': 1, 'name': 'key_2', 'value': 'value_2'},
            {'type': 2, 'name': 'key_3', 'value': '1.1.1.1,2.2.2.2'}
        ],
        'job_task_id': 12345
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            'ex_data': u"无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法"
        }),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call(
            username='executor_token',
            biz_cc_id=1,
            ip_str='1.1.1.1,2.2.2.2',
            use_cache=False)]),
    ],
    patchers=[
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={'ip_result': []}),
    ])
