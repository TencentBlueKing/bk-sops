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
    ScheduleAssertion,
    Call,
    Patcher
)
from pipeline_plugins.components.collections.sites.open.job import JobPushLocalFilesComponent


class JobPushLocalFilesComponentTest(TestCase, ComponentTestMixin):

    def cases(self):
        return [
            FILE_MANAGER_NOT_CONFIG_CASE(),
            FILE_MANAGER_TYPE_ERR_CASE(),
            PUSH_FILE_TO_IPS_FAIL_CASE(),
            CALLBACK_INVALID_CASE(),
            CALLBACK_STRUCT_ERR_CASE(),
            CALLBACK_FAIL_CASE(),
            SUCCESS_CASE()
        ]

    def component_cls(self):
        return JobPushLocalFilesComponent


# mock path
GET_CLIENT_BY_USER = 'pipeline_plugins.components.collections.sites.open.job.get_client_by_user'
CC_GET_IPS_INFO_BY_STR = 'pipeline_plugins.components.collections.sites.open.job.cc_get_ips_info_by_str'
GET_NODE_CALLBACK_URL = 'pipeline_plugins.components.collections.sites.open.job.get_node_callback_url'
ENVIRONMENT_VAR_GET = 'pipeline_plugins.components.collections.sites.open.job.EnvironmentVariables.objects.get_var'
FACTORY_GET_MANAGER = 'pipeline_plugins.components.collections.sites.open.job.ManagerFactory.get_manager'
GET_JOB_INSTANCE_URL = 'pipeline_plugins.components.collections.sites.open.job.get_job_instance_url'


def FILE_MANAGER_NOT_CONFIG_CASE():
    return ComponentTestCase(
        name='push_local_files file manager not config case',
        inputs={
            'biz_cc_id': 'biz_cc_id',
            'job_local_files': 'job_local_files',
            'job_target_ip_list': 'job_target_ip_list',
            'job_target_account': 'job_target_account',
            'job_target_path': 'job_target_path'
        },
        parent_data={
            'executor': 'executor',
            'project_id': 'project_id'
        },
        execute_assertion=ExecuteAssertion(
            success=False,
            outputs={'ex_data': 'File Manager configuration error, contact administrator please.'}
        ),
        schedule_assertion=None,
        patchers=[
            Patcher(target=ENVIRONMENT_VAR_GET, return_value=None)
        ]
    )


def FILE_MANAGER_TYPE_ERR_CASE():
    NOT_EXIST_TYPE = 'NOT_EXIST_TYPE'
    MANAGER_GET_EXCEPTION = Exception('exc')

    return ComponentTestCase(
        name='push_local_files manager type err case',
        inputs={
            'biz_cc_id': 'biz_cc_id',
            'job_local_files': 'job_local_files',
            'job_target_ip_list': 'job_target_ip_list',
            'job_target_account': 'job_target_account',
            'job_target_path': 'job_target_path'
        },
        parent_data={
            'executor': 'executor',
            'project_id': 'project_id'
        },
        execute_assertion=ExecuteAssertion(
            success=False,
            outputs={'ex_data': 'can not get file manager for type: {}\n err: {}'.format(
                NOT_EXIST_TYPE,
                MANAGER_GET_EXCEPTION
            )}
        ),
        schedule_assertion=None,
        patchers=[
            Patcher(target=ENVIRONMENT_VAR_GET, return_value=NOT_EXIST_TYPE),
            Patcher(target=FACTORY_GET_MANAGER, side_effect=MANAGER_GET_EXCEPTION)
        ]
    )


