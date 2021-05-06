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
import json

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
from pipeline_plugins.components.collections.sites.ieod.job.cc_execute_script.v1_0 import JobCcExecuteScriptComponent


class JobCcExecuteScriptComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        # return the component class which should be testet
        return JobCcExecuteScriptComponent

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
        get_job_instance_log_return=None,
    ):
        self.job = MagicMock()
        self.job.fast_execute_script = MagicMock(return_value=fast_execute_script_return)
        self.job.get_job_instance_log = MagicMock(return_value=get_job_instance_log_return)


# mock path
GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.ieod.job.cc_execute_script.v1_0.get_client_by_user"
GET_NODE_CALLBACK_URL = (
    "pipeline_plugins.components.collections.sites.ieod.job.cc_execute_script.v1_0.get_node_callback_url"
)
JOB_HANDLE_API_ERROR = (
    "pipeline_plugins.components.collections.sites.ieod.job.cc_execute_script.v1_0.job_handle_api_error"
)
GET_JOB_INSTANCE_URL = (
    "pipeline_plugins.components.collections.sites.ieod.job.cc_execute_script.v1_0.get_job_instance_url"
)
ENVIRONMENT_VAIRABLES_GET = "pipeline_plugins.components.collections.sites.open.wechat_work.wechat_work_send_message.v1_0.EnvironmentVariables.objects.get_var"  # noqa

# manual inputs
MANUAL_INPUTS = {
    "job_script_param": "1",
    "job_script_timeout": "100",
    "job_script_list_public": "",
    "job_script_list_general": "",
    "job_script_source": "manual",
    "job_script_type": "1",
    "job_content": "echo",
    "job_output_param": "hostName,InnerIP",
    "job_output_breakline": ",",
}

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
                        {
                            "ip": "1.1.1.1",
                            "log_content": "hostName\tIDC\tInnerIP\n" "NULL\t重庆\t127.0.0.1\nfea\t成都\t172.0.0.1",
                        },
                    ],
                    "ip_status": 9,
                }
            ],
        },
    ],
}

# parent_data
PARENT_DATA = {"executor": "executor", "biz_cc_id": 1}

# mock clients
FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT = MockClient(
    fast_execute_script_return=SUCCESS_RESULT,
    get_job_instance_log_return=EXECUTE_SUCCESS_GET_LOG_RETURN,
)

# mock clients
FAST_EXECUTE_SCRIPT_FAIL_CLIENT = MockClient(fast_execute_script_return=FAIL_RESULT)

# 手动输入脚本成功样例输出
MANUAL_SUCCESS_OUTPUTS = {
    "job_inst_id": SUCCESS_RESULT["data"]["job_instance_id"],
    "job_inst_name": "API Quick execution script1521100521303",
    "job_inst_url": "instance_url_token",
    "client": FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT,
}

# MANUAL_KWARGS
MANUAL_KWARGS = {
    "bk_biz_id": 1,
    "script_timeout": "100",
    "account": "admin",
    "ip_list": [{"ip": "127.0.0.1", "bk_cloud_id": "0"}],
    "bk_callback_url": "callback_url",
    "script_param": "MQ==",
    "script_type": "1",
    "script_content": "ZWNobw==",
}

# 异步回调函数成功输出
SCHEDULE_SUCCESS_OUTPUTS = {"name": "value"}

# 手动输入脚本失败样例输出
MANUAL_FAIL_OUTPUTS = {
    "ex_data": "调用作业平台(JOB)接口job.fast_execute_script返回失败, params={params}, error={error}, "
    "request_id=4a487ef38cf14157a0c3795310bad1a3".format(params=json.dumps(MANUAL_KWARGS), error=FAIL_RESULT["message"])
}


def get_env_value(param):
    env_value = {"SOPS_CC_SCRIPT_IP": "0:127.0.0.1", "SOPS_CC_SCRIPT_ACCOUNT": "admin"}
    return env_value[param]


# 手动输入脚本成功异步执行成功样例
FAST_EXECUTE_MANUAL_SCRIPT_SUCCESS_SCHEDULE_SUCCESS_CASE = ComponentTestCase(
    name="fast execute manual script and schedule success test case",
    inputs=MANUAL_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs=MANUAL_SUCCESS_OUTPUTS),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs=dict(
            MANUAL_SUCCESS_OUTPUTS, **{"cc_outputs": {"hostName": "NULL,fea", "InnerIP": "127.0.0.1,172.0.0.1"}}
        ),
        callback_data={"job_instance_id": 10000, "status": 3},
    ),
    execute_call_assertion=[
        CallAssertion(func=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT.job.fast_execute_script, calls=[Call(MANUAL_KWARGS)]),
    ],
    patchers=[
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="callback_url"),
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=ENVIRONMENT_VAIRABLES_GET, side_effect=get_env_value),
    ],
)

# 手动输入脚本成功异步执行失败样例
FAST_EXECUTE_MANUAL_SCRIPT_SUCCESS_SCHEDULE_CALLBACK_DATA_ERROR_CASE = ComponentTestCase(
    name="fast execute manual script success schedule callback data error test case",
    inputs=MANUAL_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs=MANUAL_SUCCESS_OUTPUTS),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs=dict(
            MANUAL_SUCCESS_OUTPUTS, **{"ex_data": "invalid callback_data, job_instance_id: None, status: None"}
        ),
        callback_data={},
    ),
    execute_call_assertion=[
        CallAssertion(func=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT.job.fast_execute_script, calls=[Call(MANUAL_KWARGS)]),
    ],
    patchers=[
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="callback_url"),
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=ENVIRONMENT_VAIRABLES_GET, side_effect=get_env_value),
    ],
)

# 手动输入脚本失败样例
FAST_EXECUTE_MANUAL_SCRIPT_FAIL_CASE = ComponentTestCase(
    name="fast execute manual script fail test case",
    inputs=MANUAL_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "ex_data": "调用作业平台(JOB)接口job.fast_execute_script返回失败, "
            'params={"bk_biz_id":1,"script_timeout":"100",'
            '"account":"admin","ip_list":[{"ip":"127.0.0.1",'
            '"bk_cloud_id":"0"}],"bk_callback_url":"callback_url",'
            '"script_param":"MQ==","script_type":"1","script_content":'
            '"ZWNobw=="}, error=IP 10.0.0.1 does not belong '
            "to this Business, request_id=aac7755b09944e4296b2848d81bd9411"
        },
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=FAST_EXECUTE_SCRIPT_FAIL_CLIENT.job.fast_execute_script, calls=[Call(MANUAL_KWARGS)]),
    ],
    patchers=[
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="callback_url"),
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SCRIPT_FAIL_CLIENT),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=ENVIRONMENT_VAIRABLES_GET, side_effect=get_env_value),
    ],
)
