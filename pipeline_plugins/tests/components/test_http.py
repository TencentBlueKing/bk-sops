# -*- coding: utf-8 -*-
import logging
from unittest import TestCase

import mock

from pipeline_plugins.components import http


class HttpComponentTestCase(TestCase):
    def setUp(self):
        self.logger = logging.getLogger("test")
        self.url = "http://example.com/api"
        self.params = {"key": "value"}
        self.headers = {"Auth": "token"}

    @mock.patch("requests.Session")
    def test_get_success(self, mock_session_cls):
        mock_session = mock_session_cls.return_value
        mock_resp = mock.Mock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"code": 0, "data": "success"}
        mock_session.get.return_value = mock_resp

        result, data = http.get(self.url, self.params, self.logger, self.headers)

        self.assertTrue(result)
        self.assertEqual(data, {"code": 0, "data": "success"})
        mock_session.get.assert_called_with(self.url, params=self.params)
        self.assertEqual(mock_session.headers["Content-Type"], "application/json")
        self.assertEqual(mock_session.headers["Auth"], "token")

    @mock.patch("requests.Session")
    def test_post_success(self, mock_session_cls):
        mock_session = mock_session_cls.return_value
        mock_resp = mock.Mock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"code": 0, "data": "success"}
        mock_session.post.return_value = mock_resp

        result, data = http.post(self.url, self.params, self.logger)

        self.assertTrue(result)
        self.assertEqual(data, {"code": 0, "data": "success"})
        # post calls json.dumps(params)
        mock_session.post.assert_called()
        self.assertEqual(mock_session.headers["Content-Type"], "application/json")

    @mock.patch("requests.Session")
    def test_request_exception(self, mock_session_cls):
        mock_session = mock_session_cls.return_value
        mock_session.get.side_effect = Exception("network error")

        result, data = http.get(self.url, self.params, self.logger)

        self.assertFalse(result)
        self.assertFalse(data["result"])
        self.assertIn("network error", data["message"])

    @mock.patch("requests.Session")
    def test_response_not_ok(self, mock_session_cls):
        mock_session = mock_session_cls.return_value
        mock_resp = mock.Mock()
        mock_resp.ok = False
        mock_resp.status_code = 500
        mock_session.get.return_value = mock_resp

        result, data = http.get(self.url, self.params, self.logger)

        self.assertFalse(result)
        self.assertFalse(data["result"])
        self.assertIn("500", data["message"])

    @mock.patch("requests.Session")
    def test_json_decode_error(self, mock_session_cls):
        mock_session = mock_session_cls.return_value
        mock_resp = mock.Mock()
        mock_resp.ok = True
        mock_resp.json.side_effect = Exception("json error")
        mock_session.get.return_value = mock_resp

        result, data = http.get(self.url, self.params, self.logger)

        self.assertFalse(result)
        self.assertFalse(data["result"])
        self.assertIn("json error", data["message"])
