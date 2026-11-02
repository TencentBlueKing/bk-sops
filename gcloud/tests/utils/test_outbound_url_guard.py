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

from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from gcloud.utils.validate import DomainValidator


class OutboundUrlGuardTestCase(SimpleTestCase):
    @override_settings(ENABLE_HTTP_PLUGIN_DOMAINS_CHECK=True, ALLOWED_HTTP_PLUGIN_DOMAINS="example.com")
    def test_private_callback_target_is_rejected_before_resolution(self):
        valid, _allowed_domains = DomainValidator.validate("http://127.0.0.1/callback")

        self.assertFalse(valid)

    @override_settings(ENABLE_HTTP_PLUGIN_DOMAINS_CHECK=True, ALLOWED_HTTP_PLUGIN_DOMAINS="example.com")
    @patch("gcloud.utils.validate.host_resolves_to_safe_ips", return_value=True)
    def test_listed_callback_host_is_accepted(self, _safe_ips):
        valid, _allowed_domains = DomainValidator.validate("https://hook.example.com/callback")

        self.assertTrue(valid)

    @override_settings(ENABLE_HTTP_PLUGIN_DOMAINS_CHECK=True, ALLOWED_HTTP_PLUGIN_DOMAINS="example.com")
    def test_unlisted_host_is_rejected(self):
        valid, _allowed_domains = DomainValidator.validate("https://internal.invalid/hook")

        self.assertFalse(valid)
