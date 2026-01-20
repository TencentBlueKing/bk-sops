# -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from pipeline_plugins.components.query.sites.open.file_upload import (
    _check_and_get_file_manager,
    apply_upload_ticket,
    file_upload,
    get_repo_temporary_upload_url,
)


class FileUploadTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("pipeline_plugins.components.query.sites.open.file_upload.EnvironmentVariables.objects.get_var")
    def test_check_and_get_file_manager_no_config(self, mock_get_var):
        mock_get_var.return_value = None
        ok, msg = _check_and_get_file_manager()
        self.assertFalse(ok)
        self.assertIn("File Manager 未配置", msg)

    @patch("pipeline_plugins.components.query.sites.open.file_upload.EnvironmentVariables.objects.get_var")
    @patch("pipeline_plugins.components.query.sites.open.file_upload.ManagerFactory.get_manager")
    def test_check_and_get_file_manager_exception(self, mock_get_manager, mock_get_var):
        mock_get_var.return_value = "type"
        mock_get_manager.side_effect = Exception("error")
        ok, msg = _check_and_get_file_manager()
        self.assertFalse(ok)
        self.assertEqual(msg, "error")

    @patch("pipeline_plugins.components.query.sites.open.file_upload.EnvironmentVariables.objects.get_var")
    @patch("pipeline_plugins.components.query.sites.open.file_upload.ManagerFactory.get_manager")
    def test_check_and_get_file_manager_success(self, mock_get_manager, mock_get_var):
        mock_get_var.return_value = "type"
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        ok, manager = _check_and_get_file_manager()
        self.assertTrue(ok)
        self.assertEqual(manager, mock_manager)

    @patch("pipeline_plugins.components.query.sites.open.file_upload.get_iam_client")
    @patch("pipeline_plugins.components.query.sites.open.file_upload.allow_or_raise_auth_failed")
    @patch("pipeline_plugins.components.query.sites.open.file_upload.UploadTicket.objects.check_ticket")
    @patch("pipeline_plugins.components.query.sites.open.file_upload.res_factory")
    def test_file_upload_ticket_fail(self, mock_res_factory, mock_check_ticket, mock_allow, mock_get_iam):
        request = self.factory.post("/file_upload/")
        request.user = MagicMock()
        request.user.tenant_id = "tenant"
        request.user.username = "user"
        request.META["HTTP_APP_PROJECTID"] = 1

        mock_check_ticket.return_value = (False, "error")
        mock_res_factory.resources_for_project.return_value = []

        response = file_upload(request)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json.loads(response.content)["result"])

    @patch("pipeline_plugins.components.query.sites.open.file_upload.get_iam_client")
    @patch("pipeline_plugins.components.query.sites.open.file_upload.allow_or_raise_auth_failed")
    @patch("pipeline_plugins.components.query.sites.open.file_upload.UploadTicket.objects.check_ticket")
    @patch("pipeline_plugins.components.query.sites.open.file_upload._check_and_get_file_manager")
    @patch("pipeline_plugins.components.query.sites.open.file_upload.res_factory")
    def test_file_upload_manager_fail(
        self, mock_res_factory, mock_get_manager, mock_check_ticket, mock_allow, mock_get_iam
    ):
        request = self.factory.post("/file_upload/")
        request.user = MagicMock()
        request.user.tenant_id = "tenant"
        request.user.username = "user"
        request.META["HTTP_APP_PROJECTID"] = 1

        mock_check_ticket.return_value = (True, None)
        mock_get_manager.return_value = (False, "manager error")
        mock_res_factory.resources_for_project.return_value = []

        response = file_upload(request)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(json.loads(response.content)["result"])

    @patch("pipeline_plugins.components.query.sites.open.file_upload.get_iam_client")
    @patch("pipeline_plugins.components.query.sites.open.file_upload.allow_or_raise_auth_failed")
    @patch("pipeline_plugins.components.query.sites.open.file_upload.UploadTicket.objects.check_ticket")
    @patch("pipeline_plugins.components.query.sites.open.file_upload._check_and_get_file_manager")
    @patch("pipeline_plugins.components.query.sites.open.file_upload.BartenderFactory.get_bartender")
    @patch("pipeline_plugins.components.query.sites.open.file_upload.res_factory")
    def test_file_upload_success(
        self, mock_res_factory, mock_get_bartender, mock_get_manager, mock_check_ticket, mock_allow, mock_get_iam
    ):
        request = self.factory.post("/file_upload/")
        request.user = MagicMock()
        request.user.tenant_id = "tenant"
        request.user.username = "user"
        request.META["HTTP_APP_PROJECTID"] = 1

        mock_check_ticket.return_value = (True, None)
        mock_manager = MagicMock()
        mock_manager.type = "type"
        mock_get_manager.return_value = (True, mock_manager)
        mock_res_factory.resources_for_project.return_value = []

        mock_bartender = MagicMock()
        mock_bartender.process_request.return_value = {"result": True, "tag": "tag", "code": 200}
        mock_get_bartender.return_value = mock_bartender

        response = file_upload(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)["result"])
        mock_bartender.post_handle_upload_process.assert_called_with(data="tag", username="user")

    @patch("pipeline_plugins.components.query.sites.open.file_upload.UploadTicket.objects.apply")
    def test_apply_upload_ticket(self, mock_apply):
        request = self.factory.get("/apply_upload_ticket/")
        request.user = MagicMock()
        request.user.username = "user"

        mock_ticket = MagicMock()
        mock_ticket.code = "123"
        mock_apply.return_value = mock_ticket

        response = apply_upload_ticket(request)
        self.assertTrue(json.loads(response.content)["result"])
        self.assertEqual(json.loads(response.content)["data"]["ticket"], "123")

    def test_get_repo_temporary_upload_url_missing_params(self):
        request = self.factory.get("/url/")
        response = get_repo_temporary_upload_url(request)
        self.assertFalse(json.loads(response.content)["result"])

    @patch("pipeline_plugins.components.query.sites.open.file_upload._check_and_get_file_manager")
    def test_get_repo_temporary_upload_url_manager_fail(self, mock_get_manager):
        request = self.factory.get("/url/", {"bk_biz_id": "1", "name": "name"})
        mock_get_manager.return_value = (False, "error")

        response = get_repo_temporary_upload_url(request)
        self.assertFalse(json.loads(response.content)["result"])

    @patch("pipeline_plugins.components.query.sites.open.file_upload._check_and_get_file_manager")
    def test_get_repo_temporary_upload_url_success(self, mock_get_manager):
        request = self.factory.get("/url/", {"bk_biz_id": "1", "name": "name"})
        mock_manager = MagicMock()
        mock_manager.generate_temporary_url.return_value = {"url": "http://url"}
        mock_get_manager.return_value = (True, mock_manager)

        response = get_repo_temporary_upload_url(request)
        self.assertEqual(json.loads(response.content)["url"], "http://url")
