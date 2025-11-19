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
    ScheduleAssertion,
)

from pipeline_plugins.components.collections.sites.open.job import base
from pipeline_plugins.components.collections.sites.open.job.execute_task.v1_2 import JobExecuteTaskComponent
from pipeline_plugins.tests.components.collections.sites.open.utils.cc_ipv6_mock_utils import (
    MockCMDBClientIPv6,
    build_job_target_server,
)

base.LOG_VAR_SEARCH_CONFIGS.append({"re": "<##(.+?)##>", "kv_sep": "="})


class JobExecuteTaskComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            EXECUTE_JOB_FAIL_CASE,
            # INVALID_CALLBACK_DATA_CASE,
            # JOB_EXECUTE_NOT_SUCCESS_CASE,
            GET_GLOBAL_VAR_FAIL_CASE,
            EXECUTE_SUCCESS_CASE,
            GET_VAR_ERROR_SUCCESS_CASE,
            INVALID_IP_CASE,
            # IP_IS_EXIST_CASE,  # TODO: needs more work for IPv6 mode
        ]

    def component_cls(self):
        return JobExecuteTaskComponent


class MockClient(object):
    def __init__(
        self,
        execute_job_return,
        get_global_var_return=None,
        get_job_instance_log_return=None,
        get_job_instance_ip_log_return=None,
        get_job_instance_status=None,
    ):
        self.set_bk_api_ver = MagicMock()
        self.api = MagicMock()
        self.api.execute_job_plan = MagicMock(return_value=execute_job_return)
        self.api.get_job_instance_global_var_value = MagicMock(return_value=get_global_var_return)
        self.api.get_job_instance_log = MagicMock(return_value=get_job_instance_log_return)
        self.api.get_job_instance_ip_log = MagicMock(return_value=get_job_instance_ip_log_return)
        self.api.get_job_instance_status = MagicMock(return_value=get_job_instance_status)


# Mock CMDB Client for IPv6 support
class MockCMDBClient(MockCMDBClientIPv6):
    def __init__(self):
        super(MockCMDBClient, self).__init__()


# mock path
# 因为v1.2版本的JobExecuteTaskService类直接继承了JobExecuteTaskServiceBase类,所以mock路径也使用其父类的路径
GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.job.execute_task.execute_task_base.get_client_by_username"
)

# 添加 CC client mock 路径，用于 IPv6 支持
CC_GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username"
CMDB_GET_CLIENT_BY_USERNAME = "gcloud.utils.cmdb.get_client_by_username"

GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username"

GET_CLIENT_JOB_BY_USERNAME = (
    "pipeline_plugins.components.collections.sites.open.job.execute_task.v1_2.get_client_by_username"
)

CMDB_GET_CLIENT_BY_USERNAME = "gcloud.utils.cmdb.get_client_by_username"
CMDB_GET_BUSINESS_HOST = "gcloud.utils.cmdb.get_business_host"
CMDB_GET_BUSINESS_SET_HOST = "gcloud.utils.cmdb.get_business_set_host"
GET_IPV4_HOST_LIST = "pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv4_host_list"
CC_GET_HOST_BY_INNERIP_WITH_IPV6 = (
    "pipeline_plugins.components.collections.sites.open.cc.base.cc_get_host_by_innerip_with_ipv6"
)
CC_GET_HOST_BY_INNERIP_WITH_IPV6_ACROSS_BUSINESS = (
    "pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cc_get_host_by_innerip_with_ipv6_across_business"
)

CC_GET_IPS_INFO_BY_STR = "pipeline_plugins.components.utils.sites.open.utils.cc_get_ips_info_by_str"
GET_NODE_CALLBACK_URL = (
    "pipeline_plugins.components.collections.sites.open.job.execute_task.execute_task_base.get_node_callback_url"
)
GET_JOB_INSTANCE_URL = (
    "pipeline_plugins.components.collections.sites.open.job.execute_task.execute_task_base.get_job_instance_url"
)
BASE_GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username"

# 添加 CC client mock 路径，用于 IPv6 支持
CC_GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username"
CMDB_GET_CLIENT_BY_USERNAME = "gcloud.utils.cmdb.get_client_by_username"

GET_VAR_ERROR_SUCCESS_GET_LOG_RETURN = {"code": 0, "result": False, "message": "success", "data": []}

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
                        "tag": "tag",
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
                        "tag": "tag",
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

EXECUTE_SUCCESS_GET_IP_LOG_RETURN = {
    "result": True,
    "code": 0,
    "message": "",
    "data": {
        "ip": "10.0.0.1",
        "bk_cloud_id": 0,
        "log_content": "<SOPS_VAR>key1:value1</SOPS_VAR>\ngsectl\n-rwxr-xr-x 1\n"
        "<SOPS_VAR>key4:   v   </SOPS_VAR><SOPS_VAR>key5:  </SOPS_VAR>"
        "<SOPS_VAR>key6:v:v</SOPS_VAR><SOPS_VAR>key empty</SOPS_VAR>"
        "<SOPS_VAR>:1</SOPS_VAR><SOPS_VAR>:1   fgdshgdsh</SOPS_VAR>"
        "<##{key}=v##><##{key}notvar##>"
        "&lt;SOPS_VAR&gt;key2:value2&lt;/SOPS_VAR&gt;\n"
        "dfg&lt;SOPS_VAR&gt;key3:value3&lt;/SOPS_VAR&gt;"
        "&lt;SOPS_VAR&gt;k: v  &lt;/SOPS_VAR&gt;"
        "&lt;SOPS_VAR&gt;k1: :v  &lt;/SOPS_VAR&gt;"
        "&lt;SOPS_VAR&gt;k1      &lt;/SOPS_VAR&gt;"
        "&lt;##{key2}=v##&gt;&lt;##{key3}=var##&gt;",
    },
}

