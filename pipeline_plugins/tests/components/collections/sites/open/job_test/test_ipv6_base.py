# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.sites.open.job.ipv6_base import GetJobTargetServerMixin


class DummyService(GetJobTargetServerMixin):
    pass


class GetJobTargetServerMixinTest(TestCase):
    def setUp(self):
        self.service = DummyService()
        self.tenant_id = "tenant_id"
        self.executor = "executor"
        self.biz_cc_id = 1
        self.ip_str = "1.1.1.1"
        self.logger = MagicMock()
        self.data = MagicMock()
        self.data.outputs = MagicMock()

    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.cc_get_host_by_innerip_with_ipv6")
    def test_get_target_server_ipv6__success(self, mock_cc_get, mock_settings):
        mock_settings.ENABLE_IPV6 = True
        mock_cc_get.return_value = {"result": True, "data": [{"bk_host_id": 1001}, {"bk_host_id": 1002}]}

        result, data = self.service.get_target_server_ipv6(
            self.tenant_id, self.executor, self.biz_cc_id, self.ip_str, self.logger, self.data
        )

        self.assertTrue(result)
        self.assertEqual(data["host_id_list"], [1001, 1002])
        mock_cc_get.assert_called_once_with(self.tenant_id, self.executor, self.biz_cc_id, self.ip_str)

    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.cc_get_host_by_innerip_with_ipv6")
    def test_get_target_server_ipv6__fail(self, mock_cc_get, mock_settings):
        mock_settings.ENABLE_IPV6 = True
        mock_cc_get.return_value = {"result": False, "message": "error"}

        result, data = self.service.get_target_server_ipv6(
            self.tenant_id, self.executor, self.biz_cc_id, self.ip_str, self.logger, self.data
        )

        self.assertFalse(result)
        self.assertEqual(data, {})
        self.assertIn("ip查询失败", self.data.outputs.ex_data)

    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.settings")
    @patch(
        "pipeline_plugins.components.collections.sites.open.job.ipv6_base."
        "cc_get_host_by_innerip_with_ipv6_across_business"
    )
    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.cc_get_host_by_innerip_with_ipv6")
    def test_get_target_server_ipv6_across_business__success(self, mock_cc_get, mock_cc_across, mock_settings):
        mock_settings.ENABLE_IPV6 = True
        # across returns (host_list, ipv4_not, ipv4_cloud_not, ipv6_not, ipv6_cloud_not)
        mock_cc_across.return_value = ([{"bk_host_id": 1001}], ["1.1.1.2"], [], [], [])
        # fallback to all biz search
        mock_cc_get.return_value = {"result": True, "data": [{"bk_host_id": 1002}]}

        result, data = self.service.get_target_server_ipv6_across_business(
            self.tenant_id, self.executor, self.biz_cc_id, self.ip_str, self.logger, self.data
        )

        self.assertTrue(result)
        self.assertEqual(set(data["host_id_list"]), {1001, 1002})
        mock_cc_across.assert_called_once()
        mock_cc_get.assert_called_once_with(self.tenant_id, self.executor, None, "1.1.1.2", is_biz_set=True)

    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.settings")
    @patch(
        "pipeline_plugins.components.collections.sites.open.job.ipv6_base."
        "cc_get_host_by_innerip_with_ipv6_across_business"
    )
    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.cc_get_host_by_innerip_with_ipv6")
    def test_get_target_server_ipv6_across_business__fail(self, mock_cc_get, mock_cc_across, mock_settings):
        mock_settings.ENABLE_IPV6 = True
        # across returns (host_list, ipv4_not, ipv4_cloud_not, ipv6_not, ipv6_cloud_not)
        mock_cc_across.return_value = ([{"bk_host_id": 1001}], ["1.1.1.2"], [], [], [])
        # fallback to all biz search fails
        mock_cc_get.return_value = {"result": False, "message": "error"}

        result, data = self.service.get_target_server_ipv6_across_business(
            self.tenant_id, self.executor, self.biz_cc_id, self.ip_str, self.logger, self.data
        )

        self.assertFalse(result)
        self.assertIn("ip查询失败", self.data.outputs.ex_data)

    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.settings")
    @patch(
        "pipeline_plugins.components.collections.sites.open.job.ipv6_base."
        "cc_get_host_by_innerip_with_ipv6_across_business"
    )
    def test_get_target_server_ipv6_across_business__exception(self, mock_cc_across, mock_settings):
        mock_settings.ENABLE_IPV6 = True
        mock_cc_across.side_effect = Exception("Boom")

        result, data = self.service.get_target_server_ipv6_across_business(
            self.tenant_id, self.executor, self.biz_cc_id, self.ip_str, self.logger, self.data
        )

        self.assertFalse(result)
        self.assertIn("ip查询失败", self.data.outputs.ex_data)

    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.cc_get_host_by_innerip_with_ipv6")
    def test_get_target_server_biz_set__ipv6(self, mock_cc_get, mock_settings):
        mock_settings.ENABLE_IPV6 = True
        mock_cc_get.return_value = {"result": True, "data": [{"bk_host_id": 1001}]}
        ip_table = [{"ip": "1.1.1.1", "bk_cloud_id": 0}]

        # We need to mock extract_ip_from_ip_str because build_ip_str_from_table uses it
        with patch(
            "pipeline_plugins.components.collections.sites.open.job.ipv6_base.extract_ip_from_ip_str"
        ) as mock_extract:
            # ipv6_list, ipv4_list, host_id_list
            mock_extract.return_value = ([], ["1.1.1.1"], [])

            result, data = self.service.get_target_server_biz_set(self.tenant_id, self.executor, ip_table, self.logger)

            self.assertTrue(result)
            self.assertEqual(data["host_id_list"], [1001])

    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.cc_get_host_by_innerip_with_ipv6")
    def test_get_target_server_biz_set__ipv6_fail(self, mock_cc_get, mock_settings):
        mock_settings.ENABLE_IPV6 = True
        mock_cc_get.return_value = {"result": False, "message": "error"}
        ip_table = [{"ip": "1.1.1.1", "bk_cloud_id": 0}]

        with patch(
            "pipeline_plugins.components.collections.sites.open.job.ipv6_base.extract_ip_from_ip_str"
        ) as mock_extract:
            mock_extract.return_value = ([], ["1.1.1.1"], [])

            result, data = self.service.get_target_server_biz_set(self.tenant_id, self.executor, ip_table, self.logger)

            self.assertFalse(result)

    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.settings")
    def test_get_target_server_biz_set__legacy(self, mock_settings):
        mock_settings.ENABLE_IPV6 = False
        ip_table = [{"ip": "1.1.1.1", "bk_cloud_id": 0}]

        with patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.get_ip_by_regex") as mock_get_ip:
            mock_get_ip.return_value = ["1.1.1.1"]

            result, data = self.service.get_target_server_biz_set(self.tenant_id, self.executor, ip_table, self.logger)

            self.assertTrue(result)
            self.assertEqual(data["ip_list"][0]["ip"], "1.1.1.1")
            self.assertEqual(data["ip_list"][0]["bk_cloud_id"], 0)

    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.get_biz_ip_from_frontend")
    def test_get_target_server__legacy(self, mock_get_biz_ip, mock_settings):
        mock_settings.ENABLE_IPV6 = False
        mock_get_biz_ip.return_value = (True, [{"ip": "1.1.1.1"}])

        result, data = self.service.get_target_server(
            self.tenant_id, self.executor, self.biz_cc_id, self.data, self.ip_str, self.logger
        )

        self.assertTrue(result)
        self.assertEqual(data["ip_list"][0]["ip"], "1.1.1.1")
        mock_get_biz_ip.assert_called_once()

    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.get_biz_ip_from_frontend")
    def test_get_target_server__legacy_fail(self, mock_get_biz_ip, mock_settings):
        mock_settings.ENABLE_IPV6 = False
        mock_get_biz_ip.return_value = (False, [])

        result, data = self.service.get_target_server(
            self.tenant_id, self.executor, self.biz_cc_id, self.data, self.ip_str, self.logger
        )

        self.assertFalse(result)

    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.settings")
    def test_get_target_server__ipv6(self, mock_settings):
        mock_settings.ENABLE_IPV6 = True

        with patch.object(self.service, "get_target_server_ipv6") as mock_ipv6:
            mock_ipv6.return_value = (True, {})
            self.service.get_target_server(
                self.tenant_id, self.executor, self.biz_cc_id, self.data, self.ip_str, self.logger, is_across=False
            )
            mock_ipv6.assert_called_once()

        with patch.object(self.service, "get_target_server_ipv6_across_business") as mock_ipv6_across:
            mock_ipv6_across.return_value = (True, {})
            self.service.get_target_server(
                self.tenant_id, self.executor, self.biz_cc_id, self.data, self.ip_str, self.logger, is_across=True
            )
            mock_ipv6_across.assert_called_once()

    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.get_biz_ip_from_frontend_hybrid")
    def test_get_target_server_hybrid__legacy(self, mock_get_hybrid, mock_settings):
        mock_settings.ENABLE_IPV6 = False
        mock_get_hybrid.return_value = (True, ["1.1.1.1"])

        result, data = self.service.get_target_server_hybrid(
            self.tenant_id, self.executor, self.biz_cc_id, self.data, self.ip_str, self.logger
        )
        self.assertTrue(result)
        self.assertEqual(data["ip_list"], ["1.1.1.1"])

    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.get_biz_ip_from_frontend_hybrid")
    def test_get_target_server_hybrid__legacy_fail(self, mock_get_hybrid, mock_settings):
        mock_settings.ENABLE_IPV6 = False
        mock_get_hybrid.return_value = (False, [])

        result, data = self.service.get_target_server_hybrid(
            self.tenant_id, self.executor, self.biz_cc_id, self.data, self.ip_str, self.logger
        )
        self.assertFalse(result)

    @patch("pipeline_plugins.components.collections.sites.open.job.ipv6_base.settings")
    def test_get_target_server_hybrid__ipv6(self, mock_settings):
        mock_settings.ENABLE_IPV6 = True
        with patch.object(self.service, "get_target_server_ipv6_across_business") as mock_ipv6_across:
            mock_ipv6_across.return_value = (True, {})
            self.service.get_target_server_hybrid(
                self.tenant_id, self.executor, self.biz_cc_id, self.data, self.ip_str, self.logger
            )
            mock_ipv6_across.assert_called_once()
