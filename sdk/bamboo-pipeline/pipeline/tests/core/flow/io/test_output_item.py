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
from mock import MagicMock

from pipeline.core.flow.io import OutputItem


class OutputItemTestCase(TestCase):
    def setUp(self):
        self.name = "input item"
        self.key = "input_key"
        self.type = "string"
        self.required = False
        schema = MagicMock()
        schema.as_dict = MagicMock(return_value="schema dict")
        self.schema = schema

    def test_as_dict(self):
        input_item = OutputItem(name=self.name, key=self.key, type=self.type, schema=self.schema)
        item_dict = input_item.as_dict()

        self.assertEqual(
            item_dict, {"name": self.name, "key": self.key, "type": self.type, "schema": self.schema.as_dict()}
        )
