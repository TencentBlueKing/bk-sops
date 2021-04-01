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

from pipeline.core.data.base import DataObject
from pipeline.engine.models import Data

from ..mock import IdentifyObject


class DataTestCase(TestCase):
    def test_write_node_data(self):
        node = IdentifyObject()
        data_obj = DataObject({"input_key": "value"}, outputs={"output_key": "value"})
        node.data = data_obj

        Data.objects.write_node_data(node)
        data = Data.objects.get(id=node.id)
        self.assertEqual(data.inputs, data_obj.inputs)
        self.assertEqual(data.outputs, data_obj.outputs)
        self.assertIsNone(data.ex_data)

        data_obj.inputs = {"new_inputs": "new_value"}
        Data.objects.write_node_data(node, ex_data="ex_data")
        data = Data.objects.get(id=node.id)
        self.assertEqual(data.inputs, data_obj.inputs)
        self.assertEqual(data.outputs, data_obj.outputs)
        self.assertEqual(data.ex_data, "ex_data")

        data_obj.outputs.ex_data = "new_ex_data"
        Data.objects.write_node_data(node, ex_data="ex_data")
        data = Data.objects.get(id=node.id)
        self.assertEqual(data.inputs, data_obj.inputs)
        self.assertEqual(data.outputs, data_obj.outputs)
        self.assertEqual(data.ex_data, "new_ex_data")

    def test_forced_fail(self):
        node = IdentifyObject()
        Data.objects.forced_fail(node.id, ex_data="")
        data = Data.objects.get(id=node.id)
        self.assertEqual(data.outputs, {"_forced_failed": True})
        self.assertEqual(data.ex_data, "")

        Data.objects.forced_fail(node.id, ex_data="ex_data")
        data = Data.objects.get(id=node.id)
        self.assertEqual(data.outputs, {"_forced_failed": True})
        self.assertEqual(data.ex_data, "ex_data")

    def test_write_ex_data(self):
        node = IdentifyObject()
        outoput = {"k": "v"}
        ex_data = "ex_data"
        new_ex_data = "new_ex_data"

        Data.objects.write_ex_data(node.id, ex_data=ex_data)
        data = Data.objects.get(id=node.id)
        self.assertEqual(data.ex_data, "ex_data")

        data.outputs = outoput
        data.save()
        Data.objects.write_ex_data(node.id, ex_data=new_ex_data)
        data = Data.objects.get(id=node.id)
        self.assertEqual(data.outputs, outoput)
        self.assertEqual(data.ex_data, new_ex_data)
