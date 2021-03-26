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

from bamboo_engine.eri import Data, DataInput, ExecutionData, CallbackData

from pipeline.eri.imp.data import DataMixin
from pipeline.eri.models import Data as DBData
from pipeline.eri.models import ExecutionData as DBExecutionData
from pipeline.eri.models import CallbackData as DBCallbackData
from bamboo_engine.utils.string import unique_id


class Obj:
    def __init__(self, attr1, attr2):
        self.attr1 = attr1
        self.attr2 = attr2

    def __eq__(self, other):
        return self.attr1 == other.attr1 and self.attr2 == other.attr2


class DataMixinTestCase(TransactionTestCase):
    def setUp(self):
        self.mixin = DataMixin()
        self.node_id = unique_id("n")
        self.version = unique_id("v")
        self.data_inputs = {"a": {"need_render": True, "value": 1}, "b": {"need_render": True, "value": 2}}
        self.data_outputs = {"c": 3, "d": 4}
        self.data = DBData.objects.create(
            node_id=self.node_id, inputs=json.dumps(self.data_inputs), outputs=json.dumps(self.data_outputs)
        )

        self.pickle_node_id = unique_id("n")
        self.mix_node_id = unique_id("n")
        self.json_exec_data_inputs = {"a": 1, "b": 2}
        self.json_exec_data_outputs = {"c": 3, "d": 4}
        self.pickle_exec_data_inputs = {"a": 1, "b": Obj(1, Obj(2, 3))}
        self.pickle_exec_data_outputs = {"c": 3, "d": Obj(4, Obj(5, 6))}
        self.json_exec_data = DBExecutionData.objects.create(
            node_id=self.node_id,
            inputs=self.mixin._serialize(self.json_exec_data_inputs)[0],
            inputs_serializer=self.mixin._serialize(self.json_exec_data_inputs)[1],
            outputs=self.mixin._serialize(self.json_exec_data_outputs)[0],
            outputs_serializer=self.mixin._serialize(self.json_exec_data_outputs)[1],
        )
        self.pickle_exec_data = DBExecutionData.objects.create(
            node_id=self.pickle_node_id,
            inputs=self.mixin._serialize(self.pickle_exec_data_inputs)[0],
            inputs_serializer=self.mixin._serialize(self.pickle_exec_data_inputs)[1],
            outputs=self.mixin._serialize(self.pickle_exec_data_outputs)[0],
            outputs_serializer=self.mixin._serialize(self.pickle_exec_data_outputs)[1],
        )
        self.mix_exec_data = DBExecutionData.objects.create(
            node_id=self.mix_node_id,
            inputs=self.mixin._serialize(self.json_exec_data_inputs)[0],
            inputs_serializer=self.mixin._serialize(self.json_exec_data_inputs)[1],
            outputs=self.mixin._serialize(self.pickle_exec_data_outputs)[0],
            outputs_serializer=self.mixin._serialize(self.pickle_exec_data_outputs)[1],
        )

        self.raw_callback_data = {"callback": 1}
        self.callback_data = DBCallbackData.objects.create(
            node_id=self.node_id, version=self.version, data=json.dumps(self.raw_callback_data)
        )

    def test_get_data(self):
        data = self.mixin.get_data(self.node_id)
        self.assertTrue(isinstance(data, Data))
        self.assertEqual(data.outputs, self.data_outputs)
        self.assertEqual(data.inputs["a"].value, 1)
        self.assertTrue(data.inputs["a"].value)
        self.assertEqual(data.inputs["b"].value, 2)
        self.assertTrue(data.inputs["b"].value)

    def test_get_data_inputs(self):
        inputs = self.mixin.get_data_inputs(self.node_id)
        self.assertEqual(inputs["a"].value, 1)
        self.assertTrue(inputs["a"].value)
        self.assertEqual(inputs["b"].value, 2)
        self.assertTrue(inputs["b"].value)

    def test_get_data_inputs__not_exist(self):
        self.assertRaises(DBData.DoesNotExist, self.mixin.get_data_inputs, "not_exist")

    def test_get_data_outputs(self):
        outputs = self.mixin.get_data_outputs(self.node_id)
        self.assertEqual(outputs, self.data_outputs)

    def test_get_data_output__not_exist(self):
        self.assertRaises(DBData.DoesNotExist, self.mixin.get_data_outputs, "not_exist")

    def test_set_data_inputs(self):
        self.mixin.set_data_inputs(self.node_id, {"l": DataInput(need_render=True, value=[1, 2, 3])})
        actual = self.mixin.get_data_inputs(self.node_id)
        self.assertEqual(actual["l"].need_render, True)
        self.assertEqual(actual["l"].value, [1, 2, 3])

    def test_set_data_inputs__new(self):
        node_id = unique_id("n")
        inputs = {"a": DataInput(need_render=True, value=1), "b": DataInput(need_render=True, value=2)}
        self.mixin.set_data_inputs(node_id, inputs)
        data = self.mixin.get_data(node_id)
        self.assertEqual(data.outputs, {})
        self.assertEqual(data.inputs["a"].value, 1)
        self.assertTrue(data.inputs["a"].value)
        self.assertEqual(data.inputs["b"].value, 2)
        self.assertTrue(data.inputs["b"].value)

    def test_get_execution_data(self):
        json_exec_data = self.mixin.get_execution_data(self.node_id)
        self.assertTrue(isinstance(json_exec_data, ExecutionData))
        self.assertEqual(json_exec_data.inputs, self.json_exec_data_inputs)
        self.assertEqual(json_exec_data.outputs, self.json_exec_data_outputs)

        pickle_exec_data = self.mixin.get_execution_data(self.pickle_node_id)
        self.assertTrue(isinstance(pickle_exec_data, ExecutionData))
        self.assertEqual(pickle_exec_data.inputs, self.pickle_exec_data_inputs)
        self.assertEqual(pickle_exec_data.outputs, self.pickle_exec_data_outputs)

        mix_exec_data = self.mixin.get_execution_data(self.mix_node_id)
        self.assertTrue(isinstance(mix_exec_data, ExecutionData))
        self.assertEqual(mix_exec_data.inputs, self.json_exec_data_inputs)
        self.assertEqual(mix_exec_data.outputs, self.pickle_exec_data_outputs)

    def get_execution_data_inputs(self):
        self.assertEqual(self.mixin.get_execution_data_inputs(self.node_id), self.json_exec_data_inputs)
        self.assertEqual(self.mixin.get_execution_data_inputs(self.pickle_node_id), self.pickle_exec_data_inputs)

    def get_execution_data_inputs__not_exist(self):
        self.assertRaises(DBExecutionData.DoesNotExist, self.mixin.get_execution_data_inputs, "not_exist")

    def get_execution_data_outputs(self):
        self.assertEqual(self.mixin.get_execution_data_outputs(self.node_id), self.json_exec_data_outputs)
        self.assertEqual(self.mixin.get_execution_data_outputs(self.pickle_node_id), self.pickle_exec_data_outputs)

    def get_execution_data_outputs__not_exist(self):
        self.assertRaises(DBExecutionData.DoesNotExist, self.mixin.get_execution_data_outputs, "not_exist")

    def test_set_execution_data(self):
        json_node_id = unique_id("n")
        pickle_node_id = unique_id("n")
        mix_node_id = unique_id("n")
        DBExecutionData.objects.create(
            node_id=json_node_id,
            inputs="{}",
            inputs_serializer=self.mixin.JSON_SERIALIZER,
            outputs="{}",
            outputs_serializer=self.mixin.JSON_SERIALIZER,
        )
        DBExecutionData.objects.create(
            node_id=pickle_node_id,
            inputs="{}",
            inputs_serializer=self.mixin.JSON_SERIALIZER,
            outputs="{}",
            outputs_serializer=self.mixin.JSON_SERIALIZER,
        )
        DBExecutionData.objects.create(
            node_id=mix_node_id,
            inputs="{}",
            inputs_serializer=self.mixin.JSON_SERIALIZER,
            outputs="{}",
            outputs_serializer=self.mixin.JSON_SERIALIZER,
        )

        self.mixin.set_execution_data(
            json_node_id, ExecutionData(self.json_exec_data_inputs, self.json_exec_data_outputs)
        )
        data = DBExecutionData.objects.get(node_id=json_node_id)
        self.assertEqual(self.mixin._deserialize(data.inputs, data.inputs_serializer), self.json_exec_data_inputs)
        self.assertEqual(data.inputs_serializer, self.mixin.JSON_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(data.outputs, data.outputs_serializer), self.json_exec_data_outputs)
        self.assertEqual(data.outputs_serializer, self.mixin.JSON_SERIALIZER)

        self.mixin.set_execution_data(
            pickle_node_id, ExecutionData(self.pickle_exec_data_inputs, self.pickle_exec_data_outputs)
        )
        data = DBExecutionData.objects.get(node_id=pickle_node_id)
        self.assertEqual(self.mixin._deserialize(data.inputs, data.inputs_serializer), self.pickle_exec_data_inputs)
        self.assertEqual(data.inputs_serializer, self.mixin.PICKLE_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(data.outputs, data.outputs_serializer), self.pickle_exec_data_outputs)
        self.assertEqual(data.outputs_serializer, self.mixin.PICKLE_SERIALIZER)

        self.mixin.set_execution_data(
            mix_node_id, ExecutionData(self.json_exec_data_inputs, self.pickle_exec_data_outputs)
        )
        data = DBExecutionData.objects.get(node_id=mix_node_id)
        self.assertEqual(self.mixin._deserialize(data.inputs, data.inputs_serializer), self.json_exec_data_inputs)
        self.assertEqual(data.inputs_serializer, self.mixin.JSON_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(data.outputs, data.outputs_serializer), self.pickle_exec_data_outputs)
        self.assertEqual(data.outputs_serializer, self.mixin.PICKLE_SERIALIZER)

    def test_set_execution_data__new(self):
        json_node_id = unique_id("n")
        pickle_node_id = unique_id("n")
        mix_node_id = unique_id("n")

        self.mixin.set_execution_data(
            json_node_id, ExecutionData(self.json_exec_data_inputs, self.json_exec_data_outputs)
        )
        data = DBExecutionData.objects.get(node_id=json_node_id)
        self.assertEqual(self.mixin._deserialize(data.inputs, data.inputs_serializer), self.json_exec_data_inputs)
        self.assertEqual(data.inputs_serializer, self.mixin.JSON_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(data.outputs, data.outputs_serializer), self.json_exec_data_outputs)
        self.assertEqual(data.outputs_serializer, self.mixin.JSON_SERIALIZER)

        self.mixin.set_execution_data(
            pickle_node_id, ExecutionData(self.pickle_exec_data_inputs, self.pickle_exec_data_outputs)
        )
        data = DBExecutionData.objects.get(node_id=pickle_node_id)
        self.assertEqual(self.mixin._deserialize(data.inputs, data.inputs_serializer), self.pickle_exec_data_inputs)
        self.assertEqual(data.inputs_serializer, self.mixin.PICKLE_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(data.outputs, data.outputs_serializer), self.pickle_exec_data_outputs)
        self.assertEqual(data.outputs_serializer, self.mixin.PICKLE_SERIALIZER)

        self.mixin.set_execution_data(
            mix_node_id, ExecutionData(self.json_exec_data_inputs, self.pickle_exec_data_outputs)
        )
        data = DBExecutionData.objects.get(node_id=mix_node_id)
        self.assertEqual(self.mixin._deserialize(data.inputs, data.inputs_serializer), self.json_exec_data_inputs)
        self.assertEqual(data.inputs_serializer, self.mixin.JSON_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(data.outputs, data.outputs_serializer), self.pickle_exec_data_outputs)
        self.assertEqual(data.outputs_serializer, self.mixin.PICKLE_SERIALIZER)

    def test_set_execution_data_inputs(self):
        json_node_id = unique_id("n")
        pickle_node_id = unique_id("n")

        DBExecutionData.objects.create(
            node_id=json_node_id,
            inputs="{}",
            inputs_serializer=self.mixin.JSON_SERIALIZER,
            outputs="{}",
            outputs_serializer=self.mixin.JSON_SERIALIZER,
        )
        DBExecutionData.objects.create(
            node_id=pickle_node_id,
            inputs="{}",
            inputs_serializer=self.mixin.JSON_SERIALIZER,
            outputs="{}",
            outputs_serializer=self.mixin.JSON_SERIALIZER,
        )

        self.mixin.set_execution_data_inputs(json_node_id, self.json_exec_data_inputs)
        data = DBExecutionData.objects.get(node_id=json_node_id)
        self.assertEqual(self.mixin._deserialize(data.inputs, data.inputs_serializer), self.json_exec_data_inputs)
        self.assertEqual(data.inputs_serializer, self.mixin.JSON_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(data.outputs, data.outputs_serializer), {})
        self.assertEqual(data.outputs_serializer, self.mixin.JSON_SERIALIZER)

        self.mixin.set_execution_data_inputs(pickle_node_id, self.pickle_exec_data_inputs)
        data = DBExecutionData.objects.get(node_id=pickle_node_id)
        self.assertEqual(self.mixin._deserialize(data.inputs, data.inputs_serializer), self.pickle_exec_data_inputs)
        self.assertEqual(data.inputs_serializer, self.mixin.PICKLE_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(data.outputs, data.outputs_serializer), {})
        self.assertEqual(data.outputs_serializer, self.mixin.JSON_SERIALIZER)

    def test_set_execution_data_inputs__new(self):
        json_node_id = unique_id("n")
        pickle_node_id = unique_id("n")

        self.mixin.set_execution_data_inputs(json_node_id, self.json_exec_data_inputs)
        data = DBExecutionData.objects.get(node_id=json_node_id)
        self.assertEqual(self.mixin._deserialize(data.inputs, data.inputs_serializer), self.json_exec_data_inputs)
        self.assertEqual(data.inputs_serializer, self.mixin.JSON_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(data.outputs, data.outputs_serializer), {})
        self.assertEqual(data.outputs_serializer, self.mixin.JSON_SERIALIZER)

        self.mixin.set_execution_data_inputs(pickle_node_id, self.pickle_exec_data_inputs)
        data = DBExecutionData.objects.get(node_id=pickle_node_id)
        self.assertEqual(self.mixin._deserialize(data.inputs, data.inputs_serializer), self.pickle_exec_data_inputs)
        self.assertEqual(data.inputs_serializer, self.mixin.PICKLE_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(data.outputs, data.outputs_serializer), {})
        self.assertEqual(data.outputs_serializer, self.mixin.JSON_SERIALIZER)

    def test_set_execution_data_outputs(self):
        json_node_id = unique_id("n")
        pickle_node_id = unique_id("n")

        DBExecutionData.objects.create(
            node_id=json_node_id,
            inputs="{}",
            inputs_serializer=self.mixin.JSON_SERIALIZER,
            outputs="{}",
            outputs_serializer=self.mixin.JSON_SERIALIZER,
        )
        DBExecutionData.objects.create(
            node_id=pickle_node_id,
            inputs="{}",
            inputs_serializer=self.mixin.JSON_SERIALIZER,
            outputs="{}",
            outputs_serializer=self.mixin.JSON_SERIALIZER,
        )

        self.mixin.set_execution_data_outputs(json_node_id, self.json_exec_data_outputs)
        data = DBExecutionData.objects.get(node_id=json_node_id)
        self.assertEqual(self.mixin._deserialize(data.inputs, data.inputs_serializer), {})
        self.assertEqual(data.inputs_serializer, self.mixin.JSON_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(data.outputs, data.outputs_serializer), self.json_exec_data_outputs)
        self.assertEqual(data.outputs_serializer, self.mixin.JSON_SERIALIZER)

        self.mixin.set_execution_data_outputs(pickle_node_id, self.pickle_exec_data_outputs)
        data = DBExecutionData.objects.get(node_id=pickle_node_id)
        self.assertEqual(self.mixin._deserialize(data.inputs, data.inputs_serializer), {})
        self.assertEqual(data.inputs_serializer, self.mixin.JSON_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(data.outputs, data.outputs_serializer), self.pickle_exec_data_outputs)
        self.assertEqual(data.outputs_serializer, self.mixin.PICKLE_SERIALIZER)

    def test_set_execution_data_outputs__new(self):
        json_node_id = unique_id("n")
        pickle_node_id = unique_id("n")

        self.mixin.set_execution_data_outputs(json_node_id, self.json_exec_data_outputs)
        data = DBExecutionData.objects.get(node_id=json_node_id)
        self.assertEqual(self.mixin._deserialize(data.inputs, data.inputs_serializer), {})
        self.assertEqual(data.inputs_serializer, self.mixin.JSON_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(data.outputs, data.outputs_serializer), self.json_exec_data_outputs)
        self.assertEqual(data.outputs_serializer, self.mixin.JSON_SERIALIZER)

        self.mixin.set_execution_data_outputs(pickle_node_id, self.pickle_exec_data_outputs)
        data = DBExecutionData.objects.get(node_id=pickle_node_id)
        self.assertEqual(self.mixin._deserialize(data.inputs, data.inputs_serializer), {})
        self.assertEqual(data.inputs_serializer, self.mixin.JSON_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(data.outputs, data.outputs_serializer), self.pickle_exec_data_outputs)
        self.assertEqual(data.outputs_serializer, self.mixin.PICKLE_SERIALIZER)

    def test_set_callback_data(self):
        self.raw_callback_data["c"] = 1
        data_id = self.mixin.set_callback_data(node_id=self.node_id, version=self.version, data=self.raw_callback_data)
        data_model = DBCallbackData.objects.get(id=data_id)
        self.assertEqual(data_model.node_id, self.node_id)
        self.assertEqual(data_model.version, self.version)
        self.assertEqual(json.loads(data_model.data), self.raw_callback_data)

    def test_get_callback_data(self):
        data = self.mixin.get_callback_data(self.callback_data.id)
        self.assertIsInstance(data, CallbackData)
        self.assertEqual(data.id, self.callback_data.id)
        self.assertEqual(data.node_id, self.node_id)
        self.assertEqual(data.version, self.version)
        self.assertEqual(data.data, self.raw_callback_data)
