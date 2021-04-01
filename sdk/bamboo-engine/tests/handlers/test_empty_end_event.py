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

from mock import MagicMock, call

from bamboo_engine import states
from bamboo_engine.eri import (
    ProcessInfo,
    NodeType,
    EmptyEndEvent,
    ContextValue,
    ContextValueType,
    SubProcess,
)
from bamboo_engine.handlers.empty_end_event import EmptyEndEventHandler


def test_empty_end_event_handler__root_pipeline_execute_success():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    node = EmptyEndEvent(
        id="nid",
        type=NodeType.EmptyEndEvent,
        target_flows=[],
        target_nodes=[],
        targets={},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
    )

    context_outputs = ["${a}", "${b}", "${c}", "${d}"]
    context_values = [
        ContextValue(key="${a}", value="1", type=ContextValueType.PLAIN),
        ContextValue(key="${b}", value="2", type=ContextValueType.PLAIN),
        ContextValue(key="${c}", value="3", type=ContextValueType.PLAIN),
    ]

    runtime = MagicMock()
    runtime.get_data_inputs = MagicMock(return_value={})
    runtime.get_context_outputs = MagicMock(return_value=context_outputs)
    runtime.get_context_values = MagicMock(return_value=context_values)

    handler = EmptyEndEventHandler(node, runtime)
    result = handler.execute(pi, 1, "v1")

    assert result.should_sleep == False
    assert result.schedule_ready == False
    assert result.schedule_type == None
    assert result.schedule_after == -1
    assert result.dispatch_processes == []
    assert result.next_node_id == None
    assert result.should_die == True

    runtime.get_data_inputs.assert_called_once_with("root")
    runtime.get_context_outputs.assert_called_once_with("root")
    runtime.get_context_values.assert_called_once_with(
        pipeline_id="root", keys=context_outputs
    )
    runtime.set_execution_data_outputs.assert_called_once_with(
        node_id="root",
        outputs={
            "${a}": "1",
            "${b}": "2",
            "${c}": "3",
            "${d}": "${d}",
        },
    )
    runtime.set_state.assert_has_calls(
        [
            call(
                node_id=node.id,
                to_state=states.FINISHED,
                set_archive_time=True,
            ),
            call(
                node_id="root",
                to_state=states.FINISHED,
                set_archive_time=True,
            ),
        ]
    )
    assert pi.pipeline_stack == []


def test_empty_end_event_handler__subprocess_execute_success():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root", "sub1"],
        parent_id="parent",
    )

    node = EmptyEndEvent(
        id="nid",
        type=NodeType.EmptyEndEvent,
        target_flows=[],
        target_nodes=[],
        targets={},
        root_pipeline_id="root",
        parent_pipeline_id="sub1",
        can_skip=True,
    )

    subprocess_node = SubProcess(
        id="nid",
        type=NodeType.SubProcess,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="sub1",
        can_skip=True,
        start_event_id="start_nid",
    )

    subprocess_outputs = {}

    state = MagicMock()
    state.loop = 1

    context_outputs = ["${a}", "${b}", "${c}", "${d}"]
    context_values = [
        ContextValue(key="${a}", value="1", type=ContextValueType.PLAIN),
        ContextValue(key="${b}", value="2", type=ContextValueType.PLAIN),
        ContextValue(key="${c}", value="3", type=ContextValueType.PLAIN),
    ]

    runtime = MagicMock()
    runtime.get_data_inputs = MagicMock(return_value={})
    runtime.get_context_outputs = MagicMock(return_value=context_outputs)
    runtime.get_context_values = MagicMock(return_value=context_values)
    runtime.get_node = MagicMock(return_value=subprocess_node)
    runtime.get_data_outputs = MagicMock(return_value=subprocess_outputs)
    runtime.get_state = MagicMock(return_value=state)

    handler = EmptyEndEventHandler(node, runtime)
    result = handler.execute(pi, 1, "v1")

    assert result.should_sleep == False
    assert result.schedule_ready == False
    assert result.schedule_type == None
    assert result.schedule_after == -1
    assert result.dispatch_processes == []
    assert result.next_node_id == subprocess_node.target_nodes[0]
    assert result.should_die == False

    runtime.get_data_inputs.assert_called_once_with("root")
    runtime.get_context_outputs.assert_called_once_with("sub1")
    runtime.get_context_values.assert_called_once_with(
        pipeline_id="sub1", keys=context_outputs
    )
    runtime.set_execution_data_outputs.assert_called_once_with(
        node_id="sub1",
        outputs={
            "${a}": "1",
            "${b}": "2",
            "${c}": "3",
            "${d}": "${d}",
            "_loop": 1
        },
    )
    runtime.get_node.assert_called_once_with("sub1")
    runtime.set_pipeline_stack.assert_called_once_with(pi.process_id, ["root"])
    runtime.get_data_outputs.assert_called_once_with("sub1")
    runtime.set_state.assert_has_calls(
        [
            call(
                node_id=node.id,
                to_state=states.FINISHED,
                set_archive_time=True,
            ),
            call(
                node_id="sub1",
                to_state=states.FINISHED,
                set_archive_time=True,
            ),
        ]
    )
    runtime.get_state.assert_called_once_with("sub1")
    assert pi.pipeline_stack == ["root"]