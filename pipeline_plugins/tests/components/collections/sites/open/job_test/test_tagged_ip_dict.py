# -*- coding: utf-8 -*-
import logging

from django.test import TestCase
from mock import MagicMock

from pipeline_plugins.components.collections.sites.open.job.base import (
    get_job_tagged_ip_dict,
    get_job_tagged_ip_dict_complex,
)

logger = logging.getLogger(__name__)


class MockClient(object):
    def __init__(self, status_return):
        self.api = MagicMock()
        self.api.get_job_instance_status = MagicMock(return_value=status_return)


GET_STATUS_TAGGED = {
    "result": True,
    "data": {
        "step_instance_list": [
            {
                "step_instance_id": 1001,
                "step_ip_result_list": [
                    {"ip": "1.1.1.1", "status": 9, "tag": "success-1"},
                    {"ip": "1.1.1.2", "status": 104, "tag": "failed-1"},
                    {"ip": "1.1.1.3", "status": 500, "tag": "OTHER"},
                ],
            }
        ]
    },
}
GET_STATUS_FAIL = {"result": False, "message": "error"}


class TaggedIpDictTests(TestCase):
    def test_simple_tagged_dict(self):
        client = MockClient(GET_STATUS_TAGGED)
        ok, data = get_job_tagged_ip_dict(
            tenant_id="system",
            client=client,
            service_logger=logger,
            job_instance_id=1,
            bk_biz_id=2,
        )
        self.assertTrue(ok)
        # 仅包含带 tag 的项
        self.assertIn("success-1", data)
        self.assertEqual(data["success-1"], "1.1.1.1")

    def test_complex_tagged_dict(self):
        client = MockClient(GET_STATUS_TAGGED)
        ok, data = get_job_tagged_ip_dict_complex(
            tenant_id="system",
            client=client,
            service_logger=logger,
            job_instance_id=1,
            bk_biz_id=2,
        )
        self.assertTrue(ok)
        value = data["value"]
        # SUCCESS 分组
        self.assertIn("SUCCESS", value)
        self.assertEqual(value["SUCCESS"]["TAGS"]["success-1"], "1.1.1.1")
        self.assertIn("ALL", value["SUCCESS"]["TAGS"])
        # 脚本非零返回分组
        self.assertIn("SCRIPT_NOT_ZERO_EXIT_CODE", value)
        self.assertEqual(value["SCRIPT_NOT_ZERO_EXIT_CODE"]["TAGS"]["failed-1"], "1.1.1.2")
        # 其他失败分组包含 ALL
        self.assertIn("OTHER_FAILED", value)
        self.assertIn("ALL", value["OTHER_FAILED"]["TAGS"])

    def test_error_from_status_api(self):
        client = MockClient(GET_STATUS_FAIL)
        ok, msg = get_job_tagged_ip_dict(
            tenant_id="system",
            client=client,
            service_logger=logger,
            job_instance_id=1,
            bk_biz_id=2,
        )
        self.assertFalse(ok)
        self.assertIn("调用作业平台(JOB)接口", msg)

        ok2, msg2 = get_job_tagged_ip_dict_complex(
            tenant_id="system",
            client=client,
            service_logger=logger,
            job_instance_id=1,
            bk_biz_id=2,
        )
        self.assertFalse(ok2)
        self.assertIn("调用作业平台(JOB)接口", msg2)
