# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock

from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    ExecuteAssertion,
    ScheduleAssertion,
    Patcher,
)

from pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0 import CCBatchModuleUpdateComponent


class CdVersionRepoDistributeComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            UPDATE_MODULE_SUCCESS_BY_CUSTOM,
            UPDATE_MODULE_FAILED_BY_CUSTOM,
            UPDATE_MODULE_FAILED_BY_TEMPLATE,
            UPDATE_MODULE_SUCCESS_BY_TEMPLATE,
        ]

    def component_cls(self):
        return CCBatchModuleUpdateComponent


class MockClient(object):
    def __init__(
        self, get_mainline_object_topo_return=None, search_biz_inst_topo_return=None, update_module_return=None
    ):
        self.cc = MagicMock()
        self.cc.get_mainline_object_topo = MagicMock(return_value=get_mainline_object_topo_return)
        self.cc.search_biz_inst_topo = MagicMock(return_value=search_biz_inst_topo_return)
        self.cc.update_module = MagicMock(return_value=update_module_return)


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
            "bk_obj_id": "set",
            "bk_obj_name": "集群",
            "bk_supplier_account": "0",
            "bk_next_obj": "module",
            "bk_next_name": "模块",
            "bk_pre_obj_id": "biz",
            "bk_pre_obj_name": "业务",
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
                        },
                        {
                            "bk_inst_id": 8,
                            "bk_inst_name": "module2",
                            "bk_obj_id": "module2",
                            "bk_obj_name": "module2",
                            "child": [],
                        },
                    ],
                }
            ],
        }
    ],
}

COMMON_PARENT = {"executor": "admin", "biz_cc_id": 2, "biz_supplier_account": 0, "bk_biz_name": "蓝鲸"}

UPDATE_MODULE_SUCCESS_CLIENT = MockClient(
    update_module_return={
        "code": 0,
        "permission": None,
        "result": True,
        "request_id": "122345885",
        "message": "success",
        "data": None,
    },
    get_mainline_object_topo_return=COMMON_MAINLINE,
    search_biz_inst_topo_return=COMMON_TOPO,
)

UPDATE_MODULE_FAILED_CLIENT = MockClient(
    update_module_return={
        "code": 0,
        "permission": None,
        "result": False,
        "request_id": "122345885",
        "message": "xxx",
        "data": None,
    },
    get_mainline_object_topo_return=COMMON_MAINLINE,
    search_biz_inst_topo_return=COMMON_TOPO,
)

GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.get_client_by_user"
CC_GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_user"

UPDATE_MODULE_SUCCESS_BY_CUSTOM = ComponentTestCase(
    name="update module success by custom",
    inputs={
        "cc_tag_method": "custom",
        "cc_module_update_data": [
            {
                "cc_module_select_text": "set>module",
                "bk_module_name": "test",
                "bk_module_type": "",
                "operator": "",
                "bk_bak_operator": "",
            }
        ],
        "cc_template_break_line": "",
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "module_update_success": [
                {
                    "cc_module_select_text": "set>module",
                    "bk_module_name": "test",
                    "bk_module_type": "",
                    "operator": "",
                    "bk_bak_operator": "",
                }
            ],
            "module_update_failed": [],
        },
    ),
    schedule_assertion=ScheduleAssertion(success=True, schedule_finished=True, outputs={}),
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=UPDATE_MODULE_SUCCESS_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=UPDATE_MODULE_SUCCESS_CLIENT),
    ],
)

UPDATE_MODULE_FAILED_BY_CUSTOM = ComponentTestCase(
    name="update module failed by custom",
    inputs={
        "cc_tag_method": "custom",
        "cc_module_update_data": [
            {
                "cc_module_select_text": "set>module",
                "bk_module_name": "test",
                "bk_module_type": "",
                "operator": "",
                "bk_bak_operator": "",
            }
        ],
        "cc_template_break_line": "",
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "module_update_success": [],
            "module_update_failed": [
                "module 属性更新失败, item={'cc_module_select_text': 'set>module', 'bk_module_name': 'test', "
                "'bk_module_type': '', 'operator': '', 'bk_bak_operator': ''}, data={'bk_biz_id': 2, 'bk_set_id': 5, "
                "'bk_module_id': 7, 'data': {'bk_module_name': 'test'}}, message: xxx"
            ],
            "ex_data": [
                "module 属性更新失败, item={'cc_module_select_text': 'set>module', 'bk_module_name': 'test', "
                "'bk_module_type': '', 'operator': '', 'bk_bak_operator': ''}, data={'bk_biz_id': 2, 'bk_set_id': 5, "
                "'bk_module_id': 7, 'data': {'bk_module_name': 'test'}}, message: xxx"
            ],
        },
    ),
    schedule_assertion=ScheduleAssertion(success=True, schedule_finished=True, outputs={}),
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=UPDATE_MODULE_FAILED_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=UPDATE_MODULE_SUCCESS_CLIENT),
    ],
)

