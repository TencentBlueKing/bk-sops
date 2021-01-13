# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase
from mock import patch

from pipeline_plugins.variables.utils import list_biz_hosts

LIST_BIZ_HOSTS_SUCCESS_RETURN = [{"bk_host_innerip": "192.168.15.18"}, {"bk_host_innerip": "192.168.15.4"}]
PROC_STATUS_ERROR_RETURN = []

MULTIPLE_SUCCESS_KWARGS = {"bk_module_ids": [i for i in range(1000)], "fields": ["bk_host_innerip"]}

SUCCESS_RESULT = [
    {"bk_host_innerip": "192.168.15.18"},
    {"bk_host_innerip": "192.168.15.4"},
    {"bk_host_innerip": "192.168.15.18"},
    {"bk_host_innerip": "192.168.15.4"},
]
ERROR_RESULT = ""
LIST_BIZ_HOSTS_CLIENT = "pipeline_plugins.variables.utils.batch_request"


class UtilsTestCase(TestCase):
    @patch(LIST_BIZ_HOSTS_CLIENT)
    def test_list_biz_hosts(self, batch_request_patch):
        batch_request_patch.return_value = LIST_BIZ_HOSTS_SUCCESS_RETURN
        result = list_biz_hosts(
            username="admin", bk_biz_id="123", bk_supplier_account="supplier_account", kwargs=MULTIPLE_SUCCESS_KWARGS
        )
        self.assertEqual(SUCCESS_RESULT, result)
        self.assertEqual(batch_request_patch.call_count, 2)
