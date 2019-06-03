# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import patch, MagicMock
from pipeline.component_framework.test import (ComponentTestMixin,
                                               ComponentTestCase,
                                               ExecuteAssertion)

from pipeline_plugins.components.collections.sites.open.job import CreateCronJobComponent


class ClientSuccess(object):
    class Job(object):
        def save_cron(self, arg):
            data = {
                "result": True,
                "data": {
                    "cron_id": 1
                }
            }
            return data
    job = Job()
clientSuccess = ClientSuccess()

class ClientSaveCronFail(object):
    class Job(object):
        def save_cron(self, arg):
            data = {
                "result": False,
                "message": "save cron fail",
            }
            return data
    job = Job()
clientSaveCronFail = ClientSaveCronFail()

class ClientUpdateCronStatusFail(object):
    class Job(object):
        def save_cron(self, arg):
            data = {
                "result": False,
                "message": "update cron status fail",
            }
            return data
    job = Job()
clientUpdateCronStatusFail = ClientUpdateCronStatusFail()

class CreateCronJobComponentTest(TestCase, ComponentTestMixin):

    @property
    def cases(self):
        return [
            ComponentTestCase(name='execute success case',
                              inputs={'job_task_id': '1',
                                      'cron_name': '测试定时作业-成功',
                                      'job_task_id':'11',
                                      'cron_status': '2',
                                      'cron_expression': '0 0 12 * * ? 2015'},
                              parent_data={},
                              execute_assertion=ExecuteAssertion(success=True,
                                                                 outputs={
                                                                    "cron_id": 1,
                                                                    "client": clientSuccess
                                                                 }),
                              schedule_assertion=None,
                              patchers=[
                                  patch('pipeline_plugins.components.collections.sites.open.job.get_client_by_user',
                                        MagicMock(return_value=clientSuccess)),
                              ]),
            ComponentTestCase(name='execute save cron fail case',
                              inputs={'job_task_id': '1',
                                      'cron_name': '创建任务失败',
                                      'job_task_id':'11',
                                      'cron_status': '2',
                                      'cron_expression': '0 0 12 * * ? abcd'},
                              parent_data={},
                              execute_assertion=ExecuteAssertion(success=False,
                                                                 outputs={
                                                                    "ex_data": "save cron fail"
                                                                 }),
                              schedule_assertion=None,
                              patchers=[
                                  patch('pipeline_plugins.components.collections.sites.open.job.get_client_by_user',
                                        MagicMock(return_value=clientSaveCronFail)),
                              ]),
            ComponentTestCase(name='execute update cron status fail case',
                              inputs={'job_task_id': '1',
                                      'cron_name': '创建启动状态的任务失败',
                                      'job_task_id':'11',
                                      'cron_status': '1',
                                      'cron_expression': '0 0 12 * * ? 2015'},
                              parent_data={},
                              execute_assertion=ExecuteAssertion(success=False,
                                                                 outputs={
                                                                    "cron_id": 1,
                                                                    "client": clientUpdateCronStatusFail,
                                                                    "ex_data": "定时作业创建成功 cron_id=[1]，定时作业启动失败 message=[update cron status fail]"
                                                                 }),
                              schedule_assertion=None,
                              patchers=[
                                  patch('pipeline_plugins.components.collections.sites.open.job.get_client_by_user',
                                        MagicMock(return_value=clientUpdateCronStatusFail)),
                              ]),
            ]

    @property
    def component_cls(self):
        return CreateCronJobComponent

