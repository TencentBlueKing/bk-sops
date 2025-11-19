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
from django.conf import settings
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

from pipeline_plugins.components.collections.sites.open.job.all_biz_fast_push_file.v1_0 import (
    AllBizJobFastPushFileComponent,
)
from pipeline_plugins.tests.components.collections.sites.open.utils.cc_ipv6_mock_utils import (
    CC_GET_HOST_BY_INNERIP_WITH_IPV6_PATCH,
    MockCMDBClientIPv6,
)


# MockCMDBClient class definition for IPv6 support
class MockCMDBClient(MockCMDBClientIPv6):
    pass


# Helper function to check if IPv6 is enabled
def is_ipv6_enabled():
    """检查是否启用 IPv6 模式"""
    return getattr(settings, "ENABLE_IPV6", False)


# Helper function to create environment-aware target_server
def get_expected_target_server(hosts):
    """
    获取期望的 target_server 格式
    Args:
        hosts: list of dicts with keys: bk_host_id, bk_cloud_id, and optionally ip
    Returns:
        dict with either host_id_list or ip_list based on environment
    """
    if is_ipv6_enabled():
        return {"host_id_list": [host["bk_host_id"] for host in hosts]}
    else:
        return {"ip_list": [{"ip": host.get("ip", "1.1.1.1"), "bk_cloud_id": host["bk_cloud_id"]} for host in hosts]}


# Helper function to create get_business_host return value
def create_get_business_host_return(hosts):
    """
    Create mock return value for get_business_host
    hosts: list of dict with keys: bk_host_id, bk_host_innerip, bk_cloud_id
    """
    return [
        {
            "bk_host_id": host["bk_host_id"],
            "bk_host_innerip": host["bk_host_innerip"],
            "bk_cloud_id": host["bk_cloud_id"],
        }
        for host in hosts
    ]


# Helper function to create smart mock for cc_get_host_by_innerip_with_ipv6
def create_smart_ipv6_mock(all_hosts):
    """
    Create a smart mock that returns only the hosts matching the queried IPs
    """

    def _mock(tenant_id, executor, bk_biz_id, ip_str, is_biz_set=False, host_id_detail=False):
        # Parse ip_str to extract IPs
        # Format can be: "0:127.0.0.1,127.0.0.2" or "127.0.0.1;127.0.0.2"
        matching_hosts = []

        # Split by comma first
        ip_parts = ip_str.replace(";", ",").split(",")

        for part in ip_parts:
            part = part.strip()
            if ":" in part:
                # Format: "cloud_id:ip"
                cloud_str, ip = part.split(":", 1)
                cloud_id = int(cloud_str)

                # Find matching host
                for host in all_hosts:
                    if host.get("bk_host_innerip") == ip and host.get("bk_cloud_id") == cloud_id:
                        if host not in matching_hosts:
                            matching_hosts.append(host)
            else:
                # Just IP without cloud_id
                for host in all_hosts:
                    if host.get("bk_host_innerip") == part:
                        if host not in matching_hosts:
                            matching_hosts.append(host)

        return {"result": True, "data": matching_hosts, "message": "success"}

    return _mock


class AllBizJobFastPushFilesComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [PUSH_FILE_TO_IPS_FAIL_CASE(), BIZ_SET_PUSH_FILE_TO_IPS_FAIL_CASE()]

    def component_cls(self):
        return AllBizJobFastPushFileComponent


class JobMockClient(object):
    def __init__(
        self,
        fast_push_file_return=None,
        get_job_instance_status_return=None,
    ):
        self.api = MagicMock()
        self.api.fast_transfer_file = MagicMock(side_effect=fast_push_file_return)
        self.api.get_job_instance_status = MagicMock(side_effect=get_job_instance_status_return)


class CcMockClient(object):
    def __init__(self, list_business_set_return=None):
        self.api = MagicMock()
        self.api.list_business_set = MagicMock(return_value=list_business_set_return)


class BkUserMockClient(object):
    def __init__(self, batch_lookup_virtual_user_return=None):
        self.api = MagicMock()
        self.api.batch_lookup_virtual_user = MagicMock(return_value=batch_lookup_virtual_user_return)


# mock path
GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.job.all_biz_fast_push_file.base_service.get_client_by_username"
)
BASE_GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username"

# 添加 CC client mock 路径，用于 IPv6 支持
CC_GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username"
CMDB_GET_CLIENT_BY_USERNAME = "gcloud.utils.cmdb.get_client_by_username"
CMDB_GET_BUSINESS_HOST = "gcloud.utils.cmdb.get_business_host"