# mock clients
EXECUTE_JOB_CALL_FAIL_CLIENT = MockClient(execute_job_return={"result": False, "message": "message token"})
INVALID_CALLBACK_DATA_CLIENT = MockClient(
    execute_job_return={"result": True, "data": {"job_instance_id": 56789, "job_instance_name": "job_name_token"}}
)
JOB_EXECUTE_NOT_SUCCESS_CLIENT = MockClient(
    execute_job_return={"result": True, "data": {"job_instance_id": 56789, "job_instance_name": "job_name_token"}},
    get_job_instance_status=EXECUTE_SUCCESS_GET_STATUS_RETURN,
    get_global_var_return={"result": False, "message": "global var message token"},
)
GET_GLOBAL_VAR_CALL_FAIL_CLIENT = MockClient(
    execute_job_return={"result": True, "data": {"job_instance_id": 56789, "job_instance_name": "job_name_token"}},
    get_global_var_return={"result": False, "message": "global var message token"},
    get_job_instance_status=EXECUTE_SUCCESS_GET_STATUS_RETURN,
)

# Mock CMDB client with proper api.list_biz_hosts
# 这个CMDB_CLIENT包含所有测试用例中使用的IP，确保能够正确查询到IP信息
CMDB_CLIENT = MagicMock()
CMDB_CLIENT.api.list_biz_hosts = MagicMock(
    return_value={
        "result": True,
        "data": {
            "count": 8,
            "info": [
                # EXECUTE_JOB_FAIL_CASE, GET_GLOBAL_VAR_FAIL_CASE等使用的IP
                {
                    "bk_host_id": 1,
                    "bk_host_innerip": "1.1.1.1",
                    "bk_cloud_id": 1,
                    "bk_host_innerip_v6": "",
                    "bk_agent_id": "agent1",
                },
                {
                    "bk_host_id": 2,
                    "bk_host_innerip": "2.2.2.2",
                    "bk_cloud_id": 1,
                    "bk_host_innerip_v6": "",
                    "bk_agent_id": "agent2",
                },
                # INVALID_IP_CASE使用的IP
                {
                    "bk_host_id": 3,
                    "bk_host_innerip": "3.3.3.3",
                    "bk_cloud_id": 0,
                    "bk_host_innerip_v6": "",
                    "bk_agent_id": "agent3",
                },
                {
                    "bk_host_id": 4,
                    "bk_host_innerip": "4.4.4.4",
                    "bk_cloud_id": 0,
                    "bk_host_innerip_v6": "",
                    "bk_agent_id": "agent4",
                },
                # EXECUTE_SUCCESS_CASE使用的IP
                {
                    "bk_host_id": 5,
                    "bk_host_innerip": "10.0.0.1",
                    "bk_cloud_id": 0,
                    "bk_host_innerip_v6": "",
                    "bk_agent_id": "agent5",
                },
                {
                    "bk_host_id": 6,
                    "bk_host_innerip": "10.0.0.2",
                    "bk_cloud_id": 0,
                    "bk_host_innerip_v6": "",
                    "bk_agent_id": "agent6",
                },
                # 其他测试可能使用的IP
                {
                    "bk_host_id": 7,
                    "bk_host_innerip": "127.0.0.1",
                    "bk_cloud_id": 0,
                    "bk_host_innerip_v6": "",
                    "bk_agent_id": "agent7",
                },
                {
                    "bk_host_id": 8,
                    "bk_host_innerip": "127.0.0.2",
                    "bk_cloud_id": 0,
                    "bk_host_innerip_v6": "",
                    "bk_agent_id": "agent8",
                },
            ],
        },
    }
)
CMDB_CLIENT.api.list_hosts_without_biz = MagicMock(
    return_value={
        "result": True,
        "data": {
            "count": 4,
            "info": [
                {
                    "bk_host_id": 3,
                    "bk_host_innerip": "3.3.3.3",
                    "bk_cloud_id": 0,
                    "bk_host_innerip_v6": "",
                    "bk_agent_id": "agent3",
                },
                {
                    "bk_host_id": 4,
                    "bk_host_innerip": "4.4.4.4",
                    "bk_cloud_id": 0,
                    "bk_host_innerip_v6": "",
                    "bk_agent_id": "agent4",
                },
                {
                    "bk_host_id": 7,
                    "bk_host_innerip": "127.0.0.1",
                    "bk_cloud_id": 0,
                    "bk_host_innerip_v6": "",
                    "bk_agent_id": "agent7",
                },
                {
                    "bk_host_id": 8,
                    "bk_host_innerip": "127.0.0.2",
                    "bk_cloud_id": 0,
                    "bk_host_innerip_v6": "",
                    "bk_agent_id": "agent8",
                },
            ],
        },
    }
)

