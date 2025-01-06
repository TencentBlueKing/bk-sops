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

from gcloud.utils.strings import inspect_time


class InspectTimeTestCase(TestCase):
    def test_inspect_time(self):
        cron = {"minute": "*", "hour": "*", "day_of_month": "*", "month": "*", "day_of_week": "*"}
        shortest_time = 30
        iter_count = 10
        self.assertFalse(inspect_time(cron=cron, shortest_time=shortest_time, iter_count=iter_count))

    def test_fail_inspect_time(self):
        cron = {"minute": "*/15", "hour": "*", "day_of_month": "*", "month": "*", "day_of_week": "*"}
        shortest_time = 30
        iter_count = 10
        self.assertFalse(inspect_time(cron=cron, shortest_time=shortest_time, iter_count=iter_count))

    def test_success_inspect_time(self):
        cron = {"minute": "15", "hour": "2", "day_of_month": "*", "month": "*", "day_of_week": "*"}
        shortest_time = 30
        iter_count = 10
        self.assertTrue(inspect_time(cron=cron, shortest_time=shortest_time, iter_count=iter_count))

    def test_iter_count_inspect_time(self):
        cron = {"minute": "*/15", "hour": "*", "day_of_month": "*", "month": "*", "day_of_week": "*"}
        shortest_time = 30
        iter_count = 100
        self.assertFalse(inspect_time(cron=cron, shortest_time=shortest_time, iter_count=iter_count))