GET_JOB_INSTANCE_URL = (
    "pipeline_plugins.components.collections.sites.open.job.all_biz_fast_push_file.base_service.get_job_instance_url"
)

JOB_HANDLE_API_ERROR = (
    "pipeline_plugins.components.collections.sites.open.job.all_biz_fast_push_file.base_service.job_handle_api_error"
)
UTILS_GET_CLIENT_BY_USER = "pipeline_plugins.components.utils.cc.get_client_by_username"

VIRTUAL_USERNAME_GET_CLIENT_BY_USER = "gcloud.core.api_adapter.user_info.get_client_by_username"

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

FAST_PUSH_FILE_REQUEST_FAILURE_CLIENT = JobMockClient(
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
)

FAST_PUSH_FILE_BIZ_SET_REQUEST_FAILURE_CLIENT = JobMockClient(
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
)

INVALID_IP_CLIENT = CcMockClient(
    list_business_set_return={"result": True, "data": {"info": []}},
)

INVALID_IP_CLIENT_BIZ_SET = CcMockClient(
    list_business_set_return={"result": True, "data": {"info": ["biz_set"]}},
)

CLL_INFO = MagicMock(
    side_effect=[
        {
            "data": {
                "bk_scope_type": "biz",
                "bk_scope_id": "321456",
                "bk_biz_id": 321456,
                "file_source_list": [
                    {
                        "file_list": ["/tmp/aa", "/tmp/bb"],
                        "server": {
                            "host_id_list": [1],
                        },
                        "account": {
                            "alias": "root",
                        },
                    }
                ],
                "target_server": {
                    "host_id_list": [3, 4, 5],
                },
                "account_alias": "root",
                "file_target_path": "/tmp/ee/",
            },
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
            "headers": {"X-Bk-Tenant-Id": "system"},
        },
        {
            "data": {
                "bk_scope_type": "biz",
                "bk_scope_id": "321456",
                "bk_biz_id": 321456,
                "file_source_list": [
                    {
                        "file_list": ["/tmp/aa", "/tmp/bb"],
                        "server": {
                            "host_id_list": [1],
                        },
                        "account": {
                            "alias": "root",
                        },
                    }
                ],
                "target_server": {
                    "host_id_list": [6, 7, 8],
                },
                "account_alias": "user01",
                "file_target_path": "/tmp/200/",
            },
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
            "headers": {"X-Bk-Tenant-Id": "system"},
        },
        {
            "data": {
                "bk_scope_type": "biz",
                "bk_scope_id": "321456",
                "bk_biz_id": 321456,
                "file_source_list": [
                    {
                        "file_list": ["/tmp/cc", "/tmp/dd"],
                        "server": {
                            "host_id_list": [2],
                        },
                        "account": {
                            "alias": "user00",
                        },
                    }
                ],
                "target_server": {
                    "host_id_list": [3, 4, 5],
                },
                "account_alias": "root",
                "file_target_path": "/tmp/ee/",
            },
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
            "headers": {"X-Bk-Tenant-Id": "system"},
        },
        {
            "data": {
                "bk_scope_type": "biz",
                "bk_scope_id": "321456",
                "bk_biz_id": 321456,
                "file_source_list": [
                    {
                        "file_list": ["/tmp/cc", "/tmp/dd"],
                        "server": {
                            "host_id_list": [2],
                        },
                        "account": {
                            "alias": "user00",
                        },
                    }
                ],
                "target_server": {
                    "host_id_list": [6, 7, 8],
                },
                "account_alias": "user01",
                "file_target_path": "/tmp/200/",
            },
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
            "headers": {"X-Bk-Tenant-Id": "system"},
        },
    ]
)

