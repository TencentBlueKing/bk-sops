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

from pipeline.builder.flow import DataInput


class DataInputTestCase(TestCase):
    def test_init(self):
        input = DataInput(type=DataInput.PLAIN, value="val")
        self.assertEqual(input.type, DataInput.PLAIN)
        self.assertEqual(input.value, "val")
        self.assertEqual(input.custom_type, None)

    def test_to_dict(self):
        input = DataInput(type=DataInput.PLAIN, value="val", custom_type="source_tag")
        d = input.to_dict()
        self.assertEqual(d, {"type": "plain", "value": "val", "is_param": True})
