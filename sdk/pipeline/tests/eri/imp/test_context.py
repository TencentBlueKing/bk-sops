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
import json

from django.test import TransactionTestCase

from bamboo_engine.eri import ContextValue, ContextValueType

from pipeline.eri.imp.context import ContextMixin
from pipeline.eri.models import ContextValue as DBContextValue
from pipeline.eri.models import ContextOutputs
from bamboo_engine.utils.string import unique_id


class ContextMixinTestCase(TransactionTestCase):
    def setUp(self):
        self.mixin = ContextMixin()
        self.pipeline_id = unique_id("p")
        self.outputs = ["a", "b", "c", "d"]
        DBContextValue.objects.create(
            pipeline_id=self.pipeline_id,
            key="${var_1}",
            type=ContextValueType.PLAIN.value,
            serializer=ContextMixin.JSON_SERIALIZER,
            value=json.dumps("123"),
            references="[]",
        )
        DBContextValue.objects.create(
            pipeline_id=self.pipeline_id,
            key="${var_2}",
            type=ContextValueType.PLAIN.value,
            serializer=ContextMixin.JSON_SERIALIZER,
            value=json.dumps(123),
            references="[]",
        )
        DBContextValue.objects.create(
            pipeline_id=self.pipeline_id,
            key="${var_3}",
            type=ContextValueType.SPLICE.value,
            serializer=ContextMixin.JSON_SERIALIZER,
            value=json.dumps("${var_1}_${var_2}"),
            references='["${var_1}", "${var_2}"]',
        )
        DBContextValue.objects.create(
            pipeline_id=self.pipeline_id,
            key="${var_4}",
            type=ContextValueType.COMPUTE.value,
            serializer=ContextMixin.JSON_SERIALIZER,
            value=json.dumps({"attr1": "a", "attr2": "${var_3}"}),
            references='["${var_1}", "${var_2}", "${var_3}"]',
            code="cv",
        )
        ContextOutputs.objects.create(pipeline_id=self.pipeline_id, outputs=json.dumps(self.outputs))

    def test_get_context_values(self):
        context_values = self.mixin.get_context_values(self.pipeline_id, {"${var_1}", "${var_2}"})
        self.assertEqual(len(context_values), 2)
        self.assertEqual(context_values[0].key, "${var_1}")
        self.assertEqual(context_values[0].type, ContextValueType.PLAIN)
        self.assertEqual(context_values[0].value, "123")
        self.assertIsNone(context_values[0].code)
        self.assertEqual(context_values[1].key, "${var_2}")
        self.assertEqual(context_values[1].type, ContextValueType.PLAIN)
        self.assertEqual(context_values[1].value, 123)
        self.assertIsNone(context_values[1].code)

        context_values = self.mixin.get_context_values(
            self.pipeline_id, {"${var_1}", "${var_2}", "${var_3}", "${var_4}"}
        )
        self.assertEqual(len(context_values), 4)
        self.assertEqual(context_values[0].key, "${var_1}")
        self.assertEqual(context_values[0].type, ContextValueType.PLAIN)
        self.assertEqual(context_values[0].value, "123")
        self.assertIsNone(context_values[0].code)
        self.assertEqual(context_values[1].key, "${var_2}")
        self.assertEqual(context_values[1].type, ContextValueType.PLAIN)
        self.assertEqual(context_values[1].value, 123)
        self.assertIsNone(context_values[1].code)
        self.assertEqual(context_values[2].key, "${var_3}")
        self.assertEqual(context_values[2].type, ContextValueType.SPLICE)
        self.assertEqual(context_values[2].value, "${var_1}_${var_2}")
        self.assertIsNone(context_values[2].code)
        self.assertEqual(context_values[3].key, "${var_4}")
        self.assertEqual(context_values[3].type, ContextValueType.COMPUTE)
        self.assertEqual(context_values[3].value, {"attr1": "a", "attr2": "${var_3}"})
        self.assertEqual(context_values[3].code, "cv")

    def test_get_context_key_references(self):
        references = self.mixin.get_context_key_references(self.pipeline_id, {"${var_1}", "${var_2}"})
        self.assertEqual(references, set())
        references = self.mixin.get_context_key_references(
            self.pipeline_id, {"${var_1}", "${var_2}", "${var_3}", "${var_4}"}
        )
        self.assertEqual(references, {"${var_1}", "${var_2}", "${var_3}"})

    def test_get_context(self):
        context_values = self.mixin.get_context(self.pipeline_id)
        self.assertEqual(len(context_values), 4)
        self.assertEqual(context_values[0].key, "${var_1}")
        self.assertEqual(context_values[0].type, ContextValueType.PLAIN)
        self.assertEqual(context_values[0].value, "123")
        self.assertIsNone(context_values[0].code)
        self.assertEqual(context_values[1].key, "${var_2}")
        self.assertEqual(context_values[1].type, ContextValueType.PLAIN)
        self.assertEqual(context_values[1].value, 123)
        self.assertIsNone(context_values[1].code)
        self.assertEqual(context_values[2].key, "${var_3}")
        self.assertEqual(context_values[2].type, ContextValueType.SPLICE)
        self.assertEqual(context_values[2].value, "${var_1}_${var_2}")
        self.assertIsNone(context_values[2].code)
        self.assertEqual(context_values[3].key, "${var_4}")
        self.assertEqual(context_values[3].type, ContextValueType.COMPUTE)
        self.assertEqual(context_values[3].value, {"attr1": "a", "attr2": "${var_3}"})
        self.assertEqual(context_values[3].code, "cv")

    def test_get_context_outputs(self):
        outputs = self.mixin.get_context_outputs(self.pipeline_id)
        self.assertEqual(outputs, set(self.outputs))

    def test_upsert_plain_context_values(self):
        update = {
            "${var_3}": ContextValue(key="${var_3}", type=ContextValueType.PLAIN, value="123_123"),
            "${var_4}": ContextValue(key="${var_4}", type=ContextValueType.PLAIN, value="compute_val"),
            "${var_5}": ContextValue(key="${var_5}", type=ContextValueType.PLAIN, value="5_val"),
            "${var_6}": ContextValue(key="${var_6}", type=ContextValueType.PLAIN, value="6_val"),
        }
        self.mixin.upsert_plain_context_values(self.pipeline_id, update)

        context_values = self.mixin.get_context(self.pipeline_id)
        self.assertEqual(len(context_values), 6)
        context_values = {cv.key: cv for cv in context_values}
        self.assertEqual(context_values["${var_1}"].key, "${var_1}")
        self.assertEqual(context_values["${var_1}"].type, ContextValueType.PLAIN)
        self.assertEqual(context_values["${var_1}"].value, "123")
        self.assertIsNone(context_values["${var_1}"].code)
        self.assertEqual(context_values["${var_2}"].key, "${var_2}")
        self.assertEqual(context_values["${var_2}"].type, ContextValueType.PLAIN)
        self.assertEqual(context_values["${var_2}"].value, 123)
        self.assertIsNone(context_values["${var_2}"].code)
        self.assertEqual(context_values["${var_3}"].key, "${var_3}")
        self.assertEqual(context_values["${var_3}"].type, ContextValueType.PLAIN)
        self.assertEqual(context_values["${var_3}"].value, "123_123")
        self.assertIsNone(context_values["${var_3}"].code)
        self.assertEqual(context_values["${var_4}"].key, "${var_4}")
        self.assertEqual(context_values["${var_4}"].type, ContextValueType.PLAIN)
        self.assertEqual(context_values["${var_4}"].value, "compute_val")
        self.assertIsNone(context_values["${var_4}"].code)
        self.assertEqual(context_values["${var_5}"].key, "${var_5}")
        self.assertEqual(context_values["${var_5}"].type, ContextValueType.PLAIN)
        self.assertEqual(context_values["${var_5}"].value, "5_val")
        self.assertIsNone(context_values["${var_5}"].code)
        self.assertEqual(context_values["${var_6}"].key, "${var_6}")
        self.assertEqual(context_values["${var_6}"].type, ContextValueType.PLAIN)
        self.assertEqual(context_values["${var_6}"].value, "6_val")
        self.assertIsNone(context_values["${var_6}"].code)
