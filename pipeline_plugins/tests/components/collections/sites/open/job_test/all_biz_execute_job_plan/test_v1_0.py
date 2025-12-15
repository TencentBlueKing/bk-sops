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

from gcloud.utils import crypto
from pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.v1_0 import (
    AllBizJobExecuteJobPlanComponent,
)
from pipeline_plugins.components.query.sites.open.job import JOBV3_VAR_CATEGORY_PASSWORD
from pipeline_plugins.tests.components.collections.sites.open.utils.cc_ipv6_mock_utils import MockCMDBClientIPv6


class AllBizJobExecuteJobPlanComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        # return the component class which should be testet
        return AllBizJobExecuteJobPlanComponent

    def cases(self):
        # return your component test cases here
        return [
            # SUCCESS
            EXECUTE_JOB_PLAN_SUCCESS_CASE,
            EXECUTE_JOB_PLAN_BIZ_SET_SUCCESS_CASE,
            # FAIL
            EXECUTE_JOB_PLAN_NOT_SUCCESS_CASE,
            EXECUTE_JOB_PLAN_CALL_FAIL_CASE,
            INVALID_CALLBACK_DATA_CASE,
            GET_GLOBAL_VAR_FAIL_CASE,
        ]


class JobMockClient(object):
    def __init__(
        self,
        execute_job_plan_return=None,
        get_job_instance_global_var_value_return=None,
        get_job_instance_ip_log_return=None,
        get_job_instance_status_return=None,
    ):
        self.api = MagicMock()
        self.api.execute_job_plan = MagicMock(return_value=execute_job_plan_return)
        self.api.get_job_instance_global_var_value = MagicMock(return_value=get_job_instance_global_var_value_return)
        self.api.get_job_instance_ip_log = MagicMock(return_value=get_job_instance_ip_log_return)
        self.api.get_job_instance_status = MagicMock(return_value=get_job_instance_status_return)


class CcMockClient(object):
    def __init__(self, list_business_set_return=None):
        self.api = MagicMock()
        self.api.list_business_set = MagicMock(return_value=list_business_set_return)


class BkUserMockClient(object):
    def __init__(self, batch_lookup_virtual_user_return=None):
        self.api = MagicMock()
        self.api.batch_lookup_virtual_user = MagicMock(return_value=batch_lookup_virtual_user_return)


GET_BK_USERNAME_BY_TENANT = "gcloud.core.api_adapter.user_info.get_client_by_username"

# mock path
GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.base_service."
    "get_client_by_username"
)

# 添加 CC client mock 路径，用于 IPv6 支持
CC_GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username"
CMDB_GET_CLIENT_BY_USERNAME = "gcloud.utils.cmdb.get_client_by_username"
GET_TARGET_SERVER_BIZ_SET = (
    "pipeline_plugins.components.collections.sites.open.job"
    ".all_biz_execute_job_plan.base_service.BaseAllBizJobExecuteJobPlanService.get_target_server_biz_set"
)

GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username"


# MockCMDBClient class definition for IPv6 support
class MockCMDBClient(MockCMDBClientIPv6):
    pass


GET_NODE_CALLBACK_URL = (
    "pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.base_service.get_node_callback_url"
)
JOB_HANDLE_API_ERROR = (
    "pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.base_service.job_handle_api_error"
)
GET_JOB_INSTANCE_URL = (
    "pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.base_service.get_job_instance_url"
)
UTILS_GET_CLIENT_BY_USER = "pipeline_plugins.components.utils.cc.get_client_by_username"

# 添加 CC client mock 路径，用于 IPv6 支持
CC_GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username"
CMDB_GET_CLIENT_BY_USERNAME = "gcloud.utils.cmdb.get_client_by_username"

# success result
EXECUTE_JOB_PLAN_SUCCESS_RESULT = {
    "result": True,
    "code": 0,
    "message": "success",
    "data": {"job_instance_name": "API execute_job_plan test", "job_instance_id": 10000},
}

