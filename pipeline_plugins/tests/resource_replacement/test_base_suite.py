# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.resource_replacement.base import CmdbSuite, DBHelper, JobSuite, SuiteMeta


class ConcreteCmdbSuite(CmdbSuite):
    def do(self, node_id, component):
        pass


class ConcreteJobSuite(JobSuite):
    def do(self, node_id, component):
        pass


class CmdbSuiteTestCase(TestCase):
    def setUp(self):
        self.pipeline_tree = {"constants": {"k1": {"value": "v1"}}}
        self.old_biz_map = {
            1: {
                "bk_old_biz_name": "old",
                "bk_old_biz_id": 1,
                "bk_new_biz_name": "new",
                "bk_new_biz_id": 2,
                "bk_env": "prod",
            }
        }
        self.suite_meta = SuiteMeta(
            pipeline_tree=self.pipeline_tree, offset=100, old_biz_id__new_biz_info_map=self.old_biz_map
        )
        self.db_helper = MagicMock(spec=DBHelper)
        self.suite = ConcreteCmdbSuite(self.suite_meta, self.db_helper)

    def test_to_new_topo_select(self):
        # Normal case
        self.assertEqual(self.suite.to_new_topo_select("obj_10"), "obj_110")

        # IP pattern
        self.assertEqual(self.suite.to_new_topo_select("10_1.1.1.1"), "110_1.1.1.1")

        # Biz case
        self.assertEqual(self.suite.to_new_topo_select("biz_1"), "biz_2")

        # Invalid
        self.assertEqual(self.suite.to_new_topo_select("invalid"), "invalid")

        # Biz not found
        self.assertEqual(self.suite.to_new_topo_select("biz_99"), "biz_99")

    def test_to_new_cloud_id(self):
        self.assertEqual(self.suite.to_new_cloud_id(0), 0)
        self.assertEqual(self.suite.to_new_cloud_id(1), 101)

    def test_to_new_ip_list_str_or_raise(self):
        # No cloud id
        self.assertEqual(self.suite.to_new_ip_list_str_or_raise("1.1.1.1"), "1.1.1.1")

        # With cloud id
        self.assertEqual(self.suite.to_new_ip_list_str_or_raise("1:1.1.1.1"), "101:1.1.1.1")

        # Mixed
        ip_str = "1.1.1.1\n1:2.2.2.2"
        expected = "1.1.1.1\n101:2.2.2.2"
        self.assertEqual(self.suite.to_new_ip_list_str_or_raise(ip_str), expected)

        # No match
        self.assertEqual(self.suite.to_new_ip_list_str_or_raise("invalid"), "invalid")

    def test_get_attr_data_or_raise(self):
        # Direct value
        data = {"value": "val"}
        self.assertEqual(self.suite.get_attr_data_or_raise(data), data)

        # Constant reference
        data = {"value": "k1"}
        expected = self.pipeline_tree["constants"]["k1"]
        self.assertEqual(self.suite.get_attr_data_or_raise(data), expected)
        self.assertTrue(expected["resource_replaced"])

        # Replaced constant
        with self.assertRaises(ValueError):
            self.suite.get_attr_data_or_raise(data)

        # Empty value
        with self.assertRaises(ValueError):
            self.suite.get_attr_data_or_raise({"value": ""})

    def test_process_cc_id(self):
        # Direct value
        data = {"value": 1}
        self.suite.process_cc_id("node", data)
        self.assertEqual(data["value"], 2)

        # Invalid value type
        data = {"value": "1"}
        self.suite.process_cc_id("node", data)
        self.assertEqual(data["value"], "1")

        # Not in map
        data = {"value": 99}
        self.suite.process_cc_id("node", data)
        self.assertEqual(data["value"], 99)


class JobSuiteTestCase(TestCase):
    def setUp(self):
        self.suite_meta = MagicMock()
        self.suite_meta.old_biz_id__new_biz_info_map = {1: {"bk_old_biz_name": "old", "bk_new_biz_name": "new"}}
        self.suite_meta.pipeline_tree = {}
        self.suite_meta.offset = 100
        self.db_helper = MagicMock(spec=DBHelper)
        self.suite = ConcreteJobSuite(self.suite_meta, self.db_helper)

    def test_to_new_job_id(self):
        component = {"data": {"job_id": {"value": 10}}}
        self.db_helper.fetch_resource_id_map.return_value = {10: 20}
        self.suite.get_attr_data_or_raise = MagicMock(return_value=component["data"]["job_id"])

        self.suite.to_new_job_id(component, "job_id", "type", int)
        self.assertEqual(component["data"]["job_id"]["value"], 20)

    def test_process_ip_list_str(self):
        data = {"value": "1.1.1.1"}
        self.suite.process_ip_list_str("node", data)
        self.assertEqual(data["value"], "1.1.1.1")

        data = {"value": "1:1.1.1.1"}
        self.suite.process_ip_list_str("node", data)
        self.assertEqual(data["value"], "101:1.1.1.1")

    @patch("pipeline_plugins.resource_replacement.base.cc_parse_path_text")
    def test_process_topo_select_text(self, mock_parse):
        self.suite.biz_old_name__new_name_map = {"old": "new"}
        data = {"value": "old > module"}
        mock_parse.return_value = [["old", "module"]]

        self.suite.process_topo_select_text("node", data)
        self.assertEqual(data["value"], "new > module")

    def test_process_topo_select(self):
        data = {"value": ["obj_10"]}
        self.suite.process_topo_select("node", data)
        self.assertEqual(data["value"], ["obj_110"])


