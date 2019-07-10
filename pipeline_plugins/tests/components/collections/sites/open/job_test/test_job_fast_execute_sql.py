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
from pipeline_plugins.components.collections.sites.open.job import JobFastExecuteSQLComponent


class JobFastExecuteSQLComponentTest(TestCase, ComponentTestMixin):

    def cases(self):
        return [
            FAST_EXECUTE_SQL_FAIL_CASE,
            INVALID_IP_CASE,
            INVALID_CALLBACK_DATA_CASE,
            FAST_EXECUTE_SQL_FROM_SCRIPT_CONTENT_NOT_SUCCESS_CASE,
            FAST_EXECUTE_SQL_FROM_SCRIPT_ID_NOT_SUCCESS_CASE,
            FAST_EXECUTE_SQL_FROM_SCRIPT_CONTENT_SUCCESS_CASE,
            FAST_EXECUTE_SQL_FROM_SCRIPT_ID_SUCCESS_CASE,
        ]

    def component_cls(self):
        return JobFastExecuteSQLComponent


class MockClient(object):
    def __init__(self, fast_execute_sql_return):
        self.set_bk_api_ver = MagicMock()
        self.job = MagicMock()
        self.job.fast_execute_sql = MagicMock(return_value=fast_execute_sql_return)


# mock path
GET_CLIENT_BY_USER = 'pipeline_plugins.components.collections.sites.open.job.get_client_by_user'
CC_GET_IPS_INFO_BY_STR = 'pipeline_plugins.components.collections.sites.open.job.cc_get_ips_info_by_str'
GET_NODE_CALLBACK_URL = 'pipeline_plugins.components.collections.sites.open.job.get_node_callback_url'
GET_JOB_INSTANCE_URL = 'pipeline_plugins.components.collections.sites.open.job.get_job_instance_url'

# mock clients
FAST_EXECUTE_SQL_CALL_FAIL_CLIENT = MockClient(fast_execute_sql_return={
    'result': False,
    'message': 'message token'
})
INVALID_CALLBACK_DATA_CLIENT = MockClient(fast_execute_sql_return={
    'result': True,
    'data': {
        'job_instance_id': 56789,
        'job_instance_name': 'job_name_token',
    }
})
FAST_EXECUTE_SQL_NOT_SUCCESS_CLIENT = MockClient(fast_execute_sql_return={
    'result': True,
    'data': {
        'job_instance_id': 56789,
        'job_instance_name': 'job_name_token'
    }
})
FAST_EXECUTE_SQL_SUCCESS_CLIENT = MockClient(fast_execute_sql_return={
    'result': True,
    'data': {
        'job_instance_id': 56789,
        'job_instance_name': 'job_name_token'
    }
})

# test case
FAST_EXECUTE_SQL_FAIL_CASE = ComponentTestCase(
    name='fast_execute_sql call failed case',
    inputs={
        'job_ip_list': '1.1.1.1,2.2.2.2',
        'job_sql_content': 'show databases',
        'job_sql_script_id': 1,
        'job_sql_script_source': 'general',
        'job_script_timeout': 1000,
        'job_db_account': 32,
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={'ex_data': 'message token, invalid ip: 3.3.3.3,4.4.4.4'}
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call(username='executor_token',
                                                               biz_cc_id=1,
                                                               ip_str='1.1.1.1,2.2.2.2',
                                                               use_cache=False)]),
        CallAssertion(
            func=FAST_EXECUTE_SQL_CALL_FAIL_CLIENT.job.fast_execute_sql,
            calls=[Call({
                'bk_biz_id': 1,
                'script_timeout': 1000,
                'db_account_id': 32,
                'ip_list': [
                    {'ip': '1.1.1.1', 'bk_cloud_id': 1},
                    {'ip': '2.2.2.2', 'bk_cloud_id': 1},
                ],
                'bk_callback_url': 'url_token',
                'script_id': 1,
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SQL_CALL_FAIL_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={
            'ip_result': [
                {'InnerIP': '1.1.1.1', 'Source': 1},
                {'InnerIP': '2.2.2.2', 'Source': 1},
            ],
            'invalid_ip': [
                '3.3.3.3', '4.4.4.4'
            ]
        }),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value='url_token')
    ])

INVALID_IP_CASE = ComponentTestCase(
    name='invalid ip case',
    inputs={
        'job_ip_list': '1.1.1.1,2.2.2.2',
        'job_sql_content': 'show databases',
        'job_sql_script_id': 1,
        'job_sql_script_source': 'general',
        'job_script_timeout': 1000,
        'job_db_account': 32,
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={'ex_data': u"无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法"}
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call(
            username='executor_token',
            biz_cc_id=1,
            ip_str='1.1.1.1,2.2.2.2',
            use_cache=False)]),
    ],
    patchers=[
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={'ip_result': []}),
    ])