UPDATE_MODULE_FAILED_BY_TEMPLATE = ComponentTestCase(
    name="update module failed by template",
    inputs={
        "cc_tag_method": "template",
        "cc_module_update_data": [
            {
                "cc_module_select_text": "set>module,set>module2",
                "bk_module_name": "test",
                "bk_module_type": "",
                "operator": "",
                "bk_bak_operator": "",
            }
        ],
        "cc_template_break_line": ",",
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "module_update_success": [],
            "module_update_failed": [
                "module 属性更新失败, item={'cc_module_select_text': 'set>module', 'bk_module_name': 'test', "
                "'bk_module_type': '', 'operator': '', 'bk_bak_operator': ''}, data={'bk_biz_id': 2, 'bk_set_id': 5, "
                "'bk_module_id': 7, 'data': {'bk_module_name': 'test'}}, message: xxx",
                "module 属性更新失败, item={'cc_module_select_text': 'set>module2', 'bk_module_name': 'test', "
                "'bk_module_type': '', 'operator': '', 'bk_bak_operator': ''}, data={'bk_biz_id': 2, 'bk_set_id': 5, "
                "'bk_module_id': 8, 'data': {'bk_module_name': 'test'}}, message: xxx",
            ],
            "ex_data": [
                "module 属性更新失败, item={'cc_module_select_text': 'set>module', 'bk_module_name': 'test', "
                "'bk_module_type': '', 'operator': '', 'bk_bak_operator': ''}, data={'bk_biz_id': 2, 'bk_set_id': 5, "
                "'bk_module_id': 7, 'data': {'bk_module_name': 'test'}}, message: xxx",
                "module 属性更新失败, item={'cc_module_select_text': 'set>module2', 'bk_module_name': 'test', "
                "'bk_module_type': '', 'operator': '', 'bk_bak_operator': ''}, data={'bk_biz_id': 2, 'bk_set_id': 5, "
                "'bk_module_id': 8, 'data': {'bk_module_name': 'test'}}, message: xxx",
            ],
        },
    ),
    schedule_assertion=ScheduleAssertion(success=True, schedule_finished=True, outputs={}),
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=UPDATE_MODULE_FAILED_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=UPDATE_MODULE_SUCCESS_CLIENT),
    ],
)

UPDATE_MODULE_SUCCESS_BY_TEMPLATE = ComponentTestCase(
    name="update module success by template",
    inputs={
        "cc_tag_method": "template",
        "cc_module_update_data": [
            {
                "cc_module_select_text": "set>module,set>module2",
                "bk_module_name": "test",
                "bk_module_type": "",
                "operator": "",
                "bk_bak_operator": "",
            }
        ],
        "cc_template_break_line": ",",
    },
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "module_update_success": [
                {
                    "cc_module_select_text": "set>module",
                    "bk_module_name": "test",
                    "bk_module_type": "",
                    "operator": "",
                    "bk_bak_operator": "",
                },
                {
                    "cc_module_select_text": "set>module2",
                    "bk_module_name": "test",
                    "bk_module_type": "",
                    "operator": "",
                    "bk_bak_operator": "",
                },
            ],
            "module_update_failed": [],
        },
    ),
    schedule_assertion=ScheduleAssertion(success=True, schedule_finished=True, outputs={}),
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=UPDATE_MODULE_SUCCESS_CLIENT),
        Patcher(target=CC_GET_CLIENT_BY_USER, return_value=UPDATE_MODULE_SUCCESS_CLIENT),
    ],
)