BIZ_SET_CLL_INFO = MagicMock(
    side_effect=[
        {
            "data": {
                "bk_scope_type": "biz_set",
                "bk_scope_id": "321456",
                "bk_biz_id": 321456,
                "file_source_list": [
                    {
                        "file_list": ["/tmp/aa", "/tmp/bb"],
                        "server": {
                            "host_id_list": [1],
                        },
                        "account": {
                            "alias": "root",
                        },
                    }
                ],
                "target_server": {
                    "host_id_list": [3, 4, 5],
                },
                "account_alias": "root",
                "file_target_path": "/tmp/ee/",
            },
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
            "headers": {"X-Bk-Tenant-Id": "system"},
        },
        {
            "data": {
                "bk_scope_type": "biz_set",
                "bk_scope_id": "321456",
                "bk_biz_id": 321456,
                "file_source_list": [
                    {
                        "file_list": ["/tmp/aa", "/tmp/bb"],
                        "server": {
                            "host_id_list": [1],
                        },
                        "account": {
                            "alias": "root",
                        },
                    }
                ],
                "target_server": {
                    "host_id_list": [6, 7, 8],
                },
                "account_alias": "user01",
                "file_target_path": "/tmp/200/",
            },
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
            "headers": {"X-Bk-Tenant-Id": "system"},
        },
        {
            "data": {
                "bk_scope_type": "biz_set",
                "bk_scope_id": "321456",
                "bk_biz_id": 321456,
                "file_source_list": [
                    {
                        "file_list": ["/tmp/cc", "/tmp/dd"],
                        "server": {
                            "host_id_list": [2],
                        },
                        "account": {
                            "alias": "user00",
                        },
                    }
                ],
                "target_server": {
                    "host_id_list": [3, 4, 5],
                },
                "account_alias": "root",
                "file_target_path": "/tmp/ee/",
            },
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
            "headers": {"X-Bk-Tenant-Id": "system"},
        },
        {
            "data": {
                "bk_scope_type": "biz_set",
                "bk_scope_id": "321456",
                "bk_biz_id": 321456,
                "file_source_list": [
                    {
                        "file_list": ["/tmp/cc", "/tmp/dd"],
                        "server": {
                            "host_id_list": [2],
                        },
                        "account": {
                            "alias": "user00",
                        },
                    }
                ],
                "target_server": {
                    "host_id_list": [6, 7, 8],
                },
                "account_alias": "user01",
                "file_target_path": "/tmp/200/",
            },
            "upload_speed_limit": 100,
            "download_speed_limit": 100,
            "timeout": 100,
            "headers": {"X-Bk-Tenant-Id": "system"},
        },
    ]
)


BK_USER_CLIENT = BkUserMockClient(
    batch_lookup_virtual_user_return={
        "data": [
            {"bk_username": "7idwx3b7nzk6xigs", "login_name": "zhangsan", "display_name": "zhangsan(张三)"},
            {"bk_username": "0wngfim3uzhadh1w", "login_name": "lisi", "display_name": "lisi(李四)"},
        ]
    },
)


