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
from pipeline_plugins.components.collections.sites.open.cc.host_custom_property_change.v1_0 import \
    CCHostCustomPropertyChangeComponent


class CCHostCustomPropertyChangeTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        return CCHostCustomPropertyChangeComponent

    def cases(self):
        return [
            NO_INPUT_RULE_CHANGE_HOST_PROPERTY_FAIL_CASE,
            FIND_SET_BATCH_FAIL_CHANGE_HOST_PROPERTY_FAIL_CASE,
            FIND_SET_BATCH_SUCCESS_FIND_MODULE_BATCH_FAIL_CHANGE_HOST_PROPERTY_FAIL_CASE,
            GET_HOST_BASE_INFO_FAIL_CHANGE_HOST_PROPERTY_FAIL_CASE,
            CHANGE_HOST_PROPERTY_SUCCESS_CASE,
            CHANGE_HOST_PROPERTY_FAIL_CASE,
            INVALID_IP_CASE
        ]


class MockClient(object):
    def __init__(
        self,
        batch_update_host_return=None,
        find_set_batch_return=None,
        find_module_batch_return=None,
        get_host_base_info_func=None,
    ):
        self.cc = MagicMock()
        self.cc.find_set_batch = MagicMock(return_value=find_set_batch_return)
        self.cc.find_module_batch = MagicMock(return_value=find_module_batch_return)
        self.cc.get_host_base_info = MagicMock(side_effect=get_host_base_info_func)
        self.cc.batch_update_host = MagicMock(return_value=batch_update_host_return)


def get_host_base_info(*args, **kwargs):
    if kwargs["bk_host_id"] == 1212:
        data = {
            "code": 0,
            "result": True,
            "message": "success",
            "data": [
                {"bk_property_value": "admin", "bk_property_id": "bk_bak_operator"},
                {"bk_property_value": "", "bk_property_id": "接入iFix"},
            ],
        }
    else:
        data = {
            "code": 0,
            "result": True,
            "message": "success",
            "data": [
                {"bk_property_value": "admin_q", "bk_property_id": "bk_bak_operator"},
                {"bk_property_value": "ww", "bk_property_id": "接入iFix"},
            ],
        }
    return data


def get_host_base_info_fail(*args, **kwargs):
    return {"result": False, "message": "get host base info fail"}


# mock path
GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.cc.host_custom_property_change.v1_0.get_client_by_user"
)
CC_GET_IPS_INFO_BY_STR = (
    "pipeline_plugins.components.collections.sites.open.cc.host_custom_property_change.v1_0.cc_get_ips_info_by_str"
)

# mock clients
GET_HOST_BASE_INFO_CLIENT_SUCCESS = MockClient(
    find_set_batch_return={
        "result": True,
        "message": "find set batch success",
        "data": [{"bk_set_id": 111, "bk_set_name": "set_a"}, {"bk_set_id": 222, "bk_set_name": "set_b"}],
    },
    find_module_batch_return={
        "result": True,
        "message": "find module batch success",
        "data": [
            {"bk_module_id": 1111, "bk_module_name": "module_a"},
            {"bk_module_id": 2222, "bk_module_name": "module_b"},
        ],
    },
    get_host_base_info_func=get_host_base_info,
)

GET_HOST_BASE_INFO_CLIENT_FAIL = MockClient(
    find_set_batch_return={
        "result": True,
        "message": "find set batch success",
        "data": [{"bk_set_id": 111, "bk_set_name": "set_a"}, {"bk_set_id": 222, "bk_set_name": "set_b"}],
    },
    find_module_batch_return={
        "result": True,
        "message": "find module batch success",
        "data": [
            {"bk_module_id": 1111, "bk_module_name": "module_a"},
            {"bk_module_id": 2222, "bk_module_name": "module_b"},
        ],
    },
    get_host_base_info_func=get_host_base_info_fail,
)

