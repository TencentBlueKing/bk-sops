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

from mock import patch, MagicMock
from django.test import TestCase

from pipeline_web.preview_base import PipelineTemplateWebPreviewer


class MockTemplateScheme(object):
    class MockScheme(object):
        def __init__(self, data):
            self.data = json.dumps(data)

    objects = MagicMock()
    objects.in_bulk = MagicMock(
        return_value={1: MockScheme(["node1", "node3"]), 2: MockScheme(["node1", "node5"]), 3: MockScheme(["node5"])}
    )


class PipelineTemplateWebPreviewerTestCase(TestCase):
    @patch("pipeline_web.preview_base.TemplateScheme", MockTemplateScheme)
    def test_get_template_exclude_task_nodes_with_schemes(self):
        scheme_id_list = [1, 2, 3]
        pipeline_tree = {
            "activities": {
                "node1": {"id": "node1", "type": "ServiceActivity", "optional": True},
                "node2": {"id": "node2", "type": "ServiceActivity", "optional": False},
                "node3": {"id": "node3", "type": "ServiceActivity", "optional": True},
                "node4": {"id": "node4", "type": "ServiceActivity", "optional": True},
            },
            "constants": {
                "${param1}": {"value": "${parent_param2}"},
                "${param2}": {"value": "constant_value_2"},
                "${custom_param2}": {"value": "custom_value_2"},
            },
        }
        exclude_task_nodes = PipelineTemplateWebPreviewer.get_template_exclude_task_nodes_with_schemes(
            pipeline_tree, scheme_id_list
        )
        MockTemplateScheme.objects.in_bulk.assert_called_once_with([1, 2, 3])

        self.assertEqual(set(exclude_task_nodes), {"node4"})

    def test_preview_pipeline_tree_exclude_task_nodes(self):
        exclude_task_nodes_id = ["node9ab869668031c89ee03bd3b4ce66"]
        pipeline_tree = {
            "activities": {
                "node504a6d655782f38ac63347b447ed": {
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {"hook": False, "value": "1"},
                            "force_check": {"hook": False, "value": True},
                        },
                        "version": "legacy",
                    },
                    "error_ignorable": False,
                    "id": "node504a6d655782f38ac63347b447ed",
                    "incoming": ["line6653df851ded6777580dee9b45dc"],
                    "loop": None,
                    "name": "定时",
                    "optional": True,
                    "outgoing": "linee45c9161286c0151a2ff5d80d6a3",
                    "stage_name": "",
                    "type": "ServiceActivity",
                    "retryable": True,
                    "skippable": True,
                    "labels": [],
                },
                "node9ab869668031c89ee03bd3b4ce66": {
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {"hook": False, "value": "2"},
                            "force_check": {"hook": False, "value": True},
                        },
                        "version": "legacy",
                    },
                    "error_ignorable": False,
                    "id": "node9ab869668031c89ee03bd3b4ce66",
                    "incoming": ["linee45c9161286c0151a2ff5d80d6a3"],
                    "loop": None,
                    "name": "定时",
                    "optional": True,
                    "outgoing": "lineed1489f10d79e1d1ee4cee1c5a31",
                    "stage_name": "",
                    "type": "ServiceActivity",
                    "retryable": True,
                    "skippable": True,
                    "labels": [],
                },
                "node1d3e25feb2e73e7ed0db312e45e6": {
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {"hook": False, "value": "3"},
                            "force_check": {"hook": False, "value": True},
                        },
                        "version": "legacy",
                    },
                    "error_ignorable": False,
                    "id": "node1d3e25feb2e73e7ed0db312e45e6",
                    "incoming": ["lineed1489f10d79e1d1ee4cee1c5a31"],
                    "loop": None,
                    "name": "定时",
                    "optional": True,
                    "outgoing": "line6243852bfa890e66e38fda9cd199",
                    "stage_name": "",
                    "type": "ServiceActivity",
                    "retryable": True,
                    "skippable": True,
                    "labels": [],
                },
            },
            "constants": {},
            "end_event": {
                "id": "node7ca397adbecddbb48e307c56410e",
                "incoming": ["line6243852bfa890e66e38fda9cd199"],
                "name": "",
                "outgoing": "",
                "type": "EmptyEndEvent",
                "labels": [],
            },
            "flows": {
                "line6653df851ded6777580dee9b45dc": {
                    "id": "line6653df851ded6777580dee9b45dc",
                    "is_default": False,
                    "source": "nodecc4e4eba2910fbd713360220ec0a",
                    "target": "node504a6d655782f38ac63347b447ed",
                },
                "linee45c9161286c0151a2ff5d80d6a3": {
                    "id": "linee45c9161286c0151a2ff5d80d6a3",
                    "is_default": False,
                    "source": "node504a6d655782f38ac63347b447ed",
                    "target": "node9ab869668031c89ee03bd3b4ce66",
                },
                "lineed1489f10d79e1d1ee4cee1c5a31": {
                    "id": "lineed1489f10d79e1d1ee4cee1c5a31",
                    "is_default": False,
                    "source": "node9ab869668031c89ee03bd3b4ce66",
                    "target": "node1d3e25feb2e73e7ed0db312e45e6",
                },
                "line6243852bfa890e66e38fda9cd199": {
                    "id": "line6243852bfa890e66e38fda9cd199",
                    "is_default": False,
                    "source": "node1d3e25feb2e73e7ed0db312e45e6",
                    "target": "node7ca397adbecddbb48e307c56410e",
                },
            },
            "gateways": {},
            "line": [
                {
                    "id": "line6653df851ded6777580dee9b45dc",
                    "source": {"arrow": "Right", "id": "nodecc4e4eba2910fbd713360220ec0a"},
                    "target": {"arrow": "Left", "id": "node504a6d655782f38ac63347b447ed"},
                },
                {
                    "source": {"id": "node504a6d655782f38ac63347b447ed", "arrow": "Right"},
                    "target": {"id": "node9ab869668031c89ee03bd3b4ce66", "arrow": "Top"},
                    "id": "linee45c9161286c0151a2ff5d80d6a3",
                },
                {
                    "source": {"id": "node9ab869668031c89ee03bd3b4ce66", "arrow": "Right"},
                    "target": {"id": "node1d3e25feb2e73e7ed0db312e45e6", "arrow": "Left"},
                    "id": "lineed1489f10d79e1d1ee4cee1c5a31",
                },
                {
                    "source": {"id": "node1d3e25feb2e73e7ed0db312e45e6", "arrow": "Right"},
                    "target": {"id": "node7ca397adbecddbb48e307c56410e", "arrow": "Bottom"},
                    "id": "line6243852bfa890e66e38fda9cd199",
                },
            ],
            "location": [
                {"id": "nodecc4e4eba2910fbd713360220ec0a", "type": "startpoint", "x": 40, "y": 150},
                {
                    "id": "node504a6d655782f38ac63347b447ed",
                    "type": "tasknode",
                    "name": "定时",
                    "stage_name": "",
                    "x": 240,
                    "y": 140,
                    "group": "蓝鲸服务(BK)",
                    "icon": "",
                },
                {"id": "node7ca397adbecddbb48e307c56410e", "type": "endpoint", "x": 800, "y": 160},
                {
                    "id": "node9ab869668031c89ee03bd3b4ce66",
                    "type": "tasknode",
                    "name": "定时",
                    "stage_name": "",
                    "x": 359,
                    "y": 235,
                    "group": "蓝鲸服务(BK)",
                    "icon": "",
                },
                {
                    "id": "node1d3e25feb2e73e7ed0db312e45e6",
                    "type": "tasknode",
                    "name": "定时",
                    "stage_name": "",
                    "x": 610,
                    "y": 230,
                    "group": "蓝鲸服务(BK)",
                    "icon": "",
                },
            ],
            "outputs": [],
            "start_event": {
                "id": "nodecc4e4eba2910fbd713360220ec0a",
                "incoming": "",
                "name": "",
                "outgoing": "line6653df851ded6777580dee9b45dc",
                "type": "EmptyStartEvent",
                "labels": [],
            },
        }

        PipelineTemplateWebPreviewer.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)

        self.assertEqual(
            pipeline_tree,
            {
                "activities": {
                    "node504a6d655782f38ac63347b447ed": {
                        "component": {
                            "code": "sleep_timer",
                            "data": {
                                "bk_timing": {"hook": False, "value": "1"},
                                "force_check": {"hook": False, "value": True},
                            },
                            "version": "legacy",
                        },
                        "error_ignorable": False,
                        "id": "node504a6d655782f38ac63347b447ed",
                        "incoming": ["line6653df851ded6777580dee9b45dc"],
                        "loop": None,
                        "name": "定时",
                        "optional": True,
                        "outgoing": "linee45c9161286c0151a2ff5d80d6a3",
                        "stage_name": "",
                        "type": "ServiceActivity",
                        "retryable": True,
                        "skippable": True,
                        "labels": [],
                    },
                    "node1d3e25feb2e73e7ed0db312e45e6": {
                        "component": {
                            "code": "sleep_timer",
                            "data": {
                                "bk_timing": {"hook": False, "value": "3"},
                                "force_check": {"hook": False, "value": True},
                            },
                            "version": "legacy",
                        },
                        "error_ignorable": False,
                        "id": "node1d3e25feb2e73e7ed0db312e45e6",
                        "incoming": ["linee45c9161286c0151a2ff5d80d6a3"],
                        "loop": None,
                        "name": "定时",
                        "optional": True,
                        "outgoing": "line6243852bfa890e66e38fda9cd199",
                        "stage_name": "",
                        "type": "ServiceActivity",
                        "retryable": True,
                        "skippable": True,
                        "labels": [],
                    },
                },
                "constants": {},
                "end_event": {
                    "id": "node7ca397adbecddbb48e307c56410e",
                    "incoming": ["line6243852bfa890e66e38fda9cd199"],
                    "name": "",
                    "outgoing": "",
                    "type": "EmptyEndEvent",
                    "labels": [],
                },
                "flows": {
                    "line6653df851ded6777580dee9b45dc": {
                        "id": "line6653df851ded6777580dee9b45dc",
                        "is_default": False,
                        "source": "nodecc4e4eba2910fbd713360220ec0a",
                        "target": "node504a6d655782f38ac63347b447ed",
                    },
                    "linee45c9161286c0151a2ff5d80d6a3": {
                        "id": "linee45c9161286c0151a2ff5d80d6a3",
                        "is_default": False,
                        "source": "node504a6d655782f38ac63347b447ed",
                        "target": "node1d3e25feb2e73e7ed0db312e45e6",
                    },
                    "line6243852bfa890e66e38fda9cd199": {
                        "id": "line6243852bfa890e66e38fda9cd199",
                        "is_default": False,
                        "source": "node1d3e25feb2e73e7ed0db312e45e6",
                        "target": "node7ca397adbecddbb48e307c56410e",
                    },
                },
                "gateways": {},
                "line": [
                    {
                        "id": "line6653df851ded6777580dee9b45dc",
                        "source": {"arrow": "Right", "id": "nodecc4e4eba2910fbd713360220ec0a"},
                        "target": {"arrow": "Left", "id": "node504a6d655782f38ac63347b447ed"},
                    },
                    {
                        "source": {"id": "node504a6d655782f38ac63347b447ed", "arrow": "Right"},
                        "target": {"id": "node1d3e25feb2e73e7ed0db312e45e6", "arrow": "Top"},
                        "id": "linee45c9161286c0151a2ff5d80d6a3",
                    },
                    {
                        "source": {"id": "node1d3e25feb2e73e7ed0db312e45e6", "arrow": "Right"},
                        "target": {"id": "node7ca397adbecddbb48e307c56410e", "arrow": "Bottom"},
                        "id": "line6243852bfa890e66e38fda9cd199",
                    },
                ],
                "location": [
                    {"id": "nodecc4e4eba2910fbd713360220ec0a", "type": "startpoint", "x": 40, "y": 150},
                    {
                        "id": "node504a6d655782f38ac63347b447ed",
                        "type": "tasknode",
                        "name": "定时",
                        "stage_name": "",
                        "x": 240,
                        "y": 140,
                        "group": "蓝鲸服务(BK)",
                        "icon": "",
                    },
                    {"id": "node7ca397adbecddbb48e307c56410e", "type": "endpoint", "x": 800, "y": 160},
                    {
                        "id": "node1d3e25feb2e73e7ed0db312e45e6",
                        "type": "tasknode",
                        "name": "定时",
                        "stage_name": "",
                        "x": 610,
                        "y": 230,
                        "group": "蓝鲸服务(BK)",
                        "icon": "",
                    },
                ],
                "outputs": [],
                "start_event": {
                    "id": "nodecc4e4eba2910fbd713360220ec0a",
                    "incoming": "",
                    "name": "",
                    "outgoing": "line6653df851ded6777580dee9b45dc",
                    "type": "EmptyStartEvent",
                    "labels": [],
                },
            },
        )

    def test_preview_pipeline_tree_with_appoint_task_nodes(self):
        appoint_task_nodes_id = ["node1"]
        pipeline_tree = {
            "activities": {
                "node1": {"id": "node1", "type": "ServiceActivity", "optional": True},
                "node2": {"id": "node2", "type": "ServiceActivity", "optional": False},
                "node3": {"id": "node3", "type": "ServiceActivity", "optional": True},
                "node4": {"id": "node4", "type": "ServiceActivity", "optional": True},
            },
            "constants": {
                "${param1}": {"value": "${parent_param2}"},
                "${param2}": {"value": "constant_value_2"},
                "${custom_param2}": {"value": "custom_value_2"},
            },
        }
        exclude_task_nodes_id = PipelineTemplateWebPreviewer.get_template_exclude_task_nodes_with_appoint_nodes(
            pipeline_tree, appoint_task_nodes_id
        )
        self.assertEqual(set(exclude_task_nodes_id), {"node3", "node4"})