# Mock CMDB client that returns empty results (for IP not found test cases)
CMDB_CLIENT_EMPTY = MagicMock()
CMDB_CLIENT_EMPTY.api.list_biz_hosts = MagicMock(
    return_value={
        "result": True,
        "data": {
            "count": 0,
            "info": [],
        },
    }
)
CMDB_CLIENT_EMPTY.api.list_hosts_without_biz = MagicMock(
    return_value={
        "result": True,
        "data": {
            "count": 0,
            "info": [],
        },
    }
)

EXECUTE_SUCCESS_CLIENT = MockClient(
    execute_job_return={"result": True, "data": {"job_instance_id": 56789, "job_instance_name": "job_name_token"}},
    get_global_var_return={
        "result": True,
        "data": {
            "step_instance_var_list": [
                {
                    "global_var_list": [
                        {"type": 1, "name": "key_1", "value": "new_value_1"},
                        {"type": 1, "name": "key_2", "value": "new_value_2"},
                    ]
                }
            ]
        },
    },
    get_job_instance_ip_log_return=EXECUTE_SUCCESS_GET_IP_LOG_RETURN,
    get_job_instance_status=EXECUTE_SUCCESS_GET_STATUS_RETURN,
)

GET_VAR_ERROR_SUCCESS_CLIENT = MockClient(
    execute_job_return={"result": True, "data": {"job_instance_id": 56789, "job_instance_name": "job_name_token"}},
    get_global_var_return={
        "result": True,
        "data": {
            "step_instance_var_list": [
                {
                    "global_var_list": [
                        {"type": 1, "name": "key_1", "value": "new_value_1"},
                        {"type": 1, "name": "key_2", "value": "new_value_2"},
                    ]
                }
            ]
        },
    },
    get_job_instance_log_return=GET_VAR_ERROR_SUCCESS_GET_LOG_RETURN,
    get_job_instance_ip_log_return=EXECUTE_SUCCESS_GET_IP_LOG_RETURN,
    get_job_instance_status=EXECUTE_SUCCESS_GET_STATUS_RETURN,
)


# Mock function for cc_get_host_by_innerip_with_ipv6
def mock_cc_get_host_by_innerip_with_ipv6(tenant_id, executor, bk_biz_id, ip_str, is_biz_set=False):
    """
    Mock function that returns host information based on IP string
    Returns host data matching the IPs in the test cases
    """
    # Extract IPs from ip_str
    import re

    ip_pattern = r"(?:\d+:)?(\d+\.\d+\.\d+\.\d+)"
    ips = re.findall(ip_pattern, ip_str)

    # Map of known test IPs to their host data
    ip_host_map = {
        "1.1.1.1": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 1, "bk_agent_id": "agent1"},
        "2.2.2.2": {"bk_host_id": 2, "bk_host_innerip": "2.2.2.2", "bk_cloud_id": 1, "bk_agent_id": "agent2"},
        "3.3.3.3": {"bk_host_id": 3, "bk_host_innerip": "3.3.3.3", "bk_cloud_id": 0, "bk_agent_id": "agent3"},
        "4.4.4.4": {"bk_host_id": 4, "bk_host_innerip": "4.4.4.4", "bk_cloud_id": 0, "bk_agent_id": "agent4"},
        "10.0.0.1": {"bk_host_id": 5, "bk_host_innerip": "10.0.0.1", "bk_cloud_id": 0, "bk_agent_id": "agent5"},
        "10.0.0.2": {"bk_host_id": 6, "bk_host_innerip": "10.0.0.2", "bk_cloud_id": 0, "bk_agent_id": "agent6"},
        "127.0.0.1": {"bk_host_id": 7, "bk_host_innerip": "127.0.0.1", "bk_cloud_id": 0, "bk_agent_id": "agent7"},
        "127.0.0.2": {"bk_host_id": 8, "bk_host_innerip": "127.0.0.2", "bk_cloud_id": 0, "bk_agent_id": "agent8"},
    }

    hosts = []
    for ip in ips:
        if ip in ip_host_map:
            hosts.append(ip_host_map[ip])

    return {"result": True, "data": hosts}


