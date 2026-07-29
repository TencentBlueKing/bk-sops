# -*- coding: utf-8 -*-

import mock
from django.test import SimpleTestCase

from gcloud.contrib.admin.diagnostics.evidence import build_task_evidence


class PipelineInstanceStub(object):
    instance_id = "root-pipeline-1"


class TaskStub(object):
    id = 129568046
    project_id = 1
    engine_ver = 2
    current_flow = "execute_task"
    pipeline_instance = PipelineInstanceStub()


class TaskEvidenceTestCase(SimpleTestCase):
    def test_build_task_evidence_returns_empty_sections_for_missing_task(self):
        task_qs = mock.MagicMock()
        task_qs.select_related.return_value.first.return_value = None

        with mock.patch("gcloud.contrib.admin.diagnostics.evidence.TaskFlowInstance.objects.filter") as filter_mock:
            filter_mock.return_value = task_qs
            evidence = build_task_evidence(task_id=0, node_id="node-1")

        filter_mock.assert_called_once_with(id=0)
        self.assertFalse(evidence["result"])
        self.assertEqual(evidence["message"], "task not found")
        self.assertEqual(evidence["sections"], {})

    def test_build_task_evidence_collects_task_relations_and_callback_records(self):
        task_qs = mock.MagicMock()
        task_qs.select_related.return_value.first.return_value = TaskStub()

        related_ids_qs = mock.MagicMock()
        related_ids_qs.values_list.return_value = [129570155]
        relations_qs = mock.MagicMock()
        relations_qs.values.return_value = [
            {"task_id": 129570155, "parent_task_id": 129568046, "root_task_id": 129568046},
        ]
        callback_qs = mock.MagicMock()
        callback_qs.values.return_value = [
            {"task_id": 129570155, "status": "ready", "extra_info": "{\"task_success\": true}"},
        ]

        with mock.patch("gcloud.contrib.admin.diagnostics.evidence.TaskFlowInstance.objects.filter") as task_filter:
            task_filter.return_value = task_qs
            with mock.patch("gcloud.contrib.admin.diagnostics.evidence.TaskFlowRelation.objects.filter") as rel_filter:
                rel_filter.side_effect = [related_ids_qs, relations_qs]
                with mock.patch(
                    "gcloud.contrib.admin.diagnostics.evidence.TaskCallBackRecord.objects.filter"
                ) as callback_filter:
                    callback_filter.return_value = callback_qs
                    evidence = build_task_evidence(task_id=TaskStub.id, node_id="node-1")

        self.assertTrue(evidence["result"])
        self.assertEqual(evidence["message"], "")
        self.assertEqual(evidence["sections"]["task"]["id"], TaskStub.id)
        self.assertEqual(evidence["sections"]["task"]["root_pipeline_id"], "root-pipeline-1")
        self.assertEqual(evidence["sections"]["relations"], relations_qs.values.return_value)
        self.assertEqual(evidence["sections"]["callback_records"], callback_qs.values.return_value)
        self.assertEqual(evidence["sections"]["node_id"], "node-1")
        callback_filter.assert_called_once_with(task_id__in=[TaskStub.id, 129570155])
