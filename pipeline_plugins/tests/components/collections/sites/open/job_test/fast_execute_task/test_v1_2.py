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

from pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2 import (
    JobFastExecuteScriptComponent,
)
from pipeline_plugins.tests.components.collections.sites.open.utils.cc_ipv6_mock_utils import MockCMDBClientIPv6


class JobFastExecuteScriptComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        # return the component class which should be testet
        return JobFastExecuteScriptComponent

    def cases(self):
        # return your component test cases here
        return [
            FAST_EXECUTE_MANUAL_SCRIPT_FAIL_CASE,
            FAST_EXECUTE_MANUAL_SCRIPT_SUCCESS_SCHEDULE_CALLBACK_DATA_ERROR_CASE,
            FAST_EXECUTE_MANUAL_SCRIPT_SUCCESS_SCHEDULE_SUCCESS_CASE,
        ]

    def setUp(self):
        super().setUp()
        # Save the original ENABLE_IPV6 value
        self._original_enable_ipv6 = getattr(settings, "ENABLE_IPV6", False)
        setattr(settings, "ENABLE_IPV6", False)

    def tearDown(self):
        super().tearDown()
        # Restore the original ENABLE_IPV6 value
        setattr(settings, "ENABLE_IPV6", self._original_enable_ipv6)


class MockClient(object):
    def __init__(
        self,
        fast_execute_script_return=None,
        get_job_instance_global_var_value_return=None,
        get_job_instance_log_return=None,
        get_job_instance_ip_log_return=None,
        get_job_instance_status=None,
    ):
        self.api = MagicMock()
        self.api.fast_execute_script = MagicMock(return_value=fast_execute_script_return)
        self.api.get_job_instance_global_var_value = MagicMock(return_value=get_job_instance_global_var_value_return)
        self.api.get_job_instance_log = MagicMock(return_value=get_job_instance_log_return)
        self.api.get_job_instance_ip_log = MagicMock(return_value=get_job_instance_ip_log_return)
        self.api.get_job_instance_status = MagicMock(return_value=get_job_instance_status)


# Mock CMDB Client for IPv6 support
class MockCMDBClient(MockCMDBClientIPv6):
    def __init__(self):
        super(MockCMDBClient, self).__init__()


# mock path
GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.get_client_by_username"
)

# 添加 CC client mock 路径，用于 IPv6 支持
CC_GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username"
CMDB_GET_CLIENT_BY_USERNAME = "gcloud.utils.cmdb.get_client_by_username"

GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username"

GET_NODE_CALLBACK_URL = (
    "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.get_node_callback_url"
)
CC_GET_IPS_INFO_BY_STR = "pipeline_plugins.components.utils.sites.open.utils.cc_get_ips_info_by_str"
JOB_HANDLE_API_ERROR = (
    "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.job_handle_api_error"
)
GET_JOB_INSTANCE_URL = (
    "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.get_job_instance_url"
)

# success result
SUCCESS_RESULT = {
    "result": True,
    "code": 0,
    "message": "success",
    "data": {"job_instance_name": "API Quick execution script1521100521303", "job_instance_id": 10000},
}

# success result
FAIL_RESULT = {
    "code": 1237104,
    "permission": None,
    "result": False,
    "request_id": "aac7755b09944e4296b2848d81bd9411",
    "message": "IP 10.0.0.1 does not belong to this Business",
    "data": None,
}

