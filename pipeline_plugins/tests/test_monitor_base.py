# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

from django.test import TestCase

from pipeline_plugins.components.collections.sites.open.monitor.base import MonitorBaseService


class TestMonitorService(MonitorBaseService):
    def execute(self, data, parent_data):
        pass


class MonitorBaseServiceTestCase(TestCase):
    def setUp(self):
        self.service = TestMonitorService()
        self.service.logger = MagicMock()

    def test_build_request_body(self):
        body = self.service.build_request_body("start", 1, "business", "dim", "end")
        self.assertEqual(body["bk_biz_id"], 1)
        self.assertEqual(body["category"], "scope")
        self.assertEqual(body["dimension_config"], "dim")

    @patch("pipeline_plugins.components.collections.sites.open.monitor.base.extract_ip_from_ip_str")
    def test_get_ip_list_ipv6(self, mock_extract):
        mock_extract.return_value = (["v6"], ["v4"], [])

        with patch("pipeline_plugins.components.collections.sites.open.monitor.base.settings") as mock_settings:
            mock_settings.ENABLE_IPV6 = True
            res = self.service.get_ip_list("ip")
            self.assertEqual(res, ["v6", "v4"])

    @patch("pipeline_plugins.components.collections.sites.open.monitor.base.get_ip_by_regex")
    def test_get_ip_list_ipv4(self, mock_get_ip):
        mock_get_ip.return_value = ["v4"]

        with patch("pipeline_plugins.components.collections.sites.open.monitor.base.settings") as mock_settings:
            mock_settings.ENABLE_IPV6 = False
            res = self.service.get_ip_list("ip")
            self.assertEqual(res, ["v4"])

    @patch(
        "pipeline_plugins.components.collections.sites.open.monitor.base."
        "cc_get_host_by_innerip_with_ipv6_across_business"
    )
    @patch("pipeline_plugins.components.collections.sites.open.monitor.base.cc_get_host_by_innerip_with_ipv6")
    def test_get_target_server_ipv6_across_business(self, mock_get_v6, mock_get_across):
        logger = MagicMock()
        data = MagicMock()

        # Success case
        mock_get_across.return_value = (
            [{"bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}],  # host_list
            [],
            [],
            [],
            [],  # not finds
        )
        mock_get_v6.return_value = {"result": True, "data": []}

        res, val = self.service.get_target_server_ipv6_across_business("tenant", "user", 1, "ip", logger, data)
        self.assertTrue(res)
        self.assertEqual(val["ip_list"][0]["ip"], "1.1.1.1")

        # Exception case
        mock_get_across.side_effect = Exception("error")
        res, val = self.service.get_target_server_ipv6_across_business("tenant", "user", 1, "ip", logger, data)
        self.assertFalse(res)

        # Not found case
        mock_get_across.return_value = ([], ["1.1.1.1"], [], [], [])
        mock_get_across.side_effect = None
        mock_get_v6.return_value = {"result": False, "message": "err"}
        res, val = self.service.get_target_server_ipv6_across_business("tenant", "user", 1, "ip", logger, data)
        self.assertFalse(res)

    @patch("pipeline_plugins.components.collections.sites.open.monitor.base.get_biz_ip_from_frontend_hybrid")
    def test_get_target_server_hybrid(self, mock_get_hybrid):
        logger = MagicMock()
        data = MagicMock()

        with patch("pipeline_plugins.components.collections.sites.open.monitor.base.settings") as mock_settings:
            mock_settings.ENABLE_IPV6 = False

            # Success
            mock_get_hybrid.return_value = (True, ["1.1.1.1"])
            res, val = self.service.get_target_server_hybrid("tenant", "user", 1, data, "ip", logger)
            self.assertTrue(res)

            # Fail
            mock_get_hybrid.return_value = (False, [])
            res, val = self.service.get_target_server_hybrid("tenant", "user", 1, data, "ip", logger)
            self.assertFalse(res)

            # IPv6
            mock_settings.ENABLE_IPV6 = True
            with patch.object(self.service, "get_target_server_ipv6_across_business") as mock_v6_method:
                mock_v6_method.return_value = (True, {})
                self.service.get_target_server_hybrid("tenant", "user", 1, data, "ip", logger)
                mock_v6_method.assert_called()

    def test_get_ip_dimension_config(self):
        data = MagicMock()
        with patch.object(self.service, "get_target_server_hybrid") as mock_get:
            mock_get.return_value = (True, {"ip_list": ["ip"]})
            res = self.service.get_ip_dimension_config("tenant", "scope", 1, "user", data)
            self.assertEqual(res["scope_type"], "ip")
            self.assertEqual(res["target"], ["ip"])

    def test_send_request(self):
        client = MagicMock()
        data = MagicMock()

        # Success
        client.api.add_shield.return_value = {"result": True, "data": {"id": 1}, "message": "ok"}
        res = self.service.send_request("tenant", {}, data, client)
        self.assertTrue(res)
        data.set_outputs.assert_any_call("shield_id", 1)

        # Fail
        client.api.add_shield.return_value = {"result": False, "message": "err", "code": 1}
        res = self.service.send_request("tenant", {}, data, client)
        self.assertFalse(res)

    def test_outputs_format(self):
        outputs = self.service.outputs_format()
        self.assertEqual(len(outputs), 2)
