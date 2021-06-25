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
from pipeline_plugins.components.collections.sites.open.job import JobLocalContentUploadComponent


class JobLocalContentUploadComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        # return the component class which should be test
        return JobLocalContentUploadComponent

    def cases(self):
        # return your component test cases here
        return [
            LOCAL_CONTENT_UPLOAD_SUCCESS_SCHEDULE_CALLBACK_DATA_ERROR_CASE,
            LOCAL_CONTENT_UPLOAD_SUCCESS_SCHEDULE_SUCCESS_CASE,
            FAST_EXECUTE_MANUAL_SCRIPT_FAIL_CASE,
            LOCAL_CONTENT_UPLOAD_ACROSS_BIZ_SUCCESS,
        ]


class MockClient(object):
    def __init__(
        self,
        push_config_file_return=None,
        get_job_instance_global_var_value_return=None,
        get_job_instance_log_return=None,
    ):
        self.job = MagicMock()
        self.job.push_config_file = MagicMock(return_value=push_config_file_return)
        self.job.get_job_instance_global_var_value = MagicMock(return_value=get_job_instance_global_var_value_return)
        self.job.get_job_instance_log = MagicMock(return_value=get_job_instance_log_return)


# mock path
GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.job.local_content_upload.v1_0.get_client_by_user"
)
GET_NODE_CALLBACK_URL = (
    "pipeline_plugins.components.collections.sites.open.job.local_content_upload.v1_0.get_node_callback_url"
)
CC_GET_IPS_INFO_BY_STR = (
    "pipeline_plugins.components.collections.sites.open.job.local_content_upload.v1_0.cc_get_ips_info_by_str"
)
JOB_HANDLE_API_ERROR = (
    "pipeline_plugins.components.collections.sites.open.job.local_content_upload.v1_0.job_handle_api_error"
)
GET_JOB_INSTANCE_URL = (
    "pipeline_plugins.components.collections.sites.open.job.local_content_upload.v1_0.get_job_instance_url"
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

# mock clients
LOCAL_CONTENT_UPLOAD_FAIL_CLIENT = MockClient(
    push_config_file_return=FAIL_RESULT, get_job_instance_global_var_value_return={}
)

# mock clients
LOCAL_CONTENT_UPLOAD_SUCCESS_CLIENT = MockClient(
    push_config_file_return=SUCCESS_RESULT,
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

# parent_data
PARENT_DATA = {"executor": "executor", "biz_cc_id": 1}

INPUTS = {
    "local_name": "1.txt",
    "local_content": "123\n456\n789\n",
    "job_ip_list": "1.1.1.1",
    "file_account": "root",
    "file_path": "/tmp/bk_sops_test/",
}

ACROSS_BIZ_INPUTS = {
    "local_name": "1.txt",
    "local_content": "123\n456\n789\n",
    "job_ip_list": "2:1.1.1.1",
    "file_account": "root",
    "file_path": "/tmp/bk_sops_test/",
    "job_across_biz": True,
}

KWARGS = {
    "bk_biz_id": 1,
    "account": "root",
    "file_target_path": "/tmp/bk_sops_test/",
    "file_list": [{"file_name": "1.txt", "content": "MTIzCjQ1Ngo3ODkK"}],
    "ip_list": [],
}

# 手动输入脚本失败样例输出
MANUAL_FAIL_OUTPUTS = {
    "ex_data": "调用作业平台(JOB)接口job.push_config_file返回失败, params={params}, error={error}, "
    "request_id=aac7755b09944e4296b2848d81bd9411".format(params=json.dumps(KWARGS), error=FAIL_RESULT["message"])
}

IP_IS_EXIST_FAIL_OUTPUTS = {"ex_data": "IP 校验失败，请确认输入的 IP 127.0.0.2 是否合法"}

# 手动输入脚本成功样例输出
SUCCESS_OUTPUTS = {
    "job_inst_id": SUCCESS_RESULT["data"]["job_instance_id"],
    "job_inst_name": "API Quick execution script1521100521303",
    "job_inst_url": "instance_url_token",
}

# 异步回调函数参数错误返回
SCHEDULE_CALLBACK_DATA_ERROR_OUTPUTS = {"ex_data": "invalid callback_data, job_instance_id: None, status: None"}
# 异步回调函数成功输出
SCHEDULE_SUCCESS_OUTPUTS = {"name": "value"}

# 上传文件成功异步执行失败样例
LOCAL_CONTENT_UPLOAD_SUCCESS_SCHEDULE_CALLBACK_DATA_ERROR_CASE = ComponentTestCase(
    name="local content upload success schedule callback data error test case",
    inputs=INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs=SUCCESS_OUTPUTS),
    schedule_assertion=ScheduleAssertion(
        success=True, schedule_finished=True, outputs=dict(list(SUCCESS_OUTPUTS.items())),
    ),
    execute_call_assertion=[
        CallAssertion(func=LOCAL_CONTENT_UPLOAD_SUCCESS_CLIENT.job.push_config_file, calls=[Call(KWARGS)]),
    ],
    patchers=[
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": []},),
        Patcher(target=GET_CLIENT_BY_USER, return_value=LOCAL_CONTENT_UPLOAD_SUCCESS_CLIENT),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": []}),
    ],
)

# 上传文件成功异步执行成功样例
LOCAL_CONTENT_UPLOAD_SUCCESS_SCHEDULE_SUCCESS_CASE = ComponentTestCase(
    name="local content upload success and schedule success test case",
    inputs=INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs=SUCCESS_OUTPUTS),
    schedule_assertion=ScheduleAssertion(
        success=True,
        schedule_finished=True,
        outputs=dict(list(SUCCESS_OUTPUTS.items())),
        callback_data={"job_instance_id": 10000, "status": 3},
    ),
    execute_call_assertion=[
        CallAssertion(func=LOCAL_CONTENT_UPLOAD_SUCCESS_CLIENT.job.push_config_file, calls=[Call(KWARGS)]),
    ],
    patchers=[
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": []}),
        Patcher(target=GET_CLIENT_BY_USER, return_value=LOCAL_CONTENT_UPLOAD_SUCCESS_CLIENT),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": []}),
    ],
)

