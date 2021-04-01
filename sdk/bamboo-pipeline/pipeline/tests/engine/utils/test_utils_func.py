# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import datetime

from django.test import TestCase
from django.utils import timezone

from pipeline.engine.utils import calculate_elapsed_time


class EngineUtilsFuncTestCase(TestCase):
    def test_calculate_elapsed_time(self):
        self.assertEqual(calculate_elapsed_time(None, None), 0)

        self.assertEqual(calculate_elapsed_time(started_time=None, archived_time=timezone.now()), 0)

        self.assertNotEqual(
            calculate_elapsed_time(started_time=timezone.now() - datetime.timedelta(seconds=1), archived_time=None), 0
        )

        # seconds
        start = timezone.now()
        archive = start + datetime.timedelta(seconds=59)

        self.assertEqual(calculate_elapsed_time(started_time=start, archived_time=archive), 59)

        # minutes
        start = timezone.now()
        archive = start + datetime.timedelta(minutes=3)

        self.assertEqual(calculate_elapsed_time(started_time=start, archived_time=archive), 3 * 60)

        # hours
        start = timezone.now()
        archive = start + datetime.timedelta(hours=3)

        self.assertEqual(calculate_elapsed_time(started_time=start, archived_time=archive), 3 * 60 * 60)

        # days
        start = timezone.now()
        archive = start + datetime.timedelta(days=3)

        self.assertEqual(calculate_elapsed_time(started_time=start, archived_time=archive), 3 * 24 * 60 * 60)
