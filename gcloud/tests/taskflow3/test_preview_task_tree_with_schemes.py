# -*- coding: utf-8 -*-
from unittest import mock

from django.db.models import Value
from django.test import TestCase

from gcloud.taskflow3.apis.drf.viewsets.preview_task_tree import PreviewTaskTreeWithSchemesView


@mock.patch(
    "gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.res_factory.resources_for_flow",
    mock.MagicMock(return_value=[]),
)
@mock.patch(
    "gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.res_factory.resources_for_common_flow",
    mock.MagicMock(return_value=[]),
)
@mock.patch(
    "gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.allow_or_raise_auth_failed",
    mock.MagicMock(return_value=None),
)
@mock.patch(
    "gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.is_flow_creator",
    mock.MagicMock(return_value=False),
)
class PreviewTaskTreeWithSchemesLastExecutionTest(TestCase):
    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.preview_template_tree_with_schemes")
    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.TaskFlowInstance.objects.filter")
    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.TaskTemplate.objects.get")
    def test_last_execution_id_with_project_id(self, mock_tmpl_get, mock_filter, mock_preview):
        mock_preview.return_value = {"pipeline_tree": {}, "constants_not_referred": {}}
        mock_filter.return_value.aggregate.return_value = {"max_id": 888}

        request = mock.MagicMock()
        request.user.tenant_id = "test_tenant"  # 设置租户ID以模拟真实场景
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
        mock_filter.return_value.aggregate.assert_called_once()
        filter_kwargs = mock_filter.call_args[1]
        self.assertIsInstance(filter_kwargs["is_deleted"], Value)
        self.assertIsInstance(filter_kwargs["is_child_taskflow"], Value)
        self.assertEqual(filter_kwargs["is_deleted"].value, 0)
        self.assertEqual(filter_kwargs["is_child_taskflow"].value, 0)

    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.preview_template_tree_with_schemes")
    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.CommonTemplate.objects.tenant_get")
    def test_last_execution_id_none_without_project_id(self, mock_tmpl_tenant_get, mock_preview):
        mock_preview.return_value = {"pipeline_tree": {}, "constants_not_referred": {}}
        mock_tmpl_tenant_get.return_value = mock.MagicMock(extra_info={}, pipeline_tree={})

        request = mock.MagicMock()
        request.user.tenant_id = None  # 无租户上下文时，读取点应统一走 tenant_get，不再回落到 objects.get
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

        # 确认公共流程模板的读取点已统一到 tenant_get，避免后续再被改回 objects.get 而失去租户过滤
        mock_tmpl_tenant_get.assert_called_once()
        args, kwargs = mock_tmpl_tenant_get.call_args
        self.assertIsNone(args[0])
        self.assertEqual(kwargs["pk"], "10")
        self.assertFalse(kwargs["is_deleted"])