def PUSH_FILE_TO_IPS_FAIL_CASE():
    return ComponentTestCase(
        name="all biz fast_push_files v1.0  call fail case",
        inputs=INPUT,
        parent_data={"executor": "executor", "project_id": "project_id", "tenant_id": "system"},
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
                func=FAST_PUSH_FILE_REQUEST_FAILURE_CLIENT.api.fast_transfer_file,
                calls=[
                    Call(
                        data={
                            "bk_scope_type": "biz",
                            "bk_scope_id": "321456",
                            "bk_biz_id": 321456,
                            "file_source_list": [
                                {
                                    "file_list": ["/tmp/aa", "/tmp/bb"],
                                    "server": get_expected_target_server(
                                        [{"bk_host_id": 1, "bk_cloud_id": 0, "ip": "127.0.0.1"}]
                                    ),
                                    "account": {"alias": "root"},
                                }
                            ],
                            "target_server": get_expected_target_server(
                                [
                                    {"bk_host_id": 3, "bk_cloud_id": 0, "ip": "127.0.0.3"},
                                    {"bk_host_id": 4, "bk_cloud_id": 0, "ip": "127.0.0.4"},
                                    {"bk_host_id": 5, "bk_cloud_id": 0, "ip": "127.0.0.5"},
                                ]
                            ),
                            "account_alias": "root",
                            "file_target_path": "/tmp/ee/",
                        },
                        headers={"X-Bk-Tenant-Id": "system"},
                        upload_speed_limit=100,
                        download_speed_limit=100,
                        timeout=100,
                    ),
                    Call(
                        data={
                            "bk_scope_type": "biz",
                            "bk_scope_id": "321456",
                            "bk_biz_id": 321456,
                            "file_source_list": [
                                {
                                    "file_list": ["/tmp/aa", "/tmp/bb"],
                                    "server": get_expected_target_server(
                                        [{"bk_host_id": 1, "bk_cloud_id": 0, "ip": "127.0.0.1"}]
                                    ),
                                    "account": {"alias": "root"},
                                }
                            ],
                            "target_server": get_expected_target_server(
                                [
                                    {"bk_host_id": 6, "bk_cloud_id": 1, "ip": "200.0.0.1"},
                                    {"bk_host_id": 7, "bk_cloud_id": 1, "ip": "200.0.0.2"},
                                    {"bk_host_id": 8, "bk_cloud_id": 1, "ip": "200.0.0.3"},
                                ]
                            ),
                            "account_alias": "user01",
                            "file_target_path": "/tmp/200/",
                        },
                        headers={"X-Bk-Tenant-Id": "system"},
                        upload_speed_limit=100,
                        download_speed_limit=100,
                        timeout=100,
                    ),
                    Call(
                        data={
                            "bk_scope_type": "biz",
                            "bk_scope_id": "321456",
                            "bk_biz_id": 321456,
                            "file_source_list": [
                                {
                                    "file_list": ["/tmp/cc", "/tmp/dd"],
                                    "server": get_expected_target_server(
                                        [{"bk_host_id": 2, "bk_cloud_id": 1, "ip": "127.0.0.2"}]
                                    ),
                                    "account": {"alias": "user00"},
                                }
                            ],
                            "target_server": get_expected_target_server(
                                [
                                    {"bk_host_id": 3, "bk_cloud_id": 0, "ip": "127.0.0.3"},
                                    {"bk_host_id": 4, "bk_cloud_id": 0, "ip": "127.0.0.4"},
                                    {"bk_host_id": 5, "bk_cloud_id": 0, "ip": "127.0.0.5"},
                                ]
                            ),
                            "account_alias": "root",
                            "file_target_path": "/tmp/ee/",
                        },
                        headers={"X-Bk-Tenant-Id": "system"},
                        upload_speed_limit=100,
                        download_speed_limit=100,
                        timeout=100,
                    ),
                    Call(
                        data={
                            "bk_scope_type": "biz",
                            "bk_scope_id": "321456",
                            "bk_biz_id": 321456,
                            "file_source_list": [
                                {
                                    "file_list": ["/tmp/cc", "/tmp/dd"],
                                    "server": get_expected_target_server(
                                        [{"bk_host_id": 2, "bk_cloud_id": 1, "ip": "127.0.0.2"}]
                                    ),
                                    "account": {"alias": "user00"},
                                }
                            ],
                            "target_server": get_expected_target_server(
                                [
                                    {"bk_host_id": 6, "bk_cloud_id": 1, "ip": "200.0.0.1"},
                                    {"bk_host_id": 7, "bk_cloud_id": 1, "ip": "200.0.0.2"},
                                    {"bk_host_id": 8, "bk_cloud_id": 1, "ip": "200.0.0.3"},
                                ]
                            ),
                            "account_alias": "user01",
                            "file_target_path": "/tmp/200/",
                        },
                        headers={"X-Bk-Tenant-Id": "system"},
                        upload_speed_limit=100,
                        download_speed_limit=100,
                        timeout=100,
                    ),
                ],
            )
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
            Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
            Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
            Patcher(
                target=CMDB_GET_BUSINESS_HOST,
                return_value=create_get_business_host_return(
                    [
                        {"bk_host_id": 1, "bk_host_innerip": "127.0.0.1", "bk_cloud_id": 0},
                        {"bk_host_id": 2, "bk_host_innerip": "127.0.0.2", "bk_cloud_id": 1},
                        {"bk_host_id": 3, "bk_host_innerip": "127.0.0.3", "bk_cloud_id": 0},
                        {"bk_host_id": 4, "bk_host_innerip": "127.0.0.4", "bk_cloud_id": 0},
                        {"bk_host_id": 5, "bk_host_innerip": "127.0.0.5", "bk_cloud_id": 0},
                        {"bk_host_id": 6, "bk_host_innerip": "200.0.0.1", "bk_cloud_id": 1},
                        {"bk_host_id": 7, "bk_host_innerip": "200.0.0.2", "bk_cloud_id": 1},
                        {"bk_host_id": 8, "bk_host_innerip": "200.0.0.3", "bk_cloud_id": 1},
                    ]
                ),
            ),
            Patcher(
                target=CC_GET_HOST_BY_INNERIP_WITH_IPV6_PATCH,
                side_effect=create_smart_ipv6_mock(
                    [
                        {"bk_host_id": 1, "bk_host_innerip": "127.0.0.1", "bk_cloud_id": 0},
                        {"bk_host_id": 2, "bk_host_innerip": "127.0.0.2", "bk_cloud_id": 1},
                        {"bk_host_id": 3, "bk_host_innerip": "127.0.0.3", "bk_cloud_id": 0},
                        {"bk_host_id": 4, "bk_host_innerip": "127.0.0.4", "bk_cloud_id": 0},
                        {"bk_host_id": 5, "bk_host_innerip": "127.0.0.5", "bk_cloud_id": 0},
                        {"bk_host_id": 6, "bk_host_innerip": "200.0.0.1", "bk_cloud_id": 1},
                        {"bk_host_id": 7, "bk_host_innerip": "200.0.0.2", "bk_cloud_id": 1},
                        {"bk_host_id": 8, "bk_host_innerip": "200.0.0.3", "bk_cloud_id": 1},
                    ]
                ),
            ),
            Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_REQUEST_FAILURE_CLIENT),
            Patcher(target=UTILS_GET_CLIENT_BY_USER, return_value=INVALID_IP_CLIENT),
            Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_REQUEST_FAILURE_CLIENT),
            Patcher(target=JOB_HANDLE_API_ERROR, return_value="failed"),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value="job.com/api_execute/"),
            Patcher(target=VIRTUAL_USERNAME_GET_CLIENT_BY_USER, return_value=BK_USER_CLIENT),
        ],
    )


