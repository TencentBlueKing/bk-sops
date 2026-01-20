# -*- coding: utf-8 -*-
import logging

from django.test import TestCase
from mock import MagicMock

from pipeline_plugins.components.collections.sites.open.job.base import get_job_sops_var_dict

logger = logging.getLogger(__name__)


class MockClient(object):
    def __init__(self, status_return, ip_log_return):
        self.api = MagicMock()
        self.api.get_job_instance_status = MagicMock(return_value=status_return)
        self.api.get_job_instance_ip_log = MagicMock(return_value=ip_log_return)


class GetJobSopsVarDictTests(TestCase):
    def test_honor_log_fetch_fail(self):
        status = {"result": False, "message": "error"}
        client = MockClient(status, {"result": True, "data": {"log_content": "log"}})
        result = get_job_sops_var_dict(
            tenant_id="system",
            client=client,
            service_logger=logger,
            job_instance_id=1,
            bk_biz_id=2,
        )
        self.assertFalse(result["result"])
        self.assertIn("error", result["message"])
