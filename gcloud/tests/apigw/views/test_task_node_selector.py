# -*- coding: utf-8 -*-
from types import SimpleNamespace
from unittest import TestCase

from mock import MagicMock, patch
from pipeline.core.constants import PE

from gcloud.apigw.views.task_node_selector import (
    TaskNodeSelectionValidationError,
    resolve_exclude_task_nodes_id,
)


class TaskNodeSelectorTestCase(TestCase):
    def test_resolve_with_template_schemes_id(self):
        template = SimpleNamespace(pipeline_template=SimpleNamespace(id=47))
        pipeline_tree = {PE.activities: {"node1": {}, "node2": {}, "node3": {}}}
        params = {"template_schemes_id": ["47-1", "47-2"]}

        with patch("gcloud.apigw.views.task_node_selector.TemplateScheme") as template_scheme:
            with patch("gcloud.apigw.views.task_node_selector.PipelineTemplateWebPreviewer") as previewer:
                template_scheme.objects.filter.return_value = [
                    SimpleNamespace(id=101, unique_id="47-1"),
                    SimpleNamespace(id=102, unique_id="47-2"),
                ]
                previewer.get_template_exclude_task_nodes_with_schemes = MagicMock(return_value=["node3"])

                result = resolve_exclude_task_nodes_id(template, pipeline_tree, params)

        template_scheme.objects.filter.assert_called_once_with(template_id=47, unique_id__in=["47-1", "47-2"])
        previewer.get_template_exclude_task_nodes_with_schemes.assert_called_once_with(
            pipeline_tree, [101, 102], check_schemes_exist=True
        )
        self.assertEqual(result, ["node3"])

    def test_resolve_with_template_schemes_id_string(self):
        template = SimpleNamespace(pipeline_template=SimpleNamespace(id=47))
        pipeline_tree = {PE.activities: {"node1": {}, "node2": {}, "node3": {}}}
        params = {"template_schemes_id": "47-1"}

        with patch("gcloud.apigw.views.task_node_selector.TemplateScheme") as template_scheme:
            with patch("gcloud.apigw.views.task_node_selector.PipelineTemplateWebPreviewer") as previewer:
                template_scheme.objects.filter.return_value = [SimpleNamespace(id=101, unique_id="47-1")]
                previewer.get_template_exclude_task_nodes_with_schemes = MagicMock(return_value=["node3"])

                result = resolve_exclude_task_nodes_id(template, pipeline_tree, params)

        template_scheme.objects.filter.assert_called_once_with(template_id=47, unique_id__in=["47-1"])
        previewer.get_template_exclude_task_nodes_with_schemes.assert_called_once_with(
            pipeline_tree, [101], check_schemes_exist=True
        )
        self.assertEqual(params["template_schemes_id"], ["47-1"])
        self.assertEqual(result, ["node3"])

    def test_reject_unknown_template_scheme(self):
        template = SimpleNamespace(pipeline_template=SimpleNamespace(id=47))
        pipeline_tree = {PE.activities: {}}
        params = {"template_schemes_id": ["47-1", "47-missing"]}

        with patch("gcloud.apigw.views.task_node_selector.TemplateScheme") as template_scheme:
            template_scheme.objects.filter.return_value = [SimpleNamespace(id=101, unique_id="47-1")]

            with self.assertRaises(TaskNodeSelectionValidationError) as context:
                resolve_exclude_task_nodes_id(template, pipeline_tree, params)

        self.assertIn("47-missing", str(context.exception))

    def test_reject_malformed_template_scheme_items(self):
        template = SimpleNamespace(pipeline_template=SimpleNamespace(id=47))
        pipeline_tree = {PE.activities: {}}
        params = {"template_schemes_id": ["47-1", None]}

        with patch("gcloud.apigw.views.task_node_selector.TemplateScheme") as template_scheme:
            with self.assertRaises(TaskNodeSelectionValidationError) as context:
                resolve_exclude_task_nodes_id(template, pipeline_tree, params)

        self.assertIn("template_schemes_id", str(context.exception))
        template_scheme.objects.filter.assert_not_called()

    def test_reject_duplicate_template_scheme_items(self):
        template = SimpleNamespace(pipeline_template=SimpleNamespace(id=47))
        pipeline_tree = {PE.activities: {}}
        params = {"template_schemes_id": ["47-1", "47-1"]}

        with patch("gcloud.apigw.views.task_node_selector.TemplateScheme") as template_scheme:
            with patch("gcloud.apigw.views.task_node_selector.PipelineTemplateWebPreviewer") as previewer:
                with self.assertRaises(TaskNodeSelectionValidationError) as context:
                    resolve_exclude_task_nodes_id(template, pipeline_tree, params)

        self.assertIn("duplicate template_schemes_id", str(context.exception))
        template_scheme.objects.filter.assert_not_called()
        previewer.get_template_exclude_task_nodes_with_schemes.assert_not_called()

    def test_reject_scheme_and_exclude_nodes_together(self):
        template = SimpleNamespace(pipeline_template=SimpleNamespace(id=47))
        pipeline_tree = {PE.activities: {}}
        params = {"template_schemes_id": ["47-1"], "exclude_task_nodes_id": ["node3"]}

        with self.assertRaises(TaskNodeSelectionValidationError):
            resolve_exclude_task_nodes_id(template, pipeline_tree, params)

    def test_execute_task_nodes_keep_legacy_priority(self):
        template = SimpleNamespace(pipeline_template=SimpleNamespace(id=47))
        pipeline_tree = {PE.activities: {"node1": {}, "node2": {}, "node3": {}}}
        params = {
            "template_schemes_id": [],
            "exclude_task_nodes_id": ["node3"],
            "execute_task_nodes_id": ["node1"],
        }

        result = resolve_exclude_task_nodes_id(template, pipeline_tree, params, support_execute_task_nodes=True)

        self.assertEqual(result, ["node2", "node3"])
