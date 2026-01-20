# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock
from pipeline.component_framework.test import (
    Call,
    CallAssertion,
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    Patcher,
)

from pipeline_plugins.components.collections.sites.open.cc.replace_fault_machine.legacy import (
    CCReplaceFaultMachineComponent,
)


class CCReplaceFaultMachineComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        return CCReplaceFaultMachineComponent

    def cases(self):
        return [
            SUCCESS_CASE_COPY_ATTRS,
            SEARCH_ATTR_FAIL_CASE,
            FAULT_HOST_NOT_FOUND_CASE,
            NEW_HOST_NOT_FOUND_CASE,
            BATCH_UPDATE_FAIL_CASE,
            TRANSFER_TO_FAULT_FAIL_CASE,
            TRANSFER_MODULE_FAIL_CASE,
        ]


class MockClient(object):
    def __init__(
        self,
        search_object_attribute_return=None,
        batch_update_host_return=None,
        transfer_host_to_faultmodule_return=None,
        transfer_host_module_returns=None,
    ):
        self.set_bk_api_ver = MagicMock()
        self.api = MagicMock()
        self.api.search_object_attribute = MagicMock(return_value=search_object_attribute_return)
        self.api.batch_update_host = MagicMock(return_value=batch_update_host_return)
        self.api.transfer_host_to_faultmodule = MagicMock(return_value=transfer_host_to_faultmodule_return)
        # transfer_host_module 可能会被调用多次
        if isinstance(transfer_host_module_returns, list):
            self.api.transfer_host_module = MagicMock(side_effect=transfer_host_module_returns)
        else:
            self.api.transfer_host_module = MagicMock(return_value=transfer_host_module_returns)


GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.cc.replace_fault_machine.legacy.get_client_by_username"
)
CC_HANDLE_API_ERROR = (
    "pipeline_plugins.components.collections.sites.open.cc.replace_fault_machine.legacy.cc_handle_api_error"
)
SERVICE_GET_HOST_TOPO = (
    "pipeline_plugins.components.collections.sites.open.cc.replace_fault_machine."
    "legacy.CCReplaceFaultMachineService.get_host_topo"
)


# 通用 parent_data
COMMON_PARENT = {"tenant_id": "system", "executor": "admin", "biz_cc_id": 2}

# 通用 inputs：替换故障机
COMMON_INPUTS = {
    "biz_cc_id": 2,
    "cc_host_replace_detail": [{"cc_fault_ip": "10.0.0.1", "cc_new_ip": "10.0.0.2"}],
    "copy_attributes": True,
    "_loop": 1,
}

# 通用 search_object_attribute 返回：两个属性其中一个可编辑
SEARCH_OBJECT_ATTRIBUTE_OK = {
    "result": True,
    "data": [
        {"bk_property_id": "bk_os_type", "editable": True},
        {"bk_property_id": "bk_sn", "editable": False},
    ],
}


def build_host_topo(ip, host_id, modules):
    # CCPluginIPMixin.get_host_topo 的返回结构示例
    return [
        {
            "host": {"bk_host_id": host_id, "bk_host_innerip": ip, "bk_os_type": "linux"},
            "module": [{"bk_module_id": mid} for mid in modules],
        }
    ]


# 成功用例：复制属性成功，转移到故障模块成功，转移模块成功
SUCCESS_CLIENT = MockClient(
    search_object_attribute_return=SEARCH_OBJECT_ATTRIBUTE_OK,
    batch_update_host_return={"result": True},
    transfer_host_to_faultmodule_return={"result": True},
    transfer_host_module_returns=[{"result": True}],
)

