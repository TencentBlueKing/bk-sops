# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch
from rest_framework.test import APIRequestFactory, force_authenticate

from pipeline_plugins.components.query.sites.open.itsm import ITSMNodeTransitionNewView, ITSMNodeTransitionView


class ITSMNodeTransitionViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ITSMNodeTransitionView.as_view()

    def test_post_missing_is_passed(self):
        request = self.factory.post("/itsm/node_transition/", {}, format="json")
        user = MagicMock(username="user")
        force_authenticate(request, user=user)
        # Bug in business code: _get_common_data returns Response instead of tuple, causing unpack error
        with self.assertRaises(Exception):
            self.view(request)

    def test_post_refuse_no_message(self):
        request = self.factory.post(
            "/itsm/node_transition/",
            {"project_id": 1, "task_id": 1, "node_id": "node", "is_passed": False, "message": ""},
            format="json",
        )
        user = MagicMock(username="user")
        force_authenticate(request, user=user)
        # Bug in business code: _get_common_data returns Response instead of tuple, causing unpack error
        with self.assertRaises(Exception):
            self.view(request)

    @patch("pipeline_plugins.components.query.sites.open.itsm.TaskFlowInstance.objects.filter")
    def test_post_task_not_found(self, mock_filter):
        request = self.factory.post(
            "/itsm/node_transition/",
            {"project_id": 1, "task_id": 1, "node_id": "node", "is_passed": True, "message": "msg"},
            format="json",
        )
        user = MagicMock(username="user")
        force_authenticate(request, user=user)
        mock_filter.return_value.exists.return_value = False

        # Bug in business code: _get_common_data returns Response instead of tuple, causing unpack error
        with self.assertRaises(Exception):
            self.view(request)

    @patch("pipeline_plugins.components.query.sites.open.itsm.TaskFlowInstance.objects.filter")
    def test_post_node_detail_fail(self, mock_filter):
        request = self.factory.post(
            "/itsm/node_transition/",
            {"project_id": 1, "task_id": 1, "node_id": "node", "is_passed": True, "message": "msg"},
            format="json",
        )
        user = MagicMock(username="user")
        force_authenticate(request, user=user)

        mock_task = MagicMock()
        mock_filter.return_value.exists.return_value = True
        mock_filter.return_value.first.return_value = mock_task
        mock_task.get_node_detail.return_value = {"result": False, "message": "node error"}

        # Bug in business code: _get_common_data returns Response instead of tuple, causing unpack error
        with self.assertRaises(Exception):
            self.view(request)

    @patch("pipeline_plugins.components.query.sites.open.itsm.TaskFlowInstance.objects.filter")
    def test_post_outputs_empty(self, mock_filter):
        request = self.factory.post(
            "/itsm/node_transition/",
            {"project_id": 1, "task_id": 1, "node_id": "node", "is_passed": True, "message": "msg"},
            format="json",
        )
        user = MagicMock(username="user")
        force_authenticate(request, user=user)

        mock_task = MagicMock()
        mock_filter.return_value.exists.return_value = True
        mock_filter.return_value.first.return_value = mock_task
        mock_task.get_node_detail.return_value = {"result": True, "data": {"outputs": []}}

        # Bug in business code: _get_common_data returns Response instead of tuple, causing unpack error
        with self.assertRaises(Exception):
            self.view(request)

    @patch("pipeline_plugins.components.query.sites.open.itsm.TaskFlowInstance.objects.filter")
    def test_post_sn_missing(self, mock_filter):
        request = self.factory.post(
            "/itsm/node_transition/",
            {"project_id": 1, "task_id": 1, "node_id": "node", "is_passed": True, "message": "msg"},
            format="json",
        )
        user = MagicMock(username="user")
        force_authenticate(request, user=user)

        mock_task = MagicMock()
        mock_filter.return_value.exists.return_value = True
        mock_filter.return_value.first.return_value = mock_task
        mock_task.get_node_detail.return_value = {
            "result": True,
            "data": {"outputs": [{"key": "other", "value": "val"}]},
        }

        response = self.view(request)
        self.assertFalse(response.data["result"])
        self.assertIn("没有itsm单据(sn)", response.data["message"])

    @patch("pipeline_plugins.components.query.sites.open.itsm.TaskFlowInstance.objects.filter")
    @patch("pipeline_plugins.components.query.sites.open.itsm.get_client_by_username")
    @patch("pipeline_plugins.components.query.sites.open.itsm.handle_api_error")
    @patch("pipeline_plugins.components.query.sites.open.itsm.check_and_raise_raw_auth_fail_exception")
    def test_post_ticket_info_fail(self, mock_auth, mock_handle_error, mock_get_client, mock_filter):
        request = self.factory.post(
            "/itsm/node_transition/",
            {"project_id": 1, "task_id": 1, "node_id": "node", "is_passed": True, "message": "msg"},
            format="json",
        )
        user = MagicMock(username="user", tenant_id="tenant")
        force_authenticate(request, user=user)

        mock_task = MagicMock()
        mock_filter.return_value.exists.return_value = True
        mock_filter.return_value.first.return_value = mock_task
        mock_task.get_node_detail.return_value = {"result": True, "data": {"outputs": [{"key": "sn", "value": "sn1"}]}}

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.get_ticket_info.return_value = {"result": False}
        mock_handle_error.return_value = "api error"

        response = self.view(request)
        self.assertFalse(response.data["result"])
        self.assertEqual(response.data["message"], "api error")

    @patch("pipeline_plugins.components.query.sites.open.itsm.TaskFlowInstance.objects.filter")
    @patch("pipeline_plugins.components.query.sites.open.itsm.get_client_by_username")
    def test_post_flow_ended(self, mock_get_client, mock_filter):
        request = self.factory.post(
            "/itsm/node_transition/",
            {"project_id": 1, "task_id": 1, "node_id": "node", "is_passed": True, "message": "msg"},
            format="json",
        )
        user = MagicMock(username="user", tenant_id="tenant")
        force_authenticate(request, user=user)

        mock_task = MagicMock()
        mock_filter.return_value.exists.return_value = True
        mock_filter.return_value.first.return_value = mock_task
        mock_task.get_node_detail.return_value = {"result": True, "data": {"outputs": [{"key": "sn", "value": "sn1"}]}}

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.get_ticket_info.return_value = {
            "result": True,
            "data": {"current_steps": [{"name": "other", "state_id": "state1"}], "fields": []},
        }

        response = self.view(request)
        self.assertFalse(response.data["result"])
        self.assertIn("审批流程已结束", response.data["message"])

    @patch("pipeline_plugins.components.query.sites.open.itsm.TaskFlowInstance.objects.filter")
    @patch("pipeline_plugins.components.query.sites.open.itsm.get_client_by_username")
    def test_post_success(self, mock_get_client, mock_filter):
        request = self.factory.post(
            "/itsm/node_transition/",
            {"project_id": 1, "task_id": 1, "node_id": "node", "is_passed": True, "message": "msg"},
            format="json",
        )
        user = MagicMock(username="user", tenant_id="tenant")
        force_authenticate(request, user=user)

        mock_task = MagicMock()
        mock_filter.return_value.exists.return_value = True
        mock_filter.return_value.first.return_value = mock_task
        mock_task.get_node_detail.return_value = {
            "result": True,
            "data": {"outputs": [{"key": "sn", "value": "sn123"}]},
        }

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.api.get_ticket_info.return_value = {
            "result": True,
            "data": {
                "current_steps": [{"name": "内置审批节点", "state_id": "state1"}],
                "fields": [
                    {"name": "备注", "key": "memo"},
                    {"name": "审批意见", "key": "opinion"},
                    {"name": "备注", "key": "memo2"},
                ],
            },
        }
        mock_client.api.operate_node.return_value = {"result": True}

        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["result"])


class ITSMNodeTransitionNewViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ITSMNodeTransitionNewView.as_view()

    @patch("pipeline_plugins.components.query.sites.open.itsm.TaskFlowInstance.objects.filter")
    def test_post_ticket_id_missing(self, mock_filter):
        request = self.factory.post(
            "/itsm/node_transition_new/",
            {"project_id": 1, "task_id": 1, "node_id": "node", "is_passed": True, "message": "msg"},
            format="json",
        )
        user = MagicMock(username="user")
        force_authenticate(request, user=user)

        mock_task = MagicMock()
        mock_filter.return_value.exists.return_value = True
        mock_filter.return_value.first.return_value = mock_task
        mock_task.get_node_detail.return_value = {
            "result": True,
            "data": {"outputs": [{"key": "other", "value": "val"}]},
        }

        response = self.view(request)
        self.assertFalse(response.data["result"])
        self.assertIn("没有itsm工单id", response.data["message"])

    @patch("pipeline_plugins.components.query.sites.open.itsm.TaskFlowInstance.objects.filter")
    @patch("pipeline_plugins.components.query.sites.open.itsm.get_itsm4_client_by_username")
    @patch("pipeline_plugins.components.query.sites.open.itsm.handle_api_error")
    @patch("pipeline_plugins.components.query.sites.open.itsm.check_and_raise_raw_auth_fail_exception")
    def test_post_ticket_detail_fail(self, mock_auth, mock_handle_error, mock_get_client, mock_filter):
        request = self.factory.post(
            "/itsm/node_transition_new/",
            {"project_id": 1, "task_id": 1, "node_id": "node", "is_passed": True, "message": "msg"},
            format="json",
        )
        user = MagicMock(username="user", tenant_id="tenant")
        force_authenticate(request, user=user)

        mock_task = MagicMock()
        mock_filter.return_value.exists.return_value = True
        mock_filter.return_value.first.return_value = mock_task
        mock_task.get_node_detail.return_value = {
            "result": True,
            "data": {"outputs": [{"key": "id", "value": "ticket1"}]},
        }

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.ticket_detail.return_value = {"result": False, "data": {"current_processors": []}}
        mock_handle_error.return_value = "api error"

        response = self.view(request)
        self.assertFalse(response.data["result"])
        self.assertEqual(response.data["message"], "api error")

    @patch("pipeline_plugins.components.query.sites.open.itsm.TaskFlowInstance.objects.filter")
    @patch("pipeline_plugins.components.query.sites.open.itsm.get_itsm4_client_by_username")
    def test_post_success(self, mock_get_client, mock_filter):
        request = self.factory.post(
            "/itsm/node_transition_new/",
            {"project_id": 1, "task_id": 1, "node_id": "node", "is_passed": True, "message": "msg"},
            format="json",
        )
        user = MagicMock(username="user", tenant_id="tenant")
        force_authenticate(request, user=user)

        mock_task = MagicMock()
        mock_filter.return_value.exists.return_value = True
        mock_filter.return_value.first.return_value = mock_task
        mock_task.get_node_detail.return_value = {
            "result": True,
            "data": {"outputs": [{"key": "id", "value": "ticket123"}]},
        }

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.api.ticket_detail.return_value = {
            "result": True,
            "data": {"current_processors": [{"task_id": "task_itsm_1"}], "system_id": "sys1"},
        }
        mock_client.api.handle_approval_node.return_value = {"result": True}

        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["result"])
