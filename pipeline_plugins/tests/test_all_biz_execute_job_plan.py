# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import TestCase

from pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.v1_1 import (
    AllBizJobExecuteJobPlanService,
)


class AllBizJobExecuteJobPlanServiceTestCase(TestCase):
    def setUp(self):
        self.service = AllBizJobExecuteJobPlanService()
        self.service.logger = MagicMock()

    def test_outputs_format(self):
        outputs = self.service.outputs_format()
        self.assertTrue(any(item.key == "job_tagged_ip_dict" for item in outputs))

    def test_is_need_log_outputs_even_fail(self):
        self.assertTrue(self.service.is_need_log_outputs_even_fail({}))

    @patch(
        "pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.v1_1.get_client_by_username"
    )
    @patch(
        "pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.v1_1."
        "get_job_tagged_ip_dict_complex"
    )
    def test_get_tagged_ip_dict(self, mock_get_ip_dict, mock_get_client):
        data = MagicMock()
        parent_data = MagicMock()
        job_instance_id = 123

        data.get_one_of_inputs.return_value = "biz_cc_id"
        parent_data.get_one_of_inputs.side_effect = (
            lambda x, default=None: "executor" if x == "executor" else "tenant_id"
        )

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_get_ip_dict.return_value = (True, {"tag": "ip"})

        result, tagged_ip_dict = self.service.get_tagged_ip_dict(data, parent_data, job_instance_id)

        self.assertTrue(result)
        self.assertEqual(tagged_ip_dict, {"tag": "ip"})

        mock_get_client.assert_called_with("executor", stage=settings.BK_APIGW_STAGE_NAME)
        mock_get_ip_dict.assert_called()
