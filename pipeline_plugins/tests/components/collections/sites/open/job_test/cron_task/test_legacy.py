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

import ujson as json
from django.test import TestCase
from mock import MagicMock
from pipeline.component_framework.test import (
    Call,
    CallAssertion,
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    Patcher,
)

from pipeline_plugins.components.collections.sites.open.job import JobCronTaskComponent


class JobCronComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [SAVE_CRON_FAIL_CASE, SAVE_CRON_SUCCESS_CASE, UPDATE_CRON_STATUS_FAIL_CASE, JOB_CRON_SUCCESS_CASE]

    def component_cls(self):
        return JobCronTaskComponent


class MockClient(object):
    def __init__(self, save_cron_return, update_cron_status_return):
        self.set_bk_api_ver = MagicMock()
        self.api = MagicMock()
        self.api.save_cron = MagicMock(return_value=save_cron_return)
        self.api.update_cron_status = MagicMock(return_value=update_cron_status_return)


# mock path
GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.cron_task.legacy.get_client_by_username"

# mock clients
SAVE_CRON_CALL_FAIL_CLIENT = MockClient(
    save_cron_return={"result": False, "message": "save_cron fail"}, update_cron_status_return=None
)
SAVE_CRON_CALL_SUCCESS_CLIENT = MockClient(
    save_cron_return={"result": True, "message": "save_cron success", "data": {"id": 1}},
    update_cron_status_return=None,
)
UPDATE_CRON_STATUS_CALL_FAIL_CLIENT = MockClient(
    save_cron_return={"result": True, "message": "save_cron success", "data": {"id": 1}},
    update_cron_status_return={"result": False, "message": "update_cron_status fail"},
)
JOB_CRON_SUCCESS_CLIENT = MockClient(
    save_cron_return={"result": True, "message": "save_cron success", "data": {"id": 1}},
    update_cron_status_return={"result": True},
)
# test case
SAVE_CRON_FAIL_CASE = ComponentTestCase(
    name="save cron call failed case",
    inputs={
        "job_cron_job_id": 1,
        "job_cron_name": "job_cron_name",
        "job_cron_expression": "0 0/5 * * * ?",
        "job_cron_status": 1,
    },
    parent_data={"executor": "executor", "biz_cc_id": 1, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "ex_data": ("调用作业平台(JOB)接口jobv3.save_cron返回失败, error=save_cron fail, params={params}").format(
                params=json.dumps(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 1,
                        "name": "job_cron_name",
                        "expression": "0 0/5 * * * ?",
                    }
                )
            )
        },
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=SAVE_CRON_CALL_FAIL_CLIENT.api.save_cron,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 1,
                        "name": "job_cron_name",
                        "expression": "0 0/5 * * * ?",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                ),
            ],
        ),
    ],
    patchers=[Patcher(target=GET_CLIENT_BY_USER, return_value=SAVE_CRON_CALL_FAIL_CLIENT)],
)
SAVE_CRON_SUCCESS_CASE = ComponentTestCase(
    name="save cron call success case",
    inputs={
        "job_cron_job_id": 1,
        "job_cron_name": "job_cron_name",
        "job_cron_expression": "0 0/5 * * * ?",
        "job_cron_status": 2,
    },
    parent_data={"executor": "executor", "biz_cc_id": 1, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(success=True, outputs={"cron_id": 1, "status": "暂停"}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=SAVE_CRON_CALL_SUCCESS_CLIENT.api.save_cron,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 1,
                        "name": "job_cron_name",
                        "expression": "0 0/5 * * * ?",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    patchers=[Patcher(target=GET_CLIENT_BY_USER, return_value=SAVE_CRON_CALL_SUCCESS_CLIENT)],
)
UPDATE_CRON_STATUS_FAIL_CASE = ComponentTestCase(
    name="update cron status call failed case",
    inputs={
        "job_cron_job_id": 1,
        "job_cron_name": "job_cron_name",
        "job_cron_expression": "0 0/5 * * * ?",
        "job_cron_status": 1,
    },
    parent_data={"executor": "executor", "biz_cc_id": 1, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "cron_id": 1,
            "status": "暂停",
            "ex_data": "定时任务启动失败: [作业平台]定时任务启动发生异常：调用作业平台(JOB)接口jobv3.update_cron_status返回失败, "
            "error=update_cron_status fail, "
            'params={"bk_scope_type":"biz","bk_scope_id":"1","bk_biz_id":1,"status":1,"id":1}',
        },
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=UPDATE_CRON_STATUS_CALL_FAIL_CLIENT.api.save_cron,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 1,
                        "name": "job_cron_name",
                        "expression": "0 0/5 * * * ?",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
        CallAssertion(
            func=UPDATE_CRON_STATUS_CALL_FAIL_CLIENT.api.update_cron_status,
            calls=[
                Call(
                    {"bk_scope_type": "biz", "bk_scope_id": "1", "bk_biz_id": 1, "status": 1, "id": 1},
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    patchers=[Patcher(target=GET_CLIENT_BY_USER, return_value=UPDATE_CRON_STATUS_CALL_FAIL_CLIENT)],
)
JOB_CRON_SUCCESS_CASE = ComponentTestCase(
    name="save cron and update cron status call success case",
    inputs={
        "job_cron_job_id": 1,
        "job_cron_name": "job_cron_name",
        "job_cron_expression": "0 0/5 * * * ?",
        "job_cron_status": 1,
    },
    parent_data={"executor": "executor", "biz_cc_id": 1, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(success=True, outputs={"cron_id": 1, "status": "启动"}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=JOB_CRON_SUCCESS_CLIENT.api.save_cron,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 1,
                        "name": "job_cron_name",
                        "expression": "0 0/5 * * * ?",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
        CallAssertion(
            func=JOB_CRON_SUCCESS_CLIENT.api.update_cron_status,
            calls=[
                Call(
                    {"bk_scope_type": "biz", "bk_scope_id": "1", "bk_biz_id": 1, "status": 1, "id": 1},
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    patchers=[Patcher(target=GET_CLIENT_BY_USER, return_value=JOB_CRON_SUCCESS_CLIENT)],
)
