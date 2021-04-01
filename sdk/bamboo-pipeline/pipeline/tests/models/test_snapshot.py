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

from django.test import TestCase

from pipeline.models import Snapshot


class TestSnapshot(TestCase):
    def test_create_snapshot(self):
        data = {"a": 1, "b": [1, 2, 3], "c": {"d": "d"}}
        snapshot = Snapshot.objects.create_snapshot(data)
        Snapshot.objects.create_snapshot(data)
        self.assertEqual(snapshot.data, data)
        self.assertEqual(len(snapshot.md5sum), 32)
        self.assertIsNotNone(snapshot.create_time)

    def test_no_change(self):
        data = {"a": 1, "b": [1, 2, 3], "c": {"d": "d"}}
        snapshot = Snapshot.objects.create_snapshot(data)
        md5, changed = snapshot.has_change(data)
        self.assertFalse(changed)
        self.assertEqual(md5, snapshot.md5sum)
        data = {"a": 2, "b": [1, 2, 3], "c": {"d": "d"}}
        md5, changed = snapshot.has_change(data)
        self.assertTrue(changed)
        self.assertNotEqual(md5, snapshot.md5sum)
