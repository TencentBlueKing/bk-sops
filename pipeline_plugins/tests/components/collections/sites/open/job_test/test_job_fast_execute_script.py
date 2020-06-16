# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
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
    ComponentTestMixin,
    ComponentTestCase,
    CallAssertion,
    ExecuteAssertion,
    ScheduleAssertion,
    Call,
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.job import JobFastExecuteScriptComponent


class JobFastExecuteScriptComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        # return the component class which should be testet
        return JobFastExecuteScriptComponent

    def cases(self):
        # return your component test cases here
        return [
            FAST_EXECUTE_MANUAL_SCRIPT_SUCCESS_SCHEDULE_CALLBACK_DATA_ERROR_CASE,
            FAST_EXECUTE_MANUAL_SCRIPT_SUCCESS_SCHEDULE_SUCCESS_CASE,
            FAST_EXECUTE_MANUAL_SCRIPT_FAIL_CASE,
        ]


class MockClient(object):
    def __init__(
        self,
        fast_execute_script_return=None,
        get_job_instance_global_var_value_return=None,
        get_job_instance_log_return=None,
    ):
        self.job = MagicMock()
        self.job.fast_execute_script = MagicMock(return_value=fast_execute_script_return)
        self.job.get_job_instance_global_var_value = MagicMock(return_value=get_job_instance_global_var_value_return)
        self.job.get_job_instance_log = MagicMock(return_value=get_job_instance_log_return)


# mock path
GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.get_client_by_user"
GET_NODE_CALLBACK_URL = "pipeline_plugins.components.collections.sites.open.job.get_node_callback_url"
CC_GET_IPS_INFO_BY_STR = "pipeline_plugins.components.collections.sites.open.job.cc_get_ips_info_by_str"
JOB_HANDLE_API_ERROR = "pipeline_plugins.components.collections.sites.open.job.job_handle_api_error"
GET_JOB_INSTANCE_URL = "pipeline_plugins.components.collections.sites.open.job.get_job_instance_url"

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
                            "log_content": "<SOPS_VAR>key2:value2</SOPS_VAR>\ngsectl<SOPS_VAR>key3:value3</SOPS_VAR>",
                        },
                    ],
                    "ip_status": 9,
                }
            ],
        },
    ],
}


# mock clients
FAST_EXECUTE_SCRIPT_FAIL_CLIENT = MockClient(
    fast_execute_script_return=FAIL_RESULT, get_job_instance_global_var_value_return={}
)

# mock clients
FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT = MockClient(
    fast_execute_script_return=SUCCESS_RESULT,
    get_job_instance_global_var_value_return={
        "data": {
            "job_instance_var_values": [
                {"step_instance_var_values": [{"category": 1, "name": "name", "value": "value"}]}
            ]
        },
        "result": True,
    },
    get_job_instance_log_return=EXECUTE_SUCCESS_GET_LOG_RETURN,
)

# mock GET_NODE_CALLBACK_URL
GET_NODE_CALLBACK_URL_MOCK = MagicMock(return_value="callback_url")


# parent_data
PARENT_DATA = {"executor": "executor", "biz_cc_id": 1}

# BASE_INPUTS
BASE_INPUTS = {
    "job_script_param": "1",
    "job_script_timeout": "100",
    "job_ip_list": "127.0.0.1\n127.0.0.2",
    "job_account": "root",
    "job_script_list_public": "",
    "job_script_list_general": "",
}


# manual inputs
MANUAL_INPUTS = BASE_INPUTS
MANUAL_INPUTS.update(
    {"job_script_source": "manual", "job_script_type": "1", "job_content": "echo"}
)

# MANUAL_KWARGS
MANUAL_KWARGS = {
    "bk_biz_id": 1,
    "script_timeout": "100",
    "account": "root",
    "ip_list": [],
    "bk_callback_url": "callback_url",
    "script_param": "MQ==",
    "script_type": "1",
    "script_content": "ZWNobw==",
}

# 手动输入脚本失败样例输出
MANUAL_FAIL_OUTPUTS = {
    "ex_data": "调用作业平台(JOB)接口job.fast_execute_script返回失败, params={params}, error={error}".format(
        params=json.dumps(MANUAL_KWARGS), error=FAIL_RESULT["message"]
    )
}

# 手动输入脚本成功样例输出
MANUAL_SUCCESS_OUTPUTS = {
    "job_inst_id": SUCCESS_RESULT["data"]["job_instance_id"],
    "job_inst_name": "API Quick execution script1521100521303",
    "job_inst_url": "instance_url_token",
    "client": FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT,
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
        CallAssertion(func=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT.job.fast_execute_script, calls=[Call(MANUAL_KWARGS)]),
    ],
    patchers=[
        Patcher(target=GET_NODE_CALLBACK_URL, return_value=GET_NODE_CALLBACK_URL_MOCK()),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": []},),
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
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
        outputs=dict(
            list(MANUAL_SUCCESS_OUTPUTS.items())
            + list(SCHEDULE_SUCCESS_OUTPUTS.items())
            + [("log_outputs", {"key1": "value1", "key2": "value2", "key3": "value3"})]
        ),
        callback_data={"job_instance_id": 10000, "status": 3},
    ),
    execute_call_assertion=[
        CallAssertion(func=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT.job.fast_execute_script, calls=[Call(MANUAL_KWARGS)]),
    ],
    patchers=[
        Patcher(target=GET_NODE_CALLBACK_URL, return_value=GET_NODE_CALLBACK_URL_MOCK()),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": []},),
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
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
        CallAssertion(func=FAST_EXECUTE_SCRIPT_FAIL_CLIENT.job.fast_execute_script, calls=[Call(MANUAL_KWARGS)]),
    ],
    patchers=[
        Patcher(target=GET_NODE_CALLBACK_URL, return_value=GET_NODE_CALLBACK_URL_MOCK()),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": []},),
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SCRIPT_FAIL_CLIENT),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
    ],
)
