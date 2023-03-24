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
    ComponentTestMixin,
    ComponentTestCase,
    CallAssertion,
    ExecuteAssertion,
    ScheduleAssertion,
    Call,
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.job.all_biz_fast_push_file.v1_0 import (
    AllBizJobFastPushFileComponent,
)


class AllBizJobFastPushFilesComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [PUSH_FILE_TO_IPS_FAIL_CASE(), BIZ_SET_PUSH_FILE_TO_IPS_FAIL_CASE()]

    def component_cls(self):
        return AllBizJobFastPushFileComponent


class MockClient(object):
    def __init__(self, fast_push_file_return=None, get_job_instance_status_return=None, list_business_set_return=None):
        self.jobv3 = MagicMock()
        self.jobv3.fast_transfer_file = MagicMock(side_effect=fast_push_file_return)
        self.jobv3.get_job_instance_status = MagicMock(side_effect=get_job_instance_status_return)
        self.cc = MagicMock()
        self.cc.list_business_set = MagicMock(return_value=list_business_set_return)


# mock path
GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.job.all_biz_fast_push_file.base_service.get_client_by_user"
)
BASE_GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.base.get_client_by_user"

GET_JOB_INSTANCE_URL = (
    "pipeline_plugins.components.collections.sites.open.job.all_biz_fast_push_file.base_service.get_job_instance_url"
)

JOB_HANDLE_API_ERROR = (
    "pipeline_plugins.components.collections.sites.open.job.all_biz_fast_push_file.base_service.job_handle_api_error"
)
UTILS_GET_CLIENT_BY_USER = "pipeline_plugins.components.utils.cc.get_client_by_user"

INPUT = {
    "all_biz_cc_id": "321456",
    "job_source_files": [
        {"bk_cloud_id": "0", "ip": "127.0.0.1", "files": "/tmp/aa\n/tmp/bb", "account": "root"},
        {"bk_cloud_id": "1", "ip": "127.0.0.2", "files": "/tmp/cc\n/tmp/dd", "account": "user00"},
    ],
    "upload_speed_limit": "100",
    "download_speed_limit": "100",
    "select_method": "auto",
    "job_dispatch_attr": [
        {
            "bk_cloud_id": "0",
            "job_ip_list": "127.0.0.3;127.0.0.4;127.0.0.5",
            "job_target_path": "/tmp/ee/",
            "job_target_account": "root",
        },
        {
            "bk_cloud_id": "1",
            "job_ip_list": "200.0.0.1,200.0.0.2,200.0.0.3",
            "job_target_path": "/tmp/200/",
            "job_target_account": "user01",
        },
    ],
    "break_line": ";",
    "job_timeout": "100",
}

FAST_PUSH_FILE_REQUEST_FAILURE_CLIENT = MockClient(
    fast_push_file_return=[
        {
            "result": True,
            "code": 0,
            "message": "success",
            "data": {"job_instance_name": "API Quick Distribution File1521101427176", "job_instance_id": 10000},
        },
        {
            "result": True,
            "code": 0,
            "message": "success",
            "data": {"job_instance_name": "API Quick Distribution File1521101427176", "job_instance_id": 10001},
        },
        {
            "result": True,
            "code": 0,
            "message": "success",
            "data": {"job_instance_name": "API Quick Distribution File1521101427176", "job_instance_id": 10002},
        },
        {
            "result": False,
            "code": 1,
            "message": "failed",
            "data": {"job_instance_name": "API Quick Distribution File1521101427176"},
        },
    ],
    get_job_instance_status_return=[
        {"data": {"finished": True, "job_instance": {"status": 3}}, "result": True},
        {"data": {"finished": True, "job_instance": {"status": 3}}, "result": True},
        {"data": {"finished": True, "job_instance": {"status": 3}}, "result": True},
    ],
    list_business_set_return={"result": True, "data": {"info": []}},
)

