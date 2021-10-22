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

from gcloud.utils.strings import django_celery_beat_cron_time_format_fit


class DjangoCeleryBeatCronTimeFormatFitTestCase(TestCase):
    def test__old_version_time_format_without_timezone(self):
        cron_time_str = "1 2 3 4 5 (m/h/d/dM/MY)"
        fitted_cron_time_str = django_celery_beat_cron_time_format_fit(cron_time_str)
        self.assertEqual(fitted_cron_time_str, cron_time_str)

    def test__old_version_time_format_with_timezone(self):
        cron_time_str = "1 2 3 4 5 (m/h/d/dM/MY) Asia/Shanghai"
        fitted_cron_time_str = django_celery_beat_cron_time_format_fit(cron_time_str)
        self.assertEqual(fitted_cron_time_str, cron_time_str)

    def test__new_version_time_format(self):
        cron_time_str = "1 2 3 4 5 (m/h/dM/MY/d) Asia/Shanghai"
        expected_cron_time_str = "1 2 5 3 4 (m/h/d/dM/MY) Asia/Shanghai"
        fitted_cron_time_str = django_celery_beat_cron_time_format_fit(cron_time_str)
        self.assertEqual(fitted_cron_time_str, expected_cron_time_str)
