# -*- coding: utf-8 -*-
import mock
from django.test import TestCase

from pipeline_plugins.resource_replacement import base


class ConcreteCmdbSuite(base.CmdbSuite):
    CODE = "concrete_cmdb_suite"
    TYPE = "component"

    def do(self, node_id, component):
        pass


class ConcreteJobSuite(base.JobSuite):
    CODE = "concrete_job_suite"
    TYPE = "component"

    def do(self, node_id, component):
        pass


class BaseSupplementTestCase(TestCase):
    def setUp(self):
        self.suite_meta = mock.MagicMock()
        self.suite_meta.offset = 100
        self.suite_meta.old_biz_id__new_biz_info_map = {
            1: {"bk_new_biz_id": 101, "bk_old_biz_name": "old_biz", "bk_new_biz_name": "new_biz"}
        }
        self.suite_meta.pipeline_tree = {"constants": {}}
        self.db_helper = mock.MagicMock()

        self.cmdb_suite = ConcreteCmdbSuite(self.suite_meta, self.db_helper)
        self.job_suite = ConcreteJobSuite(self.suite_meta, self.db_helper)

    def test_to_new_topo_select(self):
        # Case 1: Exception split (should return original)
        self.assertEqual(self.cmdb_suite.to_new_topo_select("invalid"), "invalid")

        # Case 2: Exception rsplit for non-ip (should return original)
        self.assertEqual(self.cmdb_suite.to_new_topo_select("obj_invalid"), "obj_invalid")

        # Case 3: biz object but not in map
        self.assertEqual(self.cmdb_suite.to_new_topo_select("biz_999"), "biz_999")

        # Case 4: Normal biz
        self.assertEqual(self.cmdb_suite.to_new_topo_select("biz_1"), "biz_101")

        # Case 5: Normal other
        self.assertEqual(self.cmdb_suite.to_new_topo_select("set_10"), "set_110")

    def test_process_cc_id(self):
        # Case 1: get_attr_data_or_raise ValueError
        with mock.patch.object(self.cmdb_suite, "get_attr_data_or_raise", side_effect=ValueError):
            self.cmdb_suite.process_cc_id("node", {})

        # Case 2: Not int
        with mock.patch.object(self.cmdb_suite, "get_attr_data_or_raise", return_value={"value": "not_int"}):
            self.cmdb_suite.process_cc_id("node", {})

        # Case 3: KeyError in map
        with mock.patch.object(self.cmdb_suite, "get_attr_data_or_raise", return_value={"value": 999}):
            self.cmdb_suite.process_cc_id("node", {})

        # Case 4: Success
        data = {"value": 1}
        schema_attr_data = {}
        with mock.patch.object(self.cmdb_suite, "get_attr_data_or_raise", return_value=data):
            self.cmdb_suite.process_cc_id("node", schema_attr_data)
            self.assertEqual(schema_attr_data["value"], 101)

    def test_process_topo_select_text(self):
        # Case 1: ValueError
        with mock.patch.object(self.cmdb_suite, "get_attr_data_or_raise", side_effect=ValueError):
            self.cmdb_suite.process_topo_select_text("node", {})

        # Case 2: Not string
        with mock.patch.object(self.cmdb_suite, "get_attr_data_or_raise", return_value={"value": 123}):
            self.cmdb_suite.process_topo_select_text("node", {})

        # Case 3: IndexError (empty path list from parse?)
        with mock.patch("pipeline_plugins.resource_replacement.base.cc_parse_path_text", return_value=[[]]):
            data = {"value": "some_path"}
            with mock.patch.object(self.cmdb_suite, "get_attr_data_or_raise", return_value=data):
                self.cmdb_suite.process_topo_select_text("node", {})
                self.assertEqual(data["value"], "")

    def test_get_attr_data_or_raise(self):
        # Case 1: No value
        with self.assertRaises(ValueError):
            self.cmdb_suite.get_attr_data_or_raise({"value": None})

        # Case 2: String value (constant), resource_replaced=True
        self.suite_meta.pipeline_tree = {"constants": {"${var}": {"value": "val", "resource_replaced": True}}}
        # Refresh meta reference if needed, but dict reference should persist
        with self.assertRaises(ValueError):
            self.cmdb_suite.get_attr_data_or_raise({"value": "${var}"})

        # Case 3: String value, constant not found (return schema_attr_data)
        self.suite_meta.pipeline_tree = {"constants": {}}
        res = self.cmdb_suite.get_attr_data_or_raise({"value": "${not_found}"})
        self.assertEqual(res["value"], "${not_found}")

        # Case 4: String value, constant found, no value in constant
        self.suite_meta.pipeline_tree = {"constants": {"${empty}": {"value": None}}}
        # Based on code, it returns the constant dict as is, without checking value if found in constants
        res = self.cmdb_suite.get_attr_data_or_raise({"value": "${empty}"})
        self.assertEqual(res["value"], None)

    def test_to_new_job_id(self):
        # Case 1: key not in data
        self.job_suite.to_new_job_id({"data": {}}, "key", "type", int)

        # Case 2: Exception
        with mock.patch.object(self.job_suite, "get_attr_data_or_raise", side_effect=Exception):
            self.job_suite.to_new_job_id({"data": {"key": {}}}, "key", "type", int)

    def test_to_new_ip_form(self):
        # Case 1: key not in data
        self.job_suite.to_new_ip_form({"data": {}}, "key", "ip_key")

        # Case 2: Exception get_attr
        with mock.patch.object(self.job_suite, "get_attr_data_or_raise", side_effect=Exception):
            self.job_suite.to_new_ip_form({"data": {"key": {}}}, "key", "ip_key")

        # Case 3: Not list
        with mock.patch.object(self.job_suite, "get_attr_data_or_raise", return_value={"value": "not_list"}):
            self.job_suite.to_new_ip_form({"data": {"key": {}}}, "key", "ip_key")

        # Case 4: Item processing exception
        data = {"value": [{"ip_key": "ip"}]}
        with mock.patch.object(self.job_suite, "get_attr_data_or_raise", return_value=data):
            with mock.patch.object(self.job_suite, "to_new_ip_list_str_or_raise", side_effect=Exception):
                self.job_suite.to_new_ip_form({"data": {"key": {}}}, "key", "ip_key")