def PUSH_FILE_TO_IPS_FAIL_CASE():

    PUSH_FAIL_RESULT = {'result': False, 'message': 'msg token'}
    PUSH_FAIL_ESB_CLIENT = MagicMock()
    PUSH_FAIL_MANAGER = MagicMock()
    PUSH_FAIL_MANAGER.push_files_to_ips = MagicMock(return_value=PUSH_FAIL_RESULT)

    return ComponentTestCase(
        name='push_local_files manager call fail case',
        inputs={
            'biz_cc_id': 'biz_cc_id',
            'job_local_files': [
                {
                    'tag': 'tag_1'
                },
                {
                    'tag': 'tag_2'
                }
            ],
            'job_target_ip_list': 'job_target_ip_list',
            'job_target_account': 'job_target_account',
            'job_target_path': 'job_target_path'
        },
        parent_data={
            'executor': 'executor',
            'project_id': 'project_id'
        },
        execute_assertion=ExecuteAssertion(
            success=False,
            outputs={'ex_data': PUSH_FAIL_RESULT['message']}
        ),
        schedule_assertion=None,
        execute_call_assertion=[
            CallAssertion(func=GET_CLIENT_BY_USER, calls=[Call('executor')]),
            CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call('executor', 'biz_cc_id', 'job_target_ip_list')]),
            CallAssertion(func=PUSH_FAIL_MANAGER.push_files_to_ips, calls=[Call(
                esb_client=PUSH_FAIL_ESB_CLIENT,
                bk_biz_id='biz_cc_id',
                file_tags=['tag_1', 'tag_2'],
                target_path='job_target_path',
                ips=[{
                    'ip': '1.1.1.1',
                    'bk_cloud_id': 0
                }],
                account='job_target_account',
                callback_url='callback_url'
            )])
        ],
        patchers=[
            Patcher(target=ENVIRONMENT_VAR_GET, return_value='a_type'),
            Patcher(target=FACTORY_GET_MANAGER, return_value=PUSH_FAIL_MANAGER),
            Patcher(target=GET_CLIENT_BY_USER, return_value=PUSH_FAIL_ESB_CLIENT),
            Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={'ip_result': [{'InnerIP': '1.1.1.1', 'Source': 0}]}),
            Patcher(target=GET_NODE_CALLBACK_URL, return_value='callback_url')
        ]
    )


def CALLBACK_INVALID_CASE():

    CALLBACK_INVALID_RESULT = {'result': True, 'data': {'job_id': 12345}}
    CALLBACK_INVALID_ESB_CLIENT = MagicMock()
    CALLBACK_INVALID_MANAGER = MagicMock()
    CALLBACK_INVALID_MANAGER.push_files_to_ips = MagicMock(return_value=CALLBACK_INVALID_RESULT)

    return ComponentTestCase(
        name='push_local_files callback invalid case',
        inputs={
            'biz_cc_id': 'biz_cc_id',
            'job_local_files': [
                {
                    'tag': 'tag_1'
                },
                {
                    'tag': 'tag_2'
                }
            ],
            'job_target_ip_list': 'job_target_ip_list',
            'job_target_account': 'job_target_account',
            'job_target_path': 'job_target_path'
        },
        parent_data={
            'executor': 'executor',
            'project_id': 'project_id'
        },
        execute_assertion=ExecuteAssertion(
            success=True,
            outputs={'job_inst_id': CALLBACK_INVALID_RESULT['data']['job_id'], 'job_inst_url': 'url_token'}
        ),
        schedule_assertion=ScheduleAssertion(
            success=False,
            outputs={
                'job_inst_id': CALLBACK_INVALID_RESULT['data']['job_id'],
                'job_inst_url': 'url_token',
                'ex_data': 'invalid callback_data, job_instance_id: None, status: None'
            },
            callback_data={},
            schedule_finished=False
        ),
        execute_call_assertion=[
            CallAssertion(func=GET_CLIENT_BY_USER, calls=[Call('executor')]),
            CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call('executor', 'biz_cc_id', 'job_target_ip_list')]),
            CallAssertion(func=CALLBACK_INVALID_MANAGER.push_files_to_ips, calls=[Call(
                esb_client=CALLBACK_INVALID_ESB_CLIENT,
                bk_biz_id='biz_cc_id',
                file_tags=['tag_1', 'tag_2'],
                target_path='job_target_path',
                ips=[{
                    'ip': '1.1.1.1',
                    'bk_cloud_id': 0
                }],
                account='job_target_account',
                callback_url='callback_url'
            )])
        ],
        patchers=[
            Patcher(target=ENVIRONMENT_VAR_GET, return_value='a_type'),
            Patcher(target=FACTORY_GET_MANAGER, return_value=CALLBACK_INVALID_MANAGER),
            Patcher(target=GET_CLIENT_BY_USER, return_value=CALLBACK_INVALID_ESB_CLIENT),
            Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={'ip_result': [{'InnerIP': '1.1.1.1', 'Source': 0}]}),
            Patcher(target=GET_NODE_CALLBACK_URL, return_value='callback_url'),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value='url_token')
        ]
    )