# fail result
EXECUTE_JOB_PLAN_FAIL_RESULT = {
    "message": "Job plan does not exist",
    "code": 1244012,
    "data": None,
    "result": False,
    "request_id": "1e4825b1f0354e509d2bc25eb172f8dc",
}

BK_USER_CLIENT = BkUserMockClient(
    batch_lookup_virtual_user_return={
        "data": [
            {"bk_username": "7idwx3b7nzk6xigs", "login_name": "zhangsan", "display_name": "zhangsan(张三)"},
            {"bk_username": "0wngfim3uzhadh1w", "login_name": "lisi", "display_name": "lisi(李四)"},
        ]
    },
)

# mock clients
INVALID_IP_CLIENT = CcMockClient(list_business_set_return={"result": True, "data": {"info": []}})
INVALID_IP_CLIENT_BIZ_SET = CcMockClient(list_business_set_return={"result": True, "data": {"info": ["biz_set"]}})
EXECUTE_JOB_PLAN_SUCCESS_CLIENT = JobMockClient(
    execute_job_plan_return=EXECUTE_JOB_PLAN_SUCCESS_RESULT,
    get_job_instance_global_var_value_return={},
)
EXECUTE_JOB_PLAN_FAIL_CLIENT = JobMockClient(
    execute_job_plan_return=EXECUTE_JOB_PLAN_FAIL_RESULT,
    get_job_instance_global_var_value_return={},
)
INVALID_CALLBACK_DATA_CLIENT = JobMockClient(
    execute_job_plan_return=EXECUTE_JOB_PLAN_SUCCESS_RESULT,
)
GET_GLOBAL_VAR_CALL_FAIL_CLIENT = JobMockClient(
    execute_job_plan_return=EXECUTE_JOB_PLAN_SUCCESS_RESULT,
    get_job_instance_global_var_value_return={"result": False, "message": "global var message token"},
)
EXECUTE_JOB_PLAN_NOT_SUCCESS_CLIENT = JobMockClient(
    execute_job_plan_return=EXECUTE_JOB_PLAN_SUCCESS_RESULT,
    get_job_instance_global_var_value_return={"result": False, "message": "global var message token"},
)
EXECUTE_JOB_PLAN_SUCCESS_CASE_CLIENT = JobMockClient(
    execute_job_plan_return=EXECUTE_JOB_PLAN_SUCCESS_RESULT,
    get_job_instance_global_var_value_return={
        "message": "",
        "code": 0,
        "data": {
            "job_instance_id": 10000,
            "step_instance_var_list": [
                {"step_instance_id": 20000000577, "global_var_list": [{"type": 1, "name": "name", "value": "test"}]},
                {"step_instance_id": 20000000578, "global_var_list": [{"type": 1, "name": "name", "value": "test"}]},
            ],
        },
        "result": True,
        "request_id": "9cd2af3c1ac743b686d9c448ac66a0b3",
    },
    get_job_instance_status_return={
        "message": "",
        "code": 0,
        "data": {
            "job_instance": {
                "job_instance_id": 10000,
                "bk_biz_id": 2,
                "name": "全业务_执行方案作业测试",
                "start_time": 1620802889923,
                "create_time": 1620802889072,
                "status": 3,
                "end_time": 1620802895090,
                "total_time": 5167,
            },
            "finished": True,
            "step_instance_list": [
                {
                    "status": 3,
                    "total_time": 3869,
                    "name": "步骤执行脚本_1",
                    "start_time": 1620802889999,
                    "step_instance_id": 20000000577,
                    "step_ip_result_list": [
                        {
                            "status": 9,
                            "total_time": 1352,
                            "ip": "192.168.20.218",
                            "start_time": 1620802890474,
                            "exit_code": 0,
                            "bk_cloud_id": 0,
                            "tag": "tag1",
                            "end_time": 1620802891826,
                            "error_code": 0,
                        }
                    ],
                    "create_time": 1620802889109,
                    "end_time": 1620802893836,
                    "execute_count": 0,
                    "type": 1,
                },
                {
                    "status": 3,
                    "total_time": 1164,
                    "name": "步骤执行脚本_2",
                    "start_time": 1620802893919,
                    "step_instance_id": 20000000578,
                    "step_ip_result_list": [
                        {
                            "status": 9,
                            "total_time": 686,
                            "ip": "192.168.20.218",
                            "start_time": 1620802893976,
                            "exit_code": 0,
                            "bk_cloud_id": 0,
                            "tag": "tag2",
                            "end_time": 1620802894662,
                            "error_code": 0,
                        }
                    ],
                    "create_time": 1620802889109,
                    "end_time": 1620802895059,
                    "execute_count": 0,
                    "type": 1,
                },
            ],
        },
        "result": True,
        "request_id": "3d5db2fa69bb4407947414661cb5a65c",
    },
    get_job_instance_ip_log_return={
        "message": "",
        "code": 0,
        "data": {
            "ip": "192.168.20.218",
            "log_content": "[2021-05-12 15:01:34][PID:15340] job_start\n",
            "bk_cloud_id": 0,
        },
        "result": True,
        "request_id": "3e6b4764ff9d40eaa2797428a0de6b8f",
    },
)
EXECUTE_JOB_PLAN_BIZ_SET_SUCCESS_CASE_CLIENT = JobMockClient(
    execute_job_plan_return=EXECUTE_JOB_PLAN_SUCCESS_RESULT,
    get_job_instance_global_var_value_return={
        "message": "",
        "code": 0,
        "data": {
            "job_instance_id": 10000,
            "step_instance_var_list": [
                {
                    "step_instance_id": 20000000577,
                    "global_var_list": [
                        # 已重新编辑，需要传递给 Job
                        {"type": JOBV3_VAR_CATEGORY_PASSWORD, "name": "password_1", "value": "test"},
                        # Job 侧脱敏，无需传递
                        {"type": JOBV3_VAR_CATEGORY_PASSWORD, "name": "password", "value": "******"},
                    ],
                },
                {"step_instance_id": 20000000578, "global_var_list": [{"type": 1, "name": "name", "value": "test"}]},
            ],
        },
        "result": True,
        "request_id": "9cd2af3c1ac743b686d9c448ac66a0b3",
    },
    get_job_instance_status_return={
        "message": "",
        "code": 0,
        "data": {
            "job_instance": {
                "job_instance_id": 10000,
                "bk_biz_id": 2,
                "name": "全业务_执行方案作业测试",
                "start_time": 1620802889923,
                "create_time": 1620802889072,
                "status": 3,
                "end_time": 1620802895090,
                "total_time": 5167,
            },
            "finished": True,
            "step_instance_list": [
                {
                    "status": 3,
                    "total_time": 3869,
                    "name": "步骤执行脚本_1",
                    "start_time": 1620802889999,
                    "step_instance_id": 20000000577,
                    "step_ip_result_list": [
                        {
                            "status": 9,
                            "total_time": 1352,
                            "ip": "192.168.20.218",
                            "start_time": 1620802890474,
                            "exit_code": 0,
                            "bk_cloud_id": 0,
                            "tag": "tag1",
                            "end_time": 1620802891826,
                            "error_code": 0,
                        }
                    ],
                    "create_time": 1620802889109,
                    "end_time": 1620802893836,
                    "execute_count": 0,
                    "type": 1,
                },
                {
                    "status": 3,
                    "total_time": 1164,
                    "name": "步骤执行脚本_2",
                    "start_time": 1620802893919,
                    "step_instance_id": 20000000578,
                    "step_ip_result_list": [
                        {
                            "status": 9,
                            "total_time": 686,
                            "ip": "192.168.20.218",
                            "start_time": 1620802893976,
                            "exit_code": 0,
                            "bk_cloud_id": 0,
                            "tag": "tag2",
                            "end_time": 1620802894662,
                            "error_code": 0,
                        }
                    ],
                    "create_time": 1620802889109,
                    "end_time": 1620802895059,
                    "execute_count": 0,
                    "type": 1,
                },
            ],
        },
        "result": True,
        "request_id": "3d5db2fa69bb4407947414661cb5a65c",
    },
    get_job_instance_ip_log_return={
        "message": "",
        "code": 0,
        "data": {
            "ip": "192.168.20.218",
            "log_content": "[2021-05-12 15:01:34][PID:15340] job_start\n",
            "bk_cloud_id": 0,
        },
        "result": True,
        "request_id": "3e6b4764ff9d40eaa2797428a0de6b8f",
    },
)

