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

from bamboo_engine.eri import ContextValue, ContextValueType, Variable
from bamboo_engine.context import Context, PlainVariable, SpliceVariable


def test_hydrate():
    class CV(Variable):
        def __init__(self, value):
            self.value = value

        def get(self):
            return "compute_result"

    compute_var = CV("compute_value")

    runtime = MagicMock()
    runtime.get_compute_variable = MagicMock(return_value=compute_var)

    values = [
        ContextValue("${a}", type=ContextValueType.PLAIN, value="1"),
        ContextValue("${b}", type=ContextValueType.PLAIN, value="2"),
        ContextValue("${c}", type=ContextValueType.SPLICE, value="${a}-${b}"),
        ContextValue("${d}", type=ContextValueType.SPLICE, value="${int(a) + int(b)}"),
        ContextValue(
            "${e}",
            type=ContextValueType.COMPUTE,
            value="compute_value",
            code="compute_var",
        ),
        ContextValue(
            "${f}", type=ContextValueType.SPLICE, value="${a}-${b}-${c}-${d}-${e}"
        ),
    ]

    context = Context(runtime, values, {"id": 1})
    hydrated = context.hydrate()
    assert hydrated == {
        "${a}": "1",
        "${b}": "2",
        "${c}": "1-2",
        "${d}": "3",
        "${e}": "compute_result",
        "${f}": "1-2-1-2-3-compute_result",
    }
    runtime.get_compute_variable.assert_called_once()

    context = Context(runtime, values, {"id": 1})
    hydrated = context.hydrate(deformat=True)
    assert hydrated == {
        "a": "1",
        "b": "2",
        "c": "1-2",
        "d": "3",
        "e": "compute_result",
        "f": "1-2-1-2-3-compute_result",
    }


def test_extract_outputs():
    pipeline_id = "pipeline"
    data_outputs = {"a": "b", "c": "d", "e": "f"}
    execution_data_outputs = {"a": 1, "e": 2}

    runtime = MagicMock()

    context = Context(runtime, [], {})
    context.extract_outputs(pipeline_id, data_outputs, execution_data_outputs)

    upsert_call_args = runtime.upsert_plain_context_values.call_args.kwargs
    assert upsert_call_args["pipeline_id"] == pipeline_id
    assert len(upsert_call_args["update"]) == 2
    assert upsert_call_args["update"]["b"].key == "b"
    assert upsert_call_args["update"]["b"].type == ContextValueType.PLAIN
    assert upsert_call_args["update"]["b"].value == 1
    assert upsert_call_args["update"]["f"].key == "f"
    assert upsert_call_args["update"]["f"].type == ContextValueType.PLAIN
    assert upsert_call_args["update"]["f"].value == 2
