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

from copy import deepcopy
from mock import MagicMock, call

from django.test import TestCase

from pipeline import exceptions
from pipeline.core.data import base, context


class TestContext(TestCase):
    def setUp(self):
        act_outputs = {
            "act_id_1": {"output_1": "gk_1_1", "output_2": "gk_1_2"},
            "act_id_2": {"output_1": "gk_2_1"},
            "act_id_4": {"output_1": "gk_4_1", "output_2": "gk_4_2"},
        }
        self.context = context.Context(act_outputs)

        class Activity(object):
            pass

        act_1 = Activity()
        act_1.id = "act_id_1"
        data_1 = base.DataObject({})
        data_1.set_outputs("output_1", "value_1_1")
        data_1.set_outputs("output_2", "value_1_2")
        act_1.data = data_1
        self.act_1 = act_1

        act_2 = Activity()
        act_2.id = "act_id_2"
        data_2 = base.DataObject({})
        data_2.set_outputs("output_1", "value_2_1")
        data_2.set_outputs("output_2", "value_2_2")
        data_2.set_outputs("output_3", "value_2_3")
        act_2.data = data_2
        self.act_2 = act_2

        act_3 = Activity()
        act_3.id = "act_id_3"
        data_3 = base.DataObject({})
        data_3.set_outputs("output_1", "value_3_1")
        data_3.set_outputs("output_2", "value_3_2")
        data_3.set_outputs("output_3", "value_3_3")
        act_3.data = data_3
        self.act_3 = act_3

        act_4 = Activity()
        act_4.id = "act_id_4"
        data_4 = base.DataObject({})
        data_4.set_outputs("output_1", "value_4_1")
        act_4.data = data_4
        self.act_4 = act_4

    def test_extract_output(self):
        self.assertEqual(self.context.change_keys, set())
        self.context.extract_output(self.act_1)
        self.assertEqual(self.context.variables, {"gk_1_1": "value_1_1", "gk_1_2": "value_1_2"})
        self.assertEqual(self.context.change_keys, {"gk_1_1", "gk_1_2"})
        self.context.extract_output(self.act_2)
        self.assertEqual(self.context.variables, {"gk_1_1": "value_1_1", "gk_1_2": "value_1_2", "gk_2_1": "value_2_1"})
        self.assertEqual(self.context.change_keys, {"gk_1_1", "gk_1_2", "gk_2_1"})
        self.context.extract_output(self.act_3)
        self.assertEqual(self.context.variables, {"gk_1_1": "value_1_1", "gk_1_2": "value_1_2", "gk_2_1": "value_2_1"})
        self.assertEqual(self.context.change_keys, {"gk_1_1", "gk_1_2", "gk_2_1"})
        self.context.extract_output(self.act_4, set_miss=False)
        self.assertEqual(
            self.context.variables,
            {"gk_1_1": "value_1_1", "gk_1_2": "value_1_2", "gk_2_1": "value_2_1", "gk_4_1": "value_4_1"},
        )
        self.assertEqual(self.context.change_keys, {"gk_1_1", "gk_1_2", "gk_2_1", "gk_4_1"})

    def test_get(self):
        self.context.extract_output(self.act_1)
        self.assertEqual(self.context.get("gk_1_1"), "value_1_1")
        self.assertRaises(exceptions.ReferenceNotExistError, self.context.get, "key_not_exist")

    def test_set_global_var(self):
        self.assertEqual(self.context.change_keys, set())
        self.context.set_global_var("key", "test_val")
        self.assertEqual(self.context.get("key"), "test_val")
        self.assertEqual(self.context.change_keys, {"key"})

    def test_update_global_var(self):
        self.assertEqual(self.context.change_keys, set())
        self.context.set_global_var("key_1", "test_val")
        self.context.update_global_var({"key_1": "test_val1", "key_2": "test_val2"})
        self.assertEqual(self.context.get("key_1"), "test_val1")
        self.assertEqual(self.context.get("key_2"), "test_val2")
        self.assertEqual(self.context.change_keys, {"key_1", "key_2"})

    def test_mark_as_output(self):
        self.context.mark_as_output("key")
        self.assertEqual(self.context._output_key, {"key"})

    def test_output(self):
        class MockPipeline(object):
            def __init__(self, data):
                self.data = data

        pipeline = MockPipeline(base.DataObject({}))
        self.context.mark_as_output("gk_1_1")
        self.context.mark_as_output("gk_1_2")
        self.context.extract_output(self.act_1)
        self.context.write_output(pipeline)
        self.assertEqual(pipeline.data.get_outputs(), {"gk_1_1": "value_1_1", "gk_1_2": "value_1_2"})

    def test_clear(self):
        self.context.set_global_var("key", "test_val")
        self.context.clear()
        self.assertRaises(exceptions.ReferenceNotExistError, self.context.get, "key")

    def test_duplicate_variables(self):
        self.context.set_global_var("k1", None)
        self.context.set_global_var("k2", None)

        self.assertRaises(exceptions.InvalidOperationException, self.context.recover_variable)
        self.context.duplicate_variables()
        self.context.set_global_var("k1", "v1")
        self.context.set_global_var("k2", "v2")
        self.context.set_global_var("gk_1_1", "v3")
        self.context.set_global_var("gk_1_2", "v4")
        self.context.set_global_var("gk_2_1", "v5")

        self.context.recover_variable()
        self.assertIsNone(self.context.get("k1"))
        self.assertIsNone(self.context.get("k2"))
        self.assertEqual(self.context.get("gk_1_1"), "v3")
        self.assertEqual(self.context.get("gk_1_2"), "v4")
        self.assertEqual(self.context.get("gk_2_1"), "v5")

    def test_change_keys(self):
        del self.context._change_keys
        self.assertFalse(hasattr(self.context, "_change_keys"))
        self.context.change_keys
        self.assertTrue(hasattr(self.context, "_change_keys"))
        self.assertEqual(self.context._change_keys, set())
        self.assertEqual(self.context.change_keys, set())

    def test_raw_variables(self):
        del self.context._raw_variables
        self.assertFalse(hasattr(self.context, "_raw_variables"))
        self.context.raw_variables
        self.assertTrue(hasattr(self.context, "_raw_variables"))
        self.assertIsNone(self.context._raw_variables)
        self.assertIsNone(self.context.raw_variables)

    def test_clear_change_keys(self):
        self.assertEqual(self.context.change_keys, set())
        self.context.update_global_var({"key_1": "test_val1", "key_2": "test_val2"})
        self.assertEqual(self.context.change_keys, {"key_1", "key_2"})
        self.context.clear_change_keys()
        self.assertEqual(self.context.change_keys, set())

    def test_sync_change(self):
        child_context = context.Context({})
        self.context.update_global_var({"key_1": "test_val1", "key_2": "test_val2"})
        self.context.clear_change_keys()
        child_context.variables = deepcopy(self.context.variables)
        child_context.set_global_var("key_1", "new_val_1")
        child_context.set_global_var("key_3", "new_val_3")
        self.context.sync_change(child_context)
        self.assertEqual(self.context.variables, {"key_1": "new_val_1", "key_2": "test_val2", "key_3": "new_val_3"})

    def test_sync_change_with_splice_vars(self):
        from pipeline.core.data.var import SpliceVariable

        child_context = context.Context({})
        self.context.update_global_var(
            {
                "key_1": "test_val1",
                "key_2": "test_val2",
                "key_3": "value3",  # not splice
                "key_4": SpliceVariable("key_4", "val3", self.context),  # splice sync success
                "key_5": SpliceVariable("key_5", "val5", self.context),  # splice parent not none
                "key_6": SpliceVariable("key_5", "val6", self.context),  # splice child none
            }
        )
        self.context.variables["key_5"]._value = "old_val5"
        self.context.clear_change_keys()

        child_context.variables = deepcopy(self.context.variables)
        child_context.set_global_var("key_1", "new_val_1")
        child_context.set_global_var("key_0", "new_val_0")
        child_context.variables["key_3"] = SpliceVariable("key_3", "val3", child_context)
        child_context.variables["key_4"] = SpliceVariable("key_4", "val4", child_context)
        child_context.variables["key_5"] = SpliceVariable("key_5", "val5", child_context)
        child_context.variables["key_6"] = SpliceVariable("key_6", "val6", child_context)
        child_context.variables["key_4"]._value = "val4"
        child_context.variables["key_5"]._value = "val5"

        self.assertIsNone(self.context.variables["key_4"]._value)
        self.context.sync_change(child_context)
        self.assertEqual(self.context.variables["key_0"], "new_val_0")
        self.assertEqual(self.context.variables["key_1"], "new_val_1")
        self.assertEqual(self.context.variables["key_2"], "test_val2")
        self.assertEqual(self.context.variables["key_3"], "value3")
        self.assertEqual(self.context.variables["key_4"]._value, "val4")
        self.assertEqual(self.context.variables["key_5"]._value, "old_val5")
        self.assertEqual(self.context.variables["key_6"]._value, None)

    def test_write_output__missing_some_keys(self):
        test_context = context.Context({})
        test_context._output_key = ["key1", "key2", "key3"]
        test_context.variables = {"key1": "val1", "key2": "val2"}

        mock_pipeline = MagicMock()
        mock_pipeline.data = MagicMock()
        test_context.write_output(mock_pipeline)
        mock_pipeline.data.set_outputs.assert_has_calls(
            [call("key1", "val1"), call("key2", "val2"), call("key3", "key3")]
        )


class TestOutputRef(TestCase):
    def setUp(self):
        act_outputs = {"act_id_1": {"output_1": "gk_1_1", "output_2": "gk_1_2"}, "act_id_2": {"output_1": "gk_2_1"}}
        self.context = context.Context(act_outputs)

        class Activity(object):
            pass

        act_1 = Activity()
        act_1.id = "act_id_1"
        data_1 = base.DataObject({})
        data_1.set_outputs("output_1", "value_1_1")
        data_1.set_outputs("output_2", "value_1_2")
        act_1.data = data_1
        self.act_1 = act_1

    def test_value(self):
        ref = context.OutputRef("gk_1_1", self.context)
        self.context.extract_output(self.act_1)
        self.assertEqual(ref.value, "value_1_1")

    def test_deep_copy(self):
        ref = context.OutputRef("gk_1_1", self.context)
        ref_copy = deepcopy(ref)
        self.assertTrue(ref_copy is ref)
        self.assertTrue(ref_copy.context is ref.context)
