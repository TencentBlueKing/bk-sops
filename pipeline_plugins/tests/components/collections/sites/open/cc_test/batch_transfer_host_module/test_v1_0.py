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
from pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0 import (
    CCBatchTransferHostModuleComponent,
)


class CCBatchTransferHostModuleComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        return CCBatchTransferHostModuleComponent

    def cases(self):
        return [TRANSFER_HOST_MODULE_SUCCESS_CASE, TRANSFER_HOST_MODULE_AUTO_COMPLETE_BIZ_SUCCESS_CASE]


class MockClient(object):
    def __init__(
        self,
        batch_transfer_host_module_return=None,
        search_biz_inst_topo_return=None,
        get_mainline_object_topo_return=None,
    ):
        self.cc = MagicMock()
        self.cc.transfer_host_module = MagicMock(return_value=batch_transfer_host_module_return)
        self.cc.search_biz_inst_topo = MagicMock(return_value=search_biz_inst_topo_return)
        self.cc.get_mainline_object_topo = MagicMock(return_value=get_mainline_object_topo_return)


GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module" ".v1_0.get_client_by_user"
)
CC_GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_user"
CC_GET_HOST_ID_BY_INNERIP = (
    "pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0" ".cc_get_host_id_by_innerip"
)
CC_LIST_SELECT_NODE_INST_ID = (
    "pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0"
    ".cc_list_select_node_inst_id"
)

COMMON_PARENT = {"executor": "admin", "biz_cc_id": 2, "biz_supplier_account": 0, "bk_biz_name": "蓝鲸"}
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

TRANSFER_MODULE_SUCCESS_CLIENT = MockClient(
    batch_transfer_host_module_return={"result": True, "code": 0, "message": "", "data": {}},
    search_biz_inst_topo_return=COMMON_TOPO,
)

TRANSFER_MODULE_SUCCESS_INPUTS = {
    "cc_module_select_method": "manual",
    "cc_host_transfer_detail": [{"cc_transfer_host_ip": "2.5.5.6", "cc_transfer_host_target_module": "蓝鲸>Tun>set"}],
    "cc_transfer_host_template_break_line": "",
    "_loop": 1,
}

TRANSFER_MODULE_SUCCESS_OUTPUTS = {
    "transfer_host_module_success": [
        {"cc_transfer_host_ip": "2.5.5.6", "cc_transfer_host_target_module": "蓝鲸>Tun>set"}
    ],
    "transfer_host_module_failed": [],
}


TRANSFER_HOST_MODULE_SUCCESS_CASE = ComponentTestCase(
    name="transfer success case",
    inputs=TRANSFER_MODULE_SUCCESS_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs=TRANSFER_MODULE_SUCCESS_OUTPUTS),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=CC_GET_HOST_ID_BY_INNERIP, calls=[Call("admin", 2, ["2.5.5.6"], 0)]),
        CallAssertion(
            func=TRANSFER_MODULE_SUCCESS_CLIENT.cc.transfer_host_module,
            calls=[
                Call(
                    {
                        "bk_biz_id": 2,
                        "bk_supplier_account": 0,
                        "bk_host_id": [2],
                        "bk_module_id": [7],
                        "is_increment": True,
                    }
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=TRANSFER_MODULE_SUCCESS_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=TRANSFER_MODULE_SUCCESS_CLIENT),
        Patcher(target=CC_GET_HOST_ID_BY_INNERIP, return_value={"result": True, "data": ["2"]}),
        Patcher(target=CC_LIST_SELECT_NODE_INST_ID, return_value={"result": True, "data": ["7"]}),
    ],
)

TRANSFER_MODULE_AUTO_COMPLETE_BIZ_SUCCESS_INPUTS = {
    "cc_module_select_method": "manual",
    "cc_host_transfer_detail": [{"cc_transfer_host_ip": "2.5.5.6", "cc_transfer_host_target_module": "Tun>set"}],
    "cc_transfer_host_template_break_line": "",
    "_loop": 1,
}

TRANSFER_MODULE_AUTO_COMPLETE_BIZ_SUCCESS_OUTPUTS = {
    "transfer_host_module_success": [{"cc_transfer_host_ip": "2.5.5.6", "cc_transfer_host_target_module": "Tun>set"}],
    "transfer_host_module_failed": [],
}


TRANSFER_HOST_MODULE_AUTO_COMPLETE_BIZ_SUCCESS_CASE = ComponentTestCase(
    name="transfer auto complete success case",
    inputs=TRANSFER_MODULE_AUTO_COMPLETE_BIZ_SUCCESS_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs=TRANSFER_MODULE_AUTO_COMPLETE_BIZ_SUCCESS_OUTPUTS),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=CC_GET_HOST_ID_BY_INNERIP, calls=[Call("admin", 2, ["2.5.5.6"], 0)]),
        CallAssertion(
            func=TRANSFER_MODULE_SUCCESS_CLIENT.cc.transfer_host_module,
            calls=[
                Call(
                    {
                        "bk_biz_id": 2,
                        "bk_supplier_account": 0,
                        "bk_host_id": [2],
                        "bk_module_id": [7],
                        "is_increment": True,
                    }
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=TRANSFER_MODULE_SUCCESS_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=TRANSFER_MODULE_SUCCESS_CLIENT),
        Patcher(target=CC_GET_HOST_ID_BY_INNERIP, return_value={"result": True, "data": ["2"]}),
        Patcher(target=CC_LIST_SELECT_NODE_INST_ID, return_value={"result": True, "data": ["7"]}),
    ],
)
