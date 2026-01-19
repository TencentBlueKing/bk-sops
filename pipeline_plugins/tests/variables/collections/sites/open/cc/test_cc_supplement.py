# -*- coding: utf-8 -*-
import mock
from django.test import TestCase

from pipeline_plugins.variables.collections.sites.open import cc


class CCVariablesSupplementTestCase(TestCase):
    def setUp(self):
        self.project = mock.MagicMock()
        self.project.bk_biz_id = 1
        self.project.from_cmdb = True
        self.pipeline_data = {"executor": "user", "project_id": 1, "tenant_id": "tenant"}

    @mock.patch("pipeline_plugins.variables.collections.sites.open.cc.Project")
    def test_VarIpPickerVariable(self, MockProject):
        MockProject.objects.get.return_value = self.project

        # Test custom method
        value = {"var_ip_method": "custom", "var_ip_custom_value": "1.1.1.1"}
        var = cc.VarIpPickerVariable(value=value, context={}, pipeline_data=self.pipeline_data, name="test")

        with mock.patch("pipeline_plugins.variables.collections.sites.open.cc.cc_get_ips_info_by_str") as mock_get_ips:
            mock_get_ips.return_value = {"ip_result": [{"InnerIP": "1.1.1.1"}]}
            self.assertEqual(var.get_value(), "1.1.1.1")

        # Test tree method exception
        value = {"var_ip_method": "tree", "var_ip_tree": ["invalid_format"]}
        var = cc.VarIpPickerVariable(value=value, context={}, pipeline_data=self.pipeline_data, name="test")

        with mock.patch(
            "pipeline_plugins.variables.collections.sites.open.cc.cc_get_inner_ip_by_module_id"
        ) as mock_get_module:
            with mock.patch(
                "pipeline_plugins.variables.collections.sites.open.cc.cc_get_ips_info_by_str"
            ) as mock_get_ips:
                mock_get_module.return_value = []
                mock_get_ips.return_value = {"ip_result": []}
                # Log warning should be called
                var.get_value()

    @mock.patch("pipeline_plugins.variables.collections.sites.open.cc.Project")
    @mock.patch("pipeline_plugins.variables.collections.sites.open.cc.get_ip_picker_result")
    def test_VarCmdbIpSelector(self, mock_get_result, MockProject):
        MockProject.objects.get.return_value = self.project
        var = cc.VarCmdbIpSelector(value={}, context={}, pipeline_data=self.pipeline_data, name="test")
        var.original_value = mock.MagicMock()
        var.original_value.key = "key"

        # Case 1: Result False
        mock_get_result.return_value = {"result": False, "message": "err"}
        with self.assertRaisesRegex(Exception, "err"):
            var.get_value()

        # Case 2: IPv6
        var.value = {"with_cloud_id": True}
        mock_get_result.return_value = {"result": True, "data": [{"bk_host_innerip": "::1", "bk_cloud_id": 0}]}
        with mock.patch("pipeline_plugins.variables.collections.sites.open.cc.settings.ENABLE_IPV6", True):
            self.assertIn("0:[::1]", var.get_value())

    @mock.patch("pipeline_plugins.variables.collections.sites.open.cc.Project")
    def test_VarCmdbAttributeQuery(self, MockProject):
        MockProject.objects.get.return_value = self.project
        var = cc.VarCmdbAttributeQuery(value="::1", context={}, pipeline_data=self.pipeline_data, name="test")

        # Test _handle_value_with_ipv4_and_ipv6 fail
        with mock.patch("pipeline_plugins.variables.collections.sites.open.cc.settings.ENABLE_IPV6", True):
            with mock.patch(
                "pipeline_plugins.variables.collections.sites.open.cc.cc_get_host_by_innerip_with_ipv6"
            ) as mock_get:
                mock_get.return_value = {"result": False}
                with self.assertRaises(Exception):
                    var.get_value()

                # Test empty host ids
                mock_get.return_value = {"result": True, "data": []}
                var.get_value()  # Should return empty dict

    @mock.patch("pipeline_plugins.variables.collections.sites.open.cc.Project")
    def test_VarCmdbIpFilter(self, MockProject):
        MockProject.objects.get.return_value = self.project
        var = cc.VarCmdbIpFilter(
            value={"origin_ips": "1.1.1.1"}, context={}, pipeline_data=self.pipeline_data, name="test"
        )

        # Test IPv6
        with mock.patch("pipeline_plugins.variables.collections.sites.open.cc.settings.ENABLE_IPV6", True):
            with mock.patch(
                "pipeline_plugins.variables.collections.sites.open.cc.GseAgentStatusIpV6Filter"
            ) as MockFilter:
                MockFilter.return_value.get_match_ip.return_value = [{"ip": "::1", "bk_cloud_id": 0}]
                # Test without cloud
                var.value["ip_cloud"] = False
                self.assertEqual(var.get_value(), "::1")

                # Test with cloud
                var.value["ip_cloud"] = True
                self.assertEqual(var.get_value(), "0:[::1]")
