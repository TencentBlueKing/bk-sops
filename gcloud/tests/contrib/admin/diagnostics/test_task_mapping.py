# -*- coding: utf-8 -*-
from datetime import datetime
from unittest import mock

from django.test import TestCase

from gcloud.contrib.admin.diagnostics import task_mapping


def _fake_task(root_id, task_id, name, proj_id, proj_name, executor, template_id):
    task = mock.MagicMock()
    task.id = task_id
    task.template_id = template_id
    task.pipeline_instance.instance_id = root_id
    task.pipeline_instance.name = name
    task.pipeline_instance.executor = executor
    task.pipeline_instance.create_time = datetime(2026, 7, 23, 10, 0, 0)
    task.project.id = proj_id
    task.project.name = proj_name
    return task


class ResolveTaskSummariesTest(TestCase):
    def test_batch_maps_hits_and_skips_misses(self):
        fake = _fake_task("root-1", 101, "任务A", 7, "业务X", "neo", "55")
        qs = mock.MagicMock()
        qs.select_related.return_value = [fake]
        with mock.patch.object(task_mapping, "TaskFlowInstance") as m_tf, mock.patch.object(
            task_mapping, "settings"
        ) as m_settings:
            m_settings.BK_SOPS_HOST = "https://sops.example.com/"
            m_tf.objects.filter.return_value = qs
            result = task_mapping.resolve_task_summaries(["root-1", "root-miss", ""])

        m_tf.objects.filter.assert_called_once_with(pipeline_instance__instance_id__in=mock.ANY)
        self.assertIn("root-1", result)
        self.assertNotIn("root-miss", result)
        summary = result["root-1"]
        self.assertEqual(summary["task_id"], 101)
        self.assertEqual(summary["task_name"], "任务A")
        self.assertEqual(summary["project_id"], 7)
        self.assertEqual(summary["project_name"], "业务X")
        self.assertEqual(summary["executor"], "neo")
        self.assertEqual(summary["template_id"], "55")
        self.assertEqual(summary["task_url"], "https://sops.example.com/taskflow/execute/7/?instance_id=101")

    def test_empty_input_returns_empty(self):
        self.assertEqual(task_mapping.resolve_task_summaries([]), {})

    def test_query_failure_degrades_to_empty(self):
        with mock.patch.object(task_mapping, "TaskFlowInstance") as m_tf:
            m_tf.objects.filter.side_effect = RuntimeError("db down")
            self.assertEqual(task_mapping.resolve_task_summaries(["root-1"]), {})

    def test_single_summary_uses_batch(self):
        with mock.patch.object(task_mapping, "resolve_task_summaries", return_value={"root-1": {"task_id": 1}}):
            self.assertEqual(task_mapping.resolve_task_summary("root-1"), {"task_id": 1})
            self.assertIsNone(task_mapping.resolve_task_summary("root-x"))


class ResolveNodeNameTest(TestCase):
    def _patch_tree(self, tree):
        pi = mock.MagicMock()
        pi.execution_data = tree
        m = mock.MagicMock()
        m.objects.filter.return_value.first.return_value = pi
        return mock.patch.object(task_mapping, "PipelineInstance", m)

    def test_finds_top_level_activity_name(self):
        tree = {"activities": {"act-1": {"name": "HTTP 请求", "type": "ServiceActivity"}}}
        with self._patch_tree(tree):
            self.assertEqual(task_mapping.resolve_node_name("root-1", "act-1"), "HTTP 请求")

    def test_finds_name_in_subprocess(self):
        tree = {
            "activities": {
                "sub-1": {
                    "name": "子流程",
                    "type": "SubProcess",
                    "pipeline": {"activities": {"act-2": {"name": "内层节点", "type": "ServiceActivity"}}},
                }
            }
        }
        with self._patch_tree(tree):
            self.assertEqual(task_mapping.resolve_node_name("root-1", "act-2"), "内层节点")

    def test_missing_node_returns_empty(self):
        tree = {"activities": {"act-1": {"name": "X", "type": "ServiceActivity"}}}
        with self._patch_tree(tree):
            self.assertEqual(task_mapping.resolve_node_name("root-1", "nope"), "")

    def test_no_instance_returns_empty(self):
        m = mock.MagicMock()
        m.objects.filter.return_value.first.return_value = None
        with mock.patch.object(task_mapping, "PipelineInstance", m):
            self.assertEqual(task_mapping.resolve_node_name("root-x", "act-1"), "")
