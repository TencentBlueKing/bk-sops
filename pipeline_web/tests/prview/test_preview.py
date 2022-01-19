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

import copy

from mock import patch, MagicMock
from django.test import TestCase

from pipeline_web.preview import preview_template_tree, preview_template_tree_with_schemes

MOCK_PIPELINE_TREE = {
    "activities": {
        "node1": {"id": "node1", "type": "ServiceActivity"},
        "node2": {"id": "node2", "type": "ServiceActivity"},
        "node3": {"id": "node3", "type": "ServiceActivity"},
        "node4": {"id": "node4", "type": "ServiceActivity"},
    },
    "constants": {
        "${param1}": {"value": "${parent_param2}"},
        "${param2}": {"value": "constant_value_2"},
    },
}


class MockTemplate(object):
    def __init__(self, pipeline_tree):
        self.pipeline_tree = pipeline_tree

    def get_pipeline_tree_by_version(self, version):
        return self.pipeline_tree

    def get_outputs(self, version):
        return {
            "${_loop}": {
                "name": "循环次数",
                "key": "${_loop}",
                "desc": "",
                "custom_type": "",
                "source_info": {"node2": ["_loop"]},
                "source_tag": "",
                "value": "",
                "show_type": "hide",
                "source_type": "component_outputs",
                "validation": "",
                "index": 1,
                "version": "legacy",
                "plugin_code": "",
            },
            "${_result}": {
                "name": "执行结果",
                "key": "${_result}",
                "desc": "",
                "custom_type": "",
                "source_info": {"node3": ["_result"]},
                "source_tag": "",
                "value": "",
                "show_type": "hide",
                "source_type": "component_outputs",
                "validation": "",
                "index": 2,
                "version": "legacy",
                "plugin_code": "",
            },
            "${_loop1}": {
                "name": "循环次数",
                "key": "${_loop1}",
                "desc": "",
                "custom_type": "",
                "source_info": {"node4": ["${_loop}"]},
                "source_tag": "",
                "value": "",
                "show_type": "hide",
                "source_type": "component_outputs",
                "validation": "",
                "index": 3,
                "version": "f7b1ef05ac43e5934cd59ce8bacfab96",
                "plugin_code": "",
            },
        }


class MockTaskTemplate(object):
    def __init__(self):
        self.objects = MagicMock()
        self.objects.get = MagicMock(return_value=MockTemplate(copy.deepcopy(MOCK_PIPELINE_TREE)))


def mock_preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id=None):
    pipeline_tree["activities"] = {
        k: v for k, v in pipeline_tree["activities"].items() if k not in exclude_task_nodes_id
    }

    pipeline_tree["constants"].pop("${param2}", "")


def mock_get_template_exclude_task_nodes_with_schemes(template_nodes_set, scheme_id_list):
    return ["node2", "node3"]


class MockPipelineTemplateWebPreviewer(object):
    def __init__(self):
        self.get_template_exclude_task_nodes_with_schemes = MagicMock(
            side_effect=mock_get_template_exclude_task_nodes_with_schemes
        )
        self.preview_pipeline_tree_exclude_task_nodes = MagicMock(
            side_effect=mock_preview_pipeline_tree_exclude_task_nodes
        )


MockTaskTemplate1 = MockTaskTemplate()
MockTaskTemplate2 = MockTaskTemplate()

MockPipelineTemplateWebPreviewer1 = MockPipelineTemplateWebPreviewer()
MockPipelineTemplateWebPreviewer2 = MockPipelineTemplateWebPreviewer()


class PipelineTemplateWebPreviewerTestCase(TestCase):
    @patch("pipeline_web.preview.TaskTemplate", MockTaskTemplate1)
    @patch("pipeline_web.preview.PipelineTemplateWebPreviewer", MockPipelineTemplateWebPreviewer1)
    def test_preview_template_tree(self):
        data = preview_template_tree(1, "project", 2, "v1", ["node1", "node4"])

        MockTaskTemplate1.objects.get.assert_called_once_with(pk=2, is_deleted=False, project_id=1)

        MockPipelineTemplateWebPreviewer1.preview_pipeline_tree_exclude_task_nodes.assert_called()

        self.assertEqual(
            data,
            {
                "pipeline_tree": {
                    "activities": {
                        "node2": {"id": "node2", "type": "ServiceActivity"},
                        "node3": {"id": "node3", "type": "ServiceActivity"},
                    },
                    "constants": {"${param1}": {"value": "${parent_param2}"}},
                },
                "constants_not_referred": {"${param2}": {"value": "constant_value_2"}},
            },
        )

    @patch("pipeline_web.preview.TaskTemplate", MockTaskTemplate2)
    @patch("pipeline_web.preview.PipelineTemplateWebPreviewer", MockPipelineTemplateWebPreviewer2)
    def test_preview_template_tree_with_schemes(self):
        data = preview_template_tree_with_schemes(1, "project", 2, "v1", [1, 2, 3])

        MockPipelineTemplateWebPreviewer2.get_template_exclude_task_nodes_with_schemes.assert_called_once_with(
            {"node2", "node1", "node3", "node4"}, [1, 2, 3]
        )
        MockPipelineTemplateWebPreviewer1.preview_pipeline_tree_exclude_task_nodes.assert_called()
        MockTaskTemplate2.objects.get.assert_called_once_with(pk=2, is_deleted=False, project_id=1)
        self.assertEqual(
            data,
            {
                "pipeline_tree": {
                    "activities": {
                        "node1": {"id": "node1", "type": "ServiceActivity"},
                        "node4": {"id": "node4", "type": "ServiceActivity"},
                    },
                    "constants": {"${param1}": {"value": "${parent_param2}"}},
                },
                "constants_not_referred": {"${param2}": {"value": "constant_value_2"}},
                "outputs": {
                    "${_loop1}": {
                        "name": "循环次数",
                        "key": "${_loop1}",
                        "desc": "",
                        "custom_type": "",
                        "source_info": {"node4": ["${_loop}"]},
                        "source_tag": "",
                        "value": "",
                        "show_type": "hide",
                        "source_type": "component_outputs",
                        "validation": "",
                        "index": 3,
                        "version": "f7b1ef05ac43e5934cd59ce8bacfab96",
                        "plugin_code": "",
                    }
                },
            },
        )
