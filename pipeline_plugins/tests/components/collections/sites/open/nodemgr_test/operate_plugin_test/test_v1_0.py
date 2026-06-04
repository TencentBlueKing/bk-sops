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
import env
from django.test import TestCase
from mock import MagicMock
from pipeline.component_framework.test import (
    Call,
    CallAssertion,
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    Patcher,
    ScheduleAssertion,
)

# 兜底注入 env 中的 nodemgr 配置, 保证非 PaaS V3 环境下也能加载组件
WEB_URL = "http://nodemgr.test"
if not getattr(env, "BK_NODEMGR_WEB_URL", None):
    env.BK_NODEMGR_WEB_URL = WEB_URL
else:
    WEB_URL = env.BK_NODEMGR_WEB_URL

from pipeline_plugins.components.collections.sites.open.nodemgr.operate_plugin.v1_0 import (  # noqa: E402
    NodemgrOperatePluginComponent,
)


class NodemgrOperatePluginComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            INSTALL_PLUGIN_SUCCESS_CASE,
            INSTALL_PLUGIN_NO_VALID_HOST_FAIL_CASE,
            INSTALL_PLUGIN_API_FAIL_CASE,
            INSTALL_PLUGIN_NO_WORKFLOW_ID_FAIL_CASE,
            UNINSTALL_PLUGIN_SUCCESS_CASE,
            UNINSTALL_PLUGIN_API_FAIL_CASE,
            UNINSTALL_PLUGIN_PARTIAL_HOST_SUCCESS_CASE,
            UNINSTALL_PLUGIN_NO_WORKFLOW_ID_FAIL_CASE,
            UNSUPPORTED_OPERATION_TYPE_FAIL_CASE,
            SCHEDULE_PLUGIN_FAILED_CASE,
        ]

    def component_cls(self):
        return NodemgrOperatePluginComponent


class MockClient(object):
    def __init__(
        self,
        host_list_return=None,
        plugin_install_return=None,
        plugin_uninstall_return=None,
        plugin_workflow_operation_list_return=None,
    ):
        self.host_list = MagicMock(return_value=host_list_return)
        self.plugin_install = MagicMock(return_value=plugin_install_return)
        self.plugin_uninstall = MagicMock(return_value=plugin_uninstall_return)
        self.plugin_workflow_operation_list = MagicMock(return_value=plugin_workflow_operation_list_return)


GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.nodemgr.base.BKNodemgrClient"
)


# ============================================================
# install plugin success
# ============================================================
INSTALL_PLUGIN_SUCCESS_CLIENT = MockClient(
    host_list_return={
        "code": 0,
        "data": {
            "items": [
                {
                    "bk_host_id": 1001,
                    "info": {
                        "bk_host_id": 1001,
                        "bk_host_innerip_list": ["1.1.1.1"],
                        "bk_host_innerip_v6_list": [],
                    },
                }
            ]
        },
    },
    plugin_install_return={"code": 0, "data": {"workflow_id": "wf-plugin-install-1"}},
    plugin_workflow_operation_list_return={
        "code": 0,
        "data": {
            "operations": [
                {
                    "operation_id": "op-pi-1",
                    "latest_oper_inst_brief_data": {"life_cycle": {"state": "SUCCESS"}},
                }
            ]
        },
    },
)
INSTALL_PLUGIN_SUCCESS_CASE = ComponentTestCase(
    name="nodemgr operate_plugin install success case",
    inputs={
        "nodemgr_biz_id": 2,
        "nodemgr_op_info": {
            "nodemgr_operation_type": "install",
            "nodemgr_batch_install": {
                "bk_networkarea_id": 1,
                "inner_ip": "1.1.1.1",
                "plugin_name": "bkmonitorbeat",
                "plugin_version": "1.0.0",
            },
        },
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "workflow_id": "wf-plugin-install-1",
            "workflow_url": "{}/#/node-manager/history/detail/wf-plugin-install-1?active=plugin".format(WEB_URL),
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        callback_data=None,
        schedule_finished=True,
        outputs={
            "workflow_id": "wf-plugin-install-1",
            "workflow_url": "{}/#/node-manager/history/detail/wf-plugin-install-1?active=plugin".format(WEB_URL),
            "success_count": 1,
            "failed_count": 0,
        },
    ),
    execute_call_assertion=[
        CallAssertion(
            func=INSTALL_PLUGIN_SUCCESS_CLIENT.plugin_install,
            calls=[
                Call(
                    plugins=[
                        {
                            "bk_host_id": 1001,
                            "plugin_name": "bkmonitorbeat",
                            "version": "1.0.0",
                        }
                    ]
                )
            ],
        ),
    ],
    schedule_call_assertion=[
        CallAssertion(
            func=INSTALL_PLUGIN_SUCCESS_CLIENT.plugin_workflow_operation_list,
            calls=[Call("wf-plugin-install-1")],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_PLUGIN_SUCCESS_CLIENT),
    ],
)


