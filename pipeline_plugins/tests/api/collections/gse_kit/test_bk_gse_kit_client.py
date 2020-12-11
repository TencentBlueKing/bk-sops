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

from django.conf import settings
from django.test import TestCase

from api.collections.gse_kit import BKGseKitClient


class BKGseKitClientTestCase(TestCase):
    def setUp(self):
        self.client = BKGseKitClient("spacesun")

    def test_pre_process_data(self):
        test1 = {"a": "1", "b": "2"}
        test2 = {"a": "1", "b": "2", "c": None}
        res = {
            "a": "1",
            "b": "2",
            "bk_username": "spacesun",
            "bk_app_code": settings.APP_CODE,
            "bk_app_secret": settings.SECRET_KEY,
        }
        assert self.client._pre_process_data(test1) == res
        assert self.client._pre_process_data(test2) == res
