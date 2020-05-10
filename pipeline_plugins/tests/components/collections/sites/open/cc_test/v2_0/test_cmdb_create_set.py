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
from django.test import TestCase
from mock import MagicMock

from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    CallAssertion,
    ExecuteAssertion,
    Call,
    Patcher
)
from pipeline_plugins.components.collections.sites.open.cc_create_set.v2_0 import CCCreateSetComponent


class CCCreateSetComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        return CCCreateSetComponent

    def cases(self):
        return [
            SELECT_BY_TEXT_SUCCESS_CASE,
            SELECT_BY_TEXT_ERROR_LEVEL_FAIL_CAST,
            SELECT_BY_TEXT_ERROR_PATH_FAIL_CAST,
            SELECT_BY_TOPO_SUCCESS_CASE
        ]


class MockClient(object):
    def __init__(self, get_mainline_object_topo_return=None, search_biz_inst_topo_return=None, create_set_return=None):
        self.set_bk_api_ver = MagicMock()
        self.cc = MagicMock()
        self.cc.get_mainline_object_topo = MagicMock(return_value=get_mainline_object_topo_return)
        self.cc.search_biz_inst_topo = MagicMock(return_value=search_biz_inst_topo_return)
        self.cc.create_set = MagicMock(return_value=create_set_return)


CC_FORMAT_PROP_DATA_SET_ENV = {'result': True, 'data': {'测试': '1', '体验': '2', '正式': '3'}}
CC_FORMAT_PROP_DATA_SERVICE_STATUS = {'result': True, 'data': {'开放': '1', '关闭': '2'}}

GET_CLIENT_BY_USER = 'pipeline_plugins.components.collections.sites.open.cc_create_set.v2_0.get_client_by_user'
CC_FORMAT_PROP_DATA = 'pipeline_plugins.components.collections.sites.open.cc_create_set.v2_0.cc_format_prop_data'


# 根据prop_i确定CC_FORMAT_PROP_DATA接口的返回值
def cc_format_prop_data_return(executor, obj_id, prop_id, language, supplier_account):
    if prop_id == 'bk_set_env':
        return CC_FORMAT_PROP_DATA_SET_ENV
    else:
        return CC_FORMAT_PROP_DATA_SERVICE_STATUS


