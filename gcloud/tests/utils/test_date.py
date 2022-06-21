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
from datetime import datetime

import pytz
from django.test import TestCase

from gcloud.utils.dates import format_datetime


class DateTestCase(TestCase):
    def test_format_datetime(self):
        dt = None
        self.assertEqual(format_datetime(dt), "")
        dt = datetime.strptime("2021-09-10T12:00:00Z", "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
        self.assertEqual(format_datetime(dt), "2021-09-10 20:00:00 +0800")
        timezone = "America/Chicago"
        tz = pytz.timezone(timezone)
        self.assertEqual(format_datetime(dt, tz), "2021-09-10 07:00:00 -0500")
