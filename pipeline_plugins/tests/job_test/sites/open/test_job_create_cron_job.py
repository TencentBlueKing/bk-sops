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
from pipeline_plugins.components.collections.sites.open.job import CreateCronJobComponent


class CreateCronJobComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            CREATE_CRON_JOB_SUCCESS_CASE,
            CREATE_CRON_JOB_SUCCESS_CRON_CASE,
            CREATE_CRON_JOB_SAVE_CRON_FAIL_CASE,
            CREATE_CRON_JOB_UPDATE_CRON_STATUS_FAIL_CASE
        ]

    def component_cls(self):
        return CreateCronJobComponent


class MockClient(object):
    def __init__(self, save_cron_return, update_cron_status_return):
        self.set_bk_api_ver = MagicMock()
        self.job = MagicMock()
        self.job.save_cron = MagicMock(return_value=save_cron_return)
        self.job.update_cron_status = MagicMock(return_value=update_cron_status_return)


# mock path
GET_CLIENT_BY_USER = 'pipeline_plugins.components.collections.sites.open.job.get_client_by_user'

# mock clients
CREATE_CRON_JOB_SUCCESS_CLIENT = MockClient(
    save_cron_return={
        "result": True,
        "data": {
            'cron_id': '1'
        }
    },
    update_cron_status_return=None)

CREATE_CRON_JOB_SUCCESS_CRON_CLIENT = MockClient(
    save_cron_return={
        "result": True,
        "data": {
            'cron_id': '1'
        }
    },
    update_cron_status_return={
        "result": True,
    })

CREATE_CRON_JOB_SAVE_CRON_FAIL_CLIENT = MockClient(
    save_cron_return={
        "result": False,
        "message": "save cron fail"
    },
    update_cron_status_return=None)

CREATE_CRON_JOB_UPDATE_CRON_STATUS_FAIL_CLIENT = MockClient(
    save_cron_return={
        "result": True,
        "data": {
            'cron_id': '1'
        }
    },
    update_cron_status_return={
        "result": False,
        "message": "update cron status fail",
    })

# test cases
CREATE_CRON_JOB_SUCCESS_CASE = ComponentTestCase(
    name='success case',
    inputs={'cron_name': 'cron_name',
            'job_task_id': '11',
            'cron_status': '2',
            'cron_expression': '0 0 12 * * ? 2015'},
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': '1',
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'cron_id': '1',
            "client": CREATE_CRON_JOB_SUCCESS_CLIENT}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CREATE_CRON_JOB_SUCCESS_CLIENT.job.save_cron,
            calls=[Call({
                'bk_biz_id': '1',
                'bk_job_id': '11',
                'cron_name': 'cron_name',
                'cron_expression': '0 0 12 * * ? 2015'
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CREATE_CRON_JOB_SUCCESS_CLIENT)
    ])

CREATE_CRON_JOB_SUCCESS_CRON_CASE = ComponentTestCase(
    name='success cron case',
    inputs={'cron_name': 'cron_name',
            'job_task_id': '11',
            'cron_status': '1',
            'cron_expression': '0 0 12 * * ? 2015'},
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': '1',
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'cron_id': '1',
            "client": CREATE_CRON_JOB_SUCCESS_CRON_CLIENT}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CREATE_CRON_JOB_SUCCESS_CRON_CLIENT.job.save_cron,
            calls=[Call({
                'bk_biz_id': '1',
                'bk_job_id': '11',
                'cron_name': 'cron_name',
                'cron_expression': '0 0 12 * * ? 2015'
            })]
        ),
        CallAssertion(
            func=CREATE_CRON_JOB_SUCCESS_CRON_CLIENT.job.update_cron_status,
            calls=[Call({
                'bk_biz_id': '1',
                'cron_status': 1,
                'cron_id': '1'
            })]
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CREATE_CRON_JOB_SUCCESS_CRON_CLIENT)
    ])

CREATE_CRON_JOB_SAVE_CRON_FAIL_CASE = ComponentTestCase(
    name='save cron fail case',
    inputs={'cron_name': 'cron_name',
            'job_task_id': '11',
            'cron_status': '1',
            'cron_expression': '0 0 12 * * ? abcd'},
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': '1',
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={"ex_data": "save cron fail"}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CREATE_CRON_JOB_SAVE_CRON_FAIL_CLIENT.job.save_cron,
            calls=[Call({
                'bk_biz_id': '1',
                'bk_job_id': '11',
                'cron_name': 'cron_name',
                'cron_expression': '0 0 12 * * ? abcd'
            })]
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CREATE_CRON_JOB_SAVE_CRON_FAIL_CLIENT)
    ])

CREATE_CRON_JOB_UPDATE_CRON_STATUS_FAIL_CASE = ComponentTestCase(
    name='update cron status case',
    inputs={'cron_name': 'cron_name',
            'job_task_id': '11',
            'cron_status': '1',
            'cron_expression': '0 0 12 * * ? 2015'},
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': '1',
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "cron_id": "1",
            "client": CREATE_CRON_JOB_UPDATE_CRON_STATUS_FAIL_CLIENT,
            "ex_data": "定时作业创建成功 cron_id=[1]，定时作业启动失败 "
            "message=[update cron status fail]"
        }),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CREATE_CRON_JOB_UPDATE_CRON_STATUS_FAIL_CLIENT.job.save_cron,
            calls=[Call({
                'bk_biz_id': '1',
                'bk_job_id': '11',
                'cron_name': 'cron_name',
                'cron_expression': '0 0 12 * * ? 2015'
            })]
        ),
        CallAssertion(
            func=CREATE_CRON_JOB_UPDATE_CRON_STATUS_FAIL_CLIENT.job.update_cron_status,
            calls=[Call({
                'bk_biz_id': '1',
                'cron_status': 1,
                'cron_id': '1'
            })]
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CREATE_CRON_JOB_UPDATE_CRON_STATUS_FAIL_CLIENT)
    ])
