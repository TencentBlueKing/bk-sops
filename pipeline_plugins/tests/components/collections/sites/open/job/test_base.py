# -*- coding: utf-8 -*-
import mock
from django.test import TestCase

from pipeline_plugins.components.collections.sites.open.job.base import (
    GetJobHistoryResultMixin,
    JobScheduleService,
    JobService,
    Jobv3ScheduleService,
    Jobv3Service,
    get_ip_from_step_ip_result,
    get_job_instance_log,
    get_job_sops_var_dict,
    get_job_tagged_ip_dict,
    get_job_tagged_ip_dict_complex,
    get_sops_var_dict_from_log_text,
)


class JobBaseUtilsTestCase(TestCase):
    def test_get_sops_var_dict_from_log_text(self):
        service_logger = mock.MagicMock()
        log_text = "<SOPS_VAR>key1:value1</SOPS_VAR>\n<SOPS_VAR>key2:value2</SOPS_VAR>"
        result = get_sops_var_dict_from_log_text(log_text, service_logger)
        self.assertEqual(result, {"key1": "value1", "key2": "value2"})

        log_text_escaped = "&lt;SOPS_VAR&gt;key1:value1&lt;/SOPS_VAR&gt;"
        result = get_sops_var_dict_from_log_text(log_text_escaped, service_logger)
        self.assertEqual(result, {"key1": "value1"})

        # Test empty or invalid
        log_text = "some log"
        result = get_sops_var_dict_from_log_text(log_text, service_logger)
        self.assertEqual(result, {})

        # Test empty key
        log_text = "<SOPS_VAR>:value1</SOPS_VAR>"
        result = get_sops_var_dict_from_log_text(log_text, service_logger)
        self.assertEqual(result, {})

    def test_get_ip_from_step_ip_result(self):
        # IPv4
        res = {"ip": "1.1.1.1"}
        self.assertEqual(get_ip_from_step_ip_result(res), "1.1.1.1")
        # IPv6
        res = {"ip": "", "ipv6": "::1"}
        self.assertEqual(get_ip_from_step_ip_result(res), "::1")
        # None
        res = {}
        self.assertEqual(get_ip_from_step_ip_result(res), "")

    def test_get_job_instance_log(self):
        tenant_id = "tenant"
        client = mock.MagicMock()
        service_logger = mock.MagicMock()
        job_instance_id = 1
        bk_biz_id = 1

        # Case 1: get_job_instance_status fail
        client.api.get_job_instance_status.return_value = {"result": False, "message": "error", "code": 1}
        result = get_job_instance_log(tenant_id, client, service_logger, job_instance_id, bk_biz_id)
        self.assertFalse(result["result"])

        # Case 2: Success
        client.api.get_job_instance_status.return_value = {
            "result": True,
            "data": {
                "step_instance_list": [
                    {"step_instance_id": 100, "step_ip_result_list": [{"ip": "1.1.1.1", "bk_cloud_id": 0}]}
                ]
            },
        }
        client.api.get_job_instance_ip_log.return_value = {"result": True, "data": {"log_content": "log"}}
        result = get_job_instance_log(tenant_id, client, service_logger, job_instance_id, bk_biz_id)
        self.assertTrue(result["result"])
        self.assertEqual(result["data"], "log")

        # Case 3: Target IP
        result = get_job_instance_log(
            tenant_id, client, service_logger, job_instance_id, bk_biz_id, target_ip="1.1.1.1"
        )
        self.assertTrue(result["result"])

        # Case 4: Target IP not found
        result = get_job_instance_log(
            tenant_id, client, service_logger, job_instance_id, bk_biz_id, target_ip="2.2.2.2"
        )
        self.assertFalse(result["result"])

        # Case 5: ip log fail
        client.api.get_job_instance_ip_log.return_value = {"result": False, "message": "err", "code": 1}
        result = get_job_instance_log(tenant_id, client, service_logger, job_instance_id, bk_biz_id)
        self.assertFalse(result["result"])

    def test_get_job_tagged_ip_dict(self):
        tenant_id = "tenant"
        client = mock.MagicMock()
        service_logger = mock.MagicMock()
        job_instance_id = 1
        bk_biz_id = 1

        # Fail
        client.api.get_job_instance_status.return_value = {"result": False, "message": "error", "code": 1}
        result, data = get_job_tagged_ip_dict(tenant_id, client, service_logger, job_instance_id, bk_biz_id)
        self.assertFalse(result)

        # Success
        client.api.get_job_instance_status.return_value = {
            "result": True,
            "data": {
                "step_instance_list": [
                    {
                        "step_ip_result_list": [
                            {"ip": "1.1.1.1", "tag": "tag1"},
                            {"ip": "2.2.2.2", "tag": "tag1"},
                            {"ip": "3.3.3.3", "tag": ""},
                        ]
                    }
                ]
            },
        }
        result, data = get_job_tagged_ip_dict(tenant_id, client, service_logger, job_instance_id, bk_biz_id)
        self.assertTrue(result)
        self.assertEqual(data["tag1"], "1.1.1.1,2.2.2.2")

    def test_get_job_tagged_ip_dict_complex(self):
        tenant_id = "tenant"
        client = mock.MagicMock()
        service_logger = mock.MagicMock()
        job_instance_id = 1
        bk_biz_id = 1

        # Fail
        client.api.get_job_instance_status.return_value = {"result": False, "message": "error", "code": 1}
        result, data = get_job_tagged_ip_dict_complex(tenant_id, client, service_logger, job_instance_id, bk_biz_id)
        self.assertFalse(result)

        # Success
        client.api.get_job_instance_status.return_value = {
            "result": True,
            "data": {
                "step_instance_list": [
                    {
                        "step_ip_result_list": [
                            {"ip": "1.1.1.1", "tag": "tag1", "status": 9},  # Success
                            {"ip": "2.2.2.2", "tag": "tag2", "status": 104},  # Script failed
                            {"ip": "3.3.3.3", "tag": "tag3", "status": 11},  # Other failed
                        ]
                    }
                ]
            },
        }
        result, data = get_job_tagged_ip_dict_complex(tenant_id, client, service_logger, job_instance_id, bk_biz_id)
        self.assertTrue(result)
        value = data["value"]
        self.assertTrue("1.1.1.1" in value["SUCCESS"]["TAGS"]["tag1"])
        self.assertTrue("2.2.2.2" in value["SCRIPT_NOT_ZERO_EXIT_CODE"]["TAGS"]["tag2"])
        # Status 11 maps to FAILED
        self.assertTrue("3.3.3.3" in value["OTHER_FAILED"]["TAGS"]["FAILED"])

    def test_get_job_sops_var_dict(self):
        tenant_id = "tenant"
        client = mock.MagicMock()
        service_logger = mock.MagicMock()
        job_instance_id = 1
        bk_biz_id = 1

        with mock.patch(
            "pipeline_plugins.components.collections.sites.open.job.base.get_job_instance_log"
        ) as mock_get_log:
            mock_get_log.return_value = {"result": False, "message": "err"}
            result = get_job_sops_var_dict(tenant_id, client, service_logger, job_instance_id, bk_biz_id)
            self.assertFalse(result["result"])

            mock_get_log.return_value = {"result": True, "data": "<SOPS_VAR>k:v</SOPS_VAR>"}
            result = get_job_sops_var_dict(tenant_id, client, service_logger, job_instance_id, bk_biz_id)
            self.assertTrue(result["result"])
            self.assertEqual(result["data"], {"k": "v"})