#  上传文件失败样例
FAST_EXECUTE_MANUAL_SCRIPT_FAIL_CASE = ComponentTestCase(
    name="fast execute manual script fail test case",
    inputs=INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=False, outputs=MANUAL_FAIL_OUTPUTS),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=LOCAL_CONTENT_UPLOAD_FAIL_CLIENT.job.push_config_file, calls=[Call(KWARGS)]),
    ],
    patchers=[
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": []},),
        Patcher(target=GET_CLIENT_BY_USER, return_value=LOCAL_CONTENT_UPLOAD_FAIL_CLIENT),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": []}),
    ],
)

# 上传文件成功异步执行成功样例
LOCAL_CONTENT_UPLOAD_ACROSS_BIZ_SUCCESS = ComponentTestCase(
    name="local content upload across biz success",
    inputs=ACROSS_BIZ_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs=SUCCESS_OUTPUTS),
    schedule_assertion=ScheduleAssertion(
        success=True,
        schedule_finished=True,
        outputs=dict(list(SUCCESS_OUTPUTS.items())),
        callback_data={"job_instance_id": 10000, "status": 3},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=LOCAL_CONTENT_UPLOAD_SUCCESS_CLIENT.job.push_config_file,
            calls=[
                Call(
                    {
                        "bk_biz_id": 1,
                        "account": "root",
                        "file_target_path": "/tmp/bk_sops_test/",
                        "file_list": [{"file_name": "1.txt", "content": "MTIzCjQ1Ngo3ODkK"}],
                        "ip_list": [{"ip": "1.1.1.1", "bk_cloud_id": "2"}],
                    }
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": []}),
        Patcher(target=GET_CLIENT_BY_USER, return_value=LOCAL_CONTENT_UPLOAD_SUCCESS_CLIENT),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": []}),
    ],
)
