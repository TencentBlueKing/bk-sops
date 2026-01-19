# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.test import TestCase

from pipeline_plugins.components.collections.sites.open.cc.ipv6_utils import (
    cc_get_host_by_innerip_with_ipv6_across_business,
    check_ip_cloud,
    compare_ip_list,
    compare_ip_with_cloud_list,
    compare_ipv6_with_cloud_list,
    format_host_with_ipv6,
    get_ipv4_hosts_with_cloud,
    get_ipv6_hosts,
)
from pipeline_plugins.components.collections.sites.open.nodeman.create_task.v7_0 import NodemanCreateTaskComponent


class ComponentsCollectionsSupplementTestCase(TestCase):

    # --- nodeman/create_task/v7_0.py ---
    def test_nodeman_create_task_v7_0(self):
        self.assertEqual(NodemanCreateTaskComponent.code, "nodeman_create_task")
        self.assertEqual(NodemanCreateTaskComponent.version, "v7.0")

    # --- cc/ipv6_utils.py ---
    def test_compare_ip_list(self):
        # Equal
        res, msg = compare_ip_list([{"ip": "1.1.1.1"}], ["1.1.1.1"], "ip")
        self.assertTrue(res)

        # Less (absent)
        res, msg = compare_ip_list([{"ip": "1.1.1.1"}], ["1.1.1.1", "2.2.2.2"], "ip")
        self.assertFalse(res)
        self.assertIn("ip not found", msg)

        # More (duplicate)
        res, msg = compare_ip_list([{"ip": "1.1.1.1"}, {"ip": "1.1.1.1"}], ["1.1.1.1"], "ip")
        self.assertFalse(res)
        self.assertIn("mutiple same innerip", msg)

    def test_compare_ip_with_cloud_list(self):
        # Equal
        res, msg = compare_ip_with_cloud_list([{"bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}], ["0:1.1.1.1"])
        self.assertTrue(res)

        # Less
        res, msg = compare_ip_with_cloud_list([], ["0:1.1.1.1"])
        self.assertFalse(res)

        # More (duplicate)
        hosts = [{"bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}, {"bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]
        res, msg = compare_ip_with_cloud_list(hosts, ["0:1.1.1.1"])
        self.assertFalse(res)

    def test_check_ip_cloud(self):
        hosts = [{"bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}, {"bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]
        res = check_ip_cloud(hosts)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], "0:1.1.1.1")

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cmdb")
    def test_get_ipv6_hosts(self, mock_cmdb):
        mock_cmdb.get_business_host_ipv6.return_value = [{"bk_host_id": 1}]

        # Normal
        res = get_ipv6_hosts("tenant", "user", 1, ["ip"])
        self.assertEqual(len(res), 1)

        # Biz Set
        mock_cmdb.get_business_set_host_ipv6.return_value = [{"bk_host_id": 2}]
        res = get_ipv6_hosts("tenant", "user", 1, ["ip"], is_biz_set=True)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["bk_host_id"], 2)

        # Empty
        res = get_ipv6_hosts("tenant", "user", 1, [])
        self.assertEqual(len(res), 0)

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cmdb")
    def test_get_ipv4_hosts_with_cloud(self, mock_cmdb):
        mock_cmdb.get_business_host.return_value = [{"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]

        # Normal
        res = get_ipv4_hosts_with_cloud("tenant", "user", 1, ["0:1.1.1.1"])
        self.assertEqual(len(res), 1)

        # Empty
        res = get_ipv4_hosts_with_cloud("tenant", "user", 1, [])
        self.assertEqual(len(res), 0)

        # Repeated host
        mock_cmdb.get_business_host.return_value = [
            {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0},
            {"bk_host_id": 2, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0},
        ]
        with self.assertRaises(Exception):
            get_ipv4_hosts_with_cloud("tenant", "user", 1, ["0:1.1.1.1"])

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv6_hosts_with_cloud")
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv6_hosts")
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv4_hosts")
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv4_hosts_with_cloud")
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_business_host_by_hosts_ids")
    def test_cc_get_host_by_innerip_with_ipv6_across_business(
        self, mock_get_ids, mock_v4_cloud, mock_v4, mock_v6, mock_v6_cloud
    ):
        # Mock returns
        mock_v6_cloud.return_value = []
        mock_v6.return_value = []
        mock_v4.return_value = []
        mock_v4_cloud.return_value = []
        mock_get_ids.return_value = []

        ip_str = "1.1.1.1\n0:2.2.2.2"
        res = cc_get_host_by_innerip_with_ipv6_across_business("tenant", "user", 1, ip_str)

        # res is a tuple of 5 lists
        self.assertEqual(len(res), 5)
        # 1.1.1.1 should be in ipv4_absent (res[1])
        self.assertIn("1.1.1.1", res[1])
        # 0:2.2.2.2 should be in ipv4_with_cloud_absent (res[2])
        self.assertIn("0:2.2.2.2", res[2])

    def test_format_host_with_ipv6(self):
        self.assertEqual(format_host_with_ipv6({"bk_host_innerip": "1.1.1.1"}), "1.1.1.1")
        self.assertEqual(format_host_with_ipv6({"bk_host_innerip_v6": "::1"}), "::1")
        self.assertEqual(format_host_with_ipv6({"bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}, True), "0:1.1.1.1")
        self.assertEqual(format_host_with_ipv6({"bk_host_innerip_v6": "::1", "bk_cloud_id": 0}, True), "0:[::1]")

        with self.assertRaises(ValueError):
            format_host_with_ipv6({})

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cmdb")
    def test_more_ipv6_utils(self, mock_cmdb):
        from pipeline_plugins.components.collections.sites.open.cc.ipv6_utils import (
            get_hosts_by_hosts_ids,
            get_ipv4_host_list,
            get_ipv4_host_with_cloud_list,
            get_ipv4_hosts,
            get_ipv6_host_list,
            get_ipv6_host_list_with_cloud_list,
            get_ipv6_hosts_with_cloud,
        )

        # get_ipv6_hosts_with_cloud
        mock_cmdb.get_business_host_ipv6.return_value = [
            {"bk_host_id": 1, "bk_host_innerip_v6": "::1", "bk_cloud_id": 0}
        ]
        res = get_ipv6_hosts_with_cloud("tenant", "user", 1, ["0:[::1]"])
        self.assertEqual(len(res), 1)

        # get_ipv4_hosts
        mock_cmdb.get_business_host.return_value = [{"bk_host_id": 1, "bk_host_innerip": "1.1.1.1"}]
        res = get_ipv4_hosts("tenant", "user", 1, ["1.1.1.1"])
        self.assertEqual(len(res), 1)

        # get_hosts_by_hosts_ids
        # Mock get_business_host_by_hosts_ids (imported from cmdb)
        with patch(
            "pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_business_host_by_hosts_ids"
        ) as mock_get_ids:
            mock_get_ids.return_value = [{"bk_host_id": 1}]
            res = get_hosts_by_hosts_ids("tenant", "user", 1, [1])
            self.assertTrue(res["result"])
            self.assertEqual(len(res["data"]), 1)

            # Missing
            mock_get_ids.return_value = []
            res = get_hosts_by_hosts_ids("tenant", "user", 1, [1])
            self.assertFalse(res["result"])

        # Wrappers
        # get_ipv6_host_list
        with patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv6_hosts") as mock_get:
            mock_get.return_value = [{"bk_host_innerip_v6": "::1"}]
            res = get_ipv6_host_list("tenant", "user", 1, ["::1"])
            self.assertTrue(res["result"])

        # get_ipv4_host_with_cloud_list
        with patch(
            "pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv4_hosts_with_cloud"
        ) as mock_get:
            mock_get.return_value = [{"bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]
            res = get_ipv4_host_with_cloud_list("tenant", "user", 1, ["0:1.1.1.1"])
            self.assertTrue(res["result"])

        # get_ipv6_host_list_with_cloud_list
        with patch(
            "pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv6_hosts_with_cloud"
        ) as mock_get:
            mock_get.return_value = [{"bk_host_innerip_v6": "::1", "bk_cloud_id": 0}]
            res = get_ipv6_host_list_with_cloud_list("tenant", "user", 1, ["0:[::1]"])
            self.assertTrue(res["result"])

        # get_ipv4_host_list
        with patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv4_hosts") as mock_get:
            mock_get.return_value = [{"bk_host_innerip": "1.1.1.1"}]
            res = get_ipv4_host_list("tenant", "user", 1, ["1.1.1.1"])
            self.assertTrue(res["result"])

    def test_ipv6_compare_errors(self):
        # compare_ipv6_with_cloud_list
        # More
        hosts = [{"bk_host_innerip_v6": "::1", "bk_cloud_id": 0}, {"bk_host_innerip_v6": "::1", "bk_cloud_id": 0}]
        res, msg = compare_ipv6_with_cloud_list(hosts, ["0:[::1]"])
        self.assertFalse(res)

        # Less
        res, msg = compare_ipv6_with_cloud_list([], ["0:[::1]"])
        self.assertFalse(res)
