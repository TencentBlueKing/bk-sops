# -*- coding: utf-8 -*-
import logging

from django.test import TestCase
from mock import MagicMock, patch
from pipeline.core.data.base import DataObject

from pipeline_plugins.components.collections.sites.open.job.base import JobScheduleService

logger = logging.getLogger(__name__)


class JobScheduleServiceTests(TestCase):
    def setUp(self):
        self.service = JobScheduleService()
        self.service.logger = logger
        self.data = DataObject({"biz_cc_id": 2})
        self.parent_data = DataObject({"executor": "user", "tenant_id": "system"})
        self.data.set_outputs("job_id_of_batch_execute", [1, 2])
        self.data.set_outputs("job_inst_url", ["http://job/detail/1", "http://job/detail/2"])
        self.data.set_outputs("success_count", 0)
        self.data.set_outputs("request_success_count", 1)
        self.data.set_outputs("final_res", True)

    @patch("pipeline_plugins.components.collections.sites.open.job.base.batch_execute_func")
    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    def test_schedule_finish_success(self, mock_get_client, mock_batch):
        # 一个成功，一个失败，结束时根据 final_res 和计数返回
        mock_get_client.return_value = type("C", (), {"api": MagicMock(get_job_instance_status=MagicMock())})()
        mock_batch.return_value = [
            {
                "params": {"data": {"job_instance_id": 1}},
                "result": {"result": True, "data": {"job_instance": {"status": 3}}},
            },
            {
                "params": {"data": {"job_instance_id": 2}},
                "result": {"result": False, "message": "error"},
            },
        ]
        res = self.service.schedule(self.data, self.parent_data)
        self.assertIsInstance(res, bool)
        self.assertTrue(res)
        self.assertEqual(self.data.outputs.success_count, 1)
        self.assertEqual(self.data.outputs.job_id_of_batch_execute, [])
        # 有失败时 ex_data 会追加失败链接
        self.assertIn("任务执行失败", self.data.outputs.ex_data)
