# -*- coding: utf-8 -*-
import base64

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
from pipeline_plugins.tests.components.collections.sites.open.utils.cc_ipv6_mock_utils import build_job_target_server

# Mock path
GET_CLIENT_BY_USERNAME = (
    "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.get_client_by_username"
)
BASE_GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username"
GET_NODE_CALLBACK_URL = (
    "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.get_node_callback_url"
)
GET_JOB_INSTANCE_URL = (
    "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.get_job_instance_url"
)
CC_GET_IPS_INFO_BY_STR = "pipeline_plugins.components.utils.sites.open.utils.cc_get_ips_info_by_str"
CMDB_GET_BUSINESS_HOST = "gcloud.utils.cmdb.get_business_host"
GET_JOB_TAGGED_IP_DICT_COMPLEX = (
    "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.get_job_tagged_ip_dict_complex"
)

MOCK_TAGGED_IP_DICT = {
    "name": "JOB执行IP分组",
    "key": "job_tagged_ip_dict",
    "value": {
        "SUCCESS": {"DESC": "执行成功", "TAGS": {"ALL": "1.1.1.1"}},
    },
}


class MockClient(object):
    def __init__(
        self,
        fast_execute_script_return=None,
        get_script_list_return=None,
        get_public_script_list_return=None,
        get_job_instance_status_return=None,
        get_job_instance_global_var_value_return=None,
    ):
        get_job_instance_global_var_value_return = get_job_instance_global_var_value_return or {
            "result": True,
            "data": {"step_instance_var_list": []},
        }
        self.api = MagicMock()
        self.api.fast_execute_script = MagicMock(return_value=fast_execute_script_return)
        self.api.get_script_list = MagicMock(return_value=get_script_list_return)
        self.api.get_public_script_list = MagicMock(return_value=get_public_script_list_return)
        self.api.get_job_instance_status = MagicMock(return_value=get_job_instance_status_return)
        self.api.get_job_instance_global_var_value = MagicMock(return_value=get_job_instance_global_var_value_return)


# Helper for CMDB return
def create_get_business_host_return(hosts):
    return [
        {
            "bk_host_id": host["bk_host_id"],
            "bk_host_innerip": host["bk_host_innerip"],
            "bk_cloud_id": host["bk_cloud_id"],
        }
        for host in hosts
    ]


SERVER_1 = build_job_target_server(host_ids=[1], ips_with_cloud=[{"ip": "1.1.1.1", "bk_cloud_id": 0}])

# Case 1: Normal Execute Success
NORMAL_EXECUTE_SUCCESS_CLIENT = MockClient(
    fast_execute_script_return={
        "result": True,
        "data": {
            "job_instance_id": 100,
            "job_instance_name": "test_job",
        },
    },
    get_job_instance_status_return={
        "result": True,
        "data": {
            "finished": True,
            "job_instance": {"status": 3},
            "step_instance_list": [],
        },
    },
)

NORMAL_EXECUTE_SUCCESS_CASE = ComponentTestCase(
    name="v1.2 normal execute success",
    inputs={
        "biz_cc_id": 1,
        "job_script_source": "manual",
        "job_script_type": "1",
        "job_content": "echo hello",
        "job_script_param": "param",
        "job_ip_list": "1.1.1.1",
        "job_account": "root",
        "job_script_timeout": 1000,
    },
    parent_data={"executor": "admin", "biz_cc_id": 1, "tenant_id": "test"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_id": 100,
            "job_inst_name": "test_job",
            "job_inst_url": "http://job.com/100",
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        schedule_finished=True,
        callback_data={"job_instance_id": 100, "status": 3},
        outputs={
            "job_inst_id": 100,
            "job_inst_name": "test_job",
            "job_inst_url": "http://job.com/100",
            "log_outputs": {},
            "job_tagged_ip_dict": MOCK_TAGGED_IP_DICT,
        },
    ),
    execute_call_assertion=[
        CallAssertion(
            func=NORMAL_EXECUTE_SUCCESS_CLIENT.api.fast_execute_script,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "timeout": 1000,
                        "account_alias": "root",
                        "target_server": SERVER_1,
                        "callback_url": "http://callback.com",
                        "script_param": base64.b64encode(b"param").decode("utf-8"),
                        "script_language": "1",
                        "script_content": base64.b64encode(b"echo hello").decode("utf-8"),
                    },
                    headers={"X-Bk-Tenant-Id": "test"},
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=NORMAL_EXECUTE_SUCCESS_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USERNAME, return_value=NORMAL_EXECUTE_SUCCESS_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="http://callback.com"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="http://job.com/100"),
        Patcher(target=GET_JOB_TAGGED_IP_DICT_COMPLEX, return_value=(True, MOCK_TAGGED_IP_DICT)),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 0}]},
        ),
        Patcher(
            target=CMDB_GET_BUSINESS_HOST,
            return_value=create_get_business_host_return(
                [{"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]
            ),
        ),
    ],
)

