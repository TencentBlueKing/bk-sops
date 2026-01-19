# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components import http as http_module


class HttpUtilsTestCase(TestCase):
    def setUp(self):
        self.url = "http://example.com/api"
        self.params = {"k": "v"}
        self.logger = MagicMock()

    @patch("pipeline_plugins.components.http.requests.Session")
    def test_get_success_returns_true_and_json(self, mock_session_cls):
        resp = MagicMock()
        resp.ok = True
        resp.status_code = 200
        resp.json = MagicMock(return_value={"result": True, "data": 1})
        session = MagicMock()
        session.get = MagicMock(return_value=resp)
        mock_session_cls.return_value = session

        success, data = http_module.get(self.url, self.params, self.logger)

        self.assertTrue(success)
        self.assertEqual(data, resp.json())
        session.get.assert_called_once_with(self.url, params=self.params)
        self.assertEqual(session.headers.get("Content-Type"), "application/json")

    @patch("pipeline_plugins.components.http.requests.Session")
    def test_post_success_with_headers_merges_content_type(self, mock_session_cls):
        headers = {"X-Token": "t"}
        resp = MagicMock()
        resp.ok = True
        resp.status_code = 200
        resp.json = MagicMock(return_value={"result": True, "data": 2})
        session = MagicMock()
        session.post = MagicMock(return_value=resp)
        mock_session_cls.return_value = session

        success, data = http_module.post(self.url, self.params, self.logger, headers=headers)

        self.assertTrue(success)
        self.assertEqual(data, resp.json())
        session.post.assert_called_once()
        called_args, called_kwargs = session.post.call_args
        self.assertEqual(called_args[0], self.url)
        self.assertEqual(called_kwargs.get("data"), http_module.json.dumps(self.params))
        self.assertEqual(session.headers.get("Content-Type"), "application/json")
        self.assertEqual(session.headers.get("X-Token"), "t")
        self.assertEqual(headers.get("Content-Type"), "application/json")

    @patch("pipeline_plugins.components.http.requests.Session")
    def test_request_exception_returns_false_and_logs(self, mock_session_cls):
        session = MagicMock()
        session.get = MagicMock(side_effect=Exception("exc_token"))
        mock_session_cls.return_value = session

        success, data = http_module.get(self.url, self.params, self.logger)

        self.assertFalse(success)
        self.assertFalse(data.get("result"))
        self.assertIn("exc_token", data.get("message"))
        self.assertTrue(self.logger.error.called)

    @patch("pipeline_plugins.components.http.requests.Session")
    def test_not_ok_status_code_returns_false(self, mock_session_cls):
        resp = MagicMock()
        resp.ok = False
        resp.status_code = 500
        session = MagicMock()
        session.post = MagicMock(return_value=resp)
        mock_session_cls.return_value = session

        success, data = http_module.http_do("post", self.url, self.params, self.logger)

        self.assertFalse(success)
        self.assertEqual(data.get("result"), False)
        self.assertIn("status code: 500", data.get("message"))

    @patch("pipeline_plugins.components.http.requests.Session")
    def test_json_exception_returns_false_and_logs(self, mock_session_cls):
        resp = MagicMock()
        resp.ok = True
        resp.status_code = 200
        resp.json = MagicMock(side_effect=Exception("bad_json"))
        session = MagicMock()
        session.get = MagicMock(return_value=resp)
        mock_session_cls.return_value = session

        success, data = http_module.get(self.url, self.params, self.logger)

        self.assertFalse(success)
        self.assertFalse(data.get("result"))
        self.assertIn("bad_json", data.get("message"))
        self.assertTrue(self.logger.error.called)
