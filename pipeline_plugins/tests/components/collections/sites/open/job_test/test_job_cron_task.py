# -*- coding: utf-8 -*-

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
from pipeline_plugins.components.collections.sites.open.job import JobCronTaskComponent


class JobCronComponentTest(TestCase, ComponentTestMixin):

    def cases(self):
        return [
            SAVE_CRON_FAIL_CASE,
            SAVE_CRON_SUCCESS_CASE,
            UPDATE_CRON_STATUS_FAIL_CASE,
            JOB_CRON_SUCCESS_CASE
        ]

    def component_cls(self):
        return JobCronTaskComponent


class MockClient(object):
    def __init__(self, save_cron_return, update_cron_status_return):
        self.set_bk_api_ver = MagicMock()
        self.job = MagicMock()
        self.job.save_cron = MagicMock(return_value=save_cron_return)
        self.job.update_cron_status = MagicMock(return_value=update_cron_status_return)


# mock path
GET_CLIENT_BY_USER = 'pipeline_plugins.components.collections.sites.open.job.get_client_by_user'

# mock clients
SAVE_CRON_CALL_FAIL_CLIENT = MockClient(
    save_cron_return={
        'result': False,
        'message': 'save_cron fail'
    },
    update_cron_status_return=None
)
SAVE_CRON_CALL_SUCCESS_CLIENT = MockClient(
    save_cron_return={
        'result': True,
        'message': 'save_cron success',
        'data': {
            'cron_id': 1
        }
    },
    update_cron_status_return=None
)
UPDATE_CRON_STATUS_CALL_FAIL_CLIENT = MockClient(
    save_cron_return={
        'result': True,
        'message': 'save_cron success',
        'data': {
            'cron_id': 1
        }
    },
    update_cron_status_return={
        'result': False,
        'message': 'update_cron_status fail'
    }
)
JOB_CRON_SUCCESS_CLIENT = MockClient(
    save_cron_return={
        'result': True,
        'message': 'save_cron success',
        'data': {
            'cron_id': 1
        }
    },
    update_cron_status_return={
        'result': True,
    }
)
# test case
SAVE_CRON_FAIL_CASE = ComponentTestCase(
    name='save cron call failed case',
    inputs={
        'job_cron_job_id': 1,
        'job_cron_name': 'job_cron_name',
        'job_cron_expression': '0 0/5 * * * ?',
        'job_cron_status': 1,
    },
    parent_data={
        'executor': 'executor',
        'biz_cc_id': 1
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={'ex_data': 'save_cron fail'}
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=SAVE_CRON_CALL_FAIL_CLIENT.job.save_cron,
            calls=[Call({
                'bk_biz_id': 1,
                'bk_job_id': 1,
                'cron_name': 'job_cron_name',
                'cron_expression': '0 0/5 * * * ?'
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SAVE_CRON_CALL_FAIL_CLIENT),
    ]
)
SAVE_CRON_SUCCESS_CASE = ComponentTestCase(
    name='save cron call success case',
    inputs={
        'job_cron_job_id': 1,
        'job_cron_name': 'job_cron_name',
        'job_cron_expression': '0 0/5 * * * ?',
        'job_cron_status': 2,
    },
    parent_data={
        'executor': 'executor',
        'biz_cc_id': 1
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'cron_id': 1,
            'status': u'暂停'
        }
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=SAVE_CRON_CALL_SUCCESS_CLIENT.job.save_cron,
            calls=[Call({
                'bk_biz_id': 1,
                'bk_job_id': 1,
                'cron_name': 'job_cron_name',
                'cron_expression': '0 0/5 * * * ?'
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SAVE_CRON_CALL_SUCCESS_CLIENT),
    ]
)
UPDATE_CRON_STATUS_FAIL_CASE = ComponentTestCase(
    name='update cron status call failed case',
    inputs={
        'job_cron_job_id': 1,
        'job_cron_name': 'job_cron_name',
        'job_cron_expression': '0 0/5 * * * ?',
        'job_cron_status': 1
    },
    parent_data={
        'executor': 'executor',
        'biz_cc_id': 1
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            'cron_id': 1,
            'ex_data': u'新建定时任务成功但是启动失败：update_cron_status fail',
            'status': u'暂停'
        }
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=UPDATE_CRON_STATUS_CALL_FAIL_CLIENT.job.save_cron,
            calls=[Call({
                'bk_biz_id': 1,
                'bk_job_id': 1,
                'cron_name': 'job_cron_name',
                'cron_expression': '0 0/5 * * * ?'
            })]
        ),
        CallAssertion(
            func=UPDATE_CRON_STATUS_CALL_FAIL_CLIENT.job.update_cron_status,
            calls=[Call({
                'bk_biz_id': 1,
                'cron_status': 1,
                'cron_id': 1,
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=UPDATE_CRON_STATUS_CALL_FAIL_CLIENT),
    ]
)
JOB_CRON_SUCCESS_CASE = ComponentTestCase(
    name='save cron and update cron status call success case',
    inputs={
        'job_cron_job_id': 1,
        'job_cron_name': 'job_cron_name',
        'job_cron_expression': '0 0/5 * * * ?',
        'job_cron_status': 1
    },
    parent_data={
        'executor': 'executor',
        'biz_cc_id': 1
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'cron_id': 1,
            'status': u'启动'
        }
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=JOB_CRON_SUCCESS_CLIENT.job.save_cron,
            calls=[Call({
                'bk_biz_id': 1,
                'bk_job_id': 1,
                'cron_name': 'job_cron_name',
                'cron_expression': '0 0/5 * * * ?'
            })]
        ),
        CallAssertion(
            func=JOB_CRON_SUCCESS_CLIENT.job.update_cron_status,
            calls=[Call({
                'bk_biz_id': 1,
                'cron_status': 1,
                'cron_id': 1,
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=JOB_CRON_SUCCESS_CLIENT),
    ]
)
