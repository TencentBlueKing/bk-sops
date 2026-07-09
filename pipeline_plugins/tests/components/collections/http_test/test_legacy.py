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

from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.common import HttpRequestService


class LegacyHttpComponentValidateTestCase(TestCase):
    def test_domain_validator_rejects_request_before_http_call(self):
        data = MagicMock()
        data.get_one_of_inputs.side_effect = {
            "bk_http_request_method": "GET",
            "bk_http_request_url": "http://127.0.0.1",
            "bk_http_request_body": "",
        }.get
        data.outputs = {}
        data.set_outputs.side_effect = data.outputs.__setitem__

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None

        with patch(
            "pipeline_plugins.components.collections.common.DomainValidator.validate",
            return_value=(False, ["bk.example.com"]),
        ), patch("pipeline_plugins.components.collections.common.requests.request") as request:
            service = HttpRequestService()
            service.logger = MagicMock()
            result = service.plugin_schedule(data, parent_data)

        self.assertFalse(result)
        self.assertEqual(data.outputs["ex_data"], "仅允许访问域名(bk.example.com)下的URL")
        request.assert_not_called()