FIND_SET_BATCH_FAIL_CLIENT = MockClient(find_set_batch_return={"result": False, "message": "find set batch fail"})
FIND_SET_BATCH_SUCCESS_FIND_MODULE_BATCH_FAIL_CLIENT = MockClient(
    find_set_batch_return={
        "result": True,
        "message": "find set batch success",
        "data": [{"bk_set_id": 111, "bk_set_name": "set_a"}, {"bk_set_id": 222, "bk_set_name": "set_b"}],
    },
    find_module_batch_return={"result": False, "message": "find module batch fail"},
)

EXECUTE_TASK_SUCCESS_CLIENT = MockClient(
    find_set_batch_return={
        "result": True,
        "message": "find set batch success",
        "data": [{"bk_set_id": 111, "bk_set_name": "set_a"}, {"bk_set_id": 222, "bk_set_name": "set_b"}],
    },
    find_module_batch_return={
        "result": True,
        "message": "find module batch success",
        "data": [
            {"bk_module_id": 1111, "bk_module_name": "module_a"},
            {"bk_module_id": 2222, "bk_module_name": "module_b"},
        ],
    },
    get_host_base_info_func=get_host_base_info,
    batch_update_host_return={
        "result": True,
        "code": 0,
        "message": "success",
        "data": None
    }
)
EXECUTE_TASK_FAIL_CLIENT = MockClient(
    find_set_batch_return={
        "result": True,
        "message": "find set batch success",
        "data": [{"bk_set_id": 111, "bk_set_name": "set_a"}, {"bk_set_id": 222, "bk_set_name": "set_b"}],
    },
    find_module_batch_return={
        "result": True,
        "message": "find module batch success",
        "data": [
            {"bk_module_id": 1111, "bk_module_name": "module_a"},
            {"bk_module_id": 2222, "bk_module_name": "module_b"},
        ],
    },
    get_host_base_info_func=get_host_base_info,
    batch_update_host_return={"result": False, "message": "Batch update host Failed"},
)

INPUT_DATA = {
    "cc_ip_list": "1.1.1.1,2.2.2.2",
    "cc_custom_property": "dbrole",
    "cc_hostname_rule": [
        {"field_rule_code": "1", "field_content": "bk_bak_operator", "field_order": "1"},
        {"field_rule_code": "2", "field_content": "bk_set_name", "field_order": "2"},
        {"field_rule_code": "3", "field_content": "bk_module_name", "field_order": "3"},
        {"field_rule_code": "1", "field_content": "接入iFix", "field_order": "7"},
    ],
    "cc_custom_rule": [
        {"field_rule_code": "4", "field_content": "%", "field_order": "4"},
        {"field_rule_code": "5", "field_content": "3", "field_order": "5"},
        {"field_rule_code": "6", "field_content": "ww", "field_order": "6"},
    ],
}

INPUT_DATA_NO_RULE = {
    "cc_ip_list": "1.1.1.1,2.2.2.2",
    "cc_custom_property": "dbrole",
    "cc_hostname_rule": [],
    "cc_custom_rule": []
}

INPUT_DATA_INVALID = {
    "cc_ip_list": "1.1.1,2.2.2.2",
    "cc_custom_property": "dbrole",
    "cc_hostname_rule": [
        {"field_rule_code": "1", "field_content": "bk_bak_operator", "field_order": "1"},
        {"field_rule_code": "2", "field_content": "bk_set_name", "field_order": "2"},
        {"field_rule_code": "3", "field_content": "bk_module_name", "field_order": "3"},
        {"field_rule_code": "1", "field_content": "接入iFix", "field_order": "7"},
    ],
    "cc_custom_rule": [
        {"field_rule_code": "4", "field_content": "%", "field_order": "4"},
        {"field_rule_code": "4", "field_content": "3", "field_order": "5"},
        {"field_rule_code": "6", "field_content": "ww", "field_order": "6"},
    ],
}

