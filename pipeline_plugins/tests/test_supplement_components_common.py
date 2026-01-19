# -*- coding: utf-8 -*-
import datetime
from unittest.mock import MagicMock, patch

from django.test import TestCase

from pipeline_plugins.components.collections.common import HttpRequestService
from pipeline_plugins.components.collections.controller import PauseService, SleepTimerService
from pipeline_plugins.components.http import get, post


class ComponentsCommonSupplementTestCase(TestCase):

    # --- common.py ---
    @patch("pipeline_plugins.components.collections.common.requests.request")
    def test_http_request_service(self, mock_request):
        service = HttpRequestService()
        service.logger = MagicMock()
        data = MagicMock()
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None  # Default language to None

        # Mock inputs
        data.get_one_of_inputs.side_effect = lambda k, default=None: {
            "bk_http_request_method": "GET",
            "bk_http_request_url": "http://test.com",
            "bk_http_request_body": "{}",
            "language": "en",
        }.get(k, default)

        # Case 1: Success
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"code": 0}
        mock_request.return_value = mock_resp

        self.assertTrue(service.schedule(data, parent_data))

        # Case 2: POST
        data.get_one_of_inputs.side_effect = lambda k, default=None: {
            "bk_http_request_method": "POST",
            "bk_http_request_url": "http://test.com",
            "bk_http_request_body": "{}",
        }.get(k, default)
        self.assertTrue(service.schedule(data, parent_data))

        # Case 3: Request Exception
        mock_request.side_effect = Exception("err")
        self.assertFalse(service.schedule(data, parent_data))

        # Case 4: Invalid JSON
        mock_request.side_effect = None
        mock_resp.json.side_effect = Exception("invalid json")
        mock_resp.content = b"invalid"
        self.assertFalse(service.schedule(data, parent_data))

        # Case 5: Status code error
        mock_resp.json.side_effect = None
        mock_resp.status_code = 500
        self.assertFalse(service.schedule(data, parent_data))

    # --- controller.py ---
    @patch("pipeline_plugins.components.collections.controller.send_taskflow_message")
    def test_pause_service(self, mock_send):
        service = PauseService()
        data = MagicMock()
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = 1

        # Execute
        self.assertTrue(service.execute(data, parent_data))
        mock_send.delay.assert_called_once()

        # Schedule
        self.assertTrue(service.schedule(data, parent_data, callback_data={}))

    @patch("pipeline_plugins.components.collections.controller.Project")
    def test_sleep_timer_service(self, mock_proj):
        service = SleepTimerService()
        service.logger = MagicMock()
        data = MagicMock()
        parent_data = MagicMock()
        parent_data.inputs.project_id = 1
        parent_data.get_one_of_inputs.return_value = None

        project = MagicMock()
        project.time_zone = "UTC"
        mock_proj.objects.get.return_value = project

        # Case 1: Seconds
        data.get_one_of_inputs.side_effect = lambda k, default=None: {"bk_timing": "10", "force_check": True}.get(
            k, default
        )

        self.assertTrue(service.execute(data, parent_data))

        # Case 2: Date
        future = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        data.get_one_of_inputs.side_effect = lambda k, default=None: {"bk_timing": future, "force_check": True}.get(
            k, default
        )
        self.assertTrue(service.execute(data, parent_data))

        # Case 3: Date in past (force check)
        past = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        data.get_one_of_inputs.side_effect = lambda k, default=None: {"bk_timing": past, "force_check": True}.get(
            k, default
        )
        self.assertFalse(service.execute(data, parent_data))

        # Case 4: Invalid format
        data.get_one_of_inputs.side_effect = lambda k, default=None: {
            "bk_timing": "invalid",
        }.get(k, default)
        self.assertFalse(service.execute(data, parent_data))

        # Schedule
        data.outputs.timing_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=10)
        data.outputs.business_tz = datetime.timezone.utc

        # Not yet
        service.interval = MagicMock()
        self.assertTrue(service.schedule(data, parent_data))

        # Finished
        data.outputs.timing_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=1)
        self.assertTrue(service.schedule(data, parent_data))

    # --- http.py ---
    @patch("pipeline_plugins.components.http.requests.Session")
    def test_http_component(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        logger = MagicMock()

        # GET Success
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"a": 1}
        mock_session.get.return_value = mock_resp

        success, data = get("http://u", {}, logger)
        self.assertTrue(success)
        self.assertEqual(data["a"], 1)

        # POST Success
        mock_session.post.return_value = mock_resp
        success, data = post("http://u", {}, logger, headers={"h": "v"})
        self.assertTrue(success)

        # Request Exception
        mock_session.get.side_effect = Exception("err")
        success, data = get("http://u", {}, logger)
        self.assertFalse(success)

        # Status error
        mock_session.get.side_effect = None
        mock_resp.ok = False
        mock_resp.status_code = 404
        success, data = get("http://u", {}, logger)
        self.assertFalse(success)

        # JSON error
        mock_resp.ok = True
        mock_resp.json.side_effect = Exception("err")
        success, data = get("http://u", {}, logger)
        self.assertFalse(success)