INVALID_CALLBACK_DATA_CASE = ComponentTestCase(
    name='invalid callback case',
    inputs={
        'job_ip_list': '1.1.1.1,2.2.2.2',
        'job_sql_content': 'show databases',
        'job_sql_script_id': 1,
        'job_sql_script_source': 'general',
        'job_script_timeout': 1000,
        'job_db_account': 32,
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': INVALID_CALLBACK_DATA_CLIENT
        }
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': INVALID_CALLBACK_DATA_CLIENT,
            'ex_data': 'invalid callback_data, job_instance_id: None, status: None'
        },
        callback_data={}
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username='executor_token',
                        biz_cc_id=1,
                        ip_str='1.1.1.1,2.2.2.2',
                        use_cache=False)]),
        CallAssertion(
            func=INVALID_CALLBACK_DATA_CLIENT.job.fast_execute_sql,
            calls=[Call({
                'bk_biz_id': 1,
                'script_timeout': 1000,
                'db_account_id': 32,
                'ip_list': [
                    {'ip': '1.1.1.1', 'bk_cloud_id': 1},
                    {'ip': '2.2.2.2', 'bk_cloud_id': 1},
                ],
                'bk_callback_url': 'url_token',
                'script_id': 1,
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INVALID_CALLBACK_DATA_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={
            'ip_result': [
                {'InnerIP': '1.1.1.1', 'Source': 1},
                {'InnerIP': '2.2.2.2', 'Source': 1},
            ],
            'invalid_ip': [
                '3.3.3.3', '4.4.4.4'
            ]
        }),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value='url_token'),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value='instance_url_token'),
    ]
)

FAST_EXECUTE_SQL_FROM_SCRIPT_CONTENT_NOT_SUCCESS_CASE = ComponentTestCase(
    name='fast execute sql script content not success case',
    inputs={
        'job_ip_list': '1.1.1.1,2.2.2.2',
        'job_sql_content': 'show databases',
        'job_sql_script_source': 'manual',
        'job_script_timeout': 1000,
        'job_db_account': 32,
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': FAST_EXECUTE_SQL_NOT_SUCCESS_CLIENT
        }
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': FAST_EXECUTE_SQL_NOT_SUCCESS_CLIENT,
            'ex_data': {
                'exception_msg': u"任务执行失败，<a href='%s' target='_blank'>"
                                 u"前往作业平台(JOB)查看详情</a>" % 'instance_url_token',
                'task_inst_id': 56789,
                'show_ip_log': True
            }
        },
        callback_data={
            'job_instance_id': 56789,
            'status': 1
        }
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username='executor_token',
                        biz_cc_id=1,
                        ip_str='1.1.1.1,2.2.2.2',
                        use_cache=False)]),
        CallAssertion(
            func=FAST_EXECUTE_SQL_NOT_SUCCESS_CLIENT.job.fast_execute_sql,
            calls=[Call({
                'bk_biz_id': 1,
                'script_timeout': 1000,
                'db_account_id': 32,
                'ip_list': [
                    {'ip': '1.1.1.1', 'bk_cloud_id': 1},
                    {'ip': '2.2.2.2', 'bk_cloud_id': 1},
                ],
                'bk_callback_url': 'url_token',
                'script_content': 'c2hvdyBkYXRhYmFzZXM='
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SQL_NOT_SUCCESS_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={
            'ip_result': [
                {'InnerIP': '1.1.1.1', 'Source': 1},
                {'InnerIP': '2.2.2.2', 'Source': 1},
            ],
            'invalid_ip': [
                '3.3.3.3', '4.4.4.4'
            ]
        }),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value='url_token'),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value='instance_url_token'),
    ]
)