class JobSuiteAdditionalTestCase(TestCase):
    def setUp(self):
        self.suite_meta = MagicMock()
        self.suite_meta.old_biz_id__new_biz_info_map = {1: {"bk_old_biz_name": "old", "bk_new_biz_name": "new"}}
        self.suite_meta.pipeline_tree = {}
        self.suite_meta.offset = 100
        self.db_helper = MagicMock(spec=DBHelper)
        self.suite = ConcreteJobSuite(self.suite_meta, self.db_helper)

    def test_to_new_ip_form(self):
        component = {"data": {"ip": {"value": [{"ip": "1.1.1.1"}, {"ip": "1:1.1.1.1"}]}}}
        # Mock get_attr_data_or_raise to return the list
        self.suite.get_attr_data_or_raise = MagicMock(return_value=component["data"]["ip"])

        self.suite.to_new_ip_form(component, "ip", "ip")

        self.assertEqual(component["data"]["ip"]["value"][0]["ip"], "1.1.1.1")
        self.assertEqual(component["data"]["ip"]["value"][1]["ip"], "101:1.1.1.1")


class DBHelperTestCase(TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.helper = DBHelper(self.conn, "source", "target")

    def test_base_fetch_data_list(self):
        cursor = MagicMock()
        self.conn.cursor.return_value.__enter__.return_value = cursor
        cursor.description = [("id",), ("name",)]
        cursor.fetchall.return_value = [(1, "a")]

        res = self.helper.base_fetch_data_list("table", "id", [1])
        self.assertEqual(res, [{"id": 1, "name": "a"}])

    def test_fetch_resource_id_map(self):
        cursor = MagicMock()
        self.conn.cursor.return_value.__enter__.return_value = cursor
        cursor.description = [("source_data",), ("target_data",)]
        cursor.fetchall.return_value = [(1, 2)]

        res = self.helper.fetch_resource_id_map("type", [1], int)
        self.assertEqual(res, {1: 2})

    def test_insert_resource_mapping(self):
        self.helper.insert_resource_mapping("table", "type", {1: 2}, int)
        self.conn.cursor.return_value.__enter__.return_value.executemany.assert_called()


class JobSuiteCMDBIDTestCase(TestCase):
    def setUp(self):
        self.suite_meta = MagicMock()
        self.suite_meta.pipeline_tree = {}
        self.suite_meta.offset = 100
        self.db_helper = MagicMock(spec=DBHelper)
        self.suite = ConcreteJobSuite(self.suite_meta, self.db_helper)

    def test_to_new_cmdb_id_form(self):
        # Test cloud id
        component = {"data": {"bk_cloud_id": {"value": 0}}}
        # We need to mock get_attr_data_or_raise behavior or mock it directly
        # But to_new_cmdb_id_form calls it.
        # Let's mock it to return the dict itself for simplicity if possible,
        # but get_attr_data_or_raise logic is complex.
        # Since I am testing to_new_cmdb_id_form, I can mock get_attr_data_or_raise on the suite instance.
        self.suite.get_attr_data_or_raise = MagicMock(return_value=component["data"]["bk_cloud_id"])

        # Test case 1: integer value (not list), returns early
        self.suite.to_new_cmdb_id_form(component, "bk_cloud_id", "bk_cloud_id")
        # Should return early because value is 0 (int), not list.
        # Wait, line 357: if not isinstance(attr_data["value"], list): return
        # So I need value to be a list.

        # Correct test case: list of dicts
        component = {"data": {"list": {"value": [{"id": 10}, {"id": "20"}, {"bk_cloud_id": 1}, {"bk_cloud_id": "1"}]}}}
        self.suite.get_attr_data_or_raise = MagicMock(return_value=component["data"]["list"])

        # Test regular ID
        self.suite.to_new_cmdb_id_form(component, "list", "id")
        self.assertEqual(component["data"]["list"]["value"][0]["id"], 110)
        self.assertEqual(component["data"]["list"]["value"][1]["id"], "120")

        # Test cloud ID
        self.suite.to_new_cmdb_id_form(component, "list", "bk_cloud_id")
        self.assertEqual(component["data"]["list"]["value"][2]["bk_cloud_id"], 101)
        self.assertEqual(component["data"]["list"]["value"][3]["bk_cloud_id"], "101")
