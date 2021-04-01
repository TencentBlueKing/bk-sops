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

from pipeline.core.flow.io import BooleanItemSchema, FloatItemSchema, IntItemSchema, StringItemSchema


class SimpleItemSchemaTestCase(TestCase):
    def setUp(self):
        self.description = "a simple item"
        self.enum = ["1", "2", "3"]

    def test_as_dict(self):
        schema = StringItemSchema(description=self.description, enum=self.enum)

        schema_dict = schema.as_dict()
        self.assertEqual(schema_dict, {"type": "string", "description": self.description, "enum": self.enum})

    def test_type(self):
        self.assertEqual("int", IntItemSchema._type())
        self.assertEqual("string", StringItemSchema._type())
        self.assertEqual("float", FloatItemSchema._type())
        self.assertEqual("boolean", BooleanItemSchema._type())
