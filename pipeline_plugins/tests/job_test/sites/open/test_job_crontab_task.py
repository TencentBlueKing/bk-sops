# -*- coding: utf-8 -*-

from django.test import TestCase
from mock import MagicMock
from pipeline.component_framework.test import (ComponentTestMixin,
                                               ComponentTestCase,
                                               ExecuteAssertion,
                                               CallAssertion,
                                               Call,
                                               Patcher
                                               )

from pipeline_plugins.components.collections.sites.open.job import JobCrontabTaskComponent

# mock path
GET_CLIENT_BY_USER = 'pipeline_plugins.components.collections.sites.open.job.get_client_by_user'


class MockClient(object):
    def __init__(self, get_job_detail_return, save_cron_return, update_cron_status_return):
        self.set_bk_api_ver = MagicMock()
        self.job = MagicMock()
        self.job.get_job_detail = MagicMock(return_value=get_job_detail_return)
        self.job.save_cron = MagicMock(return_value=save_cron_return)
        self.job.update_cron_status = MagicMock(return_value=update_cron_status_return)


# mock clients
JOB_CRON_SUCCESS_CLIENT = MockClient(
    get_job_detail_return={
        'result': True,
        'message': 'get cron name success',
        'data': {
            'name': 'cron_name',
            'bk_job_id': 1,
            'bk_biz_id': 1
        },

    },
    save_cron_return={
        'result': True,
        'message': 'save cron success',
        'data': {
            "cron_id": 1
        }
    },
    update_cron_status_return={
        'result': True,
        'message': 'update cron success',

    }
)

JOB_CRON_FAIL_CLIENT = MockClient(
    get_job_detail_return={
        'result': False,
        'message': 'get cron name fail'

    },
    save_cron_return={
        'result': False,
        'message': 'save cron fail',
    },
    update_cron_status_return= {
        'result': False,
        'message': 'update cron fail'
    }
)


# test cases
class JobCrontabTaskComponentTest(TestCase, ComponentTestMixin):

    # @property
    def cases(self):
        return [
            JOB_CRON_FAIL_CASE,
            JOB_CORN_SUCCESS_CASE
        ]

    # @property
    def component_cls(self):
        return JobCrontabTaskComponent


JOB_CRON_FAIL_CASE = ComponentTestCase(
    name='execute fail case',
    inputs={
        'job_task_id': 1,
        'job_cron_name': '',
        'job_cron_expression': '1 * * * * ?',
        'cron_status': "1"
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
        'job_task_id': 1,
        'job_cron_name': ''
    },
    schedule_assertion=None,
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'bk_biz_id': 1,
        },
    ),
    execute_call_assertion=[
        CallAssertion(
            func=JOB_CRON_FAIL_CLIENT.job.get_job_detail,
            calls=[Call({
                'bk_biz_id': 1,
                'bk_job_id': 1,
                'cron_name': 'job_cron_name',
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=JOB_CRON_FAIL_CLIENT),
    ]
)

JOB_CORN_SUCCESS_CASE = ComponentTestCase(
    name='execute success case',
    inputs={
        'job_task_id': 1,
        'job_cron_name': '',
        'job_cron_expression': '1 * * * * ?',
        'cron_status': "1"
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
        'job_task_id': 1,
        'job_cron_name': ''
    },
    schedule_assertion=None,
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'bk_biz_id': 1,
        },
    ),
    execute_call_assertion=[
        CallAssertion(
            func=JOB_CRON_SUCCESS_CLIENT.job.get_job_detail,
            calls=[Call({
                'bk_biz_id': 1,
                'bk_job_id': 1,
                'cron_name': 'job_cron_name',
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=JOB_CRON_SUCCESS_CLIENT)
    ]
)
