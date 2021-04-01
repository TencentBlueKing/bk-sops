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

from pipeline.django_signal_valve.models import Signal


class TestModels(TestCase):
    def tearDown(self):
        Signal.objects.all().delete()

    def test_manager_dump(self):
        kwargs = {"key1": "value1", "key2": [1, 2, 3], "key3": {"key4": "value4"}}
        Signal.objects.dump(module_path="path", signal_name="name", kwargs=kwargs)
        signal = Signal.objects.all()[0]
        self.assertEqual(signal.module_path, "path")
        self.assertEqual(signal.name, "name")
        self.assertEqual(signal.kwargs, kwargs)
