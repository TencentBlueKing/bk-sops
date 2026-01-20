from django.test import TestCase
from mock import patch

from pipeline_plugins.components.collections.sites.open.cc.ipv6_utils import (
    cc_get_host_by_innerip_with_ipv6_across_business,
    check_ip_cloud,
    compare_ip_list,
    compare_ip_list_and_return_with_cloud,
    compare_ip_with_cloud_list,
    compare_ipv6_list_and_return_with_cloud,
    compare_ipv6_with_cloud_list,
    format_host_with_ipv6,
    get_hosts_by_hosts_ids,
    get_ipv4_host_list,
    get_ipv4_host_with_cloud_list,
    get_ipv4_hosts,
    get_ipv4_hosts_with_cloud,
    get_ipv6_host_list,
    get_ipv6_host_list_with_cloud_list,
    get_ipv6_hosts,
    get_ipv6_hosts_with_cloud,
)


class CompareFunctionsTestCase(TestCase):
    def test_compare_ip_list_equal(self):
        host_list = [{"bk_host_innerip": "1.1.1.1"}, {"bk_host_innerip": "2.2.2.2"}]
        ip_list = ["1.1.1.1", "2.2.2.2"]
        result, message = compare_ip_list(host_list, ip_list)
        self.assertTrue(result)
        self.assertEqual(message, "")

    def test_compare_ip_list_missing(self):
        host_list = [{"bk_host_innerip": "1.1.1.1"}]
        ip_list = ["1.1.1.1", "2.2.2.2"]
        result, message = compare_ip_list(host_list, ip_list)
        self.assertFalse(result)
        self.assertIn("ip not found in business", message)
        self.assertIn("2.2.2.2", message)

    def test_compare_ip_list_duplicates(self):
        host_list = [{"bk_host_innerip": "1.1.1.1"}, {"bk_host_innerip": "1.1.1.1"}]
        ip_list = ["1.1.1.1"]
        result, message = compare_ip_list(host_list, ip_list)
        self.assertFalse(result)
        self.assertIn("mutiple same innerip host found", message)
        self.assertIn("1.1.1.1", message)

    def test_compare_ip_with_cloud_list_missing(self):
        host_list = [{"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1"}]
        ip_list = ["0:1.1.1.1", "1:2.2.2.2"]
        result, message = compare_ip_with_cloud_list(host_list, ip_list)
        self.assertFalse(result)
        self.assertIn("ip not found in business", message)
        self.assertIn("1:2.2.2.2", message)

    def test_compare_ip_with_cloud_list_duplicates(self):
        host_list = [
            {"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1"},
            {"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1"},
        ]
        ip_list = ["0:1.1.1.1"]
        result, message = compare_ip_with_cloud_list(host_list, ip_list)
        self.assertFalse(result)
        self.assertIn("mutiple same innerip host found", message)

    def test_compare_ipv6_with_cloud_list_missing(self):
        host_list = [{"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1"}]
        ip_list = ["0:[fe80::1]", "1:[fe80::2]"]
        result, message = compare_ipv6_with_cloud_list(host_list, ip_list)
        self.assertFalse(result)
        self.assertIn("ip not found in business", message)
        self.assertIn("1:[fe80::2]", message)

    def test_compare_ipv6_with_cloud_list_duplicates(self):
        host_list = [
            {"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1"},
            {"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1"},
        ]
        ip_list = ["0:[fe80::1]"]
        result, message = compare_ipv6_with_cloud_list(host_list, ip_list)
        self.assertFalse(result)
        self.assertIn("mutiple same innerip host found", message)


class CheckIpCloudTestCase(TestCase):
    def test_check_ip_cloud_ipv4(self):
        hosts = [
            {"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1"},
            {"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1"},
            {"bk_cloud_id": 0, "bk_host_innerip": "2.2.2.2"},
        ]
        result = check_ip_cloud(hosts)
        self.assertEqual(result, ["0:1.1.1.1"])

    def test_check_ip_cloud_ipv6(self):
        hosts = [
            {"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1"},
            {"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1"},
            {"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::2"},
        ]
        result = check_ip_cloud(hosts, bk_host_innerip_key="bk_host_innerip_v6")
        self.assertEqual(result, ["0:fe80::1"])


