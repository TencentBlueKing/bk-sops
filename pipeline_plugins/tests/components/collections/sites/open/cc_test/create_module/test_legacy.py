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
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.cc.create_module.legacy import CCCreateModuleComponent


class CCCreateModuleComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        return CCCreateModuleComponent

    def cases(self):
        return [
            SELECT_BY_TEXT_SUCCESS_CASE,
            SELECT_BY_TOPO_SUCCESS_CASE,
            SELECT_BY_TEXT_ERROR_PATH_FAIL_CASE,
            SELECT_BY_TEXT_ERROR_LEVEL_FAIL_CASE,
            CREATE_BY_TEMPLATE_SUCCESS_CASE,
            EMPTY_MODULE_INFOS_FAILED_CASE,
        ]


class MockClient(object):
    def __init__(
        self, get_mainline_object_topo_return=None, search_biz_inst_topo_return=None, create_module_return=None
    ):
        self.cc = MagicMock()
        self.cc.get_mainline_object_topo = MagicMock(return_value=get_mainline_object_topo_return)
        self.cc.search_biz_inst_topo = MagicMock(return_value=search_biz_inst_topo_return)
        self.cc.create_module = MagicMock(return_value=create_module_return)


GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.get_client_by_user"
CC_GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_user"
CC_FORMAT_PROP_DATA = "pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_format_prop_data"

CC_FORMAT_PROP_DATA_RETURN = {"result": True, "data": {"普通": "1", "数据库": "2"}}

COMMON_MAINLINE = {
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
            "bk_pre_obj_name": "",
        },
        {
            "bk_obj_id": "custom",
            "bk_obj_name": "自定义层级",
            "bk_supplier_account": "0",
            "bk_next_obj": "set",
            "bk_next_name": "集群",
            "bk_pre_obj_id": "biz",
            "bk_pre_obj_name": "业务",
        },
        {
            "bk_obj_id": "set",
            "bk_obj_name": "集群",
            "bk_supplier_account": "0",
            "bk_next_obj": "module",
            "bk_next_name": "模块",
            "bk_pre_obj_id": "custom",
            "bk_pre_obj_name": "自定义层级",
        },
        {
            "bk_obj_id": "module",
            "bk_obj_name": "模块",
            "bk_supplier_account": "0",
            "bk_next_obj": "host",
            "bk_next_name": "主机",
            "bk_pre_obj_id": "set",
            "bk_pre_obj_name": "集群",
        },
        {
            "bk_obj_id": "host",
            "bk_obj_name": "主机",
            "bk_supplier_account": "0",
            "bk_next_obj": "",
            "bk_next_name": "",
            "bk_pre_obj_id": "module",
            "bk_pre_obj_name": "模块",
        },
    ],
}

