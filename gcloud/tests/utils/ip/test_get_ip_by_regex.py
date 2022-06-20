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

from gcloud.utils.ip import get_ip_by_regex


class GetIPByRegexTestCase(TestCase):
    def test__normal(self):
        self.assertEqual(get_ip_by_regex("1.1.1.1,2.2.2.2,3.3.3.3"), ["1.1.1.1", "2.2.2.2", "3.3.3.3"])

    def test__empty_string(self):
        self.assertEqual(get_ip_by_regex(""), [])

    def test__check_ipv4(self):
        self.assertEqual(get_ip_by_regex("256.255.2.1,10.2.1.256,10.2.1.255"), ["10.2.1.255"])