# 通用client
COMMON_CLIENT = MockClient(
    get_mainline_object_topo_return={
        "result": True,
        "code": 0,
        "message": "success",
        "data": [
            {
                "bk_obj_id": "biz",
                "bk_obj_name": "业务",
                "bk_supplier_account": "0",
                "bk_next_obj": "set",
                "bk_next_name": "集群",
                "bk_pre_obj_id": "",
                "bk_pre_obj_name": ""
            },
            {
                "bk_obj_id": "custom",
                "bk_obj_name": "自定义层级",
                "bk_supplier_account": "0",
                "bk_next_obj": "set",
                "bk_next_name": "集群",
                "bk_pre_obj_id": "biz",
                "bk_pre_obj_name": "业务"
            },
            {
                "bk_obj_id": "set",
                "bk_obj_name": "集群",
                "bk_supplier_account": "0",
                "bk_next_obj": "module",
                "bk_next_name": "模块",
                "bk_pre_obj_id": "custom",
                "bk_pre_obj_name": "自定义层级"
            },
            {
                "bk_obj_id": "module",
                "bk_obj_name": "模块",
                "bk_supplier_account": "0",
                "bk_next_obj": "host",
                "bk_next_name": "主机",
                "bk_pre_obj_id": "set",
                "bk_pre_obj_name": "集群"
            },
            {
                "bk_obj_id": "host",
                "bk_obj_name": "主机",
                "bk_supplier_account": "0",
                "bk_next_obj": "",
                "bk_next_name": "",
                "bk_pre_obj_id": "module",
                "bk_pre_obj_name": "模块"
            }
        ]
    },
    search_biz_inst_topo_return={
        "result": True,
        "code": 0,
        "message": "success",
        "data": [
            {
                "bk_inst_id": 2,
                "bk_inst_name": u"蓝鲸",
                "bk_obj_id": "biz",
                "bk_obj_name": "business",
                "child": [
                    {
                        "bk_inst_id": 3,
                        "bk_inst_name": "Tun",
                        "bk_obj_id": "cus",
                        "bk_obj_name": "cus",
                        "child": [
                            {
                                "bk_inst_id": 5,
                                "bk_inst_name": "set",
                                "bk_obj_id": "set",
                                "bk_obj_name": "set",
                                "child": [
                                    {
                                        "bk_inst_id": 7,
                                        "bk_inst_name": "module",
                                        "bk_obj_id": "module",
                                        "bk_obj_name": "module",
                                        "child": [
                                            {
                                                "bk_inst_id": 15,
                                                "bk_inst_name": "host",
                                                "bk_obj_id": "host",
                                                "bk_obj_name": "host",
                                                "child": []
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    },
    create_set_return={
        "result": True,
        "code": 0,
        "message": "",
        "data": {
            "bk_set_id": 1
        }
    }
)

# 调用 create_set 的通用参数
COMMON_CREAT_SET_API_KWARGS = {
    "bk_supplier_account": 0,
    "bk_biz_id": 2,
    "data": {
        'bk_parent_id': 3,
        'bk_set_name': '1',
        'bk_set_desc': '1',
        'bk_set_env': '1',
        'bk_service_status': '2',
        'description': '1',
        'bk_capacity': 1
    }
}

# parent_data
PARENT_DATA = {
    'executor': 'admin',
    'biz_cc_id': 2
}

SELECT_BY_TEXT_SUCCESS_INPUTS = {
    'biz_cc_id': 2,
    'cc_select_set_parent_method': 'text',
    'cc_set_parent_select_topo': [],
    'cc_set_parent_select_text': u'蓝鲸>Tun\n\n   ',
    'cc_set_info': [{
        'bk_set_name': '1',
        'bk_set_desc': '1',
        'bk_set_env': '测试',
        'bk_service_status': '关闭',
        'description': '1',
        'bk_capacity': '1'}],
    '_loop': 1
}

SELECT_BY_TEXT_SUCCESS_CASE = ComponentTestCase(
    name='success case: select parent set by text(include newline/space)',
    inputs=SELECT_BY_TEXT_SUCCESS_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=[],
    execute_call_assertion=[
        CallAssertion(
            func=COMMON_CLIENT.cc.create_set,
            calls=[Call(COMMON_CREAT_SET_API_KWARGS)]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=COMMON_CLIENT),
        Patcher(target=CC_FORMAT_PROP_DATA, side_effect=cc_format_prop_data_return),
    ]
)

SELECT_BY_TEXT_ERROR_LEVEL_FAIL_INPUTS = {
    'biz_cc_id': 2,
    'cc_select_set_parent_method': 'text',
    'cc_set_parent_select_topo': [],
    'cc_set_parent_select_text': u'蓝鲸>blue>Tun\n\n   ',
    'cc_set_info': [{
        'bk_set_name': '1',
        'bk_set_desc': '1',
        'bk_set_env': '测试',
        'bk_service_status': '关闭',
        'description': '1',
        'bk_capacity': '1'}],
    '_loop': 1
}

SELECT_BY_TEXT_ERROR_LEVEL_FAIL_CAST = ComponentTestCase(
    name='fail case: select parent bt text with error level',
    inputs=SELECT_BY_TEXT_ERROR_LEVEL_FAIL_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=False, outputs={
        'ex_data': u'输入文本路径[蓝鲸>blue>Tun]与业务层级拓扑层级不匹配'
    }),
    schedule_assertion=[],
    execute_call_assertion=[],
    patchers=[]
)

SELECT_BY_TEXT_ERROR_PATH_FAIL_INPUTS = {
    'biz_cc_id': 2,
    'cc_select_set_parent_method': 'text',
    'cc_set_parent_select_topo': [],
    'cc_set_parent_select_text': u'蓝鲸 > blue',
    'cc_set_info': [{
        'bk_set_name': '1',
        'bk_set_desc': '1',
        'bk_set_env': '测试',
        'bk_service_status': '关闭',
        'description': '1',
        'bk_capacity': '1'}],
    '_loop': 1
}
SELECT_BY_TEXT_ERROR_PATH_FAIL_CAST = ComponentTestCase(
    name='fail case: select parent bt text with error path',
    inputs=SELECT_BY_TEXT_ERROR_PATH_FAIL_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=False, outputs={
        'ex_data': u'不存在该拓扑路径：蓝鲸>blue'
    }),
    schedule_assertion=[],
    execute_call_assertion=[],
    patchers=[]
)

SELECT_BY_TOPO_SUCCESS_INPUTS = {
    'biz_cc_id': 2,
    'cc_select_set_parent_method': 'topo',
    'cc_set_parent_select_topo': ['Tun_3'],
    'cc_set_parent_select_text': '',
    'cc_set_info': [{
        'bk_set_name': '1',
        'bk_set_desc': '1',
        'bk_set_env': '测试',
        'bk_service_status': '关闭',
        'description': '1',
        'bk_capacity': '1'}],
    '_loop': 1
}

SELECT_BY_TOPO_SUCCESS_CASE = ComponentTestCase(
    name='success case: select parent set by topo',
    inputs=SELECT_BY_TOPO_SUCCESS_INPUTS,
    parent_data=PARENT_DATA,
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=[],
    execute_call_assertion=[
        CallAssertion(
            func=COMMON_CLIENT.cc.create_set,
            calls=[Call(COMMON_CREAT_SET_API_KWARGS)]
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=COMMON_CLIENT),
        Patcher(target=CC_FORMAT_PROP_DATA, side_effect=cc_format_prop_data_return),
    ]
)