CC_GET_IPS_INFO_BY_STR_VALUE = {
    "result": True,
    "ip_count": 2,
    "ip_result": [
        {"ModuleID": 1111, "HostID": 1212, "InnerIP": "1.1.1.1", "SetID": 111,
         "Sets": [{"bk_set_id": 111}],
         "Modules": [{"bk_module_id": 1111}]},
        {"ModuleID": 2222, "HostID": 3434, "InnerIP": "2.2.2.2", "SetID": 222,
         "Sets": [{"bk_set_id": 222}],
         "Modules": [{"bk_module_id": 2222}]},
    ],
    "invalid_ip": []
}

# test case
# 没有输入规则 修改主机名不成功的案例
NO_INPUT_RULE_CHANGE_HOST_PROPERTY_FAIL_CASE = ComponentTestCase(
    name="no input rule change host property fail case",
    inputs=INPUT_DATA_NO_RULE,
    parent_data={"executor": "executor", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "请选择至少一种规则"}),
    schedule_assertion=None,
    patchers=[Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value=CC_GET_IPS_INFO_BY_STR_VALUE)],
)

# 查询集群的属性值失败的案例
FIND_SET_BATCH_FAIL_CHANGE_HOST_PROPERTY_FAIL_CASE = ComponentTestCase(
    name="find set batch fail change host property fail case",
    inputs=INPUT_DATA,
    parent_data={"executor": "executor", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            'ex_data': '调用蓝鲸配置平台(CC)接口cc.find_set_batch返回失败,'
                       ' params={"bk_biz_id":1,"bk_ids":[222,111],"fields":["bk_set_name","bk_set_id"]},'
                       ' error=find set batch fail'},
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username="executor", biz_cc_id=1, ip_str="1.1.1.1,2.2.2.2", use_cache=False)],
        ),
        CallAssertion(
            func=FIND_SET_BATCH_FAIL_CLIENT.cc.find_set_batch,
            calls=[Call({"bk_biz_id": 1, "bk_ids": [222, 111], "fields": ["bk_set_name", "bk_set_id"]})],
        ),
    ],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=FIND_SET_BATCH_FAIL_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value=CC_GET_IPS_INFO_BY_STR_VALUE),
    ],
)

# 查询module属性失败的案例
FIND_SET_BATCH_SUCCESS_FIND_MODULE_BATCH_FAIL_CHANGE_HOST_PROPERTY_FAIL_CASE = ComponentTestCase(
    name="find set batch success find module batch fail change host property fail case",
    inputs=INPUT_DATA,
    parent_data={"executor": "executor", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "ex_data": "调用蓝鲸配置平台(CC)接口cc.find_module_batch返回失败, "
            'params={"bk_biz_id":1,"bk_ids":[2222,1111],'
            '"fields":["bk_module_name","bk_module_id"]}, error=find module batch fail'
        },
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username="executor", biz_cc_id=1, ip_str="1.1.1.1,2.2.2.2", use_cache=False)],
        ),
        CallAssertion(
            func=FIND_SET_BATCH_SUCCESS_FIND_MODULE_BATCH_FAIL_CLIENT.cc.find_set_batch,
            calls=[Call({"bk_biz_id": 1, "bk_ids": [222, 111], "fields": ["bk_set_name", "bk_set_id"]})],
        ),
        CallAssertion(
            func=FIND_SET_BATCH_SUCCESS_FIND_MODULE_BATCH_FAIL_CLIENT.cc.find_module_batch,
            calls=[Call({"bk_biz_id": 1, "bk_ids": [2222, 1111], "fields": ["bk_module_name", "bk_module_id"]})],
        ),
    ],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=FIND_SET_BATCH_SUCCESS_FIND_MODULE_BATCH_FAIL_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value=CC_GET_IPS_INFO_BY_STR_VALUE),
    ],
)

