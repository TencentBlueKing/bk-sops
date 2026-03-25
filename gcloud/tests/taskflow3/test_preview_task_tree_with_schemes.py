# -*- coding: utf-8 -*-
from unittest import mock

from django.test import TestCase

from gcloud.taskflow3.apis.drf.viewsets.preview_task_tree import PreviewTaskTreeWithSchemesView


class PreviewTaskTreeWithSchemesLastExecutionTest(TestCase):

    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.preview_template_tree_with_schemes")
    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.TaskFlowInstance.objects.filter")
    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.TaskTemplate.objects.get")
    def test_last_execution_id_with_project_id(self, mock_tmpl_get, mock_filter, mock_preview):
        mock_preview.return_value = {"pipeline_tree": {}, "constants_not_referred": {}}
        mock_task = mock.MagicMock()
        mock_task.id = 888
        mock_filter.return_value.order_by.return_value.only.return_value.first.return_value = mock_task

        request = mock.MagicMock()
        request.data = {
            "project_id": 1,
            "template_id": "10",
            "version": "v1",
            "template_source": "project",
            "scheme_id_list": [],
        }

        view = PreviewTaskTreeWithSchemesView()
        view.request = request
        view.format_kwarg = None
        response = view.post(request)

        self.assertTrue(response.data["result"])
        self.assertEqual(response.data["data"]["last_execution_id"], 888)

    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.preview_template_tree_with_schemes")
    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.CommonTemplate.objects.get")
    def test_last_execution_id_none_without_project_id(self, mock_tmpl_get, mock_preview):
        mock_preview.return_value = {"pipeline_tree": {}, "constants_not_referred": {}}

        request = mock.MagicMock()
        request.data = {
            "template_id": "10",
            "version": "v1",
            "template_source": "common",
            "scheme_id_list": [],
        }

        view = PreviewTaskTreeWithSchemesView()
        view.request = request
        view.format_kwarg = None
        response = view.post(request)

        self.assertTrue(response.data["result"])
        self.assertIsNone(response.data["data"]["last_execution_id"])
