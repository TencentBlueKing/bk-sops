# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import patch

from pipeline_plugins.base.utils.adapter import cc_format_module_hosts, cc_get_inner_ip_by_module_id


class AdapterTestCase(TestCase):
    @patch("pipeline_plugins.base.utils.adapter.cmdb.get_business_host_topo")
    def test_cc_get_inner_ip_by_module_id(self, mock_get_topo):
        tenant_id = "tenant"
        username = "user"
        biz_cc_id = 1
        module_id_list = [1, 2]
        host_fields = ["bk_host_innerip"]

        mock_get_topo.return_value = [
            {
                "host": {"bk_host_innerip": "1.1.1.1"},
                "module": [{"bk_module_id": 1}],
            },
            {
                "host": {"bk_host_innerip": "2.2.2.2"},
                "module": [{"bk_module_id": 3}],
            },
        ]

        result = cc_get_inner_ip_by_module_id(tenant_id, username, biz_cc_id, module_id_list, host_fields)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["host"]["bk_host_innerip"], "1.1.1.1")

    @patch("pipeline_plugins.base.utils.adapter.cc_get_inner_ip_by_module_id")
    def test_cc_format_module_hosts_tree(self, mock_get_inner_ip):
        tenant_id = "tenant"
        username = "user"
        biz_cc_id = 1
        module_id_list = [1]
        host_fields = ["bk_host_innerip"]

        mock_get_inner_ip.return_value = [
            {
                "host": {"bk_host_innerip": "1.1.1.1"},
                "module": [{"bk_module_id": 1}],
            }
        ]

        result = cc_format_module_hosts(tenant_id, username, biz_cc_id, module_id_list, "tree", host_fields)

        self.assertIn("module_1", result)
        self.assertEqual(result["module_1"][0]["label"], "1.1.1.1")

    @patch("pipeline_plugins.base.utils.adapter.cc_get_inner_ip_by_module_id")
    def test_cc_format_module_hosts_ip(self, mock_get_inner_ip):
        tenant_id = "tenant"
        username = "user"
        biz_cc_id = 1
        module_id_list = [1]
        host_fields = ["bk_host_innerip"]

        mock_data = [{"host": {"bk_host_innerip": "1.1.1.1"}}]
        mock_get_inner_ip.return_value = mock_data

        result = cc_format_module_hosts(tenant_id, username, biz_cc_id, module_id_list, "ip", host_fields)

        self.assertEqual(result, mock_data)