FAST_PUSH_FILE_BIZ_SET_REQUEST_FAILURE_CLIENT = MockClient(
    fast_push_file_return=[
        {
            "result": True,
            "code": 0,
            "message": "success",
            "data": {"job_instance_name": "API Quick Distribution File1521101427176", "job_instance_id": 10000},
        },
        {
            "result": True,
            "code": 0,
            "message": "success",
            "data": {"job_instance_name": "API Quick Distribution File1521101427176", "job_instance_id": 10001},
        },
        {
            "result": True,
            "code": 0,
            "message": "success",
            "data": {"job_instance_name": "API Quick Distribution File1521101427176", "job_instance_id": 10002},
        },
        {
            "result": False,
            "code": 1,
            "message": "failed",
            "data": {"job_instance_name": "API Quick Distribution File1521101427176"},
        },
    ],
    get_job_instance_status_return=[
        {"data": {"finished": True, "job_instance": {"status": 3}}, "result": True},
        {"data": {"finished": True, "job_instance": {"status": 3}}, "result": True},
        {"data": {"finished": True, "job_instance": {"status": 3}}, "result": True},
    ],
    list_business_set_return={"result": True, "data": {"info": ["biz_set"]}},
)


CLL_INFO = MagicMock(
    side_effect=[
        {
            "bk_scope_type": "biz",
            "bk_scope_id": "321456",
            "bk_biz_id": 321456,
            "file_source_list": [
                {
                    "file_list": ["/tmp/aa", "/tmp/bb"],
                    "server": {
                        "ip_list": [{"ip": "127.0.0.1", "bk_cloud_id": 0}],
                    },
                    "account": {
                        "alias": "root",
                    },
                }
            ],
            "target_server": {
                "ip_list": [
                    {"ip": "127.0.0.3", "bk_cloud_id": 0},
                    {"ip": "127.0.0.4", "bk_cloud_id": 0},
                    {"ip": "127.0.0.5", "bk_cloud_id": 0},
                ],
            },
            "account_alias": "root",
            "file_target_path": "/tmp/ee/",
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
        },
        {
            "bk_scope_type": "biz",
            "bk_scope_id": "321456",
            "bk_biz_id": 321456,
            "file_source_list": [
                {
                    "file_list": ["/tmp/aa", "/tmp/bb"],
                    "server": {
                        "ip_list": [{"ip": "127.0.0.1", "bk_cloud_id": 0}],
                    },
                    "account": {
                        "alias": "root",
                    },
                }
            ],
            "target_server": {
                "ip_list": [
                    {"ip": "200.0.0.1", "bk_cloud_id": 1},
                    {"ip": "200.0.0.2", "bk_cloud_id": 1},
                    {"ip": "200.0.0.3", "bk_cloud_id": 1},
                ],
            },
            "account_alias": "user01",
            "file_target_path": "/tmp/200/",
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
        },
        {
            "bk_scope_type": "biz",
            "bk_scope_id": "321456",
            "bk_biz_id": 321456,
            "file_source_list": [
                {
                    "file_list": ["/tmp/cc", "/tmp/dd"],
                    "server": {
                        "ip_list": [{"ip": "127.0.0.2", "bk_cloud_id": 1}],
                    },
                    "account": {
                        "alias": "user00",
                    },
                }
            ],
            "target_server": {
                "ip_list": [
                    {"ip": "127.0.0.3", "bk_cloud_id": 0},
                    {"ip": "127.0.0.4", "bk_cloud_id": 0},
                    {"ip": "127.0.0.5", "bk_cloud_id": 0},
                ],
            },
            "account_alias": "root",
            "file_target_path": "/tmp/ee/",
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
        },
        {
            "bk_scope_type": "biz",
            "bk_scope_id": "321456",
            "bk_biz_id": 321456,
            "file_source_list": [
                {
                    "file_list": ["/tmp/cc", "/tmp/dd"],
                    "server": {
                        "ip_list": [{"ip": "127.0.0.2", "bk_cloud_id": 1}],
                    },
                    "account": {
                        "alias": "user00",
                    },
                }
            ],
            "target_server": {
                "ip_list": [
                    {"ip": "200.0.0.1", "bk_cloud_id": 1},
                    {"ip": "200.0.0.2", "bk_cloud_id": 1},
                    {"ip": "200.0.0.3", "bk_cloud_id": 1},
                ],
            },
            "account_alias": "user01",
            "file_target_path": "/tmp/200/",
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
        },
    ]
)

BIZ_SET_CLL_INFO = MagicMock(
    side_effect=[
        {
            "bk_scope_type": "biz_set",
            "bk_scope_id": "321456",
            "bk_biz_id": 321456,
            "file_source_list": [
                {
                    "file_list": ["/tmp/aa", "/tmp/bb"],
                    "server": {
                        "ip_list": [{"ip": "127.0.0.1", "bk_cloud_id": 0}],
                    },
                    "account": {
                        "alias": "root",
                    },
                }
            ],
            "target_server": {
                "ip_list": [
                    {"ip": "127.0.0.3", "bk_cloud_id": 0},
                    {"ip": "127.0.0.4", "bk_cloud_id": 0},
                    {"ip": "127.0.0.5", "bk_cloud_id": 0},
                ],
            },
            "account_alias": "root",
            "file_target_path": "/tmp/ee/",
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
        },
        {
            "bk_scope_type": "biz_set",
            "bk_scope_id": "321456",
            "bk_biz_id": 321456,
            "file_source_list": [
                {
                    "file_list": ["/tmp/aa", "/tmp/bb"],
                    "server": {
                        "ip_list": [{"ip": "127.0.0.1", "bk_cloud_id": 0}],
                    },
                    "account": {
                        "alias": "root",
                    },
                }
            ],
            "target_server": {
                "ip_list": [
                    {"ip": "200.0.0.1", "bk_cloud_id": 1},
                    {"ip": "200.0.0.2", "bk_cloud_id": 1},
                    {"ip": "200.0.0.3", "bk_cloud_id": 1},
                ],
            },
            "account_alias": "user01",
            "file_target_path": "/tmp/200/",
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
        },
        {
            "bk_scope_type": "biz_set",
            "bk_scope_id": "321456",
            "bk_biz_id": 321456,
            "file_source_list": [
                {
                    "file_list": ["/tmp/cc", "/tmp/dd"],
                    "server": {
                        "ip_list": [{"ip": "127.0.0.2", "bk_cloud_id": 1}],
                    },
                    "account": {
                        "alias": "user00",
                    },
                }
            ],
            "target_server": {
                "ip_list": [
                    {"ip": "127.0.0.3", "bk_cloud_id": 0},
                    {"ip": "127.0.0.4", "bk_cloud_id": 0},
                    {"ip": "127.0.0.5", "bk_cloud_id": 0},
                ],
            },
            "account_alias": "root",
            "file_target_path": "/tmp/ee/",
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
        },
        {
            "bk_scope_type": "biz_set",
            "bk_scope_id": "321456",
            "bk_biz_id": 321456,
            "file_source_list": [
                {
                    "file_list": ["/tmp/cc", "/tmp/dd"],
                    "server": {
                        "ip_list": [{"ip": "127.0.0.2", "bk_cloud_id": 1}],
                    },
                    "account": {
                        "alias": "user00",
                    },
                }
            ],
            "target_server": {
                "ip_list": [
                    {"ip": "200.0.0.1", "bk_cloud_id": 1},
                    {"ip": "200.0.0.2", "bk_cloud_id": 1},
                    {"ip": "200.0.0.3", "bk_cloud_id": 1},
                ],
            },
            "account_alias": "user01",
            "file_target_path": "/tmp/200/",
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
        },
    ]
)


def PUSH_FILE_TO_IPS_FAIL_CASE():
    return ComponentTestCase(
        name="all biz fast_push_files v1.0  call fail case",
        inputs=INPUT,
        parent_data={"executor": "executor", "project_id": "project_id"},
        execute_assertion=ExecuteAssertion(
            success=True,
            outputs={
                "requests_error": "Request Error:\nfailed\n",
                "task_count": 4,
                "job_instance_id_list": [10000, 10001, 10002],
                "job_id_of_batch_execute": [10000, 10001, 10002],
                "job_inst_url": ["job.com/api_execute/", "job.com/api_execute/", "job.com/api_execute/"],
                "request_success_count": 3,
                "success_count": 0,
                "final_res": False,
            },
        ),
        execute_call_assertion=[
            CallAssertion(
                func=FAST_PUSH_FILE_REQUEST_FAILURE_CLIENT.jobv3.fast_transfer_file,
                calls=[Call(**CLL_INFO()), Call(**CLL_INFO()), Call(**CLL_INFO()), Call(**CLL_INFO())],
            ),
        ],
        schedule_assertion=ScheduleAssertion(
            success=False,
            outputs={
                "requests_error": "Request Error:\nfailed\n",
                "task_count": 4,
                "job_instance_id_list": [10000, 10001, 10002],
                "job_id_of_batch_execute": [],
                "job_inst_url": ["job.com/api_execute/", "job.com/api_execute/", "job.com/api_execute/"],
                "request_success_count": 3,
                "success_count": 3,
                "final_res": False,
                "ex_data": "Request Error:\nfailed\n\n Get Result Error:\n",
            },
            schedule_finished=True,
        ),
        patchers=[
            Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_REQUEST_FAILURE_CLIENT),
            Patcher(target=UTILS_GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_REQUEST_FAILURE_CLIENT),
            Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_REQUEST_FAILURE_CLIENT),
            Patcher(target=JOB_HANDLE_API_ERROR, return_value="failed"),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value="job.com/api_execute/"),
        ],
    )


def BIZ_SET_PUSH_FILE_TO_IPS_FAIL_CASE():
    return ComponentTestCase(
        name="all biz biz set fast_push_files v1.0  call fail case",
        inputs=INPUT,
        parent_data={"executor": "executor", "project_id": "project_id"},
        execute_assertion=ExecuteAssertion(
            success=True,
            outputs={
                "requests_error": "Request Error:\nfailed\n",
                "task_count": 4,
                "job_instance_id_list": [10000, 10001, 10002],
                "job_id_of_batch_execute": [10000, 10001, 10002],
                "job_inst_url": ["job.com/api_execute/", "job.com/api_execute/", "job.com/api_execute/"],
                "request_success_count": 3,
                "success_count": 0,
                "final_res": False,
            },
        ),
        execute_call_assertion=[
            CallAssertion(
                func=FAST_PUSH_FILE_BIZ_SET_REQUEST_FAILURE_CLIENT.jobv3.fast_transfer_file,
                calls=[
                    Call(**BIZ_SET_CLL_INFO()),
                    Call(**BIZ_SET_CLL_INFO()),
                    Call(**BIZ_SET_CLL_INFO()),
                    Call(**BIZ_SET_CLL_INFO()),
                ],
            ),
        ],
        schedule_assertion=ScheduleAssertion(
            success=False,
            outputs={
                "requests_error": "Request Error:\nfailed\n",
                "task_count": 4,
                "job_instance_id_list": [10000, 10001, 10002],
                "job_id_of_batch_execute": [],
                "job_inst_url": ["job.com/api_execute/", "job.com/api_execute/", "job.com/api_execute/"],
                "request_success_count": 3,
                "success_count": 3,
                "final_res": False,
                "ex_data": "Request Error:\nfailed\n\n Get Result Error:\n",
            },
            schedule_finished=True,
        ),
        patchers=[
            Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_BIZ_SET_REQUEST_FAILURE_CLIENT),
            Patcher(target=UTILS_GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_BIZ_SET_REQUEST_FAILURE_CLIENT),
            Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_BIZ_SET_REQUEST_FAILURE_CLIENT),
            Patcher(target=JOB_HANDLE_API_ERROR, return_value="failed"),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value="job.com/api_execute/"),
        ],
    )