def BIZ_SET_PUSH_FILE_TO_IPS_FAIL_CASE():
    return ComponentTestCase(
        name="all biz biz set fast_push_files v1.0  call fail case",
        inputs=INPUT,
        parent_data={"executor": "executor", "project_id": "project_id", "tenant_id": "system"},
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
                func=FAST_PUSH_FILE_BIZ_SET_REQUEST_FAILURE_CLIENT.api.fast_transfer_file,
                calls=[
                    Call(
                        data={
                            "bk_scope_type": "biz_set",
                            "bk_scope_id": "321456",
                            "bk_biz_id": 321456,
                            "file_source_list": [
                                {
                                    "file_list": ["/tmp/aa", "/tmp/bb"],
                                    "server": get_expected_target_server(
                                        [{"bk_host_id": 1, "bk_cloud_id": 0, "ip": "127.0.0.1"}]
                                    ),
                                    "account": {"alias": "root"},
                                }
                            ],
                            "target_server": get_expected_target_server(
                                [
                                    {"bk_host_id": 3, "bk_cloud_id": 0, "ip": "127.0.0.3"},
                                    {"bk_host_id": 4, "bk_cloud_id": 0, "ip": "127.0.0.4"},
                                    {"bk_host_id": 5, "bk_cloud_id": 0, "ip": "127.0.0.5"},
                                ]
                            ),
                            "account_alias": "root",
                            "file_target_path": "/tmp/ee/",
                        },
                        headers={"X-Bk-Tenant-Id": "system"},
                        upload_speed_limit=100,
                        download_speed_limit=100,
                        timeout=100,
                    ),
                    Call(
                        data={
                            "bk_scope_type": "biz_set",
                            "bk_scope_id": "321456",
                            "bk_biz_id": 321456,
                            "file_source_list": [
                                {
                                    "file_list": ["/tmp/aa", "/tmp/bb"],
                                    "server": get_expected_target_server(
                                        [{"bk_host_id": 1, "bk_cloud_id": 0, "ip": "127.0.0.1"}]
                                    ),
                                    "account": {"alias": "root"},
                                }
                            ],
                            "target_server": get_expected_target_server(
                                [
                                    {"bk_host_id": 6, "bk_cloud_id": 1, "ip": "200.0.0.1"},
                                    {"bk_host_id": 7, "bk_cloud_id": 1, "ip": "200.0.0.2"},
                                    {"bk_host_id": 8, "bk_cloud_id": 1, "ip": "200.0.0.3"},
                                ]
                            ),
                            "account_alias": "user01",
                            "file_target_path": "/tmp/200/",
                        },
                        headers={"X-Bk-Tenant-Id": "system"},
                        upload_speed_limit=100,
                        download_speed_limit=100,
                        timeout=100,
                    ),
                    Call(
                        data={
                            "bk_scope_type": "biz_set",
                            "bk_scope_id": "321456",
                            "bk_biz_id": 321456,
                            "file_source_list": [
                                {
                                    "file_list": ["/tmp/cc", "/tmp/dd"],
                                    "server": get_expected_target_server(
                                        [{"bk_host_id": 2, "bk_cloud_id": 1, "ip": "127.0.0.2"}]
                                    ),
                                    "account": {"alias": "user00"},
                                }
                            ],
                            "target_server": get_expected_target_server(
                                [
                                    {"bk_host_id": 3, "bk_cloud_id": 0, "ip": "127.0.0.3"},
                                    {"bk_host_id": 4, "bk_cloud_id": 0, "ip": "127.0.0.4"},
                                    {"bk_host_id": 5, "bk_cloud_id": 0, "ip": "127.0.0.5"},
                                ]
                            ),
                            "account_alias": "root",
                            "file_target_path": "/tmp/ee/",
                        },
                        headers={"X-Bk-Tenant-Id": "system"},
                        upload_speed_limit=100,
                        download_speed_limit=100,
                        timeout=100,
                    ),
                    Call(
                        data={
                            "bk_scope_type": "biz_set",
                            "bk_scope_id": "321456",
                            "bk_biz_id": 321456,
                            "file_source_list": [
                                {
                                    "file_list": ["/tmp/cc", "/tmp/dd"],
                                    "server": get_expected_target_server(
                                        [{"bk_host_id": 2, "bk_cloud_id": 1, "ip": "127.0.0.2"}]
                                    ),
                                    "account": {"alias": "user00"},
                                }
                            ],
                            "target_server": get_expected_target_server(
                                [
                                    {"bk_host_id": 6, "bk_cloud_id": 1, "ip": "200.0.0.1"},
                                    {"bk_host_id": 7, "bk_cloud_id": 1, "ip": "200.0.0.2"},
                                    {"bk_host_id": 8, "bk_cloud_id": 1, "ip": "200.0.0.3"},
                                ]
                            ),
                            "account_alias": "user01",
                            "file_target_path": "/tmp/200/",
                        },
                        headers={"X-Bk-Tenant-Id": "system"},
                        upload_speed_limit=100,
                        download_speed_limit=100,
                        timeout=100,
                    ),
                ],
            )
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
            Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
            Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
            Patcher(
                target=CMDB_GET_BUSINESS_HOST,
                return_value=create_get_business_host_return(
                    [
                        {"bk_host_id": 1, "bk_host_innerip": "127.0.0.1", "bk_cloud_id": 0},
                        {"bk_host_id": 2, "bk_host_innerip": "127.0.0.2", "bk_cloud_id": 1},
                        {"bk_host_id": 3, "bk_host_innerip": "127.0.0.3", "bk_cloud_id": 0},
                        {"bk_host_id": 4, "bk_host_innerip": "127.0.0.4", "bk_cloud_id": 0},
                        {"bk_host_id": 5, "bk_host_innerip": "127.0.0.5", "bk_cloud_id": 0},
                        {"bk_host_id": 6, "bk_host_innerip": "200.0.0.1", "bk_cloud_id": 1},
                        {"bk_host_id": 7, "bk_host_innerip": "200.0.0.2", "bk_cloud_id": 1},
                        {"bk_host_id": 8, "bk_host_innerip": "200.0.0.3", "bk_cloud_id": 1},
                    ]
                ),
            ),
            Patcher(
                target=CC_GET_HOST_BY_INNERIP_WITH_IPV6_PATCH,
                side_effect=create_smart_ipv6_mock(
                    [
                        {"bk_host_id": 1, "bk_host_innerip": "127.0.0.1", "bk_cloud_id": 0},
                        {"bk_host_id": 2, "bk_host_innerip": "127.0.0.2", "bk_cloud_id": 1},
                        {"bk_host_id": 3, "bk_host_innerip": "127.0.0.3", "bk_cloud_id": 0},
                        {"bk_host_id": 4, "bk_host_innerip": "127.0.0.4", "bk_cloud_id": 0},
                        {"bk_host_id": 5, "bk_host_innerip": "127.0.0.5", "bk_cloud_id": 0},
                        {"bk_host_id": 6, "bk_host_innerip": "200.0.0.1", "bk_cloud_id": 1},
                        {"bk_host_id": 7, "bk_host_innerip": "200.0.0.2", "bk_cloud_id": 1},
                        {"bk_host_id": 8, "bk_host_innerip": "200.0.0.3", "bk_cloud_id": 1},
                    ]
                ),
            ),
            Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_BIZ_SET_REQUEST_FAILURE_CLIENT),
            Patcher(target=UTILS_GET_CLIENT_BY_USER, return_value=INVALID_IP_CLIENT_BIZ_SET),
            Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=FAST_PUSH_FILE_BIZ_SET_REQUEST_FAILURE_CLIENT),
            Patcher(target=JOB_HANDLE_API_ERROR, return_value="failed"),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value="job.com/api_execute/"),
        ],
    )
