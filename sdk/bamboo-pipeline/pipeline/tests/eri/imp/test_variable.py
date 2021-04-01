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

from mock import MagicMock

from django.test import TestCase

from bamboo_engine.eri import ContextValue, ContextValueType
from bamboo_engine.context import Context, SpliceVariable

from pipeline.core.data.var import LazyVariable
from pipeline.eri.imp.variable import VariableWrapper


class TestVariable(LazyVariable):
    code = "wrapper_test"
    name = "wrapper_test"

    def get_value(self):
        assert self.value == "1-2"
        assert self.pipeline_data == {"1": 1, "2": 2}
        return "heihei"


class VariableWrapperTestCase(TestCase):
    def test_get(self):
        runtime = MagicMock()

        values = [
            ContextValue("${a}", type=ContextValueType.PLAIN, value="1"),
            ContextValue("${b}", type=ContextValueType.PLAIN, value="2"),
            ContextValue("${c}", type=ContextValueType.SPLICE, value="${a}-${b}"),
        ]

        context = Context(runtime, values, {"id": 1})

        w = VariableWrapper(
            orginal_value=SpliceVariable(key="${c}", value="${a}-${b}", pool=context.pool),
            var_cls=TestVariable,
            additional_data={"1": 1, "2": 2},
        )

        self.assertEqual(w.get(), "heihei")