def CALLBACK_STRUCT_ERR_CASE():

    CALLBACK_STRUCT_ERR_RESULT = {'result': True, 'data': {'job_id': 12345}}
    CALLBACK_STRUCT_ERR_ESB_CLIENT = MagicMock()
    CALLBACK_STRUCT_ERR_MANAGER = MagicMock()
    CALLBACK_STRUCT_ERR_MANAGER.push_files_to_ips = MagicMock(return_value=CALLBACK_STRUCT_ERR_RESULT)

    return ComponentTestCase(
        name='push_local_files callback struct err case',
        inputs={
            'biz_cc_id': 'biz_cc_id',
            'job_local_files': [
                {
                    'tag': 'tag_1'
                },
                {
                    'tag': 'tag_2'
                }
            ],
            'job_target_ip_list': 'job_target_ip_list',
            'job_target_account': 'job_target_account',
            'job_target_path': 'job_target_path'
        },
        parent_data={
            'executor': 'executor',
            'project_id': 'project_id'
        },
        execute_assertion=ExecuteAssertion(
            success=True,
            outputs={'job_inst_id': CALLBACK_STRUCT_ERR_RESULT['data']['job_id'], 'job_inst_url': 'url_token'}
        ),
        schedule_assertion=ScheduleAssertion(
            success=False,
            outputs={
                'job_inst_id': CALLBACK_STRUCT_ERR_RESULT['data']['job_id'],
                'job_inst_url': 'url_token',
                'ex_data': "invalid callback_data: [], err: 'list' object has no attribute 'get'"
            },
            callback_data=[],
            schedule_finished=False
        ),
        execute_call_assertion=[
            CallAssertion(func=GET_CLIENT_BY_USER, calls=[Call('executor')]),
            CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call('executor', 'biz_cc_id', 'job_target_ip_list')]),
            CallAssertion(func=CALLBACK_STRUCT_ERR_MANAGER.push_files_to_ips, calls=[Call(
                esb_client=CALLBACK_STRUCT_ERR_ESB_CLIENT,
                bk_biz_id='biz_cc_id',
                file_tags=['tag_1', 'tag_2'],
                target_path='job_target_path',
                ips=[{
                    'ip': '1.1.1.1',
                    'bk_cloud_id': 0
                }],
                account='job_target_account',
                callback_url='callback_url'
            )])
        ],
        patchers=[
            Patcher(target=ENVIRONMENT_VAR_GET, return_value='a_type'),
            Patcher(target=FACTORY_GET_MANAGER, return_value=CALLBACK_STRUCT_ERR_MANAGER),
            Patcher(target=GET_CLIENT_BY_USER, return_value=CALLBACK_STRUCT_ERR_ESB_CLIENT),
            Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={'ip_result': [{'InnerIP': '1.1.1.1', 'Source': 0}]}),
            Patcher(target=GET_NODE_CALLBACK_URL, return_value='callback_url'),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value='url_token')
        ]
    )


