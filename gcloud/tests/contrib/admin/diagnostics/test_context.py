# -*- coding: utf-8 -*-

import mock
from django.test import SimpleTestCase

from gcloud.contrib.admin.diagnostics.context import get_task_context, resolve_task_diagnostic_context


class PipelineInstanceStub(object):
    instance_id = "root-pipeline-1"


class TaskStub(object):
    id = 129568046
    project_id = 1
    engine_ver = 2
    pipeline_instance = PipelineInstanceStub()
    template_id = "1001"
    template_source = "project"
    current_flow = "execute_task"


class TaskDiagnosticContextTestCase(SimpleTestCase):
    def test_resolve_task_context_returns_root_pipeline_id_and_relations(self):
        relation_rows = [
            {"task_id": 129570155, "parent_task_id": 129568046, "root_task_id": 129568046},
        ]
        relation_qs = mock.MagicMock()
        relation_qs.values.return_value = relation_rows

        with mock.patch("gcloud.contrib.admin.diagnostics.context.TaskFlowRelation.objects.filter") as filter_mock:
            filter_mock.return_value = relation_qs
            context = resolve_task_diagnostic_context(TaskStub())

        filter_mock.assert_called_once_with(root_task_id=TaskStub.id)
        self.assertEqual(context["task_id"], TaskStub.id)
        self.assertEqual(context["project_id"], TaskStub.project_id)
        self.assertEqual(context["engine_ver"], 2)
        self.assertEqual(context["root_pipeline_id"], "root-pipeline-1")
        self.assertEqual(context["template_id"], "1001")
        self.assertEqual(context["template_source"], "project")
        self.assertEqual(context["current_flow"], "execute_task")
        self.assertEqual(context["relations"], relation_rows)

    def test_resolve_task_context_handles_empty_pipeline_instance(self):
        task = TaskStub()
        task.pipeline_instance = None

        with mock.patch("gcloud.contrib.admin.diagnostics.context.TaskFlowRelation.objects.filter") as filter_mock:
            filter_mock.return_value.values.return_value = []
            context = resolve_task_diagnostic_context(task)

        self.assertEqual(context["root_pipeline_id"], "")
        self.assertEqual(context["relations"], [])

    def test_get_task_context_loads_task_with_pipeline_instance(self):
        select_related = mock.MagicMock()
        select_related.get.return_value = TaskStub()

        with mock.patch("gcloud.contrib.admin.diagnostics.context.TaskFlowInstance.objects.select_related") as sr:
            sr.return_value = select_related
            with mock.patch("gcloud.contrib.admin.diagnostics.context.TaskFlowRelation.objects.filter") as filter_mock:
                filter_mock.return_value.values.return_value = []
                context = get_task_context(TaskStub.id)

        sr.assert_called_once_with("pipeline_instance")
        select_related.get.assert_called_once_with(id=TaskStub.id)
        self.assertEqual(context["root_pipeline_id"], "root-pipeline-1")