# ============================================================
# install plugin fail: 没有有效节点 (host_list 没匹配)
# ============================================================
INSTALL_PLUGIN_NO_VALID_HOST_CLIENT = MockClient(
    host_list_return={"code": 0, "data": {"items": []}},
)
INSTALL_PLUGIN_NO_VALID_HOST_FAIL_CASE = ComponentTestCase(
    name="nodemgr operate_plugin install no valid host fail case",
    inputs={
        "nodemgr_biz_id": 2,
        "nodemgr_op_info": {
            "nodemgr_operation_type": "install",
            "nodemgr_batch_install": {
                "bk_networkarea_id": 1,
                "inner_ip": "2.2.2.2",
                "plugin_name": "bkmonitorbeat",
                "plugin_version": "1.0.0",
            },
        },
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={"ex_data": "没有可安装插件的有效节点"},
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(func=INSTALL_PLUGIN_NO_VALID_HOST_CLIENT.plugin_install, calls=[]),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_PLUGIN_NO_VALID_HOST_CLIENT),
    ],
)


# ============================================================
# install plugin fail: api 返回非零
# ============================================================
INSTALL_PLUGIN_API_FAIL_CLIENT = MockClient(
    host_list_return={
        "code": 0,
        "data": {
            "items": [
                {
                    "bk_host_id": 3003,
                    "info": {
                        "bk_host_id": 3003,
                        "bk_host_innerip_list": ["3.3.3.3"],
                        "bk_host_innerip_v6_list": [],
                    },
                }
            ]
        },
    },
    plugin_install_return={"code": 1, "message": "plugin install fail"},
)
INSTALL_PLUGIN_API_FAIL_CASE = ComponentTestCase(
    name="nodemgr operate_plugin install api fail case",
    inputs={
        "nodemgr_biz_id": 2,
        "nodemgr_op_info": {
            "nodemgr_operation_type": "install",
            "nodemgr_batch_install": {
                "bk_networkarea_id": 1,
                "inner_ip": "3.3.3.3",
                "plugin_name": "bkmonitorbeat",
                "plugin_version": "1.0.0",
            },
        },
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={"ex_data": "[节点管理器]操作失败: plugin install fail"},
    ),
    schedule_assertion=None,
    execute_call_assertion=[],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_PLUGIN_API_FAIL_CLIENT),
    ],
)


# ============================================================
# uninstall plugin success
# ============================================================
UNINSTALL_PLUGIN_SUCCESS_CLIENT = MockClient(
    host_list_return={
        "code": 0,
        "data": {
            "items": [
                {
                    "bk_host_id": 4004,
                    "info": {
                        "bk_host_id": 4004,
                        "bk_host_innerip_list": ["4.4.4.4"],
                        "bk_host_innerip_v6_list": [],
                    },
                }
            ]
        },
    },
    plugin_uninstall_return={"code": 0, "data": {"workflow_id": "wf-plugin-uninstall-1"}},
    plugin_workflow_operation_list_return={
        "code": 0,
        "data": {
            "operations": [
                {
                    "operation_id": "op-pu-1",
                    "latest_oper_inst_brief_data": {"life_cycle": "SUCCEEDED"},
                }
            ]
        },
    },
)
UNINSTALL_PLUGIN_SUCCESS_CASE = ComponentTestCase(
    name="nodemgr operate_plugin uninstall success case",
    inputs={
        "nodemgr_biz_id": 2,
        "nodemgr_op_info": {
            "nodemgr_operation_type": "uninstall",
            "nodemgr_batch_uninstall": {
                "bk_networkarea_id": 1,
                "inner_ip": "4.4.4.4",
                "plugin_name": "bkmonitorbeat",
            },
        },
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "workflow_id": "wf-plugin-uninstall-1",
            "workflow_url": "{}/#/node-manager/history/detail/wf-plugin-uninstall-1?active=plugin".format(WEB_URL),
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        callback_data=None,
        schedule_finished=True,
        outputs={
            "workflow_id": "wf-plugin-uninstall-1",
            "workflow_url": "{}/#/node-manager/history/detail/wf-plugin-uninstall-1?active=plugin".format(WEB_URL),
            "success_count": 1,
            "failed_count": 0,
        },
    ),
    execute_call_assertion=[
        CallAssertion(
            func=UNINSTALL_PLUGIN_SUCCESS_CLIENT.plugin_uninstall,
            calls=[
                Call(
                    plugins=[
                        {
                            "bk_host_id": 4004,
                            "plugin_name": "bkmonitorbeat",
                        }
                    ]
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=UNINSTALL_PLUGIN_SUCCESS_CLIENT),
    ],
)


# ============================================================
# uninstall plugin api fail
# ============================================================
UNINSTALL_PLUGIN_API_FAIL_CLIENT = MockClient(
    host_list_return={
        "code": 0,
        "data": {
            "items": [
                {
                    "bk_host_id": 5005,
                    "info": {
                        "bk_host_id": 5005,
                        "bk_host_innerip_list": ["5.5.5.5"],
                        "bk_host_innerip_v6_list": [],
                    },
                }
            ]
        },
    },
    plugin_uninstall_return={"code": 1, "message": "plugin uninstall fail"},
)
UNINSTALL_PLUGIN_API_FAIL_CASE = ComponentTestCase(
    name="nodemgr operate_plugin uninstall api fail case",
    inputs={
        "nodemgr_biz_id": 2,
        "nodemgr_op_info": {
            "nodemgr_operation_type": "uninstall",
            "nodemgr_batch_uninstall": {
                "bk_networkarea_id": 1,
                "inner_ip": "5.5.5.5",
                "plugin_name": "bkmonitorbeat",
            },
        },
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={"ex_data": "[节点管理器]操作失败: plugin uninstall fail"},
    ),
    schedule_assertion=None,
    execute_call_assertion=[],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=UNINSTALL_PLUGIN_API_FAIL_CLIENT),
    ],
)