# Mock function for cc_get_host_by_innerip_with_ipv6_across_business
def mock_cc_get_host_by_innerip_with_ipv6_across_business(tenant_id, executor, bk_biz_id, ip_str):
    """
    Mock function for across business IP query
    Returns (host_list, ipv4_not_find_list, ipv4_with_cloud_not_find_list,
             ipv6_not_find_list, ipv6_with_cloud_not_find_list)
    """
    # Extract IPs from ip_str
    import re

    ip_pattern = r"(?:\d+:)?(\d+\.\d+\.\d+\.\d+)"
    ips = re.findall(ip_pattern, ip_str)

    # Map of known test IPs to their host data
    ip_host_map = {
        "1.1.1.1": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 1, "bk_agent_id": "agent1"},
        "2.2.2.2": {"bk_host_id": 2, "bk_host_innerip": "2.2.2.2", "bk_cloud_id": 1, "bk_agent_id": "agent2"},
        "3.3.3.3": {"bk_host_id": 3, "bk_host_innerip": "3.3.3.3", "bk_cloud_id": 0, "bk_agent_id": "agent3"},
        "4.4.4.4": {"bk_host_id": 4, "bk_host_innerip": "4.4.4.4", "bk_cloud_id": 0, "bk_agent_id": "agent4"},
        "10.0.0.1": {"bk_host_id": 5, "bk_host_innerip": "10.0.0.1", "bk_cloud_id": 0, "bk_agent_id": "agent5"},
        "10.0.0.2": {"bk_host_id": 6, "bk_host_innerip": "10.0.0.2", "bk_cloud_id": 0, "bk_agent_id": "agent6"},
        "127.0.0.1": {"bk_host_id": 7, "bk_host_innerip": "127.0.0.1", "bk_cloud_id": 0, "bk_agent_id": "agent7"},
        "127.0.0.2": {"bk_host_id": 8, "bk_host_innerip": "127.0.0.2", "bk_cloud_id": 0, "bk_agent_id": "agent8"},
    }

    hosts = []
    not_found_ips = []
    for ip in ips:
        if ip in ip_host_map:
            hosts.append(ip_host_map[ip])
        else:
            not_found_ips.append(ip)

    # Return (host_list, ipv4_not_find_list, ipv4_with_cloud_not_find_list,
    #         ipv6_not_find_list, ipv6_with_cloud_not_find_list)
    return (hosts, not_found_ips, [], [], [])


# Mock function for get_ipv4_host_list
def mock_get_ipv4_host_list(tenant_id, executor, bk_biz_id, ipv4_list, is_biz_set=False):
    """
    Mock function for get_ipv4_host_list
    Returns list of host information
    """
    # Map of known test IPs to their host data
    ip_host_map = {
        "1.1.1.1": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 1, "bk_agent_id": "agent1"},
        "2.2.2.2": {"bk_host_id": 2, "bk_host_innerip": "2.2.2.2", "bk_cloud_id": 1, "bk_agent_id": "agent2"},
        "3.3.3.3": {"bk_host_id": 3, "bk_host_innerip": "3.3.3.3", "bk_cloud_id": 0, "bk_agent_id": "agent3"},
        "4.4.4.4": {"bk_host_id": 4, "bk_host_innerip": "4.4.4.4", "bk_cloud_id": 0, "bk_agent_id": "agent4"},
        "10.0.0.1": {"bk_host_id": 5, "bk_host_innerip": "10.0.0.1", "bk_cloud_id": 0, "bk_agent_id": "agent5"},
        "10.0.0.2": {"bk_host_id": 6, "bk_host_innerip": "10.0.0.2", "bk_cloud_id": 0, "bk_agent_id": "agent6"},
        "127.0.0.1": {"bk_host_id": 7, "bk_host_innerip": "127.0.0.1", "bk_cloud_id": 0, "bk_agent_id": "agent7"},
        "127.0.0.2": {"bk_host_id": 8, "bk_host_innerip": "127.0.0.2", "bk_cloud_id": 0, "bk_agent_id": "agent8"},
    }

    hosts = []
    for ip in ipv4_list:
        if ip in ip_host_map:
            hosts.append(ip_host_map[ip])

    return hosts


# Mock function for cmdb.get_business_host
def mock_get_business_host(tenant_id, username, bk_biz_id, host_fields, ip_list=None, bk_cloud_id=None):
    """
    Mock function for cmdb.get_business_host
    Returns list of hosts based on ip_list
    """
    if not ip_list:
        return []

    # Map of known test IPs to their host data
    ip_host_map = {
        "1.1.1.1": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 1, "bk_agent_id": "agent1"},
        "2.2.2.2": {"bk_host_id": 2, "bk_host_innerip": "2.2.2.2", "bk_cloud_id": 1, "bk_agent_id": "agent2"},
        "3.3.3.3": {"bk_host_id": 3, "bk_host_innerip": "3.3.3.3", "bk_cloud_id": 0, "bk_agent_id": "agent3"},
        "4.4.4.4": {"bk_host_id": 4, "bk_host_innerip": "4.4.4.4", "bk_cloud_id": 0, "bk_agent_id": "agent4"},
        "10.0.0.1": {"bk_host_id": 5, "bk_host_innerip": "10.0.0.1", "bk_cloud_id": 0, "bk_agent_id": "agent5"},
        "10.0.0.2": {"bk_host_id": 6, "bk_host_innerip": "10.0.0.2", "bk_cloud_id": 0, "bk_agent_id": "agent6"},
        "127.0.0.1": {"bk_host_id": 7, "bk_host_innerip": "127.0.0.1", "bk_cloud_id": 0, "bk_agent_id": "agent7"},
        "127.0.0.2": {"bk_host_id": 8, "bk_host_innerip": "127.0.0.2", "bk_cloud_id": 0, "bk_agent_id": "agent8"},
    }

    hosts = []
    for ip in ip_list:
        if ip in ip_host_map:
            host_data = ip_host_map[ip].copy()
            # Filter by cloud_id if specified
            if bk_cloud_id is not None and host_data["bk_cloud_id"] != bk_cloud_id:
                continue
            hosts.append(host_data)

    return hosts


