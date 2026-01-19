# -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from pipeline_plugins.cmdb_ip_picker.query import (
    cmdb_get_mainline_object_topo,
    cmdb_search_dynamic_group,
    cmdb_search_host,
    cmdb_search_topo_tree,
)
from pipeline_plugins.cmdb_ip_picker.utils import (
    format_agent_data,
    get_bk_cloud_id_for_host,
    get_cmdb_topo_tree,
    get_ip_picker_result,
    get_modules_id,
)


class IPPickerSupplementTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.username = "admin"
        self.user.tenant_id = "tenant"

    # --- query.py ---

    @patch("pipeline_plugins.cmdb_ip_picker.query.get_cmdb_topo_tree")
    def test_cmdb_search_topo_tree(self, mock_get_tree):
        mock_get_tree.return_value = {"result": True, "data": []}
        request = self.factory.get("/")
        request.user = self.user
        response = cmdb_search_topo_tree(request, 1)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])

    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb.get_business_host_topo")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_cmdb_topo_tree")
    def test_cmdb_search_host(self, mock_get_tree, mock_get_hosts, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.search_cloud_area.return_value = {
            "result": True,
            "data": {"info": [{"bk_cloud_id": 0, "bk_cloud_name": "default"}]},
        }

        mock_get_hosts.return_value = [
            {"host": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}, "module": [], "set": []}
        ]

        # Test basic
        request = self.factory.get("/", {"fields": json.dumps(["bk_host_innerip"])})
        request.user = self.user
        response = cmdb_search_host(request, 1)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(len(content["data"]), 1)

        # Test with topo filter
        request = self.factory.get("/", {"topo": json.dumps([{"bk_obj_id": "module", "bk_inst_id": 1}])})
        request.user = self.user
        mock_get_tree.return_value = {"result": True, "data": [{"bk_obj_id": "biz", "bk_inst_id": 1, "child": []}]}
        # Since tree is empty, no modules match, so data should be all hosts (fallback)
        response = cmdb_search_host(request, 1)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(len(content["data"]), 1)

    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_get_mainline_object_topo(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.get_mainline_object_topo.return_value = {"result": True, "code": 0, "data": [{"bk_obj_id": "host"}]}

        request = self.factory.get("/")
        request.user = self.user
        response = cmdb_get_mainline_object_topo(request, 1)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["bk_obj_name"], "IP")

    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    @patch("pipeline_plugins.cmdb_ip_picker.query.batch_request")
    def test_cmdb_search_dynamic_group(self, mock_batch, mock_get_client):
        mock_batch.return_value = [
            {"bk_obj_id": "host", "id": "g1", "name": "group1", "create_user": "admin"},
            {"bk_obj_id": "set", "id": "g2"},
        ]
        request = self.factory.get("/")
        request.user = self.user
        response = cmdb_search_dynamic_group(request, 1)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(len(content["data"]["info"]), 1)
        self.assertEqual(content["data"]["info"][0]["id"], "g1")

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_cmdb_topo_tree")
    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb.get_business_host_topo")
    def test_get_ip_picker_result(self, mock_get_hosts, mock_get_tree):
        mock_get_tree.return_value = {"result": True, "data": [{"bk_obj_id": "biz", "bk_inst_id": 1}]}
        mock_get_hosts.return_value = [
            {"host": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_host_innerip_v6": "::1", "bk_cloud_id": 0}}
        ]

        # Test ip selector
        kwargs = {"selectors": ["ip"], "ip": [{"bk_host_id": 1}], "filters": [], "excludes": []}
        result = get_ip_picker_result("tenant", "admin", 1, kwargs)
        self.assertTrue(result["result"])

        # Test manual ip
        kwargs = {
            "selectors": ["manual"],
            "manual_input": {"type": "ip", "value": "1.1.1.1"},
            "filters": [],
            "excludes": [],
        }
        with patch("pipeline_plugins.cmdb_ip_picker.utils.cc_get_ips_info_by_str") as mock_get_ip_str:
            mock_get_ip_str.return_value = {
                "invalid_ip": [],
                "ip_result": [{"InnerIP": "1.1.1.1", "HostID": 1, "Source": 0}],
            }
            result = get_ip_picker_result("tenant", "admin", 1, kwargs)
            self.assertTrue(result["result"])

    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb.get_business_host_topo")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_nodeman_client_by_username")
    @patch("pipeline_plugins.cmdb_ip_picker.query.batch_execute_func")
    @patch("pipeline_plugins.cmdb_ip_picker.query.settings")
    def test_cmdb_search_host_agent_status(
        self, mock_settings, mock_batch, mock_nodeman, mock_get_hosts, mock_get_client
    ):
        mock_settings.ENABLE_IPV6 = False
        mock_settings.ENABLE_GSE_V2 = False
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.search_cloud_area.return_value = {
            "result": True,
            "data": {"info": [{"bk_cloud_id": 0, "bk_cloud_name": "default"}]},
        }

        mock_get_hosts.return_value = [
            {"host": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}, "module": [], "set": []}
        ]

        # Mock nodeman
        mock_nodeman_client = MagicMock()
        mock_nodeman.return_value = mock_nodeman_client
        mock_batch.return_value = [
            {"result": {"result": True, "data": [{"cloud_area": {"id": 0}, "ip": "1.1.1.1", "alive": 1}]}}
        ]

        request = self.factory.get("/", {"fields": json.dumps(["agent"])})
        request.user = self.user

        response = cmdb_search_host(request, 1)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["agent"], 1)

    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb.get_business_host_topo")
    def test_cmdb_search_host_lock(self, mock_get_hosts, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.search_cloud_area.return_value = {"result": True, "data": {"info": []}}
        mock_get_hosts.return_value = [
            {"host": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}, "module": [], "set": []}
        ]

        # Mock lock
        client.api.search_host_lock.return_value = {"result": True, "data": {"1": True}}

        request = self.factory.get("/", {"search_host_lock": "1"})
        request.user = self.user
        response = cmdb_search_host(request, 1)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertTrue(content["data"][0]["bk_host_lock_status"])

    # --- utils.py ---

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_client_by_username")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.batch_request")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb.get_dynamic_group_host_list")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    def test_generator(self, mock_settings, mock_get_group_hosts, mock_batch, mock_get_client):
        mock_settings.ENABLE_IPV6 = False
        from pipeline_plugins.cmdb_ip_picker.utils import IPPickerDataGenerator

        # Test group generator
        mock_batch.return_value = [{"bk_obj_id": "host", "name": "g1", "id": "1"}]
        mock_get_group_hosts.return_value = (
            True,
            {"data": [{"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_host_innerip_v6": "::1", "bk_cloud_id": 0}]},
        )
        gen = IPPickerDataGenerator("tenant", "group", "g1", {"username": "admin"}, {}, 1)
        res = gen.generate()
        self.assertTrue(res["result"])
        self.assertEqual(len(res["data"]), 1)

        # Test ip generator
        with patch("pipeline_plugins.cmdb_ip_picker.utils.cc_get_ips_info_by_str") as mock_ip:
            mock_ip.return_value = {"invalid_ip": [], "ip_result": [{"InnerIP": "1.1.1.1", "HostID": 1, "Source": 0}]}
            gen = IPPickerDataGenerator("tenant", "ip", "1.1.1.1", {"username": "admin", "bk_biz_id": 1}, {}, 1)
            res = gen.generate()
            self.assertTrue(res["result"])
            self.assertEqual(len(res["data"]), 1)

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_cmdb_topo_tree")
    def test_handler(self, mock_get_tree):
        mock_get_tree.return_value = {"result": True, "data": [{"bk_obj_id": "biz", "bk_inst_id": 1}]}
        from pipeline_plugins.cmdb_ip_picker.utils import IPPickerHandler

        # Test filters
        filters = [{"field": "host", "value": ["1.1.1.1"]}]
        handler = IPPickerHandler("tenant", "ip", "admin", 1, filters=filters)
        self.assertIn("host_property_filter", handler.property_filters)

        # Test inject condition params (internal)
        # Test format_condition_value
        from pipeline_plugins.cmdb_ip_picker.utils import format_condition_value

        self.assertEqual(format_condition_value(["1", "2\n3"]), ["1", "2", "3"])

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_client_by_username")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb.get_dynamic_group_host_list")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_dynamic_group_list")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_cmdb_topo_tree")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb.get_business_host_topo")
    def test_group_picker_handler(
        self, mock_get_hosts, mock_get_tree, mock_get_groups, mock_get_group_hosts, mock_get_client
    ):
        from pipeline_plugins.cmdb_ip_picker.utils import IPPickerHandler

        mock_get_tree.return_value = {"result": True, "data": [{"bk_obj_id": "biz", "bk_inst_id": 1}]}
        mock_get_groups.return_value = [{"id": "g1", "name": "group1"}]
        mock_get_group_hosts.return_value = (True, {"data": [{"bk_host_id": 1, "bk_host_innerip": "1.1.1.1"}]})

        # Test without filters
        handler = IPPickerHandler("tenant", "group", "admin", 1)
        res = handler.group_picker_handler([{"id": "g1"}])
        self.assertTrue(res["result"])
        self.assertEqual(len(res["data"]), 1)

        # Test with filters (requires fetching hosts again)
        mock_get_hosts.return_value = [{"host": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1"}}]
        handler = IPPickerHandler("tenant", "group", "admin", 1, filters=[{"field": "host", "value": ["1.1.1.1"]}])
        res = handler.group_picker_handler([{"id": "g1"}])
        self.assertTrue(res["result"])
        self.assertEqual(len(res["data"]), 1)

    def test_topo_generator(self):
        from pipeline_plugins.cmdb_ip_picker.utils import IPPickerDataGenerator

        topo_tree = {
            "bk_inst_name": "biz",
            "bk_inst_id": 1,
            "bk_obj_id": "biz",
            "child": [{"bk_inst_name": "set", "bk_inst_id": 2, "bk_obj_id": "set"}],
        }
        gen = IPPickerDataGenerator("tenant", "topo", "biz>set", {"username": "admin"}, {"biz_topo_tree": topo_tree}, 1)
        res = gen.generate()
        self.assertTrue(res["result"])
        self.assertEqual(res["data"][0]["bk_inst_id"], 2)

    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb.get_business_host_topo")
    @patch("pipeline_plugins.cmdb_ip_picker.query.settings")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_gse_agent_status_ipv6")
    def test_cmdb_search_host_ipv6(self, mock_get_status, mock_settings, mock_get_hosts, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.search_cloud_area.return_value = {"result": True, "data": {"info": []}}
        mock_get_hosts.return_value = [
            {"host": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}, "module": [], "set": []}
        ]

        mock_settings.ENABLE_IPV6 = True
        mock_settings.ENABLE_GSE_V2 = False
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_get_status.return_value = {"0:1.1.1.1": 1}

        request = self.factory.get("/", {"fields": json.dumps(["agent"])})
        request.user = self.user

        response = cmdb_search_host(request, 1)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["agent"], 1)

    @patch("pipeline_plugins.cmdb_ip_picker.utils.requests.post")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    def test_get_gse_agent_status_ipv6(self, mock_settings, mock_post):
        from pipeline_plugins.cmdb_ip_picker.utils import get_gse_agent_status_ipv6

        mock_settings.BK_API_URL_TMPL = "http://api"
        mock_settings.RUN_MODE = "PRODUCT"
        mock_settings.APP_CODE = "app"
        mock_settings.SECRET_KEY = "secret"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 0, "data": [{"bk_agent_id": "0:1.1.1.1", "status_code": 2}]}
        mock_post.return_value = mock_response

        res = get_gse_agent_status_ipv6(["0:1.1.1.1"], "tenant")
        self.assertEqual(res["0:1.1.1.1"], 1)

    @patch("pipeline_plugins.cmdb_ip_picker.utils.requests.post")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    def test_get_gse_agent_status_ipv6_fail(self, mock_settings, mock_post):
        from pipeline_plugins.cmdb_ip_picker.utils import get_gse_agent_status_ipv6

        mock_settings.BK_API_URL_TMPL = "http://api"
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with self.assertRaises(Exception):
            get_gse_agent_status_ipv6(["0:1.1.1.1"], "tenant")

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_cmdb_topo_tree")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    def test_handler_ipv6(self, mock_settings, mock_get_tree):
        mock_get_tree.return_value = {"result": True, "data": [{"bk_obj_id": "biz", "bk_inst_id": 1}]}
        from pipeline_plugins.cmdb_ip_picker.utils import IPPickerHandler

        mock_settings.ENABLE_IPV6 = True

        # Test filters with ipv6
        filters = [{"field": "host", "value": ["2001:db8::1"]}]
        handler = IPPickerHandler("tenant", "ip", "admin", 1, filters=filters)
        # Should have rules for innerip, innerip_v6, host_id
        rules = handler.property_filters["host_property_filter"]["rules"][0]["rules"]
        self.assertTrue(any(r["field"] == "bk_host_innerip_v6" for r in rules))

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_client_by_username")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb.get_business_host_topo")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_cmdb_topo_tree")
    def test_topo_picker_handler(self, mock_get_tree, mock_get_hosts, mock_get_client):
        from pipeline_plugins.cmdb_ip_picker.utils import IPPickerHandler

        mock_get_tree.return_value = {"result": True, "data": [{"bk_obj_id": "biz", "bk_inst_id": 1, "child": []}]}
        mock_get_hosts.return_value = [{"host": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1"}}]

        handler = IPPickerHandler("tenant", "topo", "admin", 1)
        # Mock biz_topo_tree to match topo_list
        handler.biz_topo_tree = {
            "bk_obj_id": "biz",
            "bk_inst_id": 1,
            "child": [{"bk_obj_id": "module", "bk_inst_id": 2}],
        }

        topo_list = [{"bk_obj_id": "biz", "bk_inst_id": 1}]
        res = handler.topo_picker_handler(topo_list)
        self.assertTrue(res["result"])
        self.assertEqual(len(res["data"]), 1)

    def test_utils_functions(self):
        # format_agent_data
        agents = [{"cloud_area": {"id": 0}, "ip": "1.1.1.1", "alive": 1}]
        res = format_agent_data(agents)
        self.assertEqual(res["0:1.1.1.1"]["bk_agent_alive"], 1)

        # get_modules_id
        modules = [{"bk_module_id": 1}, {"bk_inst_id": 2}]
        self.assertEqual(get_modules_id(modules), [1, 2])

        # get_bk_cloud_id_for_host
        self.assertEqual(get_bk_cloud_id_for_host({"cloud": [{"id": 0}]}), 0)
        self.assertEqual(get_bk_cloud_id_for_host({}), "-1")

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_client_by_username")
    def test_get_cmdb_topo_tree(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Mock search_biz_inst_topo
        client.api.search_biz_inst_topo.return_value = {"result": True, "data": [{"bk_obj_id": "biz", "child": []}]}

        # Mock get_biz_internal_module
        client.api.get_biz_internal_module.return_value = {
            "result": True,
            "data": {"bk_set_id": 1, "bk_set_name": "set", "module": [{"bk_module_id": 2, "bk_module_name": "mod"}]},
        }

        res = get_cmdb_topo_tree("tenant", "user", 1)
        self.assertTrue(res["result"])
        # Check if default set is inserted
        self.assertEqual(res["data"][0]["child"][0]["bk_obj_id"], "set")