# ============================================================
# unsupported operation type
# ============================================================
UNSUPPORTED_OP_CLIENT = MockClient()
UNSUPPORTED_OPERATION_TYPE_FAIL_CASE = ComponentTestCase(
    name="nodemgr operate_plugin unsupported operation_type fail case",
    inputs={
        "nodemgr_biz_id": 2,
        "nodemgr_op_info": {"nodemgr_operation_type": "magic"},
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={"ex_data": "不支持的操作类型: magic"},
    ),
    schedule_assertion=None,
    execute_call_assertion=[],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=UNSUPPORTED_OP_CLIENT),
    ],
)


# ============================================================
# schedule fail: workflow 失败
# ============================================================
SCHEDULE_FAIL_CLIENT = MockClient(
    host_list_return={
        "code": 0,
        "data": {
            "items": [
                {
                    "bk_host_id": 6006,
                    "info": {
                        "bk_host_id": 6006,
                        "bk_host_innerip_list": ["6.6.6.6"],
                        "bk_host_innerip_v6_list": [],
                    },
                }
            ]
        },
    },
    plugin_install_return={"code": 0, "data": {"workflow_id": "wf-plugin-fail-1"}},
    plugin_workflow_operation_list_return={
        "code": 0,
        "data": {
            "operations": [
                {
                    "operation_id": "op-pf-1",
                    "latest_oper_inst_brief_data": {"life_cycle": {"state": "FAILED"}},
                }
            ]
        },
    },
)
SCHEDULE_PLUGIN_FAILED_CASE = ComponentTestCase(
    name="nodemgr operate_plugin schedule workflow failed case",
    inputs={
        "nodemgr_biz_id": 2,
        "nodemgr_op_info": {
            "nodemgr_operation_type": "install",
            "nodemgr_batch_install": {
                "bk_networkarea_id": 1,
                "inner_ip": "6.6.6.6",
                "plugin_name": "bkmonitorbeat",
                "plugin_version": "1.0.0",
            },
        },
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "workflow_id": "wf-plugin-fail-1",
            "workflow_url": "{}/#/node-manager/history/detail/wf-plugin-fail-1?active=plugin".format(WEB_URL),
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        callback_data=None,
        schedule_finished=True,
        outputs={
            "workflow_id": "wf-plugin-fail-1",
            "workflow_url": "{}/#/node-manager/history/detail/wf-plugin-fail-1?active=plugin".format(WEB_URL),
            "success_count": 0,
            "failed_count": 1,
            "ex_data": "Workflow 执行失败: Operation op-pf-1 failed",
        },
    ),
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SCHEDULE_FAIL_CLIENT),
    ],
)