# Mock function for cmdb.get_business_set_host
def mock_get_business_set_host(tenant_id, username, host_fields, ip_list=None):
    """
    Mock function for cmdb.get_business_set_host (cross-business query)
    Returns list of hosts based on ip_list
    """
    if not ip_list:
        return []

    # Map of known test IPs to their host data
    ip_host_map = {
        "1.1.1.1": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 1, "bk_agent_id": "agent1"},
        "2.2.2.2": {"bk_host_id": 2, "bk_host_innerip": "2.2.2.2", "bk_cloud_id": 1, "bk_agent_id": "agent2"},
        "3.3.3.3": {"bk_host_id": 3, "bk_host_innerip": "3.3.3.3", "bk_cloud_id": 0, "bk_agent_id": "agent3"},
        "4.4.4.4": {"bk_host_id": 4, "bk_host_innerip": "4.4.4.4", "bk_cloud_id": 0, "bk_agent_id": "agent4"},
        "10.0.0.1": {"bk_host_id": 5, "bk_host_innerip": "10.0.0.1", "bk_cloud_id": 0, "bk_agent_id": "agent5"},
        "10.0.0.2": {"bk_host_id": 6, "bk_host_innerip": "10.0.0.2", "bk_cloud_id": 0, "bk_agent_id": "agent6"},
        "127.0.0.1": {"bk_host_id": 7, "bk_host_innerip": "127.0.0.1", "bk_cloud_id": 0, "bk_agent_id": "agent7"},
        "127.0.0.2": {"bk_host_id": 8, "bk_host_innerip": "127.0.0.2", "bk_cloud_id": 0, "bk_agent_id": "agent8"},
    }

    hosts = []
    for ip in ip_list:
        if ip in ip_host_map:
            hosts.append(ip_host_map[ip])

    return hosts


# 辅助函数：根据 ENABLE_IPV6 动态生成 Job global_var 的 server 值
def _build_server_for_global_var(host_ids, ips_with_cloud):
    """
    根据当前 ENABLE_IPV6 设置生成 Job global_var 中 server 字段的正确格式

    Args:
        host_ids: 主机ID列表，例如 [1, 2]
        ips_with_cloud: IP和云区域列表，例如 [{"ip": "1.1.1.1", "bk_cloud_id": 1}, ...]

    Returns:
        dict: 根据 ENABLE_IPV6 返回相应格式的 server
    """
    return build_job_target_server(host_ids=host_ids, ips_with_cloud=ips_with_cloud)


# 预定义动态生成的 server 值，用于测试用例
# 这些值会根据当前 ENABLE_IPV6 设置自动适配格式
SERVER_1_2 = _build_server_for_global_var(
    host_ids=[1, 2], ips_with_cloud=[{"ip": "1.1.1.1", "bk_cloud_id": 1}, {"ip": "2.2.2.2", "bk_cloud_id": 1}]
)
SERVER_4_3 = _build_server_for_global_var(
    host_ids=[4, 3], ips_with_cloud=[{"ip": "4.4.4.4", "bk_cloud_id": 0}, {"ip": "3.3.3.3", "bk_cloud_id": 0}]
)


# test cases
EXECUTE_JOB_FAIL_CASE = ComponentTestCase(
    name="v1.2 execute_job call failed case",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
        ],
        "job_task_id": 12345,
        "biz_cc_id": 1,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "ex_data": ("调用作业平台(JOB)接口jobv3.execute_job_plan返回失败, error=message token, params={params}").format(
                params=json.dumps(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": SERVER_1_2,
                            },
                        ],
                        "callback_url": "url_token",
                    }
                )
            )
        },
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=EXECUTE_JOB_CALL_FAIL_CLIENT.api.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": SERVER_1_2,
                            },
                        ],
                        "callback_url": "url_token",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_JOB_CALL_FAIL_CLIENT),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 1}, {"InnerIP": "2.2.2.2", "Source": 1}]},
        ),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="url_token"),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=CMDB_CLIENT),
        Patcher(target=CC_GET_HOST_BY_INNERIP_WITH_IPV6, side_effect=mock_cc_get_host_by_innerip_with_ipv6),
        Patcher(
            target=CC_GET_HOST_BY_INNERIP_WITH_IPV6_ACROSS_BUSINESS,
            side_effect=mock_cc_get_host_by_innerip_with_ipv6_across_business,
        ),
        Patcher(target=GET_IPV4_HOST_LIST, side_effect=mock_get_ipv4_host_list),
        Patcher(target=CMDB_GET_BUSINESS_HOST, side_effect=mock_get_business_host),
        Patcher(target=CMDB_GET_BUSINESS_SET_HOST, side_effect=mock_get_business_set_host),
    ],
)

