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

from pipeline.core.flow.io import ArrayItemSchema, IntItemSchema, ObjectItemSchema, StringItemSchema


class ObjectItemSchemaTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.description = "a simple item"

        self.int_description = "a integer"
        self.int_schema = IntItemSchema(description=self.int_description)
        self.string_description = "a string"
        self.string_schema = StringItemSchema(description=self.string_description)
        self.array_description = "a array"
        self.array_item_description = "item in array"
        self.array_schema = ArrayItemSchema(
            description=self.array_description, item_schema=StringItemSchema(description=self.array_item_description)
        )
        self.inner_object_description = "inner object"
        self.inner_object_schema = ObjectItemSchema(
            description=self.inner_object_description,
            property_schemas={"int_key": self.int_schema, "str_key": self.string_schema},
        )

    def test_as_dict(self):
        object_schema = ObjectItemSchema(
            description=self.description,
            property_schemas={"array_key": self.array_schema, "object_key": self.inner_object_schema},
        )

        schema_dict = object_schema.as_dict()
        self.assertEqual(
            schema_dict,
            {
                "type": "object",
                "description": self.description,
                "enum": [],
                "properties": {
                    "array_key": {
                        "type": "array",
                        "description": self.array_description,
                        "enum": [],
                        "items": {"type": "string", "description": self.array_item_description, "enum": []},
                    },
                    "object_key": {
                        "type": "object",
                        "description": self.inner_object_description,
                        "enum": [],
                        "properties": {
                            "int_key": {"type": "int", "description": self.int_description, "enum": []},
                            "str_key": {"type": "string", "description": self.string_description, "enum": []},
                        },
                    },
                },
            },
        )
