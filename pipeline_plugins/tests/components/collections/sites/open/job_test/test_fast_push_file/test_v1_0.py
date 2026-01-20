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

from pipeline_plugins.components.collections.sites.open.job.fast_push_file.v1_0 import JobFastPushFileComponent
from pipeline_plugins.tests.components.collections.sites.open.utils.cc_ipv6_mock_utils import MockCMDBClientIPv6


class MockCMDBClient(MockCMDBClientIPv6):
    pass


class JobFastPushFilesComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            PUSH_FILE_SUCCESS_CASE(),
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


GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.fast_push_file.v1_0.get_client_by_username"
CC_GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username"
CMDB_GET_CLIENT_BY_USERNAME = "gcloud.utils.cmdb.get_client_by_username"
BASE_GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username"
GET_JOB_INSTANCE_URL = "pipeline_plugins.components.collections.sites.open.job.fast_push_file.v1_0.get_job_instance_url"
JOB_HANDLE_API_ERROR = "pipeline_plugins.components.collections.sites.open.job.fast_push_file.v1_0.job_handle_api_error"
GET_NODE_CALLBACK_URL = (
    "pipeline_plugins.components.collections.sites.open.job.fast_push_file.v1_0.get_node_callback_url"
)
GET_BIZ_IP_FROM_FRONTEND = "pipeline_plugins.components.collections.sites.open.job.ipv6_base.get_biz_ip_from_frontend"

INPUT = {
    "biz_cc_id": 1,
    "job_source_files": [
        {"ip": "127.0.0.1", "files": "/tmp/aa\n/tmp/bb", "account": "root"},
    ],
    "job_ip_list": "127.0.0.3,127.0.0.4",
    "job_account": "root",
    "job_target_path": "/tmp/ee/",
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


def PUSH_FILE_SUCCESS_CASE():
    return ComponentTestCase(
        name="fast_push_files v1_0 success",
        inputs=INPUT,
        parent_data={"executor": "executor", "project_id": "project_id", "biz_cc_id": 1, "tenant_id": "system"},
        execute_assertion=ExecuteAssertion(
            success=True,
            outputs={
                "job_inst_id": 10000,
                "job_inst_name": "API Quick Distribution File",
                "job_inst_url": "job.com/api_execute/",
            },
        ),
        execute_call_assertion=[
            CallAssertion(
                func=FAST_PUSH_FILE_SUCCESS_CLIENT.api.fast_transfer_file,
                calls=[
                    Call(
                        {
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
                                    {"ip": "127.0.0.4", "bk_cloud_id": 0},
                                ]
                            },
                            "account_alias": "root",
                            "file_target_path": "/tmp/ee/",
                            "callback_url": "callback_url",
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
            callback_data={"job_instance_id": 10000, "status": 3},
            outputs={
                "job_inst_id": 10000,
                "job_inst_name": "API Quick Distribution File",
                "job_inst_url": "job.com/api_execute/",
            },
        ),
        patchers=[
            Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
            Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
            Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_SUCCESS_CLIENT),
            Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_SUCCESS_CLIENT),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value="job.com/api_execute/"),
            Patcher(target=GET_NODE_CALLBACK_URL, return_value="callback_url"),
            Patcher(
                target=GET_BIZ_IP_FROM_FRONTEND,
                side_effect=[
                    (True, [{"ip": "127.0.0.1", "bk_cloud_id": 0}]),
                    (True, [{"ip": "127.0.0.3", "bk_cloud_id": 0}, {"ip": "127.0.0.4", "bk_cloud_id": 0}]),
                ],
            ),
        ],
    )


def PUSH_FILE_FAIL_CASE():
    return ComponentTestCase(
        name="fast_push_files v1_0 fail case",
        inputs=INPUT,
        parent_data={"executor": "executor", "project_id": "project_id", "biz_cc_id": 1, "tenant_id": "system"},
        execute_assertion=ExecuteAssertion(
            success=False,
            outputs={
                "ex_data": "failed",
            },
        ),
        schedule_assertion=None,
        patchers=[
            Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
            Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
            Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_FAIL_CLIENT),
            Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_FAIL_CLIENT),
            Patcher(target=JOB_HANDLE_API_ERROR, return_value="failed"),
            Patcher(target=GET_NODE_CALLBACK_URL, return_value="callback_url"),
            Patcher(
                target=GET_BIZ_IP_FROM_FRONTEND,
                side_effect=[
                    (True, [{"ip": "127.0.0.1", "bk_cloud_id": 0}]),
                    (True, [{"ip": "127.0.0.3", "bk_cloud_id": 0}, {"ip": "127.0.0.4", "bk_cloud_id": 0}]),
                ],
            ),
        ],
    )