INVALID_CALLBACK_DATA_CASE = ComponentTestCase(
    name="v1.2 invalid callback case",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
        ],
        "job_task_id": 12345,
        "biz_cc_id": 1,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "ex_data": "invalid callback_data, " "job_instance_id: None, status: None",
        },
        callback_data={},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=INVALID_CALLBACK_DATA_CLIENT.api.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": SERVER_1_2,
                            },
                        ],
                        "callback_url": "url_token",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=GET_CLIENT_BY_USER, return_value=INVALID_CALLBACK_DATA_CLIENT),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 1}, {"InnerIP": "2.2.2.2", "Source": 1}]},
        ),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="url_token"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=CMDB_CLIENT),
        Patcher(target=CC_GET_HOST_BY_INNERIP_WITH_IPV6, side_effect=mock_cc_get_host_by_innerip_with_ipv6),
        Patcher(
            target=CC_GET_HOST_BY_INNERIP_WITH_IPV6_ACROSS_BUSINESS,
            side_effect=mock_cc_get_host_by_innerip_with_ipv6_across_business,
        ),
        Patcher(target=GET_IPV4_HOST_LIST, side_effect=mock_get_ipv4_host_list),
        Patcher(target=CMDB_GET_BUSINESS_HOST, side_effect=mock_get_business_host),
        Patcher(target=CMDB_GET_BUSINESS_SET_HOST, side_effect=mock_get_business_set_host),
    ],
)

JOB_EXECUTE_NOT_SUCCESS_CASE = ComponentTestCase(
    name="v1.2 job execute not success case",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
        ],
        "job_task_id": 12345,
        "biz_cc_id": 1,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "ex_data": "调用作业平台(JOB)接口jobv3.get_job_instance_global_var_value返回失败, "
            "error=global var message token, "
            'params={"bk_scope_type":"biz","bk_scope_id":"1","bk_biz_id":1,"job_instance_id":56789}',
            "job_tagged_ip_dict": {
                "name": "JOB执行IP分组",
                "key": "job_tagged_ip_dict",
                "value": {
                    "SUCCESS": {"DESC": "执行成功", "TAGS": {"tag": "1.1.1.1,1.1.1.2", "ALL": "1.1.1.1,1.1.1.2"}},
                    "SCRIPT_NOT_ZERO_EXIT_CODE": {"DESC": "脚本返回值非零", "TAGS": {"ALL": ""}},
                    "OTHER_FAILED": {"desc": "其他异常", "TAGS": {"ALL": ""}},
                },
            },
        },
        callback_data={"job_instance_id": 56789, "status": 1},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=JOB_EXECUTE_NOT_SUCCESS_CLIENT.api.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": SERVER_1_2,
                            },
                        ],
                        "callback_url": "url_token",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=GET_CLIENT_BY_USER, return_value=JOB_EXECUTE_NOT_SUCCESS_CLIENT),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 1}, {"InnerIP": "2.2.2.2", "Source": 1}]},
        ),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="url_token"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=CMDB_CLIENT),
        Patcher(target=CC_GET_HOST_BY_INNERIP_WITH_IPV6, side_effect=mock_cc_get_host_by_innerip_with_ipv6),
        Patcher(
            target=CC_GET_HOST_BY_INNERIP_WITH_IPV6_ACROSS_BUSINESS,
            side_effect=mock_cc_get_host_by_innerip_with_ipv6_across_business,
        ),
        Patcher(target=GET_IPV4_HOST_LIST, side_effect=mock_get_ipv4_host_list),
        Patcher(target=CMDB_GET_BUSINESS_HOST, side_effect=mock_get_business_host),
        Patcher(target=CMDB_GET_BUSINESS_SET_HOST, side_effect=mock_get_business_set_host),
    ],
)

GET_GLOBAL_VAR_FAIL_CASE = ComponentTestCase(
    name="v1.2 get global var fail case",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
        ],
        "job_task_id": 12345,
        "biz_cc_id": 1,
        "is_tagged_ip": False,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "job_tagged_ip_dict": {
                "name": "JOB执行IP分组",
                "key": "job_tagged_ip_dict",
                "value": {
                    "SUCCESS": {"DESC": "执行成功", "TAGS": {"tag": "1.1.1.1,1.1.1.2", "ALL": "1.1.1.1,1.1.1.2"}},
                    "SCRIPT_NOT_ZERO_EXIT_CODE": {"DESC": "脚本返回值非零", "TAGS": {"ALL": ""}},
                    "OTHER_FAILED": {"desc": "其他异常", "TAGS": {"ALL": ""}},
                },
            },
            "ex_data": (
                "调用作业平台(JOB)接口jobv3.get_job_instance_global_var_value"
                "返回失败, error=global var message token, params={params}"
            ).format(
                params=json.dumps(
                    {"bk_scope_type": "biz", "bk_scope_id": "1", "bk_biz_id": 1, "job_instance_id": 56789}
                )
            ),
        },
        callback_data={"job_instance_id": 56789, "status": 3},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=GET_GLOBAL_VAR_CALL_FAIL_CLIENT.api.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": SERVER_1_2,
                            },
                        ],
                        "callback_url": "url_token",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=GET_GLOBAL_VAR_CALL_FAIL_CLIENT.api.get_job_instance_global_var_value,
            calls=[
                Call(
                    {"bk_scope_type": "biz", "bk_scope_id": "1", "bk_biz_id": 1, "job_instance_id": 56789},
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=GET_CLIENT_BY_USER, return_value=GET_GLOBAL_VAR_CALL_FAIL_CLIENT),
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=GET_GLOBAL_VAR_CALL_FAIL_CLIENT),
        Patcher(target=GET_CLIENT_JOB_BY_USERNAME, return_value=GET_GLOBAL_VAR_CALL_FAIL_CLIENT),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=CMDB_CLIENT),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 1}, {"InnerIP": "2.2.2.2", "Source": 1}]},
        ),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="url_token"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=CC_GET_HOST_BY_INNERIP_WITH_IPV6, side_effect=mock_cc_get_host_by_innerip_with_ipv6),
        Patcher(
            target=CC_GET_HOST_BY_INNERIP_WITH_IPV6_ACROSS_BUSINESS,
            side_effect=mock_cc_get_host_by_innerip_with_ipv6_across_business,
        ),
        Patcher(target=GET_IPV4_HOST_LIST, side_effect=mock_get_ipv4_host_list),
        Patcher(target=CMDB_GET_BUSINESS_HOST, side_effect=mock_get_business_host),
        Patcher(target=CMDB_GET_BUSINESS_SET_HOST, side_effect=mock_get_business_set_host),
    ],
)

