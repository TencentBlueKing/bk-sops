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

import copy

from django.test import TestCase

from gcloud.taskflow3.exceptions import InvalidOperationException
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class TaskFlowInstancePreviewPipelineTreeExcludeTaskNodesTestCase(TestCase):
    def test__remove_has_outputs_nodes(self):
        tree = {
            "name": "new20200803092536",
            "activities": {
                "node975d86544088e3a511985240d97b": {
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {"hook": False, "value": "123"},
                            "force_check": {"hook": False, "value": True},
                        },
                        "version": "legacy",
                    },
                    "error_ignorable": False,
                    "id": "node975d86544088e3a511985240d97b",
                    "incoming": ["line20166c8d6d4763d092758e4dd316", "line5a00f8629afc662d5455f773eac4"],
                    "loop": None,
                    "name": "定时",
                    "optional": False,
                    "outgoing": "line8cd7035287bde6be2271ad4e786f",
                    "stage_name": "步骤1",
                    "type": "ServiceActivity",
                    "retryable": True,
                    "skippable": True,
                    "labels": [],
                },
                "node2a9d178048898798e356c4a14383": {
                    "component": {"code": "pause_node", "data": {}, "version": "legacy"},
                    "error_ignorable": False,
                    "id": "node2a9d178048898798e356c4a14383",
                    "incoming": ["line8cd7035287bde6be2271ad4e786f"],
                    "loop": None,
                    "name": "暂停",
                    "optional": False,
                    "outgoing": "line8b8d169ee8c33e1565ffd6d8b8b7",
                    "stage_name": "步骤1",
                    "type": "ServiceActivity",
                    "retryable": True,
                    "skippable": True,
                    "labels": [],
                },
            },
            "end_event": {
                "id": "node962a0756dbf7840505f6e59a96cb",
                "incoming": ["line500f11cc131cbb4a0ba38080e6d3"],
                "name": "",
                "outgoing": "",
                "type": "EmptyEndEvent",
            },
            "flows": {
                "line20166c8d6d4763d092758e4dd316": {
                    "id": "line20166c8d6d4763d092758e4dd316",
                    "is_default": False,
                    "source": "node3387bca7a7b1ee686921dab12ff6",
                    "target": "node975d86544088e3a511985240d97b",
                },
                "line500f11cc131cbb4a0ba38080e6d3": {
                    "id": "line500f11cc131cbb4a0ba38080e6d3",
                    "is_default": False,
                    "source": "nodeec634e9245332b863b0d1760563a",
                    "target": "node962a0756dbf7840505f6e59a96cb",
                },
                "line5a00f8629afc662d5455f773eac4": {
                    "id": "line5a00f8629afc662d5455f773eac4",
                    "is_default": False,
                    "source": "nodeec634e9245332b863b0d1760563a",
                    "target": "node975d86544088e3a511985240d97b",
                },
                "line8cd7035287bde6be2271ad4e786f": {
                    "id": "line8cd7035287bde6be2271ad4e786f",
                    "is_default": False,
                    "source": "node975d86544088e3a511985240d97b",
                    "target": "node2a9d178048898798e356c4a14383",
                },
                "line8b8d169ee8c33e1565ffd6d8b8b7": {
                    "id": "line8b8d169ee8c33e1565ffd6d8b8b7",
                    "is_default": False,
                    "source": "node2a9d178048898798e356c4a14383",
                    "target": "nodeec634e9245332b863b0d1760563a",
                },
            },
            "gateways": {
                "nodeec634e9245332b863b0d1760563a": {
                    "id": "nodeec634e9245332b863b0d1760563a",
                    "incoming": ["line8b8d169ee8c33e1565ffd6d8b8b7"],
                    "name": "",
                    "outgoing": ["line500f11cc131cbb4a0ba38080e6d3", "line5a00f8629afc662d5455f773eac4"],
                    "type": "ExclusiveGateway",
                    "conditions": {
                        "line500f11cc131cbb4a0ba38080e6d3": {
                            "evaluate": "${_result_f2dd} == True",
                            "name": "1 == 1",
                            "tag": "branch_nodeec634e9245332b863b0d1760563a_node962a0756dbf7840505f6e59a96cb",
                        },
                        "line5a00f8629afc662d5455f773eac4": {
                            "evaluate": "${_result_f2dd} == False",
                            "name": "1 == 0",
                            "tag": "branch_nodeec634e9245332b863b0d1760563a_node975d86544088e3a511985240d97b",
                        },
                    },
                }
            },
            "line": [
                {
                    "id": "line20166c8d6d4763d092758e4dd316",
                    "source": {"arrow": "Right", "id": "node3387bca7a7b1ee686921dab12ff6"},
                    "target": {"arrow": "Left", "id": "node975d86544088e3a511985240d97b"},
                },
                {
                    "source": {"id": "nodeec634e9245332b863b0d1760563a", "arrow": "Right"},
                    "target": {"id": "node962a0756dbf7840505f6e59a96cb", "arrow": "Left"},
                    "id": "line500f11cc131cbb4a0ba38080e6d3",
                },
                {
                    "source": {"id": "nodeec634e9245332b863b0d1760563a", "arrow": "Bottom"},
                    "target": {"id": "node975d86544088e3a511985240d97b", "arrow": "Bottom"},
                    "id": "line5a00f8629afc662d5455f773eac4",
                },
                {
                    "source": {"arrow": "Right", "id": "node975d86544088e3a511985240d97b"},
                    "target": {"id": "node2a9d178048898798e356c4a14383", "arrow": "Left"},
                    "id": "line8cd7035287bde6be2271ad4e786f",
                },
                {
                    "source": {"arrow": "Right", "id": "node2a9d178048898798e356c4a14383"},
                    "target": {"id": "nodeec634e9245332b863b0d1760563a", "arrow": "Left"},
                    "id": "line8b8d169ee8c33e1565ffd6d8b8b7",
                },
            ],
            "location": [
                {"id": "node3387bca7a7b1ee686921dab12ff6", "x": 20, "y": 150, "type": "startpoint"},
                {
                    "id": "node975d86544088e3a511985240d97b",
                    "x": 105,
                    "y": 145,
                    "name": "定时",
                    "stage_name": "步骤1",
                    "type": "tasknode",
                    "mode": "edit",
                    "icon": "",
                    "group": "蓝鲸服务(BK)",
                    "code": "sleep_timer",
                    "skippable": True,
                    "retryable": True,
                    "optional": False,
                    "status": "",
                },
                {"id": "node962a0756dbf7840505f6e59a96cb", "x": 895, "y": 150, "type": "endpoint"},
                {"type": "branchgateway", "y": 155, "x": 650, "mode": "edit", "id": "nodeec634e9245332b863b0d1760563a"},
                {
                    "type": "tasknode",
                    "y": 145,
                    "x": 305,
                    "mode": "edit",
                    "id": "node2a9d178048898798e356c4a14383",
                    "name": "暂停",
                    "stage_name": "步骤1",
                    "icon": "",
                    "group": "蓝鲸服务(BK)",
                    "code": "pause_node",
                    "skippable": True,
                    "retryable": True,
                    "optional": False,
                    "status": "",
                },
            ],
            "outputs": [],
            "start_event": {
                "id": "node3387bca7a7b1ee686921dab12ff6",
                "incoming": "",
                "name": "",
                "outgoing": "line20166c8d6d4763d092758e4dd316",
                "type": "EmptyStartEvent",
            },
            "template_id": "",
            "constants": {
                "${_result_f2dd}": {
                    "name": "执行结果",
                    "key": "${_result_f2dd}",
                    "desc": "",
                    "custom_type": "",
                    "source_info": {"node975d86544088e3a511985240d97b": ["_result"]},
                    "source_tag": "",
                    "value": "",
                    "show_type": "hide",
                    "source_type": "component_outputs",
                    "validation": "",
                    "index": 0,
                    "version": "legacy",
                }
            },
            "projectBaseInfo": {
                "task_categories": [
                    {"value": "OpsTools", "name": "运维工具"},
                    {"value": "MonitorAlarm", "name": "监控告警"},
                    {"value": "ConfManage", "name": "配置管理"},
                    {"value": "DevTools", "name": "开发工具"},
                    {"value": "EnterpriseIT", "name": "企业IT"},
                    {"value": "OfficeApp", "name": "办公应用"},
                    {"value": "Other", "name": "其它"},
                ],
                "flow_type_list": [{"value": "common", "name": "默认任务流程"}, {"value": "common_func", "name": "职能化任务流程"}],
                "notify_group": [
                    {"value": "Maintainers", "text": "运维人员"},
                    {"value": "ProductPm", "text": "产品人员"},
                    {"value": "Developer", "text": "开发人员"},
                    {"value": "Tester", "text": "测试人员"},
                ],
                "notify_type_list": [
                    {"value": "weixin", "name": "微信"},
                    {"value": "sms", "name": "短信"},
                    {"value": "email", "name": "邮件"},
                    {"value": "voice", "name": "语音"},
                ],
            },
            "notify_receivers": {"receiver_group": [], "more_receiver": ""},
            "notify_type": [],
            "time_out": "",
            "category": "",
            "subprocess_info": {"details": [], "subproc_has_update": False},
        }

        # preview success
        TaskFlowInstance.objects.preview_pipeline_tree_exclude_task_nodes(copy.deepcopy(tree), [])

        self.assertRaises(
            InvalidOperationException,
            TaskFlowInstance.objects.preview_pipeline_tree_exclude_task_nodes,
            copy.deepcopy(tree),
            ["node975d86544088e3a511985240d97b"],
        )