SUCCESS_CASE_COPY_ATTRS = ComponentTestCase(
    name="success case: copy attributes and replace fault machine",
    inputs=COMMON_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=SUCCESS_CLIENT.api.search_object_attribute,
            calls=[
                Call(
                    {"bk_obj_id": "host"},
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
        CallAssertion(
            func=SUCCESS_CLIENT.api.batch_update_host,
            calls=[
                Call(
                    {
                        "bk_obj_id": "host",
                        "update": [{"properties": {"bk_os_type": "linux"}, "bk_host_id": 102}],
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
        CallAssertion(
            func=SUCCESS_CLIENT.api.transfer_host_to_faultmodule,
            calls=[
                Call(
                    {"bk_biz_id": 2, "bk_host_id": [101]},
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
        CallAssertion(
            func=SUCCESS_CLIENT.api.transfer_host_module,
            calls=[
                Call(
                    {
                        "bk_biz_id": 2,
                        "bk_host_id": [102],
                        "bk_module_id": [201, 202],
                        "is_increment": True,
                    },
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SUCCESS_CLIENT),
        Patcher(
            target=SERVICE_GET_HOST_TOPO,
            side_effect=[build_host_topo("10.0.0.1", 101, [201, 202]), build_host_topo("10.0.0.2", 102, [301])],
        ),
    ],
)


# 失败用例：查询可编辑属性失败
SEARCH_ATTR_FAIL_CLIENT = MockClient(search_object_attribute_return={"result": False, "message": "err"})
SEARCH_ATTR_FAIL_CASE = ComponentTestCase(
    name="fail case: search editable attributes failed",
    inputs=COMMON_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "search_attr_failed"}),
    schedule_assertion=None,
    execute_call_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEARCH_ATTR_FAIL_CLIENT),
        Patcher(target=CC_HANDLE_API_ERROR, return_value="search_attr_failed"),
    ],
)


# 失败用例：查询到故障机为空或不唯一
FAULT_HOST_NOT_FOUND_CLIENT = MockClient(search_object_attribute_return=SEARCH_OBJECT_ATTRIBUTE_OK)
FAULT_HOST_NOT_FOUND_CASE = ComponentTestCase(
    name="fail case: fault host not found",
    inputs=COMMON_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "无法查询到 10.0.0.1 机器信息，请确认该机器是否在当前业务下"}),
    schedule_assertion=None,
    execute_call_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=FAULT_HOST_NOT_FOUND_CLIENT),
        Patcher(target=SERVICE_GET_HOST_TOPO, side_effect=[[], build_host_topo("10.0.0.2", 102, [301])]),
    ],
)


# 失败用例：查询到替换机为空或不唯一
NEW_HOST_NOT_FOUND_CLIENT = MockClient(search_object_attribute_return=SEARCH_OBJECT_ATTRIBUTE_OK)
NEW_HOST_NOT_FOUND_CASE = ComponentTestCase(
    name="fail case: new host not found",
    inputs=COMMON_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "无法查询到 10.0.0.2 机器信息，请确认该机器是否在当前业务下"}),
    schedule_assertion=None,
    execute_call_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=NEW_HOST_NOT_FOUND_CLIENT),
        Patcher(target=SERVICE_GET_HOST_TOPO, side_effect=[build_host_topo("10.0.0.1", 101, [201, 202]), []]),
    ],
)


# 失败用例：批量更新替换机属性失败
UPDATE_FAIL_CLIENT = MockClient(
    search_object_attribute_return=SEARCH_OBJECT_ATTRIBUTE_OK,
    batch_update_host_return={"result": False, "message": "err"},
)
BATCH_UPDATE_FAIL_CASE = ComponentTestCase(
    name="fail case: batch update host attributes failed",
    inputs=COMMON_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "update_failed"}),
    schedule_assertion=None,
    execute_call_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=UPDATE_FAIL_CLIENT),
        Patcher(
            target=SERVICE_GET_HOST_TOPO,
            side_effect=[build_host_topo("10.0.0.1", 101, [201, 202]), build_host_topo("10.0.0.2", 102, [301])],
        ),
        Patcher(target=CC_HANDLE_API_ERROR, return_value="update_failed"),
    ],
)


# 失败用例：转移至故障机模块失败
TRANSFER_FAULT_FAIL_CLIENT = MockClient(
    search_object_attribute_return=SEARCH_OBJECT_ATTRIBUTE_OK,
    batch_update_host_return={"result": True},
    transfer_host_to_faultmodule_return={"result": False, "message": "err"},
)
TRANSFER_TO_FAULT_FAIL_CASE = ComponentTestCase(
    name="fail case: transfer to fault module failed",
    inputs=COMMON_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "transfer_fault_failed"}),
    schedule_assertion=None,
    execute_call_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=TRANSFER_FAULT_FAIL_CLIENT),
        Patcher(
            target=SERVICE_GET_HOST_TOPO,
            side_effect=[build_host_topo("10.0.0.1", 101, [201, 202]), build_host_topo("10.0.0.2", 102, [301])],
        ),
        Patcher(target=CC_HANDLE_API_ERROR, return_value="transfer_fault_failed"),
    ],
)


# 失败用例：转移模块过程中失败（部分成功）
TRANSFER_MODULE_FAIL_CLIENT = MockClient(
    search_object_attribute_return=SEARCH_OBJECT_ATTRIBUTE_OK,
    batch_update_host_return={"result": True},
    transfer_host_to_faultmodule_return={"result": True},
    transfer_host_module_returns=[{"result": False, "message": "err"}],
)
TRANSFER_MODULE_FAIL_CASE = ComponentTestCase(
    name="fail case: transfer host module failed (partial success)",
    inputs=COMMON_INPUTS,
    parent_data=COMMON_PARENT,
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "transfer_module_failed\n成功替换的机器: "}),
    schedule_assertion=None,
    execute_call_assertion=None,
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=TRANSFER_MODULE_FAIL_CLIENT),
        Patcher(
            target=SERVICE_GET_HOST_TOPO,
            side_effect=[build_host_topo("10.0.0.1", 101, [201, 202]), build_host_topo("10.0.0.2", 102, [301])],
        ),
        Patcher(target=CC_HANDLE_API_ERROR, return_value="transfer_module_failed"),
    ],
)
