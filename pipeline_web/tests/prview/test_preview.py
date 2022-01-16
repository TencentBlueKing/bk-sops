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


class MockPipelineTemplateWebPreview(object):
    def __init__(self):
        self.get_template_exclude_task_nodes_with_schemes = MagicMock(
            side_effect=mock_get_template_exclude_task_nodes_with_schemes
        )
        self.preview_pipeline_tree_exclude_task_nodes = MagicMock(
            side_effect=mock_preview_pipeline_tree_exclude_task_nodes
        )


MockTaskTemplate1 = MockTaskTemplate()
MockTaskTemplate2 = MockTaskTemplate()

MockPipelineTemplateWebPreview1 = MockPipelineTemplateWebPreview()
MockPipelineTemplateWebPreview2 = MockPipelineTemplateWebPreview()


class PipelineTemplateWebPreviewTestCase(TestCase):
    @patch("pipeline_web.preview.TaskTemplate", MockTaskTemplate1)
    @patch("pipeline_web.preview.PipelineTemplateWebPreview", MockPipelineTemplateWebPreview1)
    def test_preview_template_tree(self):
        data = preview_template_tree(1, "project", 2, "v1", ["node1", "node4"])

        MockTaskTemplate1.objects.get.assert_called_once_with(pk=2, is_deleted=False, project_id=1)

        MockPipelineTemplateWebPreview1.preview_pipeline_tree_exclude_task_nodes.assert_called()

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
    @patch("pipeline_web.preview.PipelineTemplateWebPreview", MockPipelineTemplateWebPreview2)
    def test_preview_template_tree_with_schemes(self):
        data = preview_template_tree_with_schemes(1, "project", 2, "v1", [1, 2, 3])

        MockPipelineTemplateWebPreview2.get_template_exclude_task_nodes_with_schemes.assert_called_once_with(
            {"node2", "node1", "node3", "node4"}, [1, 2, 3]
        )
        MockPipelineTemplateWebPreview1.preview_pipeline_tree_exclude_task_nodes.assert_called()
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
            },
        )