# 查询主机属性失败案例
GET_HOST_BASE_INFO_FAIL_CHANGE_HOST_PROPERTY_FAIL_CASE = ComponentTestCase(
    name="get host base info fail case",
    inputs=INPUT_DATA,
    parent_data={"executor": "executor", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "ex_data": "调用蓝鲸配置平台(CC)接口cc.get_host_base_info返回失败, "
            'params={"bk_host_id":1212}, error=get host base info fail'
        },
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username="executor", biz_cc_id=1, ip_str="1.1.1.1,2.2.2.2", use_cache=False)],
        ),
        CallAssertion(
            func=GET_HOST_BASE_INFO_CLIENT_FAIL.cc.find_set_batch,
            calls=[Call({"bk_biz_id": 1, "bk_ids": [222, 111], "fields": ["bk_set_name", "bk_set_id"]})],
        ),
        CallAssertion(
            func=GET_HOST_BASE_INFO_CLIENT_FAIL.cc.find_module_batch,
            calls=[Call({"bk_biz_id": 1, "bk_ids": [2222, 1111], "fields": ["bk_module_name", "bk_module_id"]})],
        ),
    ],
    schedule_assertion=None,
    patchers=[
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value=CC_GET_IPS_INFO_BY_STR_VALUE),
        Patcher(target=GET_CLIENT_BY_USER, return_value=GET_HOST_BASE_INFO_CLIENT_FAIL),
    ],
)

# 输入ip不合法案例
INVALID_IP_CASE = ComponentTestCase(
    name="Invalid IP Case",
    inputs=INPUT_DATA_INVALID,
    parent_data={"executor": "executor", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法"}),
    schedule_assertion=None,
    execute_call_assertion=None,
    patchers=[Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"result": False, "ip_count": 0, "ip_result": []})],
)

# 更改主机属性成功案例
CHANGE_HOST_PROPERTY_SUCCESS_CASE = ComponentTestCase(
    name="Change Host property Success Case",
    inputs=INPUT_DATA,
    parent_data={"executor": "executor", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=True, outputs={}
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username="executor", biz_cc_id=1, ip_str="1.1.1.1,2.2.2.2", use_cache=False)],
        ),
        CallAssertion(
            func=EXECUTE_TASK_SUCCESS_CLIENT.cc.batch_update_host,
            calls=[
                Call(
                    {
                        'update': [
                            {
                                'bk_host_id': 1212,
                                'properties': {
                                    'dbrole': 'adminset_amodule_a1%1%1%13ww'
                                }
                            },
                            {
                                'bk_host_id': 3434,
                                'properties': {
                                    'dbrole': 'admin_qset_bmodule_b2%2%2%24wwww'
                                }
                            }
                        ]
                    }
                )
            ],
        ),
    ],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_TASK_SUCCESS_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value=CC_GET_IPS_INFO_BY_STR_VALUE),
    ],
)

# 更改主机属性失败案例
CHANGE_HOST_PROPERTY_FAIL_CASE = ComponentTestCase(
    name="Change Host property Fail Case",
    inputs=INPUT_DATA,
    parent_data={"executor": "executor", "biz_cc_id": 1},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            'ex_data': '调用配置平台(CMDB)接口cc.batch_update_host返回失败, '
                       'params={"update":[{"bk_host_id":1212,"properties":{"dbrole":"adminset_amodule_a1%1%1%13ww"}},'
                       '{"bk_host_id":3434,"properties":{"dbrole":"admin_qset_bmodule_b2%2%2%24wwww"}}]}, '
                       'error=Batch update host Failed'
        },
    ),
    execute_call_assertion=[
        CallAssertion(
            func=CC_GET_IPS_INFO_BY_STR,
            calls=[Call(username="executor", biz_cc_id=1, ip_str="1.1.1.1,2.2.2.2", use_cache=False)],
        ),
        CallAssertion(
            func=EXECUTE_TASK_FAIL_CLIENT.cc.find_set_batch,
            calls=[Call({"bk_biz_id": 1, "bk_ids": [222, 111], "fields": ["bk_set_name", "bk_set_id"]})],
        ),
        CallAssertion(
            func=EXECUTE_TASK_FAIL_CLIENT.cc.find_module_batch,
            calls=[Call({"bk_biz_id": 1, "bk_ids": [2222, 1111], "fields": ["bk_module_name", "bk_module_id"]})],
        ),
    ],
    schedule_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=EXECUTE_TASK_FAIL_CLIENT),
        Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value=CC_GET_IPS_INFO_BY_STR_VALUE),
    ],
)