class GetIPv6HostsTestCase(TestCase):
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cmdb")
    def test_get_ipv6_hosts_biz(self, mock_cmdb):
        mock_cmdb.get_business_host_ipv6.return_value = [
            {"bk_host_id": 1, "bk_host_innerip_v6": "fe80::1", "bk_cloud_id": 0, "bk_host_innerip": ""}
        ]
        result = get_ipv6_hosts("t", "e", 2, ["fe80::1"], is_biz_set=False)
        self.assertEqual(len(result), 1)
        mock_cmdb.get_business_host_ipv6.assert_called_once()

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cmdb")
    def test_get_ipv6_hosts_biz_set(self, mock_cmdb):
        mock_cmdb.get_business_set_host_ipv6.return_value = [
            {"bk_host_id": 1, "bk_host_innerip_v6": "fe80::1", "bk_cloud_id": 0, "bk_host_innerip": ""}
        ]
        result = get_ipv6_hosts("t", "e", None, ["fe80::1"], is_biz_set=True)
        self.assertEqual(len(result), 1)
        mock_cmdb.get_business_set_host_ipv6.assert_called_once()

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cmdb")
    def test_get_ipv6_hosts_empty(self, mock_cmdb):
        mock_cmdb.get_business_host_ipv6.return_value = []
        result = get_ipv6_hosts("t", "e", 2, ["fe80::1"], is_biz_set=False)
        self.assertEqual(result, [])


class GetIPv4HostsWithCloudTestCase(TestCase):
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cmdb")
    def test_get_ipv4_hosts_with_cloud_filter(self, mock_cmdb):
        mock_cmdb.get_business_host.return_value = [
            {"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1", "bk_host_id": 1},
            {"bk_cloud_id": 1, "bk_host_innerip": "2.2.2.2", "bk_host_id": 2},
        ]
        result = get_ipv4_hosts_with_cloud("t", "e", 2, ["0:1.1.1.1"], is_biz_set=False)
        self.assertEqual(result, [{"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1", "bk_host_id": 1}])

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cmdb")
    def test_get_ipv4_hosts_with_cloud_duplicate_raise(self, mock_cmdb):
        mock_cmdb.get_business_host.return_value = [
            {"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1", "bk_host_id": 1},
            {"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1", "bk_host_id": 2},
        ]
        with self.assertRaises(Exception):
            get_ipv4_hosts_with_cloud("t", "e", 2, ["0:1.1.1.1"], is_biz_set=False)

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cmdb")
    def test_get_ipv4_hosts_with_cloud_empty(self, mock_cmdb):
        mock_cmdb.get_business_host.return_value = []
        result = get_ipv4_hosts_with_cloud("t", "e", 2, ["0:1.1.1.1"], is_biz_set=False)
        self.assertEqual(result, [])


class GetIPv6HostsWithCloudTestCase(TestCase):
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv6_and_cloud_id_from_ipv6_cloud_str")
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cmdb")
    def test_get_ipv6_hosts_with_cloud_filter(self, mock_cmdb, mock_parse):
        mock_parse.side_effect = [("0", "fe80::1")]
        mock_cmdb.get_business_host_ipv6.return_value = [
            {"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1", "bk_host_id": 1, "bk_host_innerip": ""}
        ]
        result = get_ipv6_hosts_with_cloud("t", "e", 2, ["0:[fe80::1]"], is_biz_set=False)
        self.assertEqual(
            result, [{"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1", "bk_host_id": 1, "bk_host_innerip": ""}]
        )

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv6_and_cloud_id_from_ipv6_cloud_str")
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cmdb")
    def test_get_ipv6_hosts_with_cloud_duplicate_raise(self, mock_cmdb, mock_parse):
        mock_parse.side_effect = [("0", "fe80::1")]
        mock_cmdb.get_business_host_ipv6.return_value = [
            {"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1", "bk_host_id": 1, "bk_host_innerip": ""},
            {"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1", "bk_host_id": 2, "bk_host_innerip": ""},
        ]
        with self.assertRaises(Exception):
            get_ipv6_hosts_with_cloud("t", "e", 2, ["0:[fe80::1]"], is_biz_set=False)

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv6_and_cloud_id_from_ipv6_cloud_str")
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cmdb")
    def test_get_ipv6_hosts_with_cloud_empty(self, mock_cmdb, mock_parse):
        mock_parse.side_effect = [("0", "fe80::1")]
        mock_cmdb.get_business_host_ipv6.return_value = []
        result = get_ipv6_hosts_with_cloud("t", "e", 2, ["0:[fe80::1]"], is_biz_set=False)
        self.assertEqual(result, [])


