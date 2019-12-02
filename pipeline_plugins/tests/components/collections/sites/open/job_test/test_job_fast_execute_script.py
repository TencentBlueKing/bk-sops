# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock

from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    CallAssertion,
    ExecuteAssertion,
    ScheduleAssertion,
    Call,
    Patcher
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
    def __init__(self, fast_execute_script_return=None, get_job_instance_global_var_value_return=None):
        self.job = MagicMock()
        self.job.fast_execute_script = MagicMock(return_value=fast_execute_script_return)
        self.job.get_job_instance_global_var_value = MagicMock(return_value=get_job_instance_global_var_value_return)


# mock path
GET_CLIENT_BY_USER = 'pipeline_plugins.components.collections.sites.open.job.get_client_by_user'
GET_NODE_CALLBACK_URL = 'pipeline_plugins.components.collections.sites.open.job.get_node_callback_url'
JOB_HANDLE_API_ERROR = 'pipeline_plugins.components.collections.sites.open.job.job_handle_api_error'
GET_JOB_INSTANCE_URL = 'pipeline_plugins.components.collections.sites.open.job.get_job_instance_url'

# success result
SUCCESS_RESULT = {
    'result': True,
    'code': 0,
    'message': 'success',
    'data': {
        'job_instance_name': 'API Quick execution script1521100521303',
        'job_instance_id': 10000
    },
}

# success result
FAIL_RESULT = {
    'code': 1237104,
    'permission': None,
    'result': False,
    'request_id': 'aac7755b09944e4296b2848d81bd9411',
    'message': 'IP 10.0.0.1 does not belong to this Business',
    'data': None
}


# mock clients
FAST_EXECUTE_SCRIPT_FAIL_CLIENT = MockClient(
    fast_execute_script_return=FAIL_RESULT,
    get_job_instance_global_var_value_return={}
)

# mock clients
FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT = MockClient(
    fast_execute_script_return=SUCCESS_RESULT,
    get_job_instance_global_var_value_return={
        'data': {
            'job_instance_var_values': [{
                'step_instance_var_values': [{
                    'category': 1,
                    'name': 'name',
                    'value': 'value'
                }]
            }]
        },
        'result': True
    }
)

# mock GET_NODE_CALLBACK_URL
GET_NODE_CALLBACK_URL_MOCK = MagicMock(return_value='callback_url')

# mock GET_JOB_INSTANCE_URL
GET_JOB_INSTANCE_URL_MOCK = MagicMock(return_value='?taskInstanceList&appId=1#taskInstanceId=10000')

# parent_data
PARENT_DATA = {
    'executor': 'executor',
    'biz_cc_id': 1
}

# BASE_INPUTS
BASE_INPUTS = {
    'job_script_param': '1',
    'job_script_timeout': '100',
    'job_ip_list': '127.0.0.1\n127.0.0.2',
    'job_account': 'root',
    'job_script_list_public': '',
    'job_script_list_general': '',
}


# manual inputs
MANUAL_INPUTS = BASE_INPUTS
MANUAL_INPUTS.update({
    'job_script_source': 'manual',
    'job_script_type': '1',
    'job_content': 'echo',
})

# MANUAL_KWARGS
MANUAL_KWARGS = {
    'bk_biz_id': 1,
    'bk_callback_url': 'callback_url',
    'account': 'root',
    'script_param': 'MQ==',
    'ip_list': [],
    'script_type': '1',
    'script_timeout': '100',
    'script_content': 'ZWNobw==',
}

# 手动输入脚本失败样例输出
MANUAL_FAIL_OUTPUTS = {
    'ex_data': u"调用作业平台(JOB)接口job.fast_execute_script返回失败, params={params}, error={error}".format(
        params='{"bk_biz_id":1,"bk_callback_url":"callback_url","account":"root","script_param":"MQ==","ip_list":[],'
               '"script_type":"1","script_timeout":"100","script_content":"ZWNobw=="}',
        error=FAIL_RESULT['message']
    )
}

# 手动输入脚本成功样例输出
MANUAL_SUCCESS_OUTPUTS = {
    'job_inst_id': SUCCESS_RESULT['data']['job_instance_id'],
    'job_inst_name': 'API Quick execution script1521100521303',
    'job_inst_url': u'?taskInstanceList&appId=1#taskInstanceId=10000',
    'client': FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT,
}
# 异步回调函数参数错误返回
SCHEDULE_CALLBACK_DATA_ERROR_OUTPUTS = {
    'ex_data': 'invalid callback_data, job_instance_id: None, status: None'
}
# 异步回调函数成功输出
SCHEDULE_SUCCESS_OUTPUTS = {
    'name': 'value'
}


# 手动输入脚本成功异步执行失败样例
FAST_EXECUTE_MANUAL_SCRIPT_SUCCESS_SCHEDULE_CALLBACK_DATA_ERROR_CASE = ComponentTestCase(
    name='fast execute manual script success schedule callback data error test case',
    inputs=MANUAL_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs=MANUAL_SUCCESS_OUTPUTS
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs=dict(MANUAL_SUCCESS_OUTPUTS.items() + SCHEDULE_CALLBACK_DATA_ERROR_OUTPUTS.items()),
        callback_data={}
    ),
    execute_call_assertion=[
        CallAssertion(
            func=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT.job.fast_execute_script,
            calls=[Call(MANUAL_KWARGS)]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value=GET_NODE_CALLBACK_URL_MOCK()),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value=GET_JOB_INSTANCE_URL_MOCK()),
    ]
)

# 手动输入脚本成功异步执行成功样例
FAST_EXECUTE_MANUAL_SCRIPT_SUCCESS_SCHEDULE_SUCCESS_CASE = ComponentTestCase(
    name='fast execute manual script and schedule success test case',
    inputs=MANUAL_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs=MANUAL_SUCCESS_OUTPUTS
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs=dict(MANUAL_SUCCESS_OUTPUTS.items() + SCHEDULE_SUCCESS_OUTPUTS.items()),
        callback_data={
            'job_instance_id': 10000,
            'status': 3
        }
    ),
    execute_call_assertion=[
        CallAssertion(
            func=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT.job.fast_execute_script,
            calls=[Call(MANUAL_KWARGS)]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SCRIPT_SUCCESS_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value=GET_NODE_CALLBACK_URL_MOCK()),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value=GET_JOB_INSTANCE_URL_MOCK()),
    ]
)

# 手动输入脚本失败样例
FAST_EXECUTE_MANUAL_SCRIPT_FAIL_CASE = ComponentTestCase(
    name='fast execute manual script fail test case',
    inputs=MANUAL_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs=MANUAL_FAIL_OUTPUTS
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=FAST_EXECUTE_SCRIPT_FAIL_CLIENT.job.fast_execute_script,
            calls=[Call(MANUAL_KWARGS)]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SCRIPT_FAIL_CLIENT),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value=GET_NODE_CALLBACK_URL_MOCK()),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value=GET_JOB_INSTANCE_URL_MOCK()),
    ]
)