EXECUTE_SUCCESS_GET_LOG_RETURN = {
    "code": 0,
    "result": True,
    "message": "success",
    "data": [
        {
            "status": 3,
            "step_results": [
                {
                    "tag": "",
                    "ip_logs": [
                        {"ip": "1.1.1.1", "log_content": "<SOPS_VAR>key1:value1</SOPS_VAR>\ngsectl\n-rwxr-xr-x 1\n"},
                        {"ip": "1.1.1.2", "log_content": ""},
                    ],
                    "ip_status": 9,
                }
            ],
        },
        {
            "status": 3,
            "step_results": [
                {
                    "tag": "",
                    "ip_logs": [
                        {
                            "ip": "1.1.1.1",
                            "log_content": "&lt;SOPS_VAR&gt;key2:value2&lt;/SOPS_VAR&gt;\n"
                            "dfg&lt;SOPS_VAR&gt;key3:value3&lt;/SOPS_VAR&gt;",
                        },
                    ],
                    "ip_status": 9,
                }
            ],
        },
    ],
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

EXECUTE_SUCCESS_GET_IP_LOG_RETURN = {
    "result": True,
    "code": 0,
    "message": "",
    "data": {"ip": "10.0.0.1", "bk_cloud_id": 0, "log_content": "[2018-03-15 14:39:30][PID:56875] job_start\n"},
}

# mock clients
FAST_EXECUTE_SCRIPT_FAIL_CLIENT = MockClient(
    fast_execute_script_return=FAIL_RESULT, get_job_instance_global_var_value_return={}
)

# mock clients
FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT = MockClient(
    fast_execute_script_return=SUCCESS_RESULT,
    get_job_instance_global_var_value_return={
        "data": {"step_instance_var_list": [{"global_var_list": [{"type": 1, "name": "name", "value": "value"}]}]},
        "result": True,
    },
    get_job_instance_log_return=EXECUTE_SUCCESS_GET_LOG_RETURN,
    get_job_instance_ip_log_return=EXECUTE_SUCCESS_GET_IP_LOG_RETURN,
    get_job_instance_status=EXECUTE_SUCCESS_GET_STATUS_RETURN,
)

# mock GET_NODE_CALLBACK_URL
GET_NODE_CALLBACK_URL_MOCK = MagicMock(return_value="callback_url")

# parent_data
PARENT_DATA = {"executor": "executor", "biz_cc_id": 1, "tenant_id": "system"}

# BASE_INPUTS
BASE_INPUTS = {
    "job_script_param": "1",
    "job_script_timeout": "100",
    "job_ip_list": "0:127.0.0.1;0:127.0.0.2",
    "job_account": "root",
    "job_script_list_public": "",
    "job_script_list_general": "",
    "custom_task_name": "",
    "job_rolling_config": {"job_rolling_execute": ["1"], "job_rolling_expression": "10%", "job_rolling_mode": "1"},
}
# manual inputs
MANUAL_INPUTS = BASE_INPUTS
MANUAL_INPUTS.update(
    {"job_script_source": "manual", "job_script_type": "1", "job_content": "echo", "ip_is_exist": False}
)

# ip is exist inputs
IP_EXIST_INPUTS = {
    "job_script_param": "1",
    "job_script_timeout": "100",
    "job_ip_list": "0:127.0.0.1;0:127.0.0.2",
    "job_account": "root",
    "job_script_list_public": "",
    "job_script_list_general": "",
    "job_script_source": "manual",
    "job_script_type": "1",
    "job_content": "echo",
    "job_rolling_config": {"job_rolling_execute": ["1"], "job_rolling_expression": "10%", "job_rolling_mode": "1"},
}

# MANUAL_KWARGS
MANUAL_KWARGS = {
    "bk_scope_type": "biz",
    "bk_scope_id": "1",
    "bk_biz_id": 1,
    "timeout": "100",
    "account_alias": "root",
    "target_server": {"ip_list": [{"ip": "127.0.0.1", "bk_cloud_id": 0}, {"ip": "127.0.0.2", "bk_cloud_id": 0}]},
    "callback_url": "callback_url",
    "rolling_config": {"expression": "10%", "mode": "1"},
    "script_param": "MQ==",
    "script_language": "1",
    "script_content": "ZWNobw==",
}

# 手动输入脚本失败样例输出
MANUAL_FAIL_OUTPUTS = {
    "ex_data": "调用作业平台(JOB)接口jobv3.fast_execute_script返回失败, error={error}, params={params}, "
    "request_id=aac7755b09944e4296b2848d81bd9411".format(params=json.dumps(MANUAL_KWARGS), error=FAIL_RESULT["message"])
}

IP_IS_EXIST_FAIL_OUTPUTS = MANUAL_FAIL_OUTPUTS

# 手动输入脚本成功样例输出
MANUAL_SUCCESS_OUTPUTS = {
    "job_inst_id": SUCCESS_RESULT["data"]["job_instance_id"],
    "job_inst_name": "API Quick execution script1521100521303",
    "job_inst_url": "instance_url_token",
}
MANUAL_SUCCESS_OUTPUTS2 = {
    "job_inst_id": SUCCESS_RESULT["data"]["job_instance_id"],
    "job_inst_name": "API Quick execution script1521100521303",
    "job_inst_url": "instance_url_token",
    "job_tagged_ip_dict": {
        "name": "JOB执行IP分组",
        "key": "job_tagged_ip_dict",
        "value": {
            "SUCCESS": {"DESC": "执行成功", "TAGS": {"ALL": "1.1.1.1,1.1.1.2"}},
            "SCRIPT_NOT_ZERO_EXIT_CODE": {"DESC": "脚本返回值非零", "TAGS": {"ALL": ""}},
            "OTHER_FAILED": {"desc": "其他异常", "TAGS": {"ALL": ""}},
        },
    },
    "name": "value",
    "log_outputs": {},
}

# 异步回调函数参数错误返回
SCHEDULE_CALLBACK_DATA_ERROR_OUTPUTS = {"ex_data": "invalid callback_data, job_instance_id: None, status: None"}
# 异步回调函数成功输出
SCHEDULE_SUCCESS_OUTPUTS = {"name": "value"}

# 手动输入脚本成功异步执行失败样例
FAST_EXECUTE_MANUAL_SCRIPT_SUCCESS_SCHEDULE_CALLBACK_DATA_ERROR_CASE = ComponentTestCase(
    name="fast execute manual script success schedule callback data error test case",
    inputs=MANUAL_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs=MANUAL_SUCCESS_OUTPUTS),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs=dict(list(MANUAL_SUCCESS_OUTPUTS.items()) + list(SCHEDULE_CALLBACK_DATA_ERROR_OUTPUTS.items())),
        callback_data={},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT.api.fast_execute_script,
            calls=[Call(MANUAL_KWARGS, headers={"X-Bk-Tenant-Id": "system"})],
        ),
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value=GET_NODE_CALLBACK_URL_MOCK()),
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "127.0.0.1", "Source": 1}, {"InnerIP": "127.0.0.2", "Source": 2}]},
        ),
    ],
)

