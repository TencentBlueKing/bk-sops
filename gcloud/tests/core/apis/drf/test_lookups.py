# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


from datetime import datetime
from django.test import TestCase

from gcloud.core.apis.drf.property_lookups import LookupMethods


class TestLookupMethods(TestCase):
    def test_exact(self):
        result = LookupMethods().property_exact(1, 1)
        self.assertTrue(result)
        result = LookupMethods().property_exact(1, 2)
        self.assertFalse(result)

    def test_iexact(self):
        result = LookupMethods().property_iexact(1, 1)
        self.assertFalse(result)
        result = LookupMethods().property_iexact(1, 2)
        self.assertTrue(result)

    def test_isnull(self):
        result = LookupMethods().property_isnull(None, True)
        self.assertTrue(result)
        result = LookupMethods().property_isnull(None, False)
        self.assertFalse(result)

    def test_contains(self):
        result = LookupMethods().property_contains("abc", "a")
        self.assertTrue(result)
        result = LookupMethods().property_contains("ABC", "a")
        self.assertFalse(result)

    def test_icontains(self):
        result = LookupMethods().property_icontains("Abc", "a")
        self.assertTrue(result)

    def test_in(self):
        result = LookupMethods().property_in("abcde", "bcd")
        self.assertTrue(result)

    def test_startswith(self):
        result = LookupMethods().property_startswith("abcdef", "a")
        self.assertTrue(result)
        result = LookupMethods().property_startswith("abcdef", "A")
        self.assertFalse(result)

    def test_istartswith(self):
        result = LookupMethods().property_istartswith("abcdef", "AB")
        self.assertTrue(result)

    def test_endswith(self):
        result = LookupMethods().property_endswith("abcdef", "ef")
        self.assertTrue(result)
        result = LookupMethods().property_endswith("abcdef", "EF")
        self.assertFalse(result)

    def test_iendswith(self):
        result = LookupMethods().property_iendswith("abcdef", "Ef")
        self.assertTrue(result)

    def test_regex(self):
        result = LookupMethods().property_regex("", "123")
        self.assertFalse(result)

    def test_iregex(self):
        result = LookupMethods().property_regex("", "123")
        self.assertFalse(result)

    def test_gt(self):
        result = LookupMethods().property_gt(20, 10)
        self.assertTrue(result)

    def test_gte(self):
        result = LookupMethods().property_gte(10, 10)
        self.assertTrue(result)
        result = LookupMethods().property_gte(20, 10)
        self.assertTrue(result)
        nowtime = datetime.now()
        result = LookupMethods().property_gte(nowtime, nowtime)
        self.assertTrue(result)

    def test_lt(self):
        result = LookupMethods().property_lt(10, 20)
        self.assertTrue(result)
        result = LookupMethods().property_lt(20, 20)
        self.assertFalse(result)

    def test_lte(self):
        result = LookupMethods().property_lte(10, 10)
        self.assertTrue(result)
        nowtime = datetime.now()
        result = LookupMethods().property_gte(nowtime, nowtime)
        self.assertTrue(result)

    def test_date(self):
        nowtime = datetime.now()
        result = LookupMethods().property_date(nowtime, nowtime)
        self.assertTrue(result)

    def test_year(self):
        nowtime = datetime.now()
        year = nowtime.year
        result = LookupMethods().property_year(nowtime, year)
        self.assertTrue(result)

    def test_month(self):
        nowtime = datetime.now()
        month = 13
        result = LookupMethods().property_month(nowtime, month)
        self.assertFalse(result)

    def test_hour(self):
        nowtime = datetime.now()
        hour = nowtime.hour
        result = LookupMethods().property_hour(nowtime, hour)
        self.assertTrue(result)

    def test_minute(self):
        nowtime = datetime.now()
        minute = nowtime.minute
        result = LookupMethods().property_minute(nowtime, minute)
        self.assertTrue(result)

    def test_second(self):
        nowtime = datetime.now()
        second = nowtime.second
        result = LookupMethods().property_second(nowtime, second)
        self.assertTrue(result)
