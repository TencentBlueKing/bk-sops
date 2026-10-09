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
from django.conf import settings
from django.test import TestCase


class Phase3SettingsTest(TestCase):
    def test_scanners_default_off(self):
        self.assertFalse(settings.PIPELINE_DIAGNOSTICS_WINDOW_SCAN_ENABLED)
        self.assertFalse(settings.PIPELINE_DIAGNOSTICS_SIGNATURE_SCAN_ENABLED)
        self.assertFalse(settings.PIPELINE_DIAGNOSTICS_CALLBACK_SCAN_ENABLED)

    def test_defaults(self):
        self.assertEqual(settings.PIPELINE_DIAGNOSTICS_WINDOW_TIERS, (3600, 86400))
        self.assertEqual(settings.PIPELINE_DIAGNOSTICS_WINDOW_MAX_ROOTS, 1000)
        self.assertEqual(settings.PIPELINE_DIAGNOSTICS_SIGNATURE_FAST_THRESHOLD_SECONDS, 300)
        self.assertEqual(settings.PIPELINE_DIAGNOSTICS_SIGNATURE_SLOW_THRESHOLD_SECONDS, 1800)
        self.assertEqual(settings.PIPELINE_DIAGNOSTICS_POLL_EXCLUDE_CODES, ["sleep_timer"])
        self.assertEqual(settings.PIPELINE_DIAGNOSTICS_CALLBACK_CONFIRM_SECONDS, 120)
        self.assertEqual(settings.DIAGNOSTICS_SIGNATURE_SCAN_CRON, ("*", "*", "*", "*", "*"))
        self.assertEqual(settings.DIAGNOSTICS_CALLBACK_SCAN_INTERVAL, 30)