class JobServiceTestCase(TestCase):
    def test_outputs_format(self):
        service = JobService()
        formats = service.outputs_format()
        self.assertEqual(len(formats), 2)
        self.assertEqual(formats[0].key, "job_inst_id")


class JobServiceScheduleTestCase(TestCase):
    def setUp(self):
        self.service = JobService()
        self.service.logger = mock.MagicMock()
        self.data = mock.MagicMock()
        self.parent_data = mock.MagicMock()
        self.callback_data = {"job_instance_id": 100, "status": 3}

    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_job_sops_var_dict")
    def test_schedule_success(self, mock_get_sops_vars, mock_get_client):
        # Setup
        self.data.get_one_of_inputs.return_value = "executor"
        self.parent_data.get_one_of_inputs.return_value = "executor"
        self.parent_data.inputs.tenant_id = "tenant"
        self.parent_data.inputs.biz_cc_id = 1

        client = mock.MagicMock()
        mock_get_client.return_value = client

        # Mock global var result
        client.api.get_job_instance_global_var_value.return_value = {
            "result": True,
            "data": {"step_instance_var_list": [{"global_var_list": [{"type": 1, "name": "var1", "value": "val1"}]}]},
        }

        # Mock sops var result
        mock_get_sops_vars.return_value = {"result": True, "data": {"k": "v"}}

        # Run
        result = self.service.schedule(self.data, self.parent_data, self.callback_data)

        # Verify
        self.assertTrue(result)
        self.service.logger.info.assert_called()
        self.data.set_outputs.assert_any_call("var1", "val1")
        self.data.set_outputs.assert_any_call("log_outputs", {"k": "v"})

    def test_schedule_invalid_callback(self):
        result = self.service.schedule(self.data, self.parent_data, {})
        self.assertFalse(result)
        self.assertTrue(self.data.outputs.ex_data)

    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    def test_schedule_fail_status(self, mock_get_client):
        callback_data = {"job_instance_id": 100, "status": 4}  # 4 is failed
        self.data.get_one_of_inputs.return_value = False  # need_log_outputs_even_fail

        result = self.service.schedule(self.data, self.parent_data, callback_data)

        self.assertFalse(result)
        # Should set ex_data
        self.data.set_outputs.assert_called()