class GetIPv4HostsTestCase(TestCase):
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cmdb")
    def test_get_ipv4_hosts_biz(self, mock_cmdb):
        mock_cmdb.get_business_host.return_value = [{"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1", "bk_host_id": 1}]
        result = get_ipv4_hosts("t", "e", 2, ["1.1.1.1"], is_biz_set=False)
        self.assertEqual(len(result), 1)

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.cmdb")
    def test_get_ipv4_hosts_empty(self, mock_cmdb):
        mock_cmdb.get_business_host.return_value = []
        result = get_ipv4_hosts("t", "e", 2, ["1.1.1.1"], is_biz_set=False)
        self.assertEqual(result, [])


class GetHostsByIdsTestCase(TestCase):
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_business_host_by_hosts_ids")
    def test_get_hosts_by_ids_success(self, mock_get):
        mock_get.return_value = [{"bk_host_id": 1}, {"bk_host_id": 2}]
        result = get_hosts_by_hosts_ids("t", "e", 2, [1, 2])
        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 2)

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_business_host_by_hosts_ids")
    def test_get_hosts_by_ids_empty(self, mock_get):
        mock_get.return_value = []
        result = get_hosts_by_hosts_ids("t", "e", 2, [1])
        self.assertFalse(result["result"])
        self.assertIn("return empty list", result["message"])

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_business_host_by_hosts_ids")
    def test_get_hosts_by_ids_mismatch(self, mock_get):
        mock_get.return_value = [{"bk_host_id": 1}]
        result = get_hosts_by_hosts_ids("t", "e", 2, ["1", "2"])
        self.assertFalse(result["result"])
        self.assertIn("ip not found in business", result["message"])


class WrapperFunctionsTestCase(TestCase):
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv6_hosts")
    def test_get_ipv6_host_list_success(self, mock_get):
        mock_get.return_value = [{"bk_host_innerip_v6": "fe80::1"}]
        result = get_ipv6_host_list("t", "e", 2, ["fe80::1"], is_biz_set=False)
        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 1)

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv6_hosts")
    def test_get_ipv6_host_list_fail(self, mock_get):
        mock_get.return_value = [{"bk_host_innerip_v6": "fe80::1"}]
        result = get_ipv6_host_list("t", "e", 2, ["fe80::1", "fe80::2"], is_biz_set=False)
        self.assertFalse(result["result"])
        self.assertIn("ip not found in business", result["message"])

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv4_hosts_with_cloud")
    def test_get_ipv4_host_with_cloud_list_success(self, mock_get):
        mock_get.return_value = [{"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1"}]
        result = get_ipv4_host_with_cloud_list("t", "e", 2, ["0:1.1.1.1"], is_biz_set=False)
        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 1)

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv4_hosts_with_cloud")
    def test_get_ipv4_host_with_cloud_list_fail(self, mock_get):
        mock_get.return_value = [{"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1"}]
        result = get_ipv4_host_with_cloud_list("t", "e", 2, ["0:1.1.1.1", "1:2.2.2.2"], is_biz_set=False)
        self.assertFalse(result["result"])
        self.assertIn("ip not found in business", result["message"])

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv6_hosts_with_cloud")
    def test_get_ipv6_host_list_with_cloud_list_success(self, mock_get):
        mock_get.return_value = [{"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1"}]
        result = get_ipv6_host_list_with_cloud_list("t", "e", 2, ["0:[fe80::1]"], is_biz_set=False)
        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 1)

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv6_hosts_with_cloud")
    def test_get_ipv6_host_list_with_cloud_list_fail(self, mock_get):
        mock_get.return_value = [{"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1"}]
        result = get_ipv6_host_list_with_cloud_list("t", "e", 2, ["0:[fe80::1]", "1:[fe80::2]"], is_biz_set=False)
        self.assertFalse(result["result"])
        self.assertIn("ip not found in business", result["message"])

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv4_hosts")
    def test_get_ipv4_host_list_success(self, mock_get):
        mock_get.return_value = [{"bk_host_innerip": "1.1.1.1"}]
        result = get_ipv4_host_list("t", "e", 2, ["1.1.1.1"], is_biz_set=False)
        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 1)

    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv4_hosts")
    def test_get_ipv4_host_list_fail(self, mock_get):
        mock_get.return_value = [{"bk_host_innerip": "1.1.1.1"}]
        result = get_ipv4_host_list("t", "e", 2, ["1.1.1.1", "2.2.2.2"], is_biz_set=False)
        self.assertFalse(result["result"])
        self.assertIn("ip not found in business", result["message"])


