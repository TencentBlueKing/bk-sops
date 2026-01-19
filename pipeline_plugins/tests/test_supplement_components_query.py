# -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock, patch

from django.http import JsonResponse
from django.test import RequestFactory, TestCase

from pipeline_plugins.components.query.sites.open.cc import (
    cc_find_host_by_topo,
    cc_get_business,
    cc_get_editable_module_attribute,
    cc_get_editable_set_attribute,
    cc_get_mainline_object_topo,
    cc_get_service_category_topo,
    cc_input_host_property,
    cc_list_service_category,
    cc_list_service_template,
    cc_list_set_template,
    cc_search_create_object_attribute,
    cc_search_dynamic_group,
    cc_search_host,
    cc_search_object_attribute,
    cc_search_object_attribute_all,
    cc_search_status_options,
    cc_search_topo,
    cc_search_topo_tree,
    list_business_set,
)
from pipeline_plugins.components.query.sites.open.job import (
    get_job_account_list,
    job_get_instance_detail,
    job_get_job_task_detail,
    job_get_job_tasks_by_biz,
    job_get_public_script_name_list,
    job_get_script_by_script_version,
    job_get_script_list,
    job_get_script_name_list,
    jobv3_get_instance_list,
    jobv3_get_job_plan_detail,
    jobv3_get_job_plan_list,
    jobv3_get_job_template_list,
)


class ComponentsQuerySupplementTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.username = "admin"
        self.user.tenant_id = "tenant"

    # --- cc.py ---
    @patch("pipeline_plugins.components.query.sites.open.cc.get_client_by_request")
    def test_cc_functions(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        request = self.factory.get("/")
        request.user = self.user

        # cc_search_object_attribute
        client.api.search_object_attribute.return_value = {
            "result": True,
            "data": [{"bk_property_id": "p1", "bk_property_name": "n1", "editable": True, "bk_property_type": "int"}],
        }
        resp = cc_search_object_attribute(request, "obj", 1)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(json.loads(resp.content)["result"])

        # cc_list_service_category
        client.api.list_service_category.return_value = {
            "result": True,
            "data": {"info": [{"id": 1, "name": "c1", "bk_parent_id": 0}]},
        }
        resp = cc_list_service_category(request, 1, 0)
        self.assertEqual(resp.status_code, 200)

        # cc_get_service_category_topo
        resp = cc_get_service_category_topo(request, 1)
        self.assertEqual(resp.status_code, 200)

        # cc_list_service_template
        client.api.list_service_template.return_value = {"result": True, "data": [{"id": 1, "name": "t1"}], "count": 1}
        # Mock batch_request to return data directly
        with patch(
            "pipeline_plugins.components.query.sites.open.cc.batch_request", return_value=[{"id": 1, "name": "t1"}]
        ):
            resp = cc_list_service_template(request, 1)
            self.assertEqual(resp.status_code, 200)

        # cc_search_topo
        client.api.search_biz_inst_topo.return_value = {
            "result": True,
            "data": [{"bk_obj_id": "obj", "bk_inst_id": 1, "bk_inst_name": "name", "child": []}],
        }
        resp = cc_search_topo(request, "obj", "normal", 1)
        self.assertEqual(resp.status_code, 200)

        # list_business_set
        client.api.list_business_set.return_value = {"result": True, "data": {"count": 1}}
        with patch(
            "pipeline_plugins.components.query.sites.open.cc.batch_request",
            return_value=[{"bk_biz_set_id": 1, "bk_biz_set_name": "set"}],
        ):
            resp = list_business_set(request)
            self.assertEqual(resp.status_code, 200)

        # Additional CC tests
        # cc_search_object_attribute_all
        resp = cc_search_object_attribute_all(request, "obj", 1)
        self.assertEqual(resp.status_code, 200)

        # cc_search_create_object_attribute
        resp = cc_search_create_object_attribute(request, "obj", 1)
        self.assertEqual(resp.status_code, 200)

        # wrappers (mock imported functions)
        with patch(
            "pipeline_plugins.components.query.sites.open.cc.cmdb_search_topo_tree",
            return_value=JsonResponse({"result": True}),
        ):
            cc_search_topo_tree(request, 1)
        with patch(
            "pipeline_plugins.components.query.sites.open.cc.cmdb_search_host",
            return_value=JsonResponse({"result": True}),
        ):
            cc_search_host(request, 1)
        with patch(
            "pipeline_plugins.components.query.sites.open.cc.cmdb_get_mainline_object_topo",
            return_value=JsonResponse({"result": True}),
        ):
            cc_get_mainline_object_topo(request, 1)
        with patch(
            "pipeline_plugins.components.query.sites.open.cc.cmdb_search_dynamic_group",
            return_value=JsonResponse({"result": True}),
        ):
            cc_search_dynamic_group(request, 1)

        # cc_get_business
        with patch(
            "pipeline_plugins.components.query.sites.open.cc.get_user_business_list",
            return_value=[{"bk_biz_id": 1, "bk_biz_name": "biz", "bk_data_status": "enable"}],
        ):
            resp = cc_get_business(request)
            self.assertEqual(resp.status_code, 200)

        # cc_list_set_template
        with patch(
            "pipeline_plugins.components.query.sites.open.cc.batch_request", return_value=[{"id": 1, "name": "t1"}]
        ):
            resp = cc_list_set_template(request, 1)
            self.assertEqual(resp.status_code, 200)

        # cc_get_editable_module_attribute
        resp = cc_get_editable_module_attribute(request, 1)
        self.assertEqual(resp.status_code, 200)

        # cc_input_host_property
        resp = cc_input_host_property(request, 1)
        self.assertEqual(resp.status_code, 200)

        # cc_get_editable_set_attribute
        resp = cc_get_editable_set_attribute(request, 1)
        self.assertEqual(resp.status_code, 200)

        # cc_search_status_options
        client.api.search_object_attribute.return_value = {
            "result": True,
            "data": [{"bk_property_id": "bk_service_status", "option": [{"id": 1, "name": "opt1"}]}],
        }
        resp = cc_search_status_options(request, 1)
        self.assertEqual(resp.status_code, 200)

        # cc_find_host_by_topo
        with patch(
            "pipeline_plugins.components.query.sites.open.cc.batch_execute_func",
            return_value=[{"result": {"result": True, "data": {"count": 1}}, "params": {"data": {"bk_inst_id": 1}}}],
        ):
            resp = cc_find_host_by_topo(request, 1)
            self.assertEqual(resp.status_code, 200)

        # cc_search_topo with internal module
        request_internal = self.factory.get("/", {"with_internal_module": "true"})
        request_internal.user = self.user
        client.api.get_biz_internal_module.return_value = {
            "result": True,
            "data": {"bk_set_id": 1, "bk_set_name": "set", "module": [{"bk_module_id": 2, "bk_module_name": "mod"}]},
        }
        resp = cc_search_topo(request_internal, "obj", "normal", 1)
        self.assertEqual(resp.status_code, 200)

        # cc_search_topo prev
        client.api.search_biz_inst_topo.return_value = {
            "result": True,
            "data": [{"bk_obj_id": "other", "bk_inst_id": 1, "bk_inst_name": "name", "child": []}],
        }
        resp = cc_search_topo(request, "obj", "prev", 1)
        self.assertEqual(resp.status_code, 200)

    # --- job.py ---
    @patch("pipeline_plugins.components.query.sites.open.job.settings")
    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_job_functions(self, mock_get_client, mock_settings):
        client = MagicMock()
        mock_get_client.return_value = client
        request = self.factory.get("/")
        request.user = self.user

        # job_get_script_list
        with patch(
            "pipeline_plugins.components.query.sites.open.job.batch_request", return_value=[{"id": 1, "name": "s1"}]
        ):
            resp = job_get_script_list(request, 1)
            self.assertEqual(resp.status_code, 200)

        # job_get_job_tasks_by_biz
        with patch(
            "pipeline_plugins.components.query.sites.open.job.batch_request", return_value=[{"id": 1, "name": "t1"}]
        ):
            resp = job_get_job_tasks_by_biz(request, 1)
            self.assertEqual(resp.status_code, 200)

        # job_get_job_task_detail
        client.api.get_job_plan_detail.return_value = {
            "result": True,
            "data": {
                "global_var_list": [{"id": 1, "type": 1, "name": "v1", "value": "val", "description": "desc"}],
                "step_list": [{"id": 1, "name": "step1", "type": 1, "script_info": {}}],
            },
        }
        resp = job_get_job_task_detail(request, 1, 1)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(json.loads(resp.content)["result"])

        # jobv3_get_job_plan_detail
        # Use same mock return as above logic is similar
        resp = jobv3_get_job_plan_detail(request, 1, 1)
        self.assertEqual(resp.status_code, 200)

        # jobv3_get_instance_list
        client.api.get_job_instance_list.return_value = {
            "result": True,
            "data": {"data": [{"job_instance_id": 1, "name": "job1"}]},
        }
        resp = jobv3_get_instance_list(request, 1, 1, 1)
        self.assertEqual(resp.status_code, 200)

        # job_get_job_task_detail with IP vars
        mock_settings.ENABLE_IPV6 = True
        client.api.get_job_plan_detail.return_value = {
            "result": True,
            "data": {
                "global_var_list": [
                    {
                        "id": 1,
                        "type": 3,
                        "name": "ip",
                        "value": "",
                        "description": "",
                        "server": {"ip_list": [{"bk_host_id": 1, "ip": "1.1.1.1", "bk_cloud_id": 0}]},
                    }
                ],
                "step_list": [],
            },
        }
        with patch("pipeline_plugins.components.query.sites.open.job.get_business_set_host") as mock_get_host:
            mock_get_host.return_value = [{"bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}]
            resp = job_get_job_task_detail(request, 1, 1)
            self.assertEqual(resp.status_code, 200)

        # Additional Job tests
        # job_get_script_name_list
        with patch(
            "pipeline_plugins.components.query.sites.open.job._job_get_scripts_data",
            return_value=[{"name": "s1", "online_script_version_id": 1}],
        ):
            resp = job_get_script_name_list(request, 1)
            self.assertEqual(resp.status_code, 200)

        # job_get_public_script_name_list
        with patch(
            "pipeline_plugins.components.query.sites.open.job._job_get_scripts_data",
            return_value=[{"name": "s1", "online_script_version_id": 1}],
        ):
            resp = job_get_public_script_name_list(request)
            self.assertEqual(resp.status_code, 200)

        # job_get_script_by_script_version
        client.api.get_script_version_detail.return_value = {"result": True, "data": {"name": "s1"}}
        resp = job_get_script_by_script_version(request, 1)
        self.assertEqual(resp.status_code, 200)

        # jobv3_get_job_template_list
        with patch(
            "pipeline_plugins.components.query.sites.open.job.batch_request", return_value=[{"id": 1, "name": "t1"}]
        ):
            resp = jobv3_get_job_template_list(request, 1)
            self.assertEqual(resp.status_code, 200)

        # jobv3_get_job_plan_list
        with patch(
            "pipeline_plugins.components.query.sites.open.job.batch_request", return_value=[{"id": 1, "name": "p1"}]
        ):
            resp = jobv3_get_job_plan_list(request, 1, 1)
            self.assertEqual(resp.status_code, 200)

        # get_job_account_list
        with patch("pipeline_plugins.components.query.sites.open.job.batch_request", return_value=[{"alias": "a1"}]):
            resp = get_job_account_list(request, 1)
            self.assertEqual(resp.status_code, 200)

        # job_get_instance_detail
        client.api.get_job_instance_ip_log.return_value = {
            "result": True,
            "data": [
                {
                    "step_instance_id": 1,
                    "step_results": [{"ip_logs": [{"ip": "1.1.1.1", "log_content": "log", "exit_code": 0}]}],
                }
            ],
        }
        resp = job_get_instance_detail(request, 1, 1)
        self.assertEqual(resp.status_code, 200)
