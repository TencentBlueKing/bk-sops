# -*- coding: utf-8 -*-
from django.test import TestCase

from pipeline_plugins.components.collections.sites.open.job.base import get_ip_from_step_ip_result


class GetIpFromStepIpResultTests(TestCase):
    def test_ipv4_priority(self):
        self.assertEqual(get_ip_from_step_ip_result({"ip": "1.1.1.1"}), "1.1.1.1")

    def test_ipv6_fallback(self):
        self.assertEqual(get_ip_from_step_ip_result({"ipv6": "fe80::1"}), "fe80::1")

    def test_empty_result(self):
        self.assertEqual(get_ip_from_step_ip_result({}), "")