# 手动输入脚本成功异步执行成功样例
FAST_EXECUTE_MANUAL_SCRIPT_SUCCESS_SCHEDULE_SUCCESS_CASE = ComponentTestCase(
    name="fast execute manual script and schedule success test case",
    inputs=MANUAL_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs=MANUAL_SUCCESS_OUTPUTS),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs=MANUAL_SUCCESS_OUTPUTS2,
        callback_data={"job_instance_id": 10000, "status": 3},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT.api.fast_execute_script,
            calls=[Call(MANUAL_KWARGS, headers={"X-Bk-Tenant-Id": "system"})],
        ),
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value=GET_NODE_CALLBACK_URL_MOCK()),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": []},
        ),
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT),
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "127.0.0.1", "Source": 1}, {"InnerIP": "127.0.0.2", "Source": 2}]},
        ),
    ],
)

# 手动输入脚本失败样例
FAST_EXECUTE_MANUAL_SCRIPT_FAIL_CASE = ComponentTestCase(
    name="fast execute manual script fail test case",
    inputs=MANUAL_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=False, outputs=MANUAL_FAIL_OUTPUTS),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=FAST_EXECUTE_SCRIPT_FAIL_CLIENT.api.fast_execute_script,
            calls=[Call(MANUAL_KWARGS, headers={"X-Bk-Tenant-Id": "system"})],
        ),
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value=GET_NODE_CALLBACK_URL_MOCK()),
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SCRIPT_FAIL_CLIENT),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "127.0.0.1", "Source": 1}, {"InnerIP": "127.0.0.2", "Source": 2}]},
        ),
    ],
)
