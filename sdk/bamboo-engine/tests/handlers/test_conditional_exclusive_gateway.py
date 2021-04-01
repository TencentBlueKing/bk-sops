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

from bamboo_engine import states
from bamboo_engine.eri import (
    ProcessInfo,
    NodeType,
    ExclusiveGateway,
    Condition,
)
from bamboo_engine.handlers.exclusive_gateway import (
    ExclusiveGatewayHandler,
)


def test_exclusive_gateway__execute_bool_rule_test_raise():
    conditions = [
        Condition(name="c1", evaluation="${k} == 1", target_id="t1", flow_id="f1"),
        Condition(name="c2", evaluation="0 == 1", target_id="t2", flow_id="f2"),
    ]
    node = ExclusiveGateway(
        conditions=conditions,
        id="nid",
        type=NodeType.ExclusiveGateway,
        target_flows=["f1", "f2"],
        target_nodes=["t1", "t2"],
        targets={"f1": "t1", "f2": "t2"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
    )
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )
    additional_refs = []
    context_values = []

    runtime = MagicMock()
    runtime.get_context_key_references = MagicMock(return_value=additional_refs)
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_execution_data_outputs = MagicMock(return_value={})
    runtime.get_data_inputs = MagicMock(return_value={})

    handler = ExclusiveGatewayHandler(node, runtime)
    result = handler.execute(pi, 1, "v1")

    assert result.should_sleep == True
    assert result.schedule_ready == False
    assert result.schedule_type == None
    assert result.schedule_after == -1
    assert result.dispatch_processes == []
    assert result.next_node_id == None
    assert result.should_die == False

    runtime.get_data_inputs.assert_called_once_with("root")
    runtime.get_context_key_references.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys={"${k}"}
    )
    runtime.get_context_values.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys={"${k}"}
    )
    runtime.get_execution_data_outputs.assert_called_once_with(node.id)
    runtime.set_state.assert_called_once_with(
        node_id=node.id, to_state=states.FAILED, set_archive_time=True
    )
    runtime.set_execution_data_outputs.assert_called_once()


def test_exclusive_gateway__execute_not_meet_targets():
    conditions = [
        Condition(name="c1", evaluation="0 == 1", target_id="t1", flow_id="f1"),
        Condition(name="c2", evaluation="0 == 1", target_id="t2", flow_id="f2"),
    ]
    node = ExclusiveGateway(
        conditions=conditions,
        id="nid",
        type=NodeType.ExclusiveGateway,
        target_flows=["f1", "f2"],
        target_nodes=["t1", "t2"],
        targets={"f1": "t1", "f2": "t2"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
    )
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )
    additional_refs = []
    context_values = []

    runtime = MagicMock()
    runtime.get_context_key_references = MagicMock(return_value=additional_refs)
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_execution_data_outputs = MagicMock(return_value={})
    runtime.get_data_inputs = MagicMock(return_value={})

    handler = ExclusiveGatewayHandler(node, runtime)
    result = handler.execute(pi, 1, "v1")

    assert result.should_sleep == True
    assert result.schedule_ready == False
    assert result.schedule_type == None
    assert result.schedule_after == -1
    assert result.dispatch_processes == []
    assert result.next_node_id == None
    assert result.should_die == False

    runtime.get_data_inputs.assert_called_once_with("root")
    runtime.get_context_key_references.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set()
    )
    runtime.get_context_values.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set()
    )
    runtime.get_execution_data_outputs.assert_called_once_with(node.id)
    runtime.set_state.assert_called_once_with(
        node_id=node.id, to_state=states.FAILED, set_archive_time=True
    )
    runtime.set_execution_data_outputs.assert_called_once_with(
        node.id, {"ex_data": "all conditions of branches are not meet"}
    )


def test_exclusive_gateway__execute_mutiple_meet_targets():
    conditions = [
        Condition(name="c1", evaluation="1 == 1", target_id="t1", flow_id="f1"),
        Condition(name="c2", evaluation="1 == 1", target_id="t2", flow_id="f2"),
    ]
    node = ExclusiveGateway(
        conditions=conditions,
        id="nid",
        type=NodeType.ExclusiveGateway,
        target_flows=["f1", "f2"],
        target_nodes=["t1", "t2"],
        targets={"f1": "t1", "f2": "t2"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
    )
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )
    additional_refs = []
    context_values = []

    runtime = MagicMock()
    runtime.get_context_key_references = MagicMock(return_value=additional_refs)
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_execution_data_outputs = MagicMock(return_value={})
    runtime.get_data_inputs = MagicMock(return_value={})

    handler = ExclusiveGatewayHandler(node, runtime)
    result = handler.execute(pi, 1, "v1")

    assert result.should_sleep == True
    assert result.schedule_ready == False
    assert result.schedule_type == None
    assert result.schedule_after == -1
    assert result.dispatch_processes == []
    assert result.next_node_id == None
    assert result.should_die == False

    runtime.get_data_inputs.assert_called_once_with("root")
    runtime.get_context_key_references.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set()
    )
    runtime.get_context_values.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set()
    )
    runtime.get_execution_data_outputs.assert_called_once_with(node.id)
    runtime.set_state.assert_called_once_with(
        node_id=node.id, to_state=states.FAILED, set_archive_time=True
    )
    runtime.set_execution_data_outputs.assert_called_once_with(
        node.id, {"ex_data": "multiple conditions meet: ['c1', 'c2']"}
    )


def test_exclusive_gateway__execute_success():
    conditions = [
        Condition(name="c1", evaluation="0 == 1", target_id="t1", flow_id="f1"),
        Condition(name="c2", evaluation="0 == 1", target_id="t2", flow_id="f2"),
        Condition(name="c3", evaluation="1 == 1", target_id="t3", flow_id="f3"),
    ]
    node = ExclusiveGateway(
        conditions=conditions,
        id="nid",
        type=NodeType.ExclusiveGateway,
        target_flows=["f1", "f2", "f3"],
        target_nodes=["t1", "t2", "t3"],
        targets={"f1": "t1", "f2": "t2", "f3": "t3"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
    )
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )
    additional_refs = []
    context_values = []

    runtime = MagicMock()
    runtime.get_context_key_references = MagicMock(return_value=additional_refs)
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_data_inputs = MagicMock(return_value={})

    handler = ExclusiveGatewayHandler(node, runtime)
    result = handler.execute(pi, 1, "v1")

    assert result.should_sleep == False
    assert result.schedule_ready == False
    assert result.schedule_type == None
    assert result.schedule_after == -1
    assert result.dispatch_processes == []
    assert result.next_node_id == "t3"
    assert result.should_die == False

    runtime.get_data_inputs.assert_called_once_with("root")
    runtime.get_context_key_references.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set()
    )
    runtime.get_context_values.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set()
    )
    runtime.set_state.assert_called_once_with(
        node_id=node.id, to_state=states.FINISHED, set_archive_time=True
    )