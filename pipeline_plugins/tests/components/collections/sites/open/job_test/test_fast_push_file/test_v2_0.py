# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock
from pipeline.component_framework.test import (
    Call,
    CallAssertion,
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    Patcher,
    ScheduleAssertion,
)

from pipeline_plugins.components.collections.sites.open.job.fast_push_file.v2_0 import JobFastPushFileComponent
from pipeline_plugins.tests.components.collections.sites.open.utils.cc_ipv6_mock_utils import MockCMDBClientIPv6


class MockCMDBClient(MockCMDBClientIPv6):
    pass


class JobFastPushFilesComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            PUSH_FILE_AUTO_EXPANSION_CASE(),
            PUSH_FILE_FAIL_CASE(),
        ]

    def component_cls(self):
        return JobFastPushFileComponent

    def input_output_format_valid(self):
        pass

    def setUp(self):
        super().setUp()
        from django.conf import settings

        self._original_enable_ipv6 = getattr(settings, "ENABLE_IPV6", False)
        setattr(settings, "ENABLE_IPV6", False)

    def tearDown(self):
        super().tearDown()
        from django.conf import settings

        setattr(settings, "ENABLE_IPV6", self._original_enable_ipv6)


class JobMockClient(object):
    def __init__(self, fast_push_file_return=None, get_job_instance_status_return=None):
        self.api = MagicMock()
        self.api.fast_transfer_file = MagicMock(side_effect=fast_push_file_return)
        self.api.get_job_instance_status = MagicMock(side_effect=get_job_instance_status_return)


class CcMockClient(object):
    def __init__(self, list_business_set_return=None):
        self.api = MagicMock()
        self.api.list_business_set = MagicMock(return_value=list_business_set_return)


GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.fast_push_file.v2_0.get_client_by_username"
CC_GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username"
CMDB_GET_CLIENT_BY_USERNAME = "gcloud.utils.cmdb.get_client_by_username"
BASE_GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username"
GET_JOB_INSTANCE_URL = "pipeline_plugins.components.collections.sites.open.job.fast_push_file.v2_0.get_job_instance_url"
JOB_HANDLE_API_ERROR = "pipeline_plugins.components.collections.sites.open.job.fast_push_file.v2_0.job_handle_api_error"
UTILS_GET_CLIENT_BY_USER = "pipeline_plugins.components.utils.cc.get_client_by_username"
CHUNK_TABLE_DATA = "pipeline_plugins.components.collections.sites.open.job.fast_push_file.v2_0.chunk_table_data"
GET_BIZ_IP_FROM_FRONTEND = "pipeline_plugins.components.collections.sites.open.job.ipv6_base.get_biz_ip_from_frontend"

INPUT = {
    "biz_cc_id": 1,
    "job_source_files": [
        {"ip": "0:127.0.0.1", "files": "/tmp/aa\n/tmp/bb", "account": "root"},
    ],
    "upload_speed_limit": "100",
    "download_speed_limit": "100",
    "select_method": "auto",
    "break_line": ",",
    "job_dispatch_attr": ["0:127.0.0.3,0:127.0.0.4;/tmp/ee/,/tmp/ff/;root,user01"],
    "job_timeout": "100",
}

INVALID_IP_CLIENT = CcMockClient(list_business_set_return={"result": True, "data": {"info": []}})

FAST_PUSH_FILE_SUCCESS_CLIENT = JobMockClient(
    fast_push_file_return=[
        {
            "result": True,
            "code": 0,
            "message": "success",
            "data": {"job_instance_name": "API Quick Distribution File", "job_instance_id": 10000},
        }
    ],
    get_job_instance_status_return=[
        {"data": {"finished": True, "job_instance": {"status": 3}}, "result": True},
    ],
)

FAST_PUSH_FILE_FAIL_CLIENT = JobMockClient(
    fast_push_file_return=[
        {
            "result": False,
            "code": 1,
            "message": "failed",
            "data": {},
        }
    ],
)


