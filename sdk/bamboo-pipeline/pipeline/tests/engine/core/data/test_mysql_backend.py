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

import time

from django.test import TestCase

from pipeline.engine.core.data.mysql_backend import MySQLDataBackend


class MySQLBackendTestCase(TestCase):
    def setUp(self):
        self.backend = MySQLDataBackend()
        self.key = "test_key"
        self.obj = {"a": "a", 1: "1", 2: "2", "list": [4, 5, 6]}
        self.expire = 5

    def test_set_object(self):
        result = self.backend.set_object(self.key, self.obj)
        self.assertTrue(result)

    def test_get_object(self):
        self.backend.set_object(self.key, self.obj)
        obj = self.backend.get_object(self.key)
        self.assertEqual(self.obj, obj)

    def test_del_object(self):
        self.backend.set_object(self.key, self.obj)
        result = self.backend.del_object(self.key)
        self.assertTrue(result)
        none = self.backend.get_object(self.key)
        self.assertIsNone(none)

    def test_expire_cache(self):
        self.backend.expire_cache(self.key, self.obj, self.expire)
        time.sleep(self.expire + 1)
        none = self.backend.cache_for(self.key)
        self.assertIsNone(none)

    def test_cache_for(self):
        self.backend.expire_cache(self.key, self.obj, self.expire)
        obj = self.backend.cache_for(self.key)
        self.assertEqual(self.obj, obj)
