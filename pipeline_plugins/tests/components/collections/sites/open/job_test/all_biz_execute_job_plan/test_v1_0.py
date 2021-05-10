# -*- coding: utf-8 -*-

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
from pipeline_plugins.components.collections.sites.open.job import AllBizJobExecuteJobPlanComponent


class AllBizJobExecuteJobPlanComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        # return the component class which should be testet
        return AllBizJobExecuteJobPlanComponent

    def cases(self):
        # return your component test cases here
        return [
            EXECUTE_JOB_PLAN_FAIL_CASE,
            # FAST_EXECUTE_MANUAL_SCRIPT_SUCCESS_SCHEDULE_CALLBACK_DATA_ERROR_CASE,
        ]


class MockClient(object):
    def __init__(
            self,
            execute_job_plan_return=None,
            get_job_instance_global_var_value_return=None,
            get_job_instance_ip_log_return=None,
            get_job_instance_status_return=None,
    ):
        self.jobv3 = MagicMock()
        self.jobv3.execute_job_plan = MagicMock(return_value=execute_job_plan_return)
        self.jobv3.get_job_instance_global_var_value = MagicMock(return_value=get_job_instance_global_var_value_return)
        self.jobv3.get_job_instance_ip_log = MagicMock(return_value=get_job_instance_ip_log_return)
        self.jobv3.get_job_instance_status = MagicMock(return_value=get_job_instance_status_return)


# mock path
GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.v1_0.get_client_by_user"
)
GET_NODE_CALLBACK_URL = (
    "pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.v1_0.get_node_callback_url"
)
JOB_HANDLE_API_ERROR = (
    "pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.v1_0.job_handle_api_error"
)
GET_JOB_INSTANCE_URL = (
    "pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.v1_0.get_job_instance_url"
)

# success result
SUCCESS_RESULT = {
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
    "request_id": "1e4825b1f0354e509d2bc25eb172f8dc"
}
# mock clients
EXECUTE_JOB_PLAN_FAIL_CLIENT = MockClient(
    execute_job_plan_return=EXECUTE_JOB_PLAN_FAIL_RESULT, get_job_instance_global_var_value_return={}
)

# mock GET_NODE_CALLBACK_URL
GET_NODE_CALLBACK_URL_MOCK = MagicMock(return_value="callback_url")

# execute_job_plan fail
EXECUTE_JOB_PLAN_FAIL_CASE = ComponentTestCase(
    name="all biz fast execute script fail test case",
    inputs={
        "all_biz_cc_id": 999101,
        "job_plan_id": 1000010,
        "job_global_var": [{'id': 1000030, 'type': 1, 'name': 'name', 'value': '123', 'description': ''},
                           {'id': 1000031, 'type': 3, 'name': 'ip', 'value': '0:192.168.20.218', 'description': ''}],
        "ip_is_exist": True
    },
    parent_data={"executor": "executor", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(success=False, outputs={
        'ex_data': '调用作业平台(JOB)接口jobv3.execute_job_plan返回失败, params={"bk_biz_id":999101,"job_plan_id":1000010,"global_var_list":[{"id":1000030,"value":"123"},{"id":1000031,"server":{"ip_list":[{"ip":"192.168.20.218","bk_cloud_id":"0"}]}}],"bk_callback_url":"callback_url"}, error=Job plan does not exist, request_id=1e4825b1f0354e509d2bc25eb172f8dc'
    }),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=EXECUTE_JOB_PLAN_FAIL_CLIENT.jobv3.execute_job_plan, calls=[Call({
            "bk_biz_id": 999101,
            "job_plan_id": 1000010,
            "global_var_list": [
                {
                    "id": 1000030,
                    "value": "123"
                },
                {
                    "id": 1000031,
                    "server": {
                        "ip_list": [
                            {
                                "ip": "192.168.20.218",
                                "bk_cloud_id": "0",
                            }
                        ]
                    }
                }
            ],
            "bk_callback_url": "callback_url",
        })]),
    ],
    patchers=[
        Patcher(target=GET_NODE_CALLBACK_URL, return_value=GET_NODE_CALLBACK_URL_MOCK()),
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_JOB_PLAN_FAIL_CLIENT),
    ],
)
