# -*- coding: utf-8 -*-
import mock
from django.test import TestCase

from pipeline_plugins.resource_replacement import suites


class SuitesSupplementTestCase(TestCase):
    def setUp(self):
        self.node_id = "node_id"
        self.suite_meta = mock.MagicMock()
        self.suite_meta.offset = 100
        self.db_helper = mock.MagicMock()

    def test_JobFastExecuteScriptSuite(self):
        suite = suites.JobFastExecuteScriptSuite(self.suite_meta, self.db_helper)
        suite.process_cc_id = mock.MagicMock()
        suite.to_new_ip_form = mock.MagicMock()

        # Test with biz_cc_id
        component = {"data": {"biz_cc_id": {"value": 1}, "job_source_files": [], "job_dispatch_attr": []}}
        suite.do(self.node_id, component)
        suite.process_cc_id.assert_called_with(self.node_id, component["data"]["biz_cc_id"])

        # Test super().do() which calls to_new_ip_form
        # Since we mocked to_new_ip_form, we just verify calls
        # JobLocalContentUploadSuite.do calls process_ip_list_str if job_ip_list exists
        # JobFastExecuteScriptSuite.do calls super().do()

    def test_JobCronTaskSuite(self):
        suite = suites.JobCronTaskSuite(self.suite_meta, self.db_helper)
        suite.process_cc_id = mock.MagicMock()
        suite.to_new_job_id = mock.MagicMock()

        component = {"data": {"biz_cc_id": {"value": 1}}}
        suite.do(self.node_id, component)
        suite.process_cc_id.assert_called_with(self.node_id, component["data"]["biz_cc_id"])
        suite.to_new_job_id.assert_called()

    def test_CCCreateSetSuite(self):
        suite = suites.CCCreateSetSuite(self.suite_meta, self.db_helper)
        suite.process_cc_id = mock.MagicMock()
        suite.process_topo_select = mock.MagicMock()
        suite.process_topo_select_text = mock.MagicMock()

        component = {
            "data": {
                "biz_cc_id": {"value": 1},
                "cc_set_parent_select": "select",
                "cc_set_parent_select_topo": "topo",
                "cc_set_parent_select_text": "text",
            }
        }
        suite.do(self.node_id, component)
        suite.process_cc_id.assert_called()
        suite.process_topo_select.assert_any_call(self.node_id, "select")
        suite.process_topo_select.assert_any_call(self.node_id, "topo")
        suite.process_topo_select_text.assert_called()

    def test_CCCreateModuleSuite(self):
        suite = suites.CCCreateModuleSuite(self.suite_meta, self.db_helper)
        suite.process_cc_id = mock.MagicMock()
        suite.get_attr_data_or_raise = mock.MagicMock()

        # Case 1: Normal flow with template
        component = {"data": {"biz_cc_id": {"value": 1}, "cc_module_infos_template": "template_key"}}

        suite.get_attr_data_or_raise.return_value = {"value": [{"cc_service_template": "name_1"}]}

        with mock.patch(
            "pipeline_plugins.resource_replacement.suites.cc_get_name_id_from_combine_value"
        ) as mock_get_name:
            mock_get_name.return_value = ("name", 1)
            suite.do(self.node_id, component)

            # Verify template id updated
            attr_data = suite.get_attr_data_or_raise.return_value
            self.assertEqual(attr_data["value"][0]["cc_service_template"], f"name_{1 + self.suite_meta.offset}")

    def test_CCCreateSetBySetTemplateSuite(self):
        suite = suites.CCCreateSetBySetTemplateSuite(self.suite_meta, self.db_helper)
        suite.process_cc_id = mock.MagicMock()  # from super
        suite.get_attr_data_or_raise = mock.MagicMock()

        component = {"data": {"cc_set_template": "template_key"}}

        suite.get_attr_data_or_raise.return_value = {"value": 10}

        suite.do(self.node_id, component)

        attr_data = suite.get_attr_data_or_raise.return_value
        self.assertEqual(attr_data["value"], 10 + self.suite_meta.offset)

    def test_CCUpdateSetServiceStatusSuite(self):
        suite = suites.CCUpdateSetServiceStatusSuite(self.suite_meta, self.db_helper)
        suite.get_attr_data_or_raise = mock.MagicMock()

        component = {"data": {"set_list": "set_list_key"}}

        suite.get_attr_data_or_raise.return_value = {"value": "1,2,3"}

        suite.do(self.node_id, component)

        attr_data = suite.get_attr_data_or_raise.return_value
        # offset is 100
        # 1+100=101, 2+100=102, 3+100=103
        self.assertEqual(attr_data["value"], "101,102,103")

    def test_JobExecuteTaskSuite(self):
        suite = suites.JobExecuteTaskSuite(self.suite_meta, self.db_helper)
        suite.process_cc_id = mock.MagicMock()
        suite.to_new_job_id = mock.MagicMock()
        suite.get_attr_data_or_raise = mock.MagicMock()
        suite.db_helper.fetch_resource_id_map.return_value = {1: 101}
        suite.to_new_ip_list_str_or_raise = mock.MagicMock(return_value="new_ip")

        component = {"data": {"biz_cc_id": {"value": 1}, "job_global_var": "var_key"}}

        suite.get_attr_data_or_raise.return_value = {
            "value": [{"id": 1, "category": 3, "value": "old_ip"}, {"id": 2, "category": 1, "value": "val"}]
        }

        suite.do(self.node_id, component)

        attr_data = suite.get_attr_data_or_raise.return_value
        # id 1 -> 101
        self.assertEqual(attr_data["value"][0]["id"], 101)
        # category 3 -> ip replaced
        self.assertEqual(attr_data["value"][0]["value"], "new_ip")