# Case 2: Rolling Execute Success
ROLLING_EXECUTE_SUCCESS_CLIENT = MockClient(
    fast_execute_script_return={
        "result": True,
        "data": {
            "job_instance_id": 100,
            "job_instance_name": "test_job_rolling",
        },
    },
    get_job_instance_status_return={
        "result": True,
        "data": {
            "finished": True,
            "job_instance": {"status": 3},
            "step_instance_list": [],
        },
    },
)

ROLLING_EXECUTE_SUCCESS_CASE = ComponentTestCase(
    name="v1.2 rolling execute success",
    inputs={
        "biz_cc_id": 1,
        "job_script_source": "manual",
        "job_script_type": "1",
        "job_content": "echo hello",
        "job_script_param": "param",
        "job_ip_list": "1.1.1.1",
        "job_account": "root",
        "job_script_timeout": 1000,
        "job_rolling_config": {"job_rolling_execute": True, "job_rolling_expression": "10%", "job_rolling_mode": "1"},
    },
    parent_data={"executor": "admin", "biz_cc_id": 1, "tenant_id": "test"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_id": 100,
            "job_inst_name": "test_job_rolling",
            "job_inst_url": "http://job.com/100",
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        schedule_finished=True,
        callback_data={"job_instance_id": 100, "status": 3},
        outputs={
            "job_inst_id": 100,
            "job_inst_name": "test_job_rolling",
            "job_inst_url": "http://job.com/100",
            "log_outputs": {},
            "job_tagged_ip_dict": MOCK_TAGGED_IP_DICT,
        },
    ),
    execute_call_assertion=[
        CallAssertion(
            func=ROLLING_EXECUTE_SUCCESS_CLIENT.api.fast_execute_script,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "timeout": 1000,
                        "account_alias": "root",
                        "target_server": SERVER_1,
                        "callback_url": "http://callback.com",
                        "script_param": base64.b64encode(b"param").decode("utf-8"),
                        "script_language": "1",
                        "script_content": base64.b64encode(b"echo hello").decode("utf-8"),
                        "rolling_config": {"expression": "10%", "mode": "1"},
                    },
                    headers={"X-Bk-Tenant-Id": "test"},
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=ROLLING_EXECUTE_SUCCESS_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USERNAME, return_value=ROLLING_EXECUTE_SUCCESS_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="http://callback.com"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="http://job.com/100"),
        Patcher(target=GET_JOB_TAGGED_IP_DICT_COMPLEX, return_value=(True, MOCK_TAGGED_IP_DICT)),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 0}]},
        ),
        Patcher(
            target=CMDB_GET_BUSINESS_HOST,
            return_value=create_get_business_host_return(
                [{"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]
            ),
        ),
    ],
)

# Case 3: General Script Success
GENERAL_SCRIPT_SUCCESS_CLIENT = MockClient(
    fast_execute_script_return={
        "result": True,
        "data": {
            "job_instance_id": 100,
            "job_instance_name": "test_job",
        },
    },
    get_script_list_return={"result": True, "data": {"data": [{"id": 999, "name": "test_script"}], "total": 1}},
    get_job_instance_status_return={
        "result": True,
        "data": {
            "finished": True,
            "job_instance": {"status": 3},
            "step_instance_list": [],
        },
    },
)

GENERAL_SCRIPT_SUCCESS_CASE = ComponentTestCase(
    name="v1.2 general script success",
    inputs={
        "biz_cc_id": 1,
        "job_script_source": "general",
        "job_script_list_general": "test_script",
        "job_script_param": "param",
        "job_ip_list": "1.1.1.1",
        "job_account": "root",
        "job_script_timeout": 1000,
    },
    parent_data={"executor": "admin", "biz_cc_id": 1, "tenant_id": "test"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_id": 100,
            "job_inst_name": "test_job",
            "job_inst_url": "http://job.com/100",
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        schedule_finished=True,
        callback_data={"job_instance_id": 100, "status": 3},
        outputs={
            "job_inst_id": 100,
            "job_inst_name": "test_job",
            "job_inst_url": "http://job.com/100",
            "log_outputs": {},
            "job_tagged_ip_dict": MOCK_TAGGED_IP_DICT,
        },
    ),
    execute_call_assertion=[
        CallAssertion(
            func=GENERAL_SCRIPT_SUCCESS_CLIENT.api.fast_execute_script,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "timeout": 1000,
                        "account_alias": "root",
                        "target_server": SERVER_1,
                        "callback_url": "http://callback.com",
                        "script_param": base64.b64encode(b"param").decode("utf-8"),
                        "script_id": 999,
                    },
                    headers={"X-Bk-Tenant-Id": "test"},
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=GENERAL_SCRIPT_SUCCESS_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USERNAME, return_value=GENERAL_SCRIPT_SUCCESS_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="http://callback.com"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="http://job.com/100"),
        Patcher(target=GET_JOB_TAGGED_IP_DICT_COMPLEX, return_value=(True, MOCK_TAGGED_IP_DICT)),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 0}]},
        ),
        Patcher(
            target=CMDB_GET_BUSINESS_HOST,
            return_value=create_get_business_host_return(
                [{"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]
            ),
        ),
    ],
)