# mock CALLBACK_URL
EXECUTE_JOB_PLAN_FAIL_CALLBACK_URL_MOCK = MagicMock(return_value="callback_url")

# execute_job_plan_success
EXECUTE_JOB_PLAN_SUCCESS_CASE = ComponentTestCase(
    name="get var failed but execute result must be success",
    inputs={
        "all_biz_job_config": {
            "all_biz_cc_id": 2,
            "job_plan_id": 1000010,
            "is_tagged_ip": True,
            "job_global_var": [
                {"id": 1000030, "type": 1, "name": "name", "value": "test", "description": ""},
                {"id": 1000031, "type": 3, "name": "ip", "value": "0:192.168.20.218", "description": ""},
            ],
        }
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 2, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 10000,
            "job_inst_name": "API execute_job_plan test",
            "biz_cc_id": 2,
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 10000,
            "job_inst_name": "API execute_job_plan test",
            "biz_cc_id": 2,
            "job_tagged_ip_dict": {"tag2": "192.168.20.218"},
            "name": "test",
            "log_outputs": {},
        },
        callback_data={"job_instance_id": 10000, "status": 3},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=EXECUTE_JOB_PLAN_SUCCESS_CASE_CLIENT.api.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "2",
                        "bk_biz_id": 2,
                        "job_plan_id": 1000010,
                        "global_var_list": [
                            {"id": 1000030, "value": "test"},
                            {"id": 1000031, "server": {"ip_list": [{"ip": "192.168.20.218", "bk_cloud_id": 0}]}},
                        ],
                        "callback_url": "callback_url",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=EXECUTE_JOB_PLAN_SUCCESS_CASE_CLIENT.api.get_job_instance_global_var_value,
            calls=[
                Call(
                    {"bk_scope_type": "biz", "bk_scope_id": "2", "bk_biz_id": 2, "job_instance_id": 10000},
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(
            target=GET_TARGET_SERVER_BIZ_SET,
            return_value=(True, {"ip_list": [{"ip": "192.168.20.218", "bk_cloud_id": 0}]}),
        ),
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_JOB_PLAN_SUCCESS_CASE_CLIENT),
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=EXECUTE_JOB_PLAN_SUCCESS_CASE_CLIENT),
        Patcher(target=UTILS_GET_CLIENT_BY_USER, return_value=EXECUTE_JOB_PLAN_SUCCESS_CASE_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="callback_url"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=GET_BK_USERNAME_BY_TENANT, return_value=BK_USER_CLIENT),
    ],
)
# 作业执行不成功
EXECUTE_JOB_PLAN_NOT_SUCCESS_CASE = ComponentTestCase(
    name="execute job plan not success case",
    inputs={
        "all_biz_job_config": {
            "all_biz_cc_id": 2,
            "job_plan_id": 1000010,
            "job_global_var": [
                {"id": 1000030, "type": 1, "name": "name", "value": "test", "description": ""},
                {"id": 1000031, "type": 3, "name": "ip", "value": "0:192.168.20.218", "description": ""},
            ],
        }
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 2, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 10000,
            "job_inst_name": "API execute_job_plan test",
            "biz_cc_id": 2,
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 10000,
            "job_inst_name": "API execute_job_plan test",
            "biz_cc_id": 2,
            "ex_data": {
                "exception_msg": "任务执行失败，<a href='{job_inst_url}' target='_blank'>前往作业平台(JOB)查看详情</a>".format(
                    job_inst_url="instance_url_token"
                ),
                "task_inst_id": 10000,
                "show_ip_log": True,
            },
        },
        callback_data={"job_instance_id": 10000, "status": 1},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=EXECUTE_JOB_PLAN_NOT_SUCCESS_CLIENT.api.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "2",
                        "bk_biz_id": 2,
                        "job_plan_id": 1000010,
                        "global_var_list": [
                            {"id": 1000030, "value": "test"},
                            {"id": 1000031, "server": {"ip_list": [{"ip": "192.168.20.218", "bk_cloud_id": 0}]}},
                        ],
                        "callback_url": "callback_url",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(
            target=GET_TARGET_SERVER_BIZ_SET,
            return_value=(True, {"ip_list": [{"ip": "192.168.20.218", "bk_cloud_id": 0}]}),
        ),
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_JOB_PLAN_NOT_SUCCESS_CLIENT),
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=EXECUTE_JOB_PLAN_NOT_SUCCESS_CLIENT),
        Patcher(target=UTILS_GET_CLIENT_BY_USER, return_value=EXECUTE_JOB_PLAN_NOT_SUCCESS_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="callback_url"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=GET_BK_USERNAME_BY_TENANT, return_value=BK_USER_CLIENT),
    ],
)
# 调用作业平台执行作业失败
EXECUTE_JOB_PLAN_CALL_FAIL_CASE = ComponentTestCase(
    name="all biz execute job plan failed case",
    inputs={
        "all_biz_job_config": {
            "all_biz_cc_id": 999101,
            "job_plan_id": 1000010,
            "job_global_var": [
                {"id": 1000030, "type": 1, "name": "name", "value": "123", "description": ""},
                {"id": 1000031, "type": 3, "name": "ip", "value": "0:192.168.20.218", "description": ""},
            ],
        }
    },
    parent_data={"executor": "executor", "biz_cc_id": 1, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "ex_data": (
                "调用作业平台(JOB)接口jobv3.execute_job_plan返回失败, error={error}, params={params}, request_id={request_id}"
            ).format(
                params=json.dumps(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "999101",
                        "bk_biz_id": 999101,
                        "job_plan_id": 1000010,
                        "global_var_list": [
                            {"id": 1000030, "value": "123"},
                            {"id": 1000031, "server": {"ip_list": [{"ip": "192.168.20.218", "bk_cloud_id": 0}]}},
                        ],
                        "callback_url": "callback_url",
                    }
                ),
                error="Job plan does not exist",
                request_id="1e4825b1f0354e509d2bc25eb172f8dc",
            )
        },
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=EXECUTE_JOB_PLAN_FAIL_CLIENT.api.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "999101",
                        "bk_biz_id": 999101,
                        "job_plan_id": 1000010,
                        "global_var_list": [
                            {"id": 1000030, "value": "123"},
                            {"id": 1000031, "server": {"ip_list": [{"ip": "192.168.20.218", "bk_cloud_id": 0}]}},
                        ],
                        "callback_url": "callback_url",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(
            target=GET_TARGET_SERVER_BIZ_SET,
            return_value=(True, {"ip_list": [{"ip": "192.168.20.218", "bk_cloud_id": 0}]}),
        ),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="callback_url"),
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_JOB_PLAN_FAIL_CLIENT),
        Patcher(target=UTILS_GET_CLIENT_BY_USER, return_value=EXECUTE_JOB_PLAN_FAIL_CLIENT),
        Patcher(target=GET_BK_USERNAME_BY_TENANT, return_value=BK_USER_CLIENT),
    ],
)
# 回调不合法
INVALID_CALLBACK_DATA_CASE = ComponentTestCase(
    name="all biz execute job plan invalid callback case",
    inputs={
        "all_biz_job_config": {
            "all_biz_cc_id": 2,
            "job_plan_id": 1000010,
            "job_global_var": [
                {"id": 1000030, "type": 1, "name": "name", "value": "test", "description": ""},
                {"id": 1000031, "type": 3, "name": "ip", "value": "0:192.168.20.218", "description": ""},
            ],
        }
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 1, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 10000,
            "job_inst_name": "API execute_job_plan test",
            "biz_cc_id": 2,
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 10000,
            "job_inst_name": "API execute_job_plan test",
            "biz_cc_id": 2,
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
                        "bk_scope_id": "2",
                        "bk_biz_id": 2,
                        "job_plan_id": 1000010,
                        "global_var_list": [
                            {"id": 1000030, "value": "test"},
                            {"id": 1000031, "server": {"ip_list": [{"ip": "192.168.20.218", "bk_cloud_id": 0}]}},
                        ],
                        "callback_url": "callback_url",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(
            target=GET_TARGET_SERVER_BIZ_SET,
            return_value=(True, {"ip_list": [{"ip": "192.168.20.218", "bk_cloud_id": 0}]}),
        ),
        Patcher(target=GET_CLIENT_BY_USER, return_value=INVALID_CALLBACK_DATA_CLIENT),
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=INVALID_CALLBACK_DATA_CLIENT),
        Patcher(target=UTILS_GET_CLIENT_BY_USER, return_value=INVALID_CALLBACK_DATA_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="callback_url"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=GET_BK_USERNAME_BY_TENANT, return_value=BK_USER_CLIENT),
    ],
)
# 获取全局变量失败
GET_GLOBAL_VAR_FAIL_CASE = ComponentTestCase(
    name="all biz execute job plan get global var fail case",
    inputs={
        "all_biz_job_config": {
            "all_biz_cc_id": 2,
            "job_plan_id": 1000010,
            "is_tagged_ip": False,
            "job_global_var": [
                {"id": 1000030, "type": 1, "name": "name", "value": "test", "description": ""},
                {"id": 1000031, "type": 3, "name": "ip", "value": "0:192.168.20.218", "description": ""},
            ],
        }
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 2, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 10000,
            "job_inst_name": "API execute_job_plan test",
            "biz_cc_id": 2,
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 10000,
            "job_inst_name": "API execute_job_plan test",
            "biz_cc_id": 2,
            "job_tagged_ip_dict": {},
            "ex_data": (
                "调用作业平台(JOB)接口jobv3.get_job_instance_global_var_value"
                "返回失败, error=global var message token, params={params}"
            ).format(
                params=json.dumps(
                    {"bk_scope_type": "biz", "bk_scope_id": "2", "bk_biz_id": 2, "job_instance_id": 10000}
                )
            ),
        },
        callback_data={"job_instance_id": 10000, "status": 3},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=GET_GLOBAL_VAR_CALL_FAIL_CLIENT.api.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "2",
                        "bk_biz_id": 2,
                        "job_plan_id": 1000010,
                        "global_var_list": [
                            {"id": 1000030, "value": "test"},
                            {"id": 1000031, "server": {"ip_list": [{"ip": "192.168.20.218", "bk_cloud_id": 0}]}},
                        ],
                        "callback_url": "callback_url",
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
                    {"bk_scope_type": "biz", "bk_scope_id": "2", "bk_biz_id": 2, "job_instance_id": 10000},
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(
            target=GET_TARGET_SERVER_BIZ_SET,
            return_value=(True, {"ip_list": [{"ip": "192.168.20.218", "bk_cloud_id": 0}]}),
        ),
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=GET_GLOBAL_VAR_CALL_FAIL_CLIENT),
        Patcher(target=GET_CLIENT_BY_USER, return_value=GET_GLOBAL_VAR_CALL_FAIL_CLIENT),
        Patcher(target=UTILS_GET_CLIENT_BY_USER, return_value=GET_GLOBAL_VAR_CALL_FAIL_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="callback_url"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=GET_BK_USERNAME_BY_TENANT, return_value=BK_USER_CLIENT),
    ],
)
# execute_job_plan_success biz set case
EXECUTE_JOB_PLAN_BIZ_SET_SUCCESS_CASE = ComponentTestCase(
    name="biz set execute success case",
    inputs={
        "all_biz_job_config": {
            "all_biz_cc_id": 2,
            "job_plan_id": 1000010,
            "is_tagged_ip": True,
            "job_global_var": [
                {"id": 1000030, "type": 1, "name": "name", "value": "test", "description": ""},
                {
                    "id": 1000032,
                    "type": JOBV3_VAR_CATEGORY_PASSWORD,
                    "name": "password",
                    # 密文变量
                    "value": {"tag": "variable", "value": crypto.encrypt("123")},
                },
                {
                    "id": 1000033,
                    "type": 1,
                    "name": "dict",
                    # 结构化数据
                    "value": {"value": 1, "test": True},
                },
                {
                    "id": 1000034,
                    "type": 1,
                    "name": "int from page",
                    # 页面输入的整型
                    "value": 0,
                },
                {
                    "id": 1000035,
                    "type": 1,
                    "name": "int from page",
                    # 页面输入的整型
                    "value": 1232314345,
                },
                {"id": 1000031, "type": 3, "name": "ip", "value": "0:192.168.20.218", "description": ""},
            ],
        }
    },
    parent_data={"executor": "executor_token", "biz_cc_id": 2, "tenant_id": "system"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 10000,
            "job_inst_name": "API execute_job_plan test",
            "biz_cc_id": 2,
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs={
            "job_inst_url": "instance_url_token",
            "job_inst_id": 10000,
            "job_inst_name": "API execute_job_plan test",
            "biz_cc_id": 2,
            "job_tagged_ip_dict": {"tag2": "192.168.20.218"},
            "name": "test",
            "log_outputs": {},
        },
        callback_data={"job_instance_id": 10000, "status": 3},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=EXECUTE_JOB_PLAN_BIZ_SET_SUCCESS_CASE_CLIENT.api.execute_job_plan,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz_set",
                        "bk_scope_id": "2",
                        "bk_biz_id": 2,
                        "job_plan_id": 1000010,
                        "global_var_list": [
                            {"id": 1000030, "value": "test"},
                            {"id": 1000032, "value": "123"},
                            {"id": 1000033, "value": "{'value': 1, 'test': True}"},
                            {"id": 1000034, "value": "0"},
                            {"id": 1000035, "value": "1232314345"},
                            {"id": 1000031, "server": {"ip_list": [{"ip": "192.168.20.218", "bk_cloud_id": 0}]}},
                        ],
                        "callback_url": "callback_url",
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=EXECUTE_JOB_PLAN_BIZ_SET_SUCCESS_CASE_CLIENT.api.get_job_instance_global_var_value,
            calls=[
                Call(
                    {"bk_scope_type": "biz_set", "bk_scope_id": "2", "bk_biz_id": 2, "job_instance_id": 10000},
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=MockCMDBClient()),
        Patcher(
            target=GET_TARGET_SERVER_BIZ_SET,
            return_value=(True, {"ip_list": [{"ip": "192.168.20.218", "bk_cloud_id": 0}]}),
        ),
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_JOB_PLAN_BIZ_SET_SUCCESS_CASE_CLIENT),
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=EXECUTE_JOB_PLAN_BIZ_SET_SUCCESS_CASE_CLIENT),
        Patcher(target=UTILS_GET_CLIENT_BY_USER, return_value=INVALID_IP_CLIENT_BIZ_SET),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="callback_url"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="instance_url_token"),
        Patcher(target=GET_BK_USERNAME_BY_TENANT, return_value=BK_USER_CLIENT),
    ],
)
