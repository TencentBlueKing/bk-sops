# -*- coding: utf-8 -*-
import json

from django.test import RequestFactory, TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.query.sites.open.monitor import monitor_get_strategy


class MonitorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("pipeline_plugins.components.query.sites.open.monitor.get_client_by_username")
    @patch("pipeline_plugins.components.query.sites.open.monitor.check_and_raise_raw_auth_fail_exception")
    def test_monitor_get_strategy_fail(self, mock_auth, mock_get_client):
        request = self.factory.get("/monitor/")
        request.user = MagicMock(username="user", tenant_id="tenant")

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.search_alarm_strategy.return_value = {"result": False, "message": "error"}

        response = monitor_get_strategy(request, biz_cc_id=1)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse(content["result"])
        self.assertIn("请求策略失败", content["message"])

    @patch("pipeline_plugins.components.query.sites.open.monitor.get_client_by_username")
    def test_monitor_get_strategy_success(self, mock_get_client):
        request = self.factory.get("/monitor/")
        request.user = MagicMock(username="user", tenant_id="tenant")

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.search_alarm_strategy.return_value = {
            "result": True,
            "data": {"strategy_config_list": [{"id": 1, "name": "s1"}]},
        }

        response = monitor_get_strategy(request, biz_cc_id=1)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"], [{"value": 1, "text": "s1"}])