class JobScheduleServiceTestCase(TestCase):
    def setUp(self):
        self.service = JobScheduleService()
        self.service.logger = mock.MagicMock()
        self.data = mock.MagicMock()
        self.parent_data = mock.MagicMock()

    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.batch_execute_func")
    def test_schedule(self, mock_batch_exec, mock_get_client):
        self.data.outputs.job_id_of_batch_execute = [100, 101]
        self.data.outputs.job_inst_url = ["url_100", "url_101"]
        self.data.outputs.success_count = 0
        self.data.outputs.request_success_count = 2

        client = mock.MagicMock()
        mock_get_client.return_value = client

        # Mock batch result
        # 100 success (3), 101 running (2)
        mock_batch_exec.return_value = [
            {
                "result": {"result": True, "data": {"job_instance": {"status": 3}}},
                "params": {"data": {"job_instance_id": 100}},
            },
            {
                "result": {"result": True, "data": {"job_instance": {"status": 2}}},
                "params": {"data": {"job_instance_id": 101}},
            },
        ]

        result = self.service.schedule(self.data, self.parent_data)

        # Result should be False because 101 is still running
        self.assertFalse(result)
        self.assertEqual(self.data.outputs.job_id_of_batch_execute, [101])
        self.assertEqual(self.data.outputs.success_count, 1)

    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.batch_execute_func")
    def test_schedule_all_finished(self, mock_batch_exec, mock_get_client):
        self.data.outputs.job_id_of_batch_execute = [100]
        self.data.outputs.success_count = 0
        self.data.outputs.request_success_count = 1
        self.data.outputs.final_res = True

        mock_batch_exec.return_value = [
            {
                "result": {"result": True, "data": {"job_instance": {"status": 3}}},
                "params": {"data": {"job_instance_id": 100}},
            }
        ]

        result = self.service.schedule(self.data, self.parent_data)

        self.assertTrue(result)


