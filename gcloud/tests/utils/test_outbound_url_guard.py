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

import ipaddress
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from gcloud.utils.validate import DomainValidator, OutboundCallbackValidator

RESOLVE_HOST_IPS = "gcloud.utils.validate.resolve_host_ips"


def resolved(*ips):
    return [ipaddress.ip_address(ip) for ip in ips]


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


@override_settings(
    ENABLE_OUTBOUND_CALLBACK_DOMAINS_CHECK=True,
    ALLOWED_OUTBOUND_CALLBACK_DOMAINS="callback.example.com",
    ALLOW_OUTBOUND_CALLBACK_PRIVATE_IP=False,
    ALLOWED_AI_NOTIFY_WEBHOOK_DOMAINS="qyapi.weixin.qq.com",
    ALLOWED_HTTP_PLUGIN_DOMAINS="plugin.example.com",
    BK_URL="https://paas.bk.example.org",
)
class OutboundCallbackValidatorTestCase(SimpleTestCase):
    @patch(RESOLVE_HOST_IPS, return_value=resolved("93.184.216.34"))
    def test_listed_host_resolved_to_public_ip_is_accepted(self, _resolve):
        valid, _allowed_domains = OutboundCallbackValidator.validate("https://api.callback.example.com/notify")

        self.assertTrue(valid)

    @patch(RESOLVE_HOST_IPS, return_value=resolved("93.184.216.34"))
    def test_http_plugin_allowlist_does_not_open_callback_targets(self, _resolve):
        valid, _allowed_domains = OutboundCallbackValidator.validate("https://plugin.example.com/notify")

        self.assertFalse(valid)

    @override_settings(ALLOWED_OUTBOUND_CALLBACK_DOMAINS="")
    @patch(RESOLVE_HOST_IPS, return_value=resolved("93.184.216.34"))
    def test_empty_allowlist_falls_back_to_blueking_domain(self, _resolve):
        valid, _allowed_domains = OutboundCallbackValidator.validate("https://bkflow.example.org/callback")
        other_valid, _allowed_domains = OutboundCallbackValidator.validate("https://attacker.example.net/callback")

        self.assertTrue(valid)
        self.assertFalse(other_valid)

    @patch(RESOLVE_HOST_IPS, return_value=resolved("10.0.0.8"))
    def test_private_ip_is_rejected_by_default(self, _resolve):
        valid, _allowed_domains = OutboundCallbackValidator.validate("https://api.callback.example.com/notify")

        self.assertFalse(valid)

    @override_settings(ALLOW_OUTBOUND_CALLBACK_PRIVATE_IP=True)
    @patch(RESOLVE_HOST_IPS, return_value=resolved("10.0.0.8"))
    def test_private_ip_is_accepted_when_enabled(self, _resolve):
        valid, _allowed_domains = OutboundCallbackValidator.validate("https://api.callback.example.com/notify")

        self.assertTrue(valid)

    @override_settings(ALLOW_OUTBOUND_CALLBACK_PRIVATE_IP=True)
    def test_loopback_and_metadata_ips_are_always_rejected(self):
        for ip in ("127.0.0.1", "169.254.169.254"):
            with self.subTest(ip=ip), patch(RESOLVE_HOST_IPS, return_value=resolved(ip)):
                valid, _allowed_domains = OutboundCallbackValidator.validate("https://api.callback.example.com/notify")

                self.assertFalse(valid)

    @patch(RESOLVE_HOST_IPS, return_value=resolved("93.184.216.34"))
    def test_ai_notify_allows_robot_domain_only_for_ai_notify(self, _resolve):
        url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=fake"

        ai_valid, _allowed_domains = OutboundCallbackValidator.validate_ai_notify_webhook(url)
        callback_valid, _allowed_domains = OutboundCallbackValidator.validate(url)

        self.assertTrue(ai_valid)
        self.assertFalse(callback_valid)

    @override_settings(ENABLE_OUTBOUND_CALLBACK_DOMAINS_CHECK=False)
    def test_check_can_be_disabled(self):
        valid, _allowed_domains = OutboundCallbackValidator.validate("http://127.0.0.1/callback")

        self.assertTrue(valid)