FAST_EXECUTE_SQL_FROM_SCRIPT_ID_NOT_SUCCESS_CASE = ComponentTestCase(
    name='fast execute sql script id not success case',
    inputs={
        'job_ip_list': '1.1.1.1,2.2.2.2',
        'job_sql_script_source': 'general',
        'job_sql_script_id': 1,
        'job_script_timeout': 1000,
        'job_db_account': 32,
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': FAST_EXECUTE_SQL_NOT_SUCCESS_CLIENT
        }
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': FAST_EXECUTE_SQL_NOT_SUCCESS_CLIENT,
            'ex_data': {
                'exception_msg': u"任务执行失败，<a href='%s' target='_blank'>"
                                 u"前往作业平台(JOB)查看详情</a>" % 'instance_url_token',
                'task_inst_id': 56789,
                'show_ip_log': True
            }
        },
        callback_data={
            'job_instance_id': 56789,
            'status': 1
        }
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username='executor_token',
                        biz_cc_id=1,
                        ip_str='1.1.1.1,2.2.2.2',
                        use_cache=False)]),
        CallAssertion(
            func=FAST_EXECUTE_SQL_NOT_SUCCESS_CLIENT.job.fast_execute_sql,
            calls=[Call({
                'bk_biz_id': 1,
                'script_timeout': 1000,
                'db_account_id': 32,
                'ip_list': [
                    {'ip': '1.1.1.1', 'bk_cloud_id': 1},
                    {'ip': '2.2.2.2', 'bk_cloud_id': 1},
                ],
                'bk_callback_url': 'url_token',
                'script_id': 1
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SQL_NOT_SUCCESS_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={
            'ip_result': [
                {'InnerIP': '1.1.1.1', 'Source': 1},
                {'InnerIP': '2.2.2.2', 'Source': 1},
            ],
            'invalid_ip': [
                '3.3.3.3', '4.4.4.4'
            ]
        }),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value='url_token'),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value='instance_url_token'),
    ]
)

FAST_EXECUTE_SQL_FROM_SCRIPT_CONTENT_SUCCESS_CASE = ComponentTestCase(
    name='fast execute sql script content success case',
    inputs={
        'job_ip_list': '1.1.1.1,2.2.2.2',
        'job_sql_content': 'show databases',
        'job_sql_script_source': 'manual',
        'job_script_timeout': 1000,
        'job_db_account': 32,
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': FAST_EXECUTE_SQL_SUCCESS_CLIENT
        }
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': FAST_EXECUTE_SQL_SUCCESS_CLIENT,
        },
        callback_data={
            'job_instance_id': 56789,
            'status': 3
        }
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username='executor_token',
                        biz_cc_id=1,
                        ip_str='1.1.1.1,2.2.2.2',
                        use_cache=False)]),
        CallAssertion(
            func=FAST_EXECUTE_SQL_SUCCESS_CLIENT.job.fast_execute_sql,
            calls=[Call({
                'bk_biz_id': 1,
                'script_timeout': 1000,
                'db_account_id': 32,
                'ip_list': [
                    {'ip': '1.1.1.1', 'bk_cloud_id': 1},
                    {'ip': '2.2.2.2', 'bk_cloud_id': 1},
                ],
                'bk_callback_url': 'url_token',
                'script_content': 'c2hvdyBkYXRhYmFzZXM='
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SQL_SUCCESS_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={
            'ip_result': [
                {'InnerIP': '1.1.1.1', 'Source': 1},
                {'InnerIP': '2.2.2.2', 'Source': 1},
            ],
        }),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value='url_token'),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value='instance_url_token'),
    ]
)

FAST_EXECUTE_SQL_FROM_SCRIPT_ID_SUCCESS_CASE = ComponentTestCase(
    name='fast execute sql script id success case',
    inputs={
        'job_ip_list': '1.1.1.1,2.2.2.2',
        'job_sql_script_source': 'general',
        'job_sql_script_id': 1,
        'job_script_timeout': 1000,
        'job_db_account': 32,
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 1,
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': FAST_EXECUTE_SQL_SUCCESS_CLIENT
        }
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        outputs={
            'job_inst_url': 'instance_url_token',
            'job_inst_id': 56789,
            'job_inst_name': 'job_name_token',
            'client': FAST_EXECUTE_SQL_SUCCESS_CLIENT,
        },
        callback_data={
            'job_instance_id': 56789,
            'status': 3
        }
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username='executor_token',
                        biz_cc_id=1,
                        ip_str='1.1.1.1,2.2.2.2',
                        use_cache=False)]),
        CallAssertion(
            func=FAST_EXECUTE_SQL_SUCCESS_CLIENT.job.fast_execute_sql,
            calls=[Call({
                'bk_biz_id': 1,
                'script_timeout': 1000,
                'db_account_id': 32,
                'ip_list': [
                    {'ip': '1.1.1.1', 'bk_cloud_id': 1},
                    {'ip': '2.2.2.2', 'bk_cloud_id': 1},
                ],
                'bk_callback_url': 'url_token',
                'script_id': 1
            })]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAST_EXECUTE_SQL_SUCCESS_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={
            'ip_result': [
                {'InnerIP': '1.1.1.1', 'Source': 1},
                {'InnerIP': '2.2.2.2', 'Source': 1},
            ],
        }),
        Patcher(target=GET_NODE_CALLBACK_URL, return_value='url_token'),
        Patcher(target=GET_JOB_INSTANCE_URL, return_value='instance_url_token'),
    ]
)
