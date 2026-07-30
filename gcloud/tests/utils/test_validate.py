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
from django.test.utils import override_settings
from mock import patch

from gcloud.utils.validate import DomainValidator


def getaddrinfo_result(ip):
    return [(None, None, None, "", (ip, 0))]


class DomainValidatorTestCase(TestCase):
    @override_settings(ENABLE_HTTP_PLUGIN_DOMAINS_CHECK=True, ALLOWED_HTTP_PLUGIN_DOMAINS="example.com")
    def test_allow_allowed_domain_resolved_to_public_ip(self):
        with patch("gcloud.utils.validate.socket.getaddrinfo", return_value=getaddrinfo_result("93.184.216.34")):
            valid, allowed_domains = DomainValidator.validate("https://api.example.com/resource")

        self.assertTrue(valid)
        self.assertEqual(allowed_domains, [])

    @override_settings(ENABLE_HTTP_PLUGIN_DOMAINS_CHECK=True, ALLOWED_HTTP_PLUGIN_DOMAINS="example.com")
    def test_reject_allowed_domain_resolved_to_private_ip(self):
        with patch("gcloud.utils.validate.socket.getaddrinfo", return_value=getaddrinfo_result("127.0.0.1")):
            valid, allowed_domains = DomainValidator.validate("https://api.example.com/resource")

        self.assertFalse(valid)
        self.assertEqual(allowed_domains, ["example.com"])

    @override_settings(ENABLE_HTTP_PLUGIN_DOMAINS_CHECK=True, ALLOWED_HTTP_PLUGIN_DOMAINS="127.0.0.1")
    def test_reject_private_ip_literal(self):
        valid, allowed_domains = DomainValidator.validate("http://127.0.0.1/metadata")

        self.assertFalse(valid)
        self.assertEqual(allowed_domains, ["127.0.0.1"])

    @override_settings(ENABLE_HTTP_PLUGIN_DOMAINS_CHECK=True, ALLOWED_HTTP_PLUGIN_DOMAINS="2130706433")
    def test_reject_integer_encoded_loopback(self):
        with patch("gcloud.utils.validate.socket.getaddrinfo", return_value=getaddrinfo_result("127.0.0.1")):
            valid, allowed_domains = DomainValidator.validate("http://2130706433/metadata")

        self.assertFalse(valid)
        self.assertEqual(allowed_domains, ["2130706433"])

    @override_settings(ENABLE_HTTP_PLUGIN_DOMAINS_CHECK=True, ALLOWED_HTTP_PLUGIN_DOMAINS="example.com")
    def test_reject_disallowed_domain_before_dns_resolve(self):
        with patch("gcloud.utils.validate.socket.getaddrinfo") as mocked_getaddrinfo:
            valid, allowed_domains = DomainValidator.validate("https://api.other.com/resource")

        self.assertFalse(valid)
        self.assertEqual(allowed_domains, ["example.com"])
        mocked_getaddrinfo.assert_not_called()

    @override_settings(ENABLE_HTTP_PLUGIN_DOMAINS_CHECK=True, ALLOWED_HTTP_PLUGIN_DOMAINS="example.com")
    def test_reject_unsupported_scheme(self):
        valid, allowed_domains = DomainValidator.validate("file://example.com/etc/passwd")

        self.assertFalse(valid)
        self.assertEqual(allowed_domains, ["example.com"])
