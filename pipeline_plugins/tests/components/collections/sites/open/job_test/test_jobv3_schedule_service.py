# -*- coding: utf-8 -*-
import logging

from django.test import TestCase
from mock import MagicMock, patch
from pipeline.core.data.base import DataObject

from pipeline_plugins.components.collections.sites.open.job.base import Jobv3ScheduleService

logger = logging.getLogger(__name__)


class Jobv3ScheduleServiceTests(TestCase):
    def setUp(self):
        self.service = Jobv3ScheduleService()
        self.service.logger = logger
        self.data = DataObject({"biz_cc_id": 2})
        self.parent_data = DataObject({"executor": "user", "tenant_id": "system"})
        self.data.set_outputs("job_id_of_batch_execute", [1])
        self.data.set_outputs("job_inst_url", ["http://job/detail/1"])
        self.data.set_outputs("success_count", 0)
        self.data.set_outputs("request_success_count", 1)
        self.data.set_outputs("final_res", True)

    @patch("pipeline_plugins.components.collections.sites.open.job.base.batch_execute_func")
    @patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    def test_schedule_finish_with_log_error_message(self, mock_get_client, mock_batch):
        mock_get_client.return_value = type("C", (), {"api": MagicMock(get_job_instance_status=MagicMock())})()
        mock_batch.return_value = [
            {
                "params": {"data": {"job_instance_id": 1}},
                "result": {
                    "result": True,
                    "data": [
                        {
                            "status": 4,
                            "step_results": [{"ip_logs": [{"log_content": "detail error"}]}],
                        }
                    ],
                },
            }
        ]
        res = self.service.schedule(self.data, self.parent_data)
        # 结束调度并返回 overall 结果
        self.assertIsInstance(res, bool)
        self.assertFalse(res)
        self.assertIn("错误信息", self.data.outputs.ex_data)
        self.assertEqual(self.data.outputs.job_id_of_batch_execute, [])
