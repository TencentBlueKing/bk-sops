# -*- coding: utf-8 -*-
import logging

from django.test import TestCase
from mock import MagicMock, patch
from pipeline.core.data.base import DataObject

from pipeline_plugins.components.collections.sites.open.job.base import JobService, Jobv3Service

logger = logging.getLogger(__name__)


class MinimalJobService(JobService):
    need_get_sops_var = False
    need_is_tagged_ip = False
    reload_outputs = True


class JobServiceScheduleTests(TestCase):
    def setUp(self):
        self.service = MinimalJobService()
        self.service.logger = logger
        self.callback_success = {"job_instance_id": 1, "status": 3}
        self.callback_fail = {"job_instance_id": 1, "status": 4}
        self.data = DataObject(
            {
                "biz_cc_id": 2,
                "need_log_outputs_even_fail": False,
                "is_tagged_ip": False,
            }
        )
        self.parent_data = DataObject({"executor": "user", "tenant_id": "system", "biz_cc_id": 2})
        self.data.set_outputs("job_inst_url", "http://job/detail/1")

    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    def test_schedule_success_without_log_var(self, mock_get_client):
        client = MagicMock()
        client.api.get_job_instance_global_var_value = MagicMock(
            return_value={"result": True, "data": {"step_instance_var_list": [{"global_var_list": []}]}}
        )
        mock_get_client.return_value = client
        result = self.service.schedule(self.data, self.parent_data, self.callback_success)
        self.assertTrue(result)
        # 未设置 log_outputs
        self.assertNotIn("log_outputs", self.data.outputs)

    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_job_sops_var_dict")
    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    def test_schedule_fail_with_need_log_even_fail(self, mock_get_client, mock_get_log_vars):
        # 失败但仍需提取日志变量
        self.data.inputs["need_log_outputs_even_fail"] = True
        client = MagicMock()
        client.api.get_job_instance_global_var_value = MagicMock(
            return_value={"result": True, "data": {"step_instance_var_list": [{"global_var_list": []}]}}
        )
        mock_get_client.return_value = client
        mock_get_log_vars.return_value = {"result": True, "data": {"k": "v"}}
        result = self.service.schedule(self.data, self.parent_data, self.callback_fail)
        self.assertFalse(result)
        self.assertEqual(self.data.outputs["log_outputs"], {"k": "v"})
        self.assertIn("exception_msg", self.data.outputs["ex_data"])

    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_job_tagged_ip_dict")
    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    def test_schedule_with_tagged_ip(self, mock_get_client, mock_get_tagged):
        # 启用 IP 分组
        self.service.need_is_tagged_ip = True
        self.data.inputs["is_tagged_ip"] = True
        client = MagicMock()
        client.api.get_job_instance_global_var_value = MagicMock(
            return_value={"result": True, "data": {"step_instance_var_list": [{"global_var_list": []}]}}
        )
        mock_get_client.return_value = client
        mock_get_tagged.return_value = (True, {"success-1": "1.1.1.1"})
        result = self.service.schedule(self.data, self.parent_data, self.callback_success)
        self.assertTrue(result)
        self.assertEqual(self.data.outputs["job_tagged_ip_dict"], {"success-1": "1.1.1.1"})

    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_job_tagged_ip_dict")
    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    def test_schedule_tagged_ip_fail(self, mock_get_client, mock_get_tagged):
        self.service.need_is_tagged_ip = True
        self.data.inputs["is_tagged_ip"] = True
        client = MagicMock()
        client.api.get_job_instance_global_var_value = MagicMock(
            return_value={"result": True, "data": {"step_instance_var_list": [{"global_var_list": []}]}}
        )
        mock_get_client.return_value = client
        mock_get_tagged.return_value = (False, "error")
        result = self.service.schedule(self.data, self.parent_data, self.callback_success)
        self.assertFalse(result)
        self.assertEqual(self.data.outputs["ex_data"], "error")

    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_job_sops_var_dict")
    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    def test_schedule_log_extract_fail(self, mock_get_client, mock_get_log_vars):
        # 失败提取日志分支
        self.service.need_get_sops_var = True
        client = MagicMock()
        client.api.get_job_instance_global_var_value = MagicMock(
            return_value={"result": True, "data": {"step_instance_var_list": [{"global_var_list": []}]}}
        )
        mock_get_client.return_value = client
        mock_get_log_vars.return_value = {"result": False, "message": "extract error"}
        result = self.service.schedule(self.data, self.parent_data, self.callback_success)
        self.assertFalse(result)
        self.assertEqual(self.data.outputs["log_outputs"], {})


class MinimalJobv3Service(Jobv3Service):
    need_get_sops_var = False
    need_is_tagged_ip = False
    reload_outputs = True


class Jobv3ServiceScheduleTests(TestCase):
    def setUp(self):
        self.service = MinimalJobv3Service()
        self.service.logger = logger
        self.callback_success = {"job_instance_id": 1, "status": 3}
        self.callback_fail = {"job_instance_id": 1, "status": 4}
        self.data = DataObject(
            {
                "biz_cc_id": 2,
                "need_log_outputs_even_fail": False,
                "is_tagged_ip": False,
            }
        )
        self.parent_data = DataObject({"executor": "user", "tenant_id": "system", "biz_cc_id": 2})

    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    def test_schedule_success(self, mock_get_client):
        client = MagicMock()
        client.api.get_job_instance_global_var_value = MagicMock(
            return_value={"result": True, "data": {"step_instance_var_list": [{"global_var_list": []}]}}
        )
        mock_get_client.return_value = client
        result = self.service.schedule(self.data, self.parent_data, self.callback_success)
        self.assertTrue(result)

    def test_invalid_callback(self):
        # 非法 callback 导致异常分支
        result = self.service.schedule(self.data, self.parent_data, None)
        self.assertFalse(result)
        self.assertIn("invalid callback_data", self.data.outputs["ex_data"])

    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_job_tagged_ip_dict")
    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    def test_tagged_ip_fail(self, mock_get_client, mock_get_tagged):
        self.service.need_is_tagged_ip = True
        self.data.inputs["is_tagged_ip"] = True
        client = MagicMock()
        client.api.get_job_instance_global_var_value = MagicMock(
            return_value={"result": True, "data": {"step_instance_var_list": [{"global_var_list": []}]}}
        )
        mock_get_client.return_value = client
        mock_get_tagged.return_value = (False, "error")
        result = self.service.schedule(self.data, self.parent_data, self.callback_success)
        self.assertFalse(result)
        self.assertEqual(self.data.outputs["ex_data"], "error")

    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_job_sops_var_dict")
    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    def test_log_extract_fail_should_still_success(self, mock_get_client, mock_get_log_vars):
        # 日志提取失败时返回 True（job 成功）
        self.service.need_get_sops_var = True
        client = MagicMock()
        client.api.get_job_instance_global_var_value = MagicMock(
            return_value={"result": True, "data": {"step_instance_var_list": [{"global_var_list": []}]}}
        )
        mock_get_client.return_value = client
        mock_get_log_vars.return_value = {"result": False, "message": "extract error"}
        result = self.service.schedule(self.data, self.parent_data, self.callback_success)
        self.assertTrue(result)
        self.assertEqual(self.data.outputs["log_outputs"], {})