COMMON_TOPO = {
    "result": True,
    "code": 0,
    "message": "success",
    "data": [
        {
            "bk_inst_id": 2,
            "bk_inst_name": "蓝鲸",
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
                                            "child": [],
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    ],
}

COMMON_PARENT = {"executor": "admin", "biz_cc_id": 2, "biz_supplier_account": 0}

SELECT_BY_TEXT_SUCCESS_CLIENT = MockClient(
    get_mainline_object_topo_return=COMMON_MAINLINE,
    search_biz_inst_topo_return=COMMON_TOPO,
    create_module_return={"result": True, "code": 0, "message": "", "data": {}},
)

SELECT_BY_TEXT_SUCCESS_INPUTS = {
    "biz_cc_id": 2,
    "cc_set_select_method": "text",
    "cc_set_select_topo": [],
    "cc_set_select_text": "    蓝鲸>Tun>set\n\n",
    "cc_create_method": "category",
    "cc_module_infos_category": [
        {
            "bk_module_name": "1",
            "bk_module_type": "普通",
            "operator": "1",
            "bk_bak_operator": "1",
            "cc_service_category": [1, 2],
        }
    ],
    "cc_module_infos_template": [],
    "_loop": 1,
}

SELECT_BY_TEXT_SUCCESS_CASE = ComponentTestCase(
    name="success case: select set by text(include newline/space)",
    inputs=SELECT_BY_TEXT_SUCCESS_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=SELECT_BY_TEXT_SUCCESS_CLIENT.cc.create_module,
            calls=[
                Call(
                    {
                        "bk_biz_id": 2,
                        "bk_set_id": 5,
                        "data": {
                            "bk_parent_id": 5,
                            "bk_module_name": "1",
                            "bk_module_type": "1",
                            "operator": "1",
                            "bk_bak_operator": "1",
                            "service_category_id": 2,
                        },
                    }
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SELECT_BY_TEXT_SUCCESS_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=SELECT_BY_TEXT_SUCCESS_CLIENT),
        Patcher(target=CC_FORMAT_PROP_DATA, return_value=CC_FORMAT_PROP_DATA_RETURN),
    ],
)


SELECT_BY_TOPO_SUCCESS_CLIENT = MockClient(
    get_mainline_object_topo_return=COMMON_MAINLINE,
    search_biz_inst_topo_return=COMMON_TOPO,
    create_module_return={"result": True, "code": 0, "message": "", "data": {}},
)

SELECT_BY_TOPO_SUCCESS_INPUTS = {
    "biz_cc_id": 2,
    "cc_set_select_method": "topo",
    "cc_set_select_topo": ["set_5"],
    "cc_set_select_text": "",
    "cc_create_method": "category",
    "cc_module_infos_category": [
        {
            "bk_module_name": "1",
            "bk_module_type": "普通",
            "operator": "1",
            "bk_bak_operator": "1",
            "cc_service_category": [1, 2],
        }
    ],
    "cc_module_infos_template": [],
    "_loop": 1,
}

SELECT_BY_TOPO_SUCCESS_CASE = ComponentTestCase(
    name="success case: select set by topo",
    inputs=SELECT_BY_TOPO_SUCCESS_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=SELECT_BY_TOPO_SUCCESS_CLIENT.cc.create_module,
            calls=[
                Call(
                    {
                        "bk_biz_id": 2,
                        "bk_set_id": 5,
                        "data": {
                            "bk_parent_id": 5,
                            "bk_module_name": "1",
                            "bk_module_type": "1",
                            "operator": "1",
                            "bk_bak_operator": "1",
                            "service_category_id": 2,
                        },
                    }
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SELECT_BY_TOPO_SUCCESS_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=SELECT_BY_TEXT_SUCCESS_CLIENT),
        Patcher(target=CC_FORMAT_PROP_DATA, return_value=CC_FORMAT_PROP_DATA_RETURN),
    ],
)


SELECT_BY_TEXT_ERROR_PATH_FAIL_CLIENT = MockClient(
    get_mainline_object_topo_return=COMMON_MAINLINE, search_biz_inst_topo_return=COMMON_TOPO
)


SELECT_BY_TEXT_ERROR_PATH_FAIL_INPUTS = {
    "biz_cc_id": 2,
    "cc_set_select_method": "text",
    "cc_set_select_topo": [],
    "cc_set_select_text": "    蓝鲸>Yun >set\n\n",
    "cc_create_method": "category",
    "cc_module_infos_category": [
        {
            "bk_module_name": "1",
            "bk_module_type": "普通",
            "operator": "1",
            "bk_bak_operator": "1",
            "cc_service_category": [1, 2],
        }
    ],
    "cc_module_infos_template": [],
    "_loop": 1,
}

SELECT_BY_TEXT_ERROR_PATH_FAIL_CASE = ComponentTestCase(
    name="fail case: select set by text with error path",
    inputs=SELECT_BY_TEXT_ERROR_PATH_FAIL_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "不存在该拓扑路径：蓝鲸>Yun>set"}),
    schedule_assertion=None,
    execute_call_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SELECT_BY_TEXT_ERROR_PATH_FAIL_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=SELECT_BY_TEXT_ERROR_PATH_FAIL_CLIENT),
        Patcher(target=CC_FORMAT_PROP_DATA, return_value=CC_FORMAT_PROP_DATA_RETURN),
    ],
)