def CALLBACK_FAIL_CASE():

    CALLBACK_FAIL_RESULT = {'result': True, 'data': {'job_id': 12345}}
    CALLBACK_FAIL_ESB_CLIENT = MagicMock()
    CALLBACK_FAIL_MANAGER = MagicMock()
    CALLBACK_FAIL_MANAGER.push_files_to_ips = MagicMock(return_value=CALLBACK_FAIL_RESULT)

    return ComponentTestCase(
        name='push_local_files callback fail case',
        inputs={
            'biz_cc_id': 'biz_cc_id',
            'job_local_files': [
                {
                    'tag': 'tag_1'
                },
                {
                    'tag': 'tag_2'
                }
            ],
            'job_target_ip_list': 'job_target_ip_list',
            'job_target_account': 'job_target_account',
            'job_target_path': 'job_target_path'
        },
        parent_data={
            'executor': 'executor',
            'project_id': 'project_id'
        },
        execute_assertion=ExecuteAssertion(
            success=True,
            outputs={'job_inst_id': CALLBACK_FAIL_RESULT['data']['job_id'], 'job_inst_url': 'url_token'}
        ),
        schedule_assertion=ScheduleAssertion(
            success=False,
            outputs={
                'job_inst_id': CALLBACK_FAIL_RESULT['data']['job_id'],
                'job_inst_url': 'url_token',
                'ex_data': {
                    'exception_msg': ("任务执行失败，<a href='{}' target='_blank'>"
                                      "前往作业平台(JOB)查看详情</a>").format('url_token'),
                    'show_ip_log': True,
                    'task_inst_id': 12345
                }
            },
            callback_data={'status': 4, 'job_instance_id': 12345},
            schedule_finished=False
        ),
        execute_call_assertion=[
            CallAssertion(func=GET_CLIENT_BY_USER, calls=[Call('executor')]),
            CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call('executor', 'biz_cc_id', 'job_target_ip_list')]),
            CallAssertion(func=CALLBACK_FAIL_MANAGER.push_files_to_ips, calls=[Call(
                esb_client=CALLBACK_FAIL_ESB_CLIENT,
                bk_biz_id='biz_cc_id',
                file_tags=['tag_1', 'tag_2'],
                target_path='job_target_path',
                ips=[{
                    'ip': '1.1.1.1',
                    'bk_cloud_id': 0
                }],
                account='job_target_account',
                callback_url='callback_url'
            )])
        ],
        patchers=[
            Patcher(target=ENVIRONMENT_VAR_GET, return_value='a_type'),
            Patcher(target=FACTORY_GET_MANAGER, return_value=CALLBACK_FAIL_MANAGER),
            Patcher(target=GET_CLIENT_BY_USER, return_value=CALLBACK_FAIL_ESB_CLIENT),
            Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={'ip_result': [{'InnerIP': '1.1.1.1', 'Source': 0}]}),
            Patcher(target=GET_NODE_CALLBACK_URL, return_value='callback_url'),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value='url_token')
        ]
    )


def SUCCESS_CASE():

    SUCCESS_RESULT = {'result': True, 'data': {'job_id': 12345}}
    SUCCESS_ESB_CLIENT = MagicMock()
    SUCCESS_MANAGER = MagicMock()
    SUCCESS_MANAGER.push_files_to_ips = MagicMock(return_value=SUCCESS_RESULT)

    return ComponentTestCase(
        name='push_local_files success case',
        inputs={
            'biz_cc_id': 'biz_cc_id',
            'job_local_files': [
                {
                    'tag': 'tag_1'
                },
                {
                    'tag': 'tag_2'
                }
            ],
            'job_target_ip_list': 'job_target_ip_list',
            'job_target_account': 'job_target_account',
            'job_target_path': 'job_target_path'
        },
        parent_data={
            'executor': 'executor',
            'project_id': 'project_id'
        },
        execute_assertion=ExecuteAssertion(
            success=True,
            outputs={'job_inst_id': SUCCESS_RESULT['data']['job_id'], 'job_inst_url': 'url_token'}
        ),
        schedule_assertion=ScheduleAssertion(
            success=True,
            outputs={
                'job_inst_id': SUCCESS_RESULT['data']['job_id'],
                'job_inst_url': 'url_token'
            },
            callback_data={'status': 3, 'job_instance_id': 12345},
            schedule_finished=True
        ),
        execute_call_assertion=[
            CallAssertion(func=GET_CLIENT_BY_USER, calls=[Call('executor')]),
            CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call('executor', 'biz_cc_id', 'job_target_ip_list')]),
            CallAssertion(func=SUCCESS_MANAGER.push_files_to_ips, calls=[Call(
                esb_client=SUCCESS_ESB_CLIENT,
                bk_biz_id='biz_cc_id',
                file_tags=['tag_1', 'tag_2'],
                target_path='job_target_path',
                ips=[{
                    'ip': '1.1.1.1',
                    'bk_cloud_id': 0
                }],
                account='job_target_account',
                callback_url='callback_url'
            )])
        ],
        patchers=[
            Patcher(target=ENVIRONMENT_VAR_GET, return_value='a_type'),
            Patcher(target=FACTORY_GET_MANAGER, return_value=SUCCESS_MANAGER),
            Patcher(target=GET_CLIENT_BY_USER, return_value=SUCCESS_ESB_CLIENT),
            Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={'ip_result': [{'InnerIP': '1.1.1.1', 'Source': 0}]}),
            Patcher(target=GET_NODE_CALLBACK_URL, return_value='callback_url'),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value='url_token')
        ]
    )