class Jobv3ServiceTestCase(TestCase):
    def setUp(self):
        self.service = Jobv3Service()
        self.service.logger = mock.MagicMock()
        self.data = mock.MagicMock()
        self.parent_data = mock.MagicMock()
        self.callback_data = {"job_instance_id": 100, "status": 3}

    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_job_sops_var_dict")
    def test_schedule_success(self, mock_get_sops_vars, mock_get_client):
        # Setup
        self.service.need_get_sops_var = True
        self.data.get_one_of_inputs.return_value = "executor"
        self.parent_data.get_one_of_inputs.return_value = "executor"
        self.parent_data.inputs.tenant_id = "tenant"
        self.parent_data.inputs.biz_cc_id = 1

        client = mock.MagicMock()
        mock_get_client.return_value = client

        # Mock global var result
        client.api.get_job_instance_global_var_value.return_value = {
            "result": True,
            "data": {"step_instance_var_list": [{"global_var_list": [{"type": 1, "name": "var1", "value": "val1"}]}]},
        }

        # Mock sops var result
        mock_get_sops_vars.return_value = {"result": True, "data": {"k": "v"}}

        # Run
        result = self.service.schedule(self.data, self.parent_data, self.callback_data)

        # Verify
        self.assertTrue(result)
        self.service.logger.info.assert_called()
        self.data.set_outputs.assert_any_call("var1", "val1")
        self.data.set_outputs.assert_any_call("log_outputs", {"k": "v"})


class Jobv3ScheduleServiceTestCase(TestCase):
    def setUp(self):
        self.service = Jobv3ScheduleService()
        self.service.logger = mock.MagicMock()
        self.data = mock.MagicMock()
        self.parent_data = mock.MagicMock()

    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.batch_execute_func")
    def test_schedule(self, mock_batch_exec, mock_get_client):
        self.data.outputs.job_id_of_batch_execute = [100]
        self.data.outputs.job_inst_url = ["url_100"]
        self.data.outputs.success_count = 0
        self.data.outputs.request_success_count = 1
        self.data.outputs.final_res = True

        client = mock.MagicMock()
        mock_get_client.return_value = client

        # Mock batch result for Jobv3
        mock_batch_exec.return_value = [
            {
                "result": {
                    "result": True,
                    "data": [{"status": 3, "step_results": [{"ip_logs": [{"log_content": "content"}]}]}],
                },
                "params": {"data": {"job_instance_id": 100}},
            }
        ]

        result = self.service.schedule(self.data, self.parent_data)

        self.assertTrue(result)
        self.assertEqual(self.data.outputs.success_count, 1)


class GetJobHistoryResultMixinTestCase(TestCase):
    def setUp(self):
        self.mixin = GetJobHistoryResultMixin()
        self.mixin.logger = mock.MagicMock()
        self.mixin.need_get_sops_var = True
        self.data = mock.MagicMock()
        self.parent_data = mock.MagicMock()

    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_job_sops_var_dict")
    def test_get_job_history_result_success(self, mock_get_sops_vars, mock_get_client):
        client = mock.MagicMock()
        mock_get_client.return_value = client

        client.api.get_job_instance_status.return_value = {
            "result": True,
            "data": {"job_instance": {"status": 3}},  # 3 is success
        }

        mock_get_sops_vars.return_value = {"result": True, "data": {"k": "v"}}

        result = self.mixin.get_job_history_result(self.data, self.parent_data)

        self.assertTrue(result)
        self.data.set_outputs.assert_called_with("log_outputs", {"k": "v"})

    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    def test_get_job_history_result_fail(self, mock_get_client):
        client = mock.MagicMock()
        mock_get_client.return_value = client

        client.api.get_job_instance_status.return_value = {
            "result": True,
            "data": {"job_instance": {"status": 4}},  # 4 is failed
        }

        result = self.mixin.get_job_history_result(self.data, self.parent_data)

        self.assertFalse(result)
