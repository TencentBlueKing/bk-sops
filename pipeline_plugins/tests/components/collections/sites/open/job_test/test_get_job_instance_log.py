# -*- coding: utf-8 -*-
import logging

from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.sites.open.job.base import get_job_instance_log

logger = logging.getLogger(__name__)


class MockClient(object):
    def __init__(self, status_return, ip_log_return):
        self.api = MagicMock()
        self.api.get_job_instance_status = MagicMock(return_value=status_return)
        self.api.get_job_instance_ip_log = MagicMock(return_value=ip_log_return)


GET_STATUS_OK = {
    "result": True,
    "data": {
        "step_instance_list": [
            {
                "step_instance_id": 1001,
                "bk_host_id": None,
                "step_ip_result_list": [
                    {"ip": "1.1.1.1", "bk_cloud_id": 0},
                    {"ip": "1.1.1.2", "bk_cloud_id": 0},
                ],
            }
        ]
    },
}

GET_STATUS_OK_IPV6 = {
    "result": True,
    "data": {
        "step_instance_list": [
            {
                "step_instance_id": 1001,
                "bk_host_id": 9999,
                "step_ip_result_list": [
                    {"ip": "fe80::1", "ipv6": "fe80::1", "bk_cloud_id": 0},
                ],
            }
        ]
    },
}

GET_IP_LOG_OK = {"result": True, "data": {"log_content": "log1"}}
GET_IP_LOG_OK_2 = {"result": True, "data": {"log_content": "log2"}}
GET_STATUS_FAIL = {"result": False, "message": "error"}
GET_IP_LOG_FAIL = {"result": False, "message": "ip log error"}


class GetJobInstanceLogTests(TestCase):
    @patch("pipeline_plugins.components.collections.sites.open.job.base.settings.ENABLE_IPV6", False)
    def test_success_collect_default_ip(self):
        client = MockClient(GET_STATUS_OK, GET_IP_LOG_OK)
        result = get_job_instance_log(
            tenant_id="system",
            client=client,
            service_logger=logger,
            job_instance_id=1,
            bk_biz_id=2,
        )
        self.assertTrue(result["result"])
        self.assertEqual(result["data"], "log1")
        client.api.get_job_instance_status.assert_called_once()
        client.api.get_job_instance_ip_log.assert_called_once()

    @patch("pipeline_plugins.components.collections.sites.open.job.base.settings.ENABLE_IPV6", False)
    def test_target_ip_not_in_result(self):
        client = MockClient(GET_STATUS_OK, GET_IP_LOG_OK)
        result = get_job_instance_log(
            tenant_id="system",
            client=client,
            service_logger=logger,
            job_instance_id=1,
            bk_biz_id=2,
            target_ip="9.9.9.9",
        )
        self.assertFalse(result["result"])
        self.assertIn("不属于IP列表", result["message"])

    @patch("pipeline_plugins.components.collections.sites.open.job.base.settings.ENABLE_IPV6", True)
    def test_ipv6_with_bk_host_id_uses_bk_host_id(self):
        client = MockClient(GET_STATUS_OK_IPV6, GET_IP_LOG_OK)
        result = get_job_instance_log(
            tenant_id="system",
            client=client,
            service_logger=logger,
            job_instance_id=1,
            bk_biz_id=2,
        )
        self.assertTrue(result["result"])
        # 验证调用时优先使用 bk_host_id 而不是 ip
        call_kwargs = client.api.get_job_instance_ip_log.call_args[0][0]
        self.assertIn("bk_host_id", call_kwargs)
        self.assertNotIn("ip", call_kwargs)

    def test_status_api_fail(self):
        client = MockClient(GET_STATUS_FAIL, GET_IP_LOG_OK)
        result = get_job_instance_log(
            tenant_id="system",
            client=client,
            service_logger=logger,
            job_instance_id=1,
            bk_biz_id=2,
        )
        self.assertFalse(result["result"])
        self.assertIn("调用作业平台(JOB)接口", result["message"])

    def test_ip_log_api_fail(self):
        client = MockClient(GET_STATUS_OK, GET_IP_LOG_FAIL)
        result = get_job_instance_log(
            tenant_id="system",
            client=client,
            service_logger=logger,
            job_instance_id=1,
            bk_biz_id=2,
        )
        self.assertFalse(result["result"])
        self.assertIn("调用作业平台(JOB)接口", result["message"])

    def test_empty_step_ip_result_list(self):
        status = {"result": True, "data": {"step_instance_list": [{"step_instance_id": 1, "step_ip_result_list": []}]}}
        client = MockClient(status, GET_IP_LOG_OK)
        result = get_job_instance_log(
            tenant_id="system",
            client=client,
            service_logger=logger,
            job_instance_id=1,
            bk_biz_id=2,
        )
        self.assertTrue(result["result"])
        self.assertEqual(result["data"], "")
