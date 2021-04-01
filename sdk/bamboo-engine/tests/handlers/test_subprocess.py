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
specific language governing permissions and limitations underExecutableEndEvent the License.
"""

from mock import MagicMock, call

from bamboo_engine import states
from bamboo_engine.eri import (
    ProcessInfo,
    NodeType,
    SubProcess,
    ContextValue,
    ContextValueType,
    Data,
    DataInput,
)
from bamboo_engine.handlers.subprocess import SubProcessHandler


def test_subprocess_handler__execute_success():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    node = SubProcess(
        id="nid",
        type=NodeType.ExecutableEndEvent,
        target_flows=[],
        target_nodes=[],
        targets={},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        start_event_id="sid",
    )

    data = Data(
        inputs={
            "${k1}": DataInput(need_render=True, value="${v1}"),
            "${k2}": DataInput(need_render=True, value="${sub_loop}"),
        },
        outputs={"_loop": "${sub_loop}"},
    )

    context_values = [
        ContextValue(key="${v1}", value="var", type=ContextValueType.PLAIN)
    ]

    runtime = MagicMock()
    runtime.get_data = MagicMock(return_value=data)
    runtime.get_context_key_references = MagicMock(return_value=set())
    runtime.get_context_values = MagicMock(return_value=context_values)

    handler = SubProcessHandler(node, runtime)
    result = handler.execute(pi, 1, "v1")

    assert result.should_sleep == False
    assert result.schedule_ready == False
    assert result.schedule_type == None
    assert result.schedule_after == -1
    assert result.dispatch_processes == []
    assert result.next_node_id == node.start_event_id
    assert result.should_die == False

    runtime.get_data.assert_called_once_with(node.id)
    runtime.get_data_inputs.assert_called_once_with(pi.root_pipeline_id)
    runtime.get_context_key_references.assert_called_once_with(
        pipeline_id="root", keys={"${v1}", "${sub_loop}"}
    )
    runtime.get_context_values.assert_called_once_with(
        pipeline_id="root", keys={"${v1}", "${sub_loop}"}
    )
    upsert_call_args = runtime.upsert_plain_context_values.call_args.args
    assert upsert_call_args[0] == node.id
    assert upsert_call_args[1]["${k1}"].key == "${k1}"
    assert upsert_call_args[1]["${k1}"].type == ContextValueType.PLAIN
    assert upsert_call_args[1]["${k1}"].value == "var"
    assert upsert_call_args[1]["${k2}"].key == "${k2}"
    assert upsert_call_args[1]["${k2}"].type == ContextValueType.PLAIN
    assert upsert_call_args[1]["${k2}"].value == 1
    runtime.set_pipeline_stack.assert_called_once_with(pi.process_id, ["root", "nid"])
    assert pi.pipeline_stack == ["root", "nid"]