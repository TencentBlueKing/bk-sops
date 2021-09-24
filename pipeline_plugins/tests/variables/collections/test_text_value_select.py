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

from pipeline_plugins.variables.collections.common import TextValueSelect


class TextValueSelectTestCase(TestCase):
    def setUp(self):
        self.name = "name_token"
        self.pipeline_data = {}
        self.context = {}

    def test_get_value_multiple_units__all(self):
        meta_data = r'[{"text": "t1", "value": "v1"},{"text": "t2", "value": "v2"}]'
        info_value = ["v1", "v2"]
        data = {"meta_data": meta_data, "info_value": info_value}
        TextValueSelect_ins = TextValueSelect(
            name=self.name, value=data, context=self.context, pipeline_data=self.pipeline_data
        )
        normal_outputs = {"text": "t1,t2", "value": "v1,v2", "text_not_selected": "", "value_not_selected": ""}
        outputs = TextValueSelect_ins.get_value()
        self.assertEqual(outputs, normal_outputs)

    def test_get_value_multiple_units__not_all(self):
        meta_data = r'[{"text": "t1", "value": "v1"},{"text": "t2", "value": "v2"}]'
        info_value = ["v2"]
        data = {"meta_data": meta_data, "info_value": info_value}
        TextValueSelect_ins = TextValueSelect(
            name=self.name, value=data, context=self.context, pipeline_data=self.pipeline_data
        )
        normal_outputs = {"text": "t2", "value": "v2", "text_not_selected": "t1", "value_not_selected": "v1"}
        outputs = TextValueSelect_ins.get_value()
        self.assertEqual(outputs, normal_outputs)

    def test_get_value_single_units(self):
        meta_data = r'[{"text": "t1", "value": "v1"},{"text": "t2", "value": "v2"}]'
        info_value = "v2"
        data = {"meta_data": meta_data, "info_value": info_value}
        TextValueSelect_ins = TextValueSelect(
            name=self.name, value=data, context=self.context, pipeline_data=self.pipeline_data
        )
        normal_outputs = {"text": "t2", "value": "v2", "text_not_selected": "t1", "value_not_selected": "v1"}
        outputs = TextValueSelect_ins.get_value()
        self.assertEqual(outputs, normal_outputs)

    def test_process_meta_avalue(self):
        meta_data = {"value": {"items_text": r'[{"text": "t1", "value": "v1"},{"text": "t2", "value": "v2"}]'}}
        info_value = "v1"
        TextValueSelect_ins = TextValueSelect(
            name=self.name, value="", context=self.context, pipeline_data=self.pipeline_data
        )
        normal_outputs = {
            "meta_data": r'[{"text": "t1", "value": "v1"},{"text": "t2", "value": "v2"}]',
            "info_value": "v1",
        }
        outputs = TextValueSelect_ins.process_meta_avalue(meta_data, info_value)
        self.assertEqual(outputs, normal_outputs)
