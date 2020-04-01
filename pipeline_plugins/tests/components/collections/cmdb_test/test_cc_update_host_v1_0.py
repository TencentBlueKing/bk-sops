# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
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
    ComponentTestCase,
    ComponentTestMixin,
    CallAssertion,
    ExecuteAssertion,
    Call,
    Patcher
)
from pipeline_plugins.components.collections.cmdb.cc_update_host import CCUpdateHostComponent


class CCUpdateHostComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            HOST_UPDATE_SUCCESS_CASE,
            HOST_UPDATE_ERR_CASE,
            INVALID_IP_CASE,
        ]

    def component_cls(self):
        return CCUpdateHostComponent


class MockClient(object):
    def __init__(self, search_host_return=None, batch_update_host_return=None):
        self.set_bk_api_ver = MagicMock()
        self.cc = MagicMock()
        self.cc.search_host = MagicMock(return_value=search_host_return)
        self.cc.batch_update_host = MagicMock(return_value=batch_update_host_return)


SEARCH_HOST_RETURN_INFO = {
    "code": 0,
    "permission": None,
    "result": True,
    "request_id": "99ba6ec77f164155b9f6a04bae217e06",
    "message": "success",
    "data": {
        "count": 2,
        "info": [
            {
                "host": {
                    "bk_host_id": 1,
                    "bk_cloud_id": [
                        {
                            "bk_obj_name": "",
                            "id": "0",
                            "bk_obj_id": "plat",
                            "bk_obj_icon": "",
                            "bk_inst_id": 0,
                            "bk_inst_name": "default area"
                        }
                    ],
                    "bk_host_innerip": "127.0.0.1"
                },
                "set": [],
                "biz": [],
                "module": []
            },
            {
                "host": {
                    "bk_host_id": 5,
                    "bk_cloud_id": [
                        {
                            "bk_obj_name": "",
                            "id": "0",
                            "bk_obj_id": "plat",
                            "bk_obj_icon": "",
                            "bk_inst_id": 0,
                            "bk_inst_name": "default area"
                        }
                    ],
                    "bk_host_innerip": "192.168.1.1"
                },
                "set": [],
                "biz": [],
                "module": []
            }
        ]
    }}

INPUT_INFO = {
    'cc_host_info': [
        {
            'bk_host_innerip': '127.0.0.1',
            'bk_host_outerip': '111.111.111.111',
            'operator': 'executor_token',
            'bk_bak_operator': 'bk_bak_operator',
            'bk_sn': '',
            'bk_comment': '',
            'bk_state_name': '',
            'bk_province_name': '',
            'bk_isp_name': '',
        },
        {
            'bk_host_innerip': '192.168.1.1',
            'bk_host_outerip': '222.222.222.222',
            'operator': 'executor_token',
            'bk_bak_operator': 'bk_bak_operator',
            'bk_sn': '',
            'bk_comment': '',
            'bk_state_name': '',
            'bk_province_name': '',
            'bk_isp_name': '',
        }
    ]
}

FAILED_INPUT = """\
{"bk_supplier_account":0,"update":[{"properties":{"bk_host_outerip":"111.111.111.111","operator":"executor_token",\
"bk_bak_operator":"bk_bak_operator"},"bk_host_id":1},{"properties":{"bk_host_outerip":"222.222.222.222","operator":\
"executor_token","bk_bak_operator":"bk_bak_operator"},"bk_host_id":2}]}\
"""
# mock path
GET_CLIENT_BY_USER = 'pipeline_plugins.components.collections.cmdb.cc_update_host.get_client_by_user'
CC_GET_HOST_ID_DICT_BY_INNERIP = 'pipeline_plugins.components.collections.cmdb.cc_update_host.' \
                                 'get_host_id_dict_by_innerip'

# mock client
HOST_UPDATE_SUCCESS_CLIENT = MockClient(
    search_host_return=SEARCH_HOST_RETURN_INFO,
    batch_update_host_return={
        "result": True,
        "code": 0,
        "message": "success",
        "data": None
    }
)

HOST_UPDATE_FAIL_CLIENT = MockClient(
    search_host_return={
        "result": False,
        "code": 0,
        "message": "failed",
        "data": {}
    },
    batch_update_host_return={
        "result": False,
        "code": 0,
        "message": "failed",
        "data": {}
    }
)
HOST_UPDATE_SUCCESS_CASE = ComponentTestCase(
    name='cc host update v1 success case',
    inputs=INPUT_INFO,
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 2,
        'biz_supplier_account': 0
    },
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
        }),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=CC_GET_HOST_ID_DICT_BY_INNERIP,
                      calls=[Call('executor_token', 2, ['127.0.0.1', '192.168.1.1'], 0)]),
        CallAssertion(func=HOST_UPDATE_SUCCESS_CLIENT.cc.batch_update_host,
                      calls=[Call({
                          "bk_supplier_account": 0,
                          "update": [
                              {
                                  "bk_host_id": 1,
                                  "properties": {
                                      "bk_host_outerip": "111.111.111.111",
                                      "operator": "executor_token",
                                      "bk_bak_operator": "bk_bak_operator"}},
                              {
                                  "bk_host_id": 2,
                                  "properties": {
                                      "bk_host_outerip": "222.222.222.222",
                                      "operator": "executor_token",
                                      "bk_bak_operator": "bk_bak_operator"}}]})])
    ],
    # add patch
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=HOST_UPDATE_SUCCESS_CLIENT),
        Patcher(target=CC_GET_HOST_ID_DICT_BY_INNERIP, return_value={'result': True,
                                                                     'data': {"127.0.0.1": 1, "192.168.1.1": 2}})]
)

HOST_UPDATE_ERR_CASE = ComponentTestCase(
    name='cc host update v1 error case',
    inputs=INPUT_INFO,
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 2,
        'biz_supplier_account': 0
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={'ex_data': (
            '调用配置平台(CMDB)接口cc.update_host返回失败, params={params}, error=failed').
            format(params=FAILED_INPUT)}

    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=CC_GET_HOST_ID_DICT_BY_INNERIP,
                      calls=[Call('executor_token', 2, ['127.0.0.1', '192.168.1.1'], 0)]),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=HOST_UPDATE_FAIL_CLIENT),
        Patcher(target=CC_GET_HOST_ID_DICT_BY_INNERIP, return_value={'result': True,
                                                                     'data': {"127.0.0.1": 1, "192.168.1.1": 2}})]
)

INVALID_IP_CASE = ComponentTestCase(
    name='invalid ip case',
    inputs={
        'cc_host_info': [
            {
                'bk_host_innerip': 'sss.sss.sss.sss',
                'bk_host_outerip': '111.111.111.111',
                'operator': 'executor_token',
                'bk_bak_operator': 'bk_bak_operator',
                'bk_sn': '',
                'bk_comment': '',
                'bk_state_name': '',
                'bk_province_name': '',
                'bk_isp_name': '',
            },
        ]
    },
    parent_data={
        'executor': 'executor_token',
        'biz_cc_id': 2,
        'biz_supplier_account': 0
    },
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            'ex_data': '内网ip(sss.sss.sss.sss)格式错误'
        }),
    schedule_assertion=None,
    execute_call_assertion=[
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=HOST_UPDATE_FAIL_CLIENT),
        ]
)