SELECT_BY_TEXT_ERROR_LEVEL_FAIL_CLIENT = MockClient(
    get_mainline_object_topo_return=COMMON_MAINLINE, search_biz_inst_topo_return=COMMON_TOPO
)


SELECT_BY_TEXT_ERROR_LEVEL_FAIL_INPUTS = {
    "biz_cc_id": 2,
    "cc_set_select_method": "text",
    "cc_set_select_topo": [],
    "cc_set_select_text": "    蓝鲸>Yun\n\n",
    "cc_create_method": "category",
    "cc_module_infos_category": [
        {
            "bk_module_name": "1",
            "bk_module_type": "普通",
            "operator": "1",
            "bk_bak_operator": "1",
            "cc_service_category": [1, 2],
        }
    ],
    "cc_module_infos_template": [],
    "_loop": 1,
}

SELECT_BY_TEXT_ERROR_LEVEL_FAIL_CASE = ComponentTestCase(
    name="fail case: select set by text with error level",
    inputs=SELECT_BY_TEXT_ERROR_LEVEL_FAIL_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "输入文本路径[蓝鲸>Yun]与业务拓扑层级不匹配"}),
    schedule_assertion=None,
    execute_call_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SELECT_BY_TEXT_ERROR_LEVEL_FAIL_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=SELECT_BY_TEXT_ERROR_LEVEL_FAIL_CLIENT),
        Patcher(target=CC_FORMAT_PROP_DATA, return_value=CC_FORMAT_PROP_DATA_RETURN),
    ],
)


CREATE_BY_TEMPLATE_SUCCESS_CLIENT = MockClient(
    get_mainline_object_topo_return=COMMON_MAINLINE,
    search_biz_inst_topo_return=COMMON_TOPO,
    create_module_return={"result": True, "code": 0, "message": "", "data": {}},
)

CREATE_BY_TEMPLATE_SUCCESS_INPUTS = {
    "biz_cc_id": 2,
    "cc_set_select_method": "text",
    "cc_set_select_topo": [],
    "cc_set_select_text": "    蓝鲸>Tun>set\n\n",
    "cc_create_method": "template",
    "cc_module_infos_template": [{"cc_service_template": "cxx_100"}],
    "cc_module_infos_category": [],
    "_loop": 1,
}

CREATE_BY_TEMPLATE_SUCCESS_CASE = ComponentTestCase(
    name="success case: create module by template",
    inputs=CREATE_BY_TEMPLATE_SUCCESS_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=SELECT_BY_TEXT_SUCCESS_CLIENT.cc.create_module,
            calls=[
                Call(
                    {
                        "bk_biz_id": 2,
                        "bk_set_id": 5,
                        "data": {"bk_parent_id": 5, "bk_module_name": "cxx", "service_template_id": 100},
                    }
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SELECT_BY_TEXT_SUCCESS_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=SELECT_BY_TEXT_SUCCESS_CLIENT),
        Patcher(target=CC_FORMAT_PROP_DATA, return_value=CC_FORMAT_PROP_DATA_RETURN),
    ],
)


EMPTY_MODULE_INFOS_FAILED_CLIENT = MockClient(
    get_mainline_object_topo_return=COMMON_MAINLINE,
    search_biz_inst_topo_return=COMMON_TOPO,
)

EMPTY_MODULE_INFOS_FAILED_INPUTS = {
    "biz_cc_id": 2,
    "cc_set_select_method": "text",
    "cc_set_select_topo": [],
    "cc_set_select_text": "    蓝鲸>Tun>set\n\n",
    "cc_create_method": "template",
    "cc_module_infos_template": [],
    "cc_module_infos_category": [],
    "_loop": 1,
}

EMPTY_MODULE_INFOS_FAILED_CASE = ComponentTestCase(
    name="fail case: module infos is empty",
    inputs=EMPTY_MODULE_INFOS_FAILED_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "模块信息不能为空"}),
    schedule_assertion=None,
    execute_call_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=EMPTY_MODULE_INFOS_FAILED_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=EMPTY_MODULE_INFOS_FAILED_CLIENT),
        Patcher(target=CC_FORMAT_PROP_DATA, return_value=CC_FORMAT_PROP_DATA_RETURN),
    ],
)