def PUSH_FILE_AUTO_EXPANSION_CASE():
    return ComponentTestCase(
        name="fast_push_files v2_0 auto expansion success",
        inputs=INPUT,
        parent_data={"executor": "executor", "project_id": "project_id", "biz_cc_id": 1, "tenant_id": "system"},
        execute_assertion=ExecuteAssertion(
            success=True,
            outputs={
                "task_count": 1,
                "request_success_count": 1,
                "success_count": 0,
                "final_res": True,
                "requests_error": "",
                "job_instance_id_list": [10000],
                "job_id_of_batch_execute": [10000],
                "job_inst_url": ["job.com/api_execute/"],
            },
        ),
        execute_call_assertion=[
            CallAssertion(
                func=FAST_PUSH_FILE_SUCCESS_CLIENT.api.fast_transfer_file,
                calls=[
                    Call(
                        data={
                            "bk_scope_type": "biz",
                            "bk_scope_id": "1",
                            "bk_biz_id": 1,
                            "file_source_list": [
                                {
                                    "file_list": ["/tmp/aa", "/tmp/bb"],
                                    "server": {"ip_list": [{"ip": "127.0.0.1", "bk_cloud_id": 0}]},
                                    "account": {"alias": "root"},
                                }
                            ],
                            "target_server": {
                                "ip_list": [
                                    {"ip": "127.0.0.3", "bk_cloud_id": 0},
                                ]
                            },
                            "account_alias": "root",
                            "file_target_path": "/tmp/ee/",
                            "upload_speed_limit": 100,
                            "download_speed_limit": 100,
                            "timeout": 100,
                        },
                        headers={"X-Bk-Tenant-Id": "system"},
                    )
                ],
            ),
        ],
        schedule_assertion=ScheduleAssertion(
            success=True,
            schedule_finished=True,
            outputs={
                "task_count": 1,
                "request_success_count": 1,
                "success_count": 1,
                "job_instance_id_list": [10000],
                "job_inst_url": ["job.com/api_execute/"],
                "requests_error": "",
                "job_id_of_batch_execute": [],
                "final_res": True,
            },
        ),
        patchers=[
            Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
            Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
            Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_SUCCESS_CLIENT),
            Patcher(target=UTILS_GET_CLIENT_BY_USER, return_value=INVALID_IP_CLIENT),
            Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_SUCCESS_CLIENT),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value="job.com/api_execute/"),
            Patcher(
                target=CHUNK_TABLE_DATA,
                return_value={
                    "result": True,
                    "data": [{"job_ip_list": "0:127.0.0.3", "job_target_path": "/tmp/ee/", "job_account": "root"}],
                },
            ),
            Patcher(
                target=GET_BIZ_IP_FROM_FRONTEND,
                side_effect=[
                    (True, [{"ip": "127.0.0.1", "bk_cloud_id": 0}]),
                    (True, [{"ip": "127.0.0.3", "bk_cloud_id": 0}]),
                ],
            ),
        ],
    )


def PUSH_FILE_FAIL_CASE():
    return ComponentTestCase(
        name="fast_push_files v2_0 call fail case",
        inputs=INPUT,
        parent_data={"executor": "executor", "project_id": "project_id", "biz_cc_id": 1, "tenant_id": "system"},
        execute_assertion=ExecuteAssertion(
            success=False,
            outputs={
                "requests_error": "Request Error:\nfailed\n",
                "task_count": 1,
                "job_instance_id_list": [],
                "job_id_of_batch_execute": [],
                "job_inst_url": [],
                "request_success_count": 0,
                "success_count": 0,
                "ex_data": "Request Error:\nfailed\n",
            },
        ),
        schedule_assertion=None,
        patchers=[
            Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
            Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
            Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_FAIL_CLIENT),
            Patcher(target=UTILS_GET_CLIENT_BY_USER, return_value=INVALID_IP_CLIENT),
            Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_FAIL_CLIENT),
            Patcher(target=JOB_HANDLE_API_ERROR, return_value="failed"),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value="job.com/api_execute/"),
            Patcher(
                target=CHUNK_TABLE_DATA,
                return_value={
                    "result": True,
                    "data": [{"job_ip_list": "0:127.0.0.3", "job_target_path": "/tmp/ee/", "job_account": "root"}],
                },
            ),
            Patcher(
                target=GET_BIZ_IP_FROM_FRONTEND,
                side_effect=[
                    (True, [{"ip": "127.0.0.1", "bk_cloud_id": 0}]),
                    (True, [{"ip": "127.0.0.3", "bk_cloud_id": 0}]),
                ],
            ),
        ],
    )