# ============================================================
# install plugin fail: 缺少 workflow_id
# ============================================================
INSTALL_PLUGIN_NO_WF_CLIENT = MockClient(
    host_list_return={
        "code": 0,
        "data": {
            "items": [
                {
                    "bk_host_id": 7007,
                    "info": {
                        "bk_host_id": 7007,
                        "bk_host_innerip_list": ["7.7.7.7"],
                        "bk_host_innerip_v6_list": [],
                    },
                }
            ]
        },
    },
    plugin_install_return={"code": 0, "data": {}},
)
INSTALL_PLUGIN_NO_WORKFLOW_ID_FAIL_CASE = ComponentTestCase(
    name="install plugin missing workflow_id fail case",
    inputs={
        "nodemgr_biz_id": 2,
        "nodemgr_op_info": {
            "nodemgr_operation_type": "install",
            "nodemgr_batch_install": {
                "bk_networkarea_id": 1,
                "inner_ip": "7.7.7.7",
                "plugin_name": "bkmonitorbeat",
                "plugin_version": "1.0.0",
            },
        },
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={"ex_data": "未获取到 workflow_id"},
    ),
    schedule_assertion=None,
    execute_call_assertion=[],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=INSTALL_PLUGIN_NO_WF_CLIENT),
    ],
)


# ============================================================
# uninstall plugin success: 部分 host 在 fetched_hosts 中找不到, 跳过, 其它正常处理
# ============================================================
UNINSTALL_PLUGIN_PARTIAL_CLIENT = MockClient(
    host_list_return={
        "code": 0,
        "data": {
            "items": [
                {
                    "bk_host_id": 8008,
                    "info": {
                        "bk_host_id": 8008,
                        "bk_host_innerip_list": ["8.8.8.8"],
                        "bk_host_innerip_v6_list": [],
                    },
                }
            ]
        },
    },
    plugin_uninstall_return={"code": 0, "data": {"workflow_id": "wf-partial-1"}},
    plugin_workflow_operation_list_return={
        "code": 0,
        "data": {
            "operations": [
                {
                    "operation_id": "op-partial-1",
                    "latest_oper_inst_brief_data": {"life_cycle": "SUCCESS"},
                }
            ]
        },
    },
)
UNINSTALL_PLUGIN_PARTIAL_HOST_SUCCESS_CASE = ComponentTestCase(
    name="uninstall plugin partial host success case",
    inputs={
        "nodemgr_biz_id": 2,
        "nodemgr_op_info": {
            "nodemgr_operation_type": "uninstall",
            "nodemgr_batch_uninstall": {
                "bk_networkarea_id": 1,
                # 一个匹配, 一个匹配不上
                "inner_ip": "8.8.8.8\n7.7.7.7",
                "plugin_name": "bkmonitorbeat",
            },
        },
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "workflow_id": "wf-partial-1",
            "workflow_url": "{}/#/node-manager/history/detail/wf-partial-1?active=plugin".format(WEB_URL),
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=True,
        callback_data=None,
        schedule_finished=True,
        outputs={
            "workflow_id": "wf-partial-1",
            "workflow_url": "{}/#/node-manager/history/detail/wf-partial-1?active=plugin".format(WEB_URL),
            "success_count": 1,
            "failed_count": 0,
        },
    ),
    execute_call_assertion=[
        CallAssertion(
            func=UNINSTALL_PLUGIN_PARTIAL_CLIENT.plugin_uninstall,
            calls=[
                Call(
                    plugins=[
                        {"bk_host_id": 8008, "plugin_name": "bkmonitorbeat"},
                    ]
                )
            ],
        ),
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=UNINSTALL_PLUGIN_PARTIAL_CLIENT),
    ],
)


# ============================================================
# uninstall plugin fail: 缺少 workflow_id
# ============================================================
UNINSTALL_PLUGIN_NO_WF_CLIENT = MockClient(
    host_list_return={
        "code": 0,
        "data": {
            "items": [
                {
                    "bk_host_id": 9009,
                    "info": {
                        "bk_host_id": 9009,
                        "bk_host_innerip_list": ["9.9.9.9"],
                        "bk_host_innerip_v6_list": [],
                    },
                }
            ]
        },
    },
    plugin_uninstall_return={"code": 0, "data": {}},
)
UNINSTALL_PLUGIN_NO_WORKFLOW_ID_FAIL_CASE = ComponentTestCase(
    name="uninstall plugin missing workflow_id fail case",
    inputs={
        "nodemgr_biz_id": 2,
        "nodemgr_op_info": {
            "nodemgr_operation_type": "uninstall",
            "nodemgr_batch_uninstall": {
                "bk_networkarea_id": 1,
                "inner_ip": "9.9.9.9",
                "plugin_name": "bkmonitorbeat",
            },
        },
    },
    parent_data={"executor": "tester"},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={"ex_data": "未获取到 workflow_id"},
    ),
    schedule_assertion=None,
    execute_call_assertion=[],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=UNINSTALL_PLUGIN_NO_WF_CLIENT),
    ],
)