EXECUTE_SUCCESS_CASE = ComponentTestCase(
    name="v1.2 execute success case",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
            {"category": 3, "name": "key_3", "value": "0:4.4.4.4,0:3.3.3.3"},
        ],
        "job_task_id": 12345,
        "is_tagged_ip": True,
        "biz_cc_id": 1,
        "biz_across": True,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "job_tagged_ip_dict": {
                "name": "JOB执行IP分组",
                "key": "job_tagged_ip_dict",
                "value": {
                    "SUCCESS": {"DESC": "执行成功", "TAGS": {"tag": "1.1.1.1,1.1.1.2", "ALL": "1.1.1.1,1.1.1.2"}},
                    "SCRIPT_NOT_ZERO_EXIT_CODE": {"DESC": "脚本返回值非零", "TAGS": {"ALL": ""}},
                    "OTHER_FAILED": {"desc": "其他异常", "TAGS": {"ALL": ""}},
                },
            },
            "key_1": "new_value_1",
            "key_2": "new_value_2",
            "log_outputs": {
                "key1": "value1",
                "key4": "   v   ",
                "key5": "  ",
                "key6": "v:v",
                "key2": "value2",
                "{key}": "v",
                "key3": "value3",
                "k": " v  ",
                "k1": " :v  ",
                "{key2}": "v",
                "{key3}": "var",
            },
        },
        callback_data={"job_instance_id": 56789, "status": 3},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=EXECUTE_SUCCESS_CLIENT.api.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": SERVER_1_2,
                            },
                            {
                                "name": "key_3",
                                "server": SERVER_4_3,
                            },
                        ],
                        "callback_url": "url_token",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=EXECUTE_SUCCESS_CLIENT.api.get_job_instance_global_var_value,
            calls=[
                Call(
                    {"bk_scope_type": "biz", "bk_scope_id": "1", "bk_biz_id": 1, "job_instance_id": 56789},
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_SUCCESS_CLIENT),
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=EXECUTE_SUCCESS_CLIENT),
        Patcher(target=GET_CLIENT_JOB_BY_USERNAME, return_value=EXECUTE_SUCCESS_CLIENT),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 1}, {"InnerIP": "2.2.2.2", "Source": 1}]},
        ),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="url_token"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=CMDB_CLIENT),
        Patcher(target=CC_GET_HOST_BY_INNERIP_WITH_IPV6, side_effect=mock_cc_get_host_by_innerip_with_ipv6),
        Patcher(
            target=CC_GET_HOST_BY_INNERIP_WITH_IPV6_ACROSS_BUSINESS,
            side_effect=mock_cc_get_host_by_innerip_with_ipv6_across_business,
        ),
        Patcher(target=GET_IPV4_HOST_LIST, side_effect=mock_get_ipv4_host_list),
        Patcher(target=CMDB_GET_BUSINESS_HOST, side_effect=mock_get_business_host),
        Patcher(target=CMDB_GET_BUSINESS_SET_HOST, side_effect=mock_get_business_set_host),
    ],
)