class CompareReturnWithCloudTestCase(TestCase):
    def test_compare_ip_list_and_return_with_cloud_raise(self):
        host_list = [
            {"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1"},
            {"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1"},
        ]
        with self.assertRaises(Exception):
            compare_ip_list_and_return_with_cloud(host_list, ["0:1.1.1.1"])

    def test_compare_ip_list_and_return_with_cloud_absent(self):
        host_list = [{"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1"}]
        absent = compare_ip_list_and_return_with_cloud(host_list, ["0:1.1.1.1", "1:2.2.2.2"])
        self.assertEqual(absent, {"1:2.2.2.2"})

    def test_compare_ipv6_list_and_return_with_cloud_raise(self):
        host_list = [
            {"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1"},
            {"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1"},
        ]
        with self.assertRaises(Exception):
            compare_ipv6_list_and_return_with_cloud(host_list, ["0:[fe80::1]"])

    def test_compare_ipv6_list_and_return_with_cloud_absent(self):
        host_list = [{"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1"}]
        absent = compare_ipv6_list_and_return_with_cloud(host_list, ["0:[fe80::1]", "1:[fe80::2]"])
        self.assertEqual(absent, {"1:[fe80::2]"})


class CCAcrossBusinessTestCase(TestCase):
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.extract_ip_from_ip_str")
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv6_hosts_with_cloud")
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv6_hosts")
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv4_hosts")
    @patch("pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_ipv4_hosts_with_cloud")
    def test_cc_get_host_by_innerip_with_ipv6_across_business(
        self, mock_ipv4_cloud, mock_ipv4, mock_ipv6, mock_ipv6_cloud, mock_extract
    ):
        mock_extract.return_value = (
            ["fe80::1"],
            ["1.1.1.1", "2.2.2.2"],
            [3],
            ["0:2.2.2.2"],
            ["0:[fe80::2]"],
        )
        mock_ipv6_cloud.return_value = []
        mock_ipv6.return_value = [{"bk_host_innerip_v6": "fe80::1"}]
        mock_ipv4.return_value = [{"bk_host_innerip": "1.1.1.1"}]
        mock_ipv4_cloud.return_value = [{"bk_cloud_id": 0, "bk_host_innerip": "2.2.2.2"}]
        (
            hosts,
            ipv4_absent,
            ipv4_cloud_absent,
            ipv6_absent,
            ipv6_cloud_absent,
        ) = cc_get_host_by_innerip_with_ipv6_across_business("t", "e", 2, "0:[fe80::2],fe80::1,1.1.1.1,0:2.2.2.2,3")
        self.assertEqual(len(hosts), 4)
        self.assertEqual(ipv4_absent, ["2.2.2.2"])
        self.assertEqual(ipv4_cloud_absent, [])
        self.assertEqual(ipv6_absent, [])
        self.assertEqual(ipv6_cloud_absent, ["0:[fe80::2]"])


class FormatHostWithIpv6TestCase(TestCase):
    def test_format_host_with_ipv4(self):
        host = {"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1"}
        self.assertEqual(format_host_with_ipv6(host, with_cloud=False), "1.1.1.1")
        self.assertEqual(format_host_with_ipv6(host, with_cloud=True), "0:1.1.1.1")

    def test_format_host_with_ipv6(self):
        host = {"bk_cloud_id": 0, "bk_host_innerip_v6": "fe80::1"}
        self.assertEqual(format_host_with_ipv6(host, with_cloud=False), "fe80::1")
        self.assertEqual(format_host_with_ipv6(host, with_cloud=True), "0:[fe80::1]")
