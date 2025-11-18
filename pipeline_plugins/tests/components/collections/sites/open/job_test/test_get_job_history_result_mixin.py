# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

import mock
from django.test import TestCase
from mock import MagicMock
from pipeline.core.data.base import DataObject

from pipeline_plugins.components.collections.sites.open.job.base import GetJobHistoryResultMixin
from pipeline_plugins.tests.components.collections.sites.open.utils.cc_ipv6_mock_utils import MockCMDBClientIPv6

TEST_INPUTS = {"job_success_id": 12345, "biz_cc_id": 11111, "executor": "executor", "tenant_id": "system"}
TEST_DATA = DataObject(TEST_INPUTS)
TEST_PARENT_DATA = DataObject(TEST_INPUTS)

logger = logging.getLogger("component")

GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username"

# 添加 CC client mock 路径，用于 IPv6 支持
CC_GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username"
CMDB_GET_CLIENT_BY_USERNAME = "gcloud.utils.cmdb.get_client_by_username"
GET_JOB_INSTANCE_URL = "pipeline_plugins.components.collections.sites.open.job.base.get_job_instance_status"
GET_JOB_STATUS_RETURN = {
    "result": True,
    "code": 0,
    "message": "",
    "data": {
        "finished": True,
        "job_instance": {
            "job_instance_id": 100,
            "bk_biz_id": 1,
            "name": "API Quick execution script1521089795887",
            "create_time": 1605064271000,
            "status": 3,
            "start_time": 1605064271000,
            "end_time": 1605064272000,
            "total_time": 1000,
        },
        "step_instance_list": [
            {
                "status": 3,
                "total_time": 1000,
                "name": "API Quick execution scriptxxx",
                "step_instance_id": 75,
                "execute_count": 0,
                "create_time": 1605064271000,
                "end_time": 1605064272000,
                "type": 1,
                "start_time": 1605064271000,
                "step_ip_result_list": [
                    {
                        "ip": "1.1.1.1",
                        "bk_cloud_id": 0,
                        "status": 9,
                        "tag": "",
                        "exit_code": 0,
                        "error_code": 0,
                        "start_time": 1605064271000,
                        "end_time": 1605064272000,
                        "total_time": 1000,
                    },
                    {
                        "ip": "1.1.1.2",
                        "bk_cloud_id": 0,
                        "status": 9,
                        "tag": "",
                        "exit_code": 0,
                        "error_code": 0,
                        "start_time": 1605064271000,
                        "end_time": 1605064272000,
                        "total_time": 1000,
                    },
                ],
            }
        ],
    },
}
EXECUTE_SUCCESS_GET_IP_LOG_RETURN = {
    "result": True,
    "code": 0,
    "message": "",
    "data": {
        "ip": "10.0.0.1",
        "bk_cloud_id": 0,
        "log_content": "<SOPS_VAR>key1:value1</SOPS_VAR>\ngsectl\n-rwxr-xr-x 1\n"
        "<SOPS_VAR>key4:   v   </SOPS_VAR><SOPS_VAR>key5:  </SOPS_VAR>"
        "<SOPS_VAR>key6:v:v</SOPS_VAR><SOPS_VAR>key empty</SOPS_VAR>"
        "<SOPS_VAR>:1</SOPS_VAR><SOPS_VAR>:1   fgdshgdsh</SOPS_VAR>"
        "<##{key}=v##><##{key}notvar##>"
        "&lt;SOPS_VAR&gt;key2:value2&lt;/SOPS_VAR&gt;\n"
        "dfg&lt;SOPS_VAR&gt;key3:value3&lt;/SOPS_VAR&gt;"
        "&lt;SOPS_VAR&gt;k: v  &lt;/SOPS_VAR&gt;"
        "&lt;SOPS_VAR&gt;k1: :v  &lt;/SOPS_VAR&gt;"
        "&lt;SOPS_VAR&gt;k1      &lt;/SOPS_VAR&gt;"
        "&lt;##{key2}=v##&gt;&lt;##{key3}=var##&gt;",
    },
}


class MockClient(object):
    def __init__(self):
        self.set_bk_api_ver = MagicMock()
        self.api = MagicMock()
        self.api.get_job_instance_ip_log = MagicMock(return_value=EXECUTE_SUCCESS_GET_IP_LOG_RETURN)
        self.api.get_job_instance_status = MagicMock(return_value=GET_JOB_STATUS_RETURN)


# Mock CMDB Client for IPv6 support
class MockCMDBClient(MockCMDBClientIPv6):
    pass


class TestGetJobHistoryResultMixin(TestCase):
    def setUp(self):
        self.mixin = GetJobHistoryResultMixin()
        self.mixin.logger = logger
        self.mixin.need_get_sops_var = True
        self.get_job_result = self.mixin.get_job_history_result

    def test_get_job_history_result(self):
        with mock.patch(GET_CLIENT_BY_USER, return_value=MockClient()):
            result = self.get_job_result(TEST_DATA, TEST_PARENT_DATA)
            self.assertTrue(result)