GET_VAR_ERROR_SUCCESS_CASE = ComponentTestCase(
    name="v1.2 get var failed but execute result must be success",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
        ],
        "job_task_id": 12345,
        "biz_cc_id": 1,
        "is_tagged_ip": True,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
            "job_tagged_ip_dict": {
                "name": "JOB执行IP分组",
                "key": "job_tagged_ip_dict",
                "value": {
                    "SUCCESS": {"DESC": "执行成功", "TAGS": {"tag": "1.1.1.1,1.1.1.2", "ALL": "1.1.1.1,1.1.1.2"}},
                    "SCRIPT_NOT_ZERO_EXIT_CODE": {"DESC": "脚本返回值非零", "TAGS": {"ALL": ""}},
                    "OTHER_FAILED": {"desc": "其他异常", "TAGS": {"ALL": ""}},
                },
            },
            "key_1": "new_value_1",
            "key_2": "new_value_2",
            "log_outputs": {
                "key1": "value1",
                "key4": "   v   ",
                "key5": "  ",
                "key6": "v:v",
                "key2": "value2",
                "{key}": "v",
                "key3": "value3",
                "k": " v  ",
                "k1": " :v  ",
                "{key2}": "v",
                "{key3}": "var",
            },
        },
        callback_data={"job_instance_id": 56789, "status": 3},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=GET_VAR_ERROR_SUCCESS_CLIENT.api.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": SERVER_1_2,
                            },
                        ],
                        "callback_url": "url_token",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=GET_VAR_ERROR_SUCCESS_CLIENT.api.get_job_instance_global_var_value,
            calls=[
                Call(
                    {"bk_scope_type": "biz", "bk_scope_id": "1", "bk_biz_id": 1, "job_instance_id": 56789},
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=GET_CLIENT_BY_USER, return_value=GET_VAR_ERROR_SUCCESS_CLIENT),
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=GET_VAR_ERROR_SUCCESS_CLIENT),
        Patcher(target=GET_CLIENT_JOB_BY_USERNAME, return_value=GET_VAR_ERROR_SUCCESS_CLIENT),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 1}, {"InnerIP": "2.2.2.2", "Source": 1}]},
        ),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="url_token"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=CMDB_CLIENT),
        Patcher(target=CC_GET_HOST_BY_INNERIP_WITH_IPV6, side_effect=mock_cc_get_host_by_innerip_with_ipv6),
        Patcher(
            target=CC_GET_HOST_BY_INNERIP_WITH_IPV6_ACROSS_BUSINESS,
            side_effect=mock_cc_get_host_by_innerip_with_ipv6_across_business,
        ),
        Patcher(target=GET_IPV4_HOST_LIST, side_effect=mock_get_ipv4_host_list),
        Patcher(target=CMDB_GET_BUSINESS_HOST, side_effect=mock_get_business_host),
        Patcher(target=CMDB_GET_BUSINESS_SET_HOST, side_effect=mock_get_business_set_host),
    ],
)

INVALID_IP_CASE = ComponentTestCase(
    name="v1.2 invalid ip case",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
        ],
        "job_task_id": 12345,
        "biz_cc_id": 1,
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={"ex_data": "无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法。查询失败 IP： 1.1.1.1,2.2.2.2"},
    ),
    schedule_assertion=None,
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_SUCCESS_CLIENT),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=CMDB_CLIENT_EMPTY),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": []}),
        Patcher(target=CC_GET_HOST_BY_INNERIP_WITH_IPV6, return_value={"result": True, "data": []}),
        Patcher(
            target=CC_GET_HOST_BY_INNERIP_WITH_IPV6_ACROSS_BUSINESS,
            return_value=([], ["1.1.1.1", "2.2.2.2"], [], [], []),
        ),
        Patcher(target=GET_IPV4_HOST_LIST, return_value=[]),
        Patcher(target=CMDB_GET_BUSINESS_HOST, return_value=[]),
        Patcher(target=CMDB_GET_BUSINESS_SET_HOST, return_value=[]),
    ],
)

IP_IS_EXIST_CASE = ComponentTestCase(
    name="v1.2 ip is exist case",
    inputs={
        "job_global_var": [
            {"category": 1, "name": "key_1", "value": "value_1"},
            {"category": 1, "name": "key_2", "value": "value_2"},
            {"category": 3, "name": "key_3", "value": "1.1.1.1,2.2.2.2"},
        ],
        "job_task_id": 12345,
        "biz_cc_id": 1,
        "ip_is_exist": True,  # v1.2版本默认不校验IP，此参数无效
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=True,  # v1.2版本默认不校验IP，总是成功
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 56789,
            "job_inst_name": "job_name_token",
        },
    ),
    schedule_assertion=None,
    # v1.2版本的check_ip_is_exist方法默认返回False，不会调用cc_get_ips_info_by_str
    # v1.2版本使用get_target_server_hybrid，在非IPV6模式下返回ip_list
    execute_call_assertion=[
        CallAssertion(
            func=EXECUTE_SUCCESS_CLIENT.api.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "job_plan_id": 12345,
                        "global_var_list": [
                            {"name": "key_1", "value": "value_1"},
                            {"name": "key_2", "value": "value_2"},
                            {
                                "name": "key_3",
                                "server": SERVER_1_2,
                            },
                        ],
                        "callback_url": "url_token",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_SUCCESS_CLIENT),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=CMDB_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="url_token"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 1}, {"InnerIP": "2.2.2.2", "Source": 1}]},
        ),
        Patcher(target=CC_GET_HOST_BY_INNERIP_WITH_IPV6, side_effect=mock_cc_get_host_by_innerip_with_ipv6),
        Patcher(
            target=CC_GET_HOST_BY_INNERIP_WITH_IPV6_ACROSS_BUSINESS,
            side_effect=mock_cc_get_host_by_innerip_with_ipv6_across_business,
        ),
        Patcher(target=GET_IPV4_HOST_LIST, side_effect=mock_get_ipv4_host_list),
        Patcher(target=CMDB_GET_BUSINESS_HOST, side_effect=mock_get_business_host),
        Patcher(target=CMDB_GET_BUSINESS_SET_HOST, side_effect=mock_get_business_set_host),
    ],
)
