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

from pipeline.engine.models import DataSnapshot


class DataSnapshotTestCase(TestCase):
    def setUp(self):
        self.key_1 = "test_key_1"
        self.key_2 = "test_key_2"
        self.not_exist_key = "not_exist"
        self.obj_1 = {"a": "a", 1: "1", 2: "2", "list": [1, 2, 3]}
        self.obj_2 = [1, 5, 3]
        self.obj_3 = [1, 2, 3]

    def test_set_object(self):
        set_result = DataSnapshot.objects.set_object(self.key_1, self.obj_1)
        self.assertTrue(set_result)
        obj_1 = DataSnapshot.objects.get_object(self.key_1)
        self.assertEqual(self.obj_1, obj_1)

        # override
        set_result = DataSnapshot.objects.set_object(self.key_1, self.obj_2)
        self.assertTrue(set_result)
        obj_2 = DataSnapshot.objects.get_object(self.key_1)
        self.assertEqual(self.obj_2, obj_2)

        # new obj
        set_result = DataSnapshot.objects.set_object(self.key_2, self.obj_3)
        self.assertTrue(set_result)
        obj_3 = DataSnapshot.objects.get_object(self.key_2)
        self.assertEqual(self.obj_3, obj_3)

    def test_get_object(self):
        DataSnapshot.objects.set_object(self.key_1, self.obj_1)
        obj_1 = DataSnapshot.objects.get_object(self.key_1)
        self.assertEqual(self.obj_1, obj_1)

        # none
        none = DataSnapshot.objects.get_object(self.not_exist_key)
        self.assertIsNone(none)

    def test_del_object(self):
        DataSnapshot.objects.set_object(self.key_1, self.obj_1)
        del_result = DataSnapshot.objects.del_object(self.key_1)
        self.assertTrue(del_result)
        none = DataSnapshot.objects.get_object(self.key_1)
        self.assertIsNone(none)
        del_result = DataSnapshot.objects.del_object(self.key_1)
        self.assertFalse(del_result)
