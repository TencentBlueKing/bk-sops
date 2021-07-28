# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
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
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.job.fetch_task_log.v1_0 import JobFetchTaskLogComponent


class JobFetchTaskLogComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            FETCH_TASK_LOG_SUCCESS_CASE,
            FETCH_TASK_LOG_WITH_TARGET_IP_SUCCESS_CASE,
            FETCH_TASK_LOG_WITH_NOT_EXISTING_TARGET_IP_FAIL_CASE,
        ]

    def component_cls(self):
        return JobFetchTaskLogComponent


class MockClient(object):
    def __init__(self, get_job_instance_ip_log_return=None, get_job_instance_status=None):
        self.jobv3 = MagicMock()
        self.jobv3.get_job_instance_ip_log = MagicMock(return_value=get_job_instance_ip_log_return)
        self.jobv3.get_job_instance_status = MagicMock(return_value=get_job_instance_status)


# mock path
GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.fetch_task_log.v1_0.get_client_by_user"
BASE_GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.base.get_client_by_user"
EXECUTE_SUCCESS_GET_IP_LOG_RETURN = {
    "result": True,
    "code": 0,
    "message": "",
    "data": {"ip": "1.1.1.1", "bk_cloud_id": 0, "log_content": "log text\n"},
}
EXECUTE_SUCCESS_GET_STATUS_RETURN = {
    "result": True,
    "code": 0,
    "message": "",
    "data": {
        "finished": True,
        "job_instance": {
            "job_instance_id": 100,
            "bk_biz_id": 1,
            "name": "API Quick execution script1521089795887",
            "create_time": 1605064271000,
            "status": 4,
            "start_time": 1605064271000,
            "end_time": 1605064272000,
            "total_time": 1000,
        },
        "step_instance_list": [
            {
                "status": 4,
                "total_time": 1000,
                "name": "API Quick execution scriptxxx",
                "step_instance_id": 75,
                "execute_count": 0,
                "create_time": 1605064271000,
                "end_time": 1605064272000,
                "type": 1,
                "start_time": 1605064271000,
                "step_ip_result_list": [
                    {
                        "ip": "1.1.1.1",
                        "bk_cloud_id": 0,
                        "status": 9,
                        "tag": "",
                        "exit_code": 0,
                        "error_code": 0,
                        "start_time": 1605064271000,
                        "end_time": 1605064272000,
                        "total_time": 1000,
                    },
                    {
                        "ip": "1.1.1.2",
                        "bk_cloud_id": 0,
                        "status": 9,
                        "tag": "",
                        "exit_code": 0,
                        "error_code": 0,
                        "start_time": 1605064271000,
                        "end_time": 1605064272000,
                        "total_time": 1000,
                    },
                ],
            }
        ],
    },
}

MANUAL_KWARGS = {
    "job_instance_id": "12345",
    "bk_biz_id": 1,
    "step_instance_id": 75,
    "bk_cloud_id": 0,
    "ip": "1.1.1.1",
}

FETCH_TASK_LOG_CLIENT = MockClient(
    get_job_instance_status=EXECUTE_SUCCESS_GET_STATUS_RETURN,
    get_job_instance_ip_log_return=EXECUTE_SUCCESS_GET_IP_LOG_RETURN,
)


FETCH_TASK_LOG_SUCCESS_CASE = ComponentTestCase(
    name="fetch task log success case",
    inputs={"biz_cc_id": 1, "job_task_id": "12345"},
    parent_data={"executor": "executor", "project_id": "project_id", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(success=True, outputs={"job_task_log": "log text\n"},),
    execute_call_assertion=[
        CallAssertion(func=FETCH_TASK_LOG_CLIENT.jobv3.get_job_instance_ip_log, calls=[Call(MANUAL_KWARGS)]),
    ],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=FETCH_TASK_LOG_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=FETCH_TASK_LOG_CLIENT),
    ],
)

FETCH_TASK_LOG_WITH_TARGET_IP_SUCCESS_CASE = ComponentTestCase(
    name="fetch task log with target ip success case",
    inputs={"biz_cc_id": 1, "job_task_id": "12345", "job_target_ip": "1.1.1.1"},
    parent_data={"executor": "executor", "project_id": "project_id", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(success=True, outputs={"job_task_log": "log text\n"},),
    execute_call_assertion=[
        CallAssertion(func=FETCH_TASK_LOG_CLIENT.jobv3.get_job_instance_ip_log, calls=[Call(MANUAL_KWARGS)]),
    ],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=FETCH_TASK_LOG_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=FETCH_TASK_LOG_CLIENT),
    ],
)

FETCH_TASK_LOG_WITH_NOT_EXISTING_TARGET_IP_FAIL_CASE = ComponentTestCase(
    name="fetch task log with not existing target ip fail case",
    inputs={"biz_cc_id": 1, "job_task_id": "12345", "job_target_ip": "1.1.1.3"},
    parent_data={"executor": "executor", "project_id": "project_id", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "ex_data": "[get_job_instance_log] target_ip: 1.1.1.3 does not match any ip in ip_list: [1.1.1.1,1.1.1.2]"
        },
    ),
    execute_call_assertion=[],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=FETCH_TASK_LOG_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=FETCH_TASK_LOG_CLIENT),
    ],
)
