# -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from pipeline_plugins.variables.query.sites.open.select import variable_select_source_data_proxy


class VariablesSelectTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("pipeline_plugins.variables.query.sites.open.select.requests.get")
    def test_variable_select_source_data_proxy_success(self, mock_get):
        request = self.factory.get("/", {"url": "http://example.com/api"})

        mock_response = MagicMock()
        mock_response.json.return_value = [{"text": "t1", "value": "v1"}]
        mock_get.return_value = mock_response

        response = variable_select_source_data_proxy(request)

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]["text"], "t1")

    @patch("pipeline_plugins.variables.query.sites.open.select.requests.get")
    def test_variable_select_source_data_proxy_request_exception(self, mock_get):
        request = self.factory.get("/", {"url": "http://example.com/api"})

        mock_get.side_effect = Exception("Network Error")

        response = variable_select_source_data_proxy(request)

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
        self.assertIn("请求数据异常", content[0]["text"])

    @patch("pipeline_plugins.variables.query.sites.open.select.requests.get")
    def test_variable_select_source_data_proxy_invalid_json(self, mock_get):
        request = self.factory.get("/", {"url": "http://example.com/api"})

        mock_response = MagicMock()
        mock_response.json.side_effect = Exception("Invalid JSON")
        mock_response.content = b"Not JSON"
        mock_response.encoding = "utf-8"
        mock_get.return_value = mock_response

        response = variable_select_source_data_proxy(request)

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
        self.assertIn("返回数据格式错误", content[0]["text"])

    @patch("pipeline_plugins.variables.query.sites.open.select.requests.get")
    def test_variable_select_source_data_proxy_transform_function(self, mock_get):
        request = self.factory.get("/", {"url": "http://example.com/api"})

        mock_response = MagicMock()
        mock_response.json.return_value = {"raw": "data"}
        mock_get.return_value = mock_response

        def transform(data):
            return [{"text": "transformed", "value": data["raw"]}]

        with patch("pipeline_plugins.variables.query.sites.open.select.settings") as mock_settings:
            mock_settings.REMOTE_SOURCE_DATA_TRANSFORM_FUNCTION = transform

            response = variable_select_source_data_proxy(request)

            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertEqual(content[0]["text"], "transformed")
            self.assertEqual(content[0]["value"], "data")

    @patch("pipeline_plugins.variables.query.sites.open.select.requests.get")
    def test_variable_select_source_data_proxy_transform_exception(self, mock_get):
        request = self.factory.get("/", {"url": "http://example.com/api"})

        mock_response = MagicMock()
        mock_response.json.return_value = {"raw": "data"}
        mock_get.return_value = mock_response

        def transform(data):
            raise Exception("Transform Error")

        with patch("pipeline_plugins.variables.query.sites.open.select.settings") as mock_settings:
            mock_settings.REMOTE_SOURCE_DATA_TRANSFORM_FUNCTION = transform

            response = variable_select_source_data_proxy(request)

            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertIn("远程数据源数据转换失败", content[0]["text"])