# Case 4: Public Script Success
PUBLIC_SCRIPT_SUCCESS_CLIENT = MockClient(
    fast_execute_script_return={
        "result": True,
        "data": {
            "job_instance_id": 100,
            "job_instance_name": "test_job",
        },
    },
    get_public_script_list_return={
        "result": True,
        "data": {"data": [{"id": 888, "name": "public_script"}], "total": 1},
    },
    get_job_instance_status_return={
        "result": True,
        "data": {
            "finished": True,
            "job_instance": {"status": 3},
            "step_instance_list": [],
        },
    },
)

PUBLIC_SCRIPT_SUCCESS_CASE = ComponentTestCase(
    name="v1.2 public script success",
    inputs={
        "biz_cc_id": 1,
        "job_script_source": "public",
        "job_script_list_public": "public_script",
        "job_script_param": "param",
        "job_ip_list": "1.1.1.1",
        "job_account": "root",
        "job_script_timeout": 1000,
    },
    parent_data={"executor": "admin", "biz_cc_id": 1, "tenant_id": "test"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "job_inst_id": 100,
            "job_inst_name": "test_job",
            "job_inst_url": "http://job.com/100",
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        schedule_finished=True,
        callback_data={"job_instance_id": 100, "status": 3},
        outputs={
            "job_inst_id": 100,
            "job_inst_name": "test_job",
            "job_inst_url": "http://job.com/100",
            "log_outputs": {},
            "job_tagged_ip_dict": MOCK_TAGGED_IP_DICT,
        },
    ),
    execute_call_assertion=[
        CallAssertion(
            func=PUBLIC_SCRIPT_SUCCESS_CLIENT.api.fast_execute_script,
            calls=[
                Call(
                    {
                        "bk_scope_type": "biz",
                        "bk_scope_id": "1",
                        "bk_biz_id": 1,
                        "timeout": 1000,
                        "account_alias": "root",
                        "target_server": SERVER_1,
                        "callback_url": "http://callback.com",
                        "script_param": base64.b64encode(b"param").decode("utf-8"),
                        "script_id": 888,
                    },
                    headers={"X-Bk-Tenant-Id": "test"},
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USERNAME, return_value=PUBLIC_SCRIPT_SUCCESS_CLIENT),
        Patcher(target=BASE_GET_CLIENT_BY_USERNAME, return_value=PUBLIC_SCRIPT_SUCCESS_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value="http://callback.com"),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value="http://job.com/100"),
        Patcher(target=GET_JOB_TAGGED_IP_DICT_COMPLEX, return_value=(True, MOCK_TAGGED_IP_DICT)),
        Patcher(
            target=CC_GET_IPS_INFO_BY_STR,
            return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 0}]},
        ),
        Patcher(
            target=CMDB_GET_BUSINESS_HOST,
            return_value=create_get_business_host_return(
                [{"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]
            ),
        ),
    ],
)


class JobFastExecuteScriptComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            NORMAL_EXECUTE_SUCCESS_CASE,
            ROLLING_EXECUTE_SUCCESS_CASE,
            GENERAL_SCRIPT_SUCCESS_CASE,
            PUBLIC_SCRIPT_SUCCESS_CASE,
        ]

    def component_cls(self):
        # Patch the component to fix the invalid type definition in inputs_format
        original_service = JobFastExecuteScriptComponent.bound_service

        class PatchedService(original_service):
            def inputs_format(self):
                formats = super(PatchedService, self).inputs_format()
                for item in formats:
                    if item.key == "job_rolling_execute":
                        item.type = "boolean"
                return formats

            def outputs_format(self):
                formats = super(PatchedService, self).outputs_format()
                for item in formats:
                    if item.key == "log_outputs":
                        item.type = "object"
                    elif item.key == "job_tagged_ip_dict":
                        item.type = "object"  # Fix type for testing
                        from pipeline.core.flow.io import ObjectItemSchema

                        item.schema = ObjectItemSchema(description=item.schema.description, property_schemas={})
                return formats

        class PatchedComponent(JobFastExecuteScriptComponent):
            bound_service = PatchedService

        return PatchedComponent
