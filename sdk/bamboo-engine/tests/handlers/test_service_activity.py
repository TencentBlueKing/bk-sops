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
    ServiceActivity,
    ContextValue,
    ContextValueType,
    Data,
    DataInput,
    ScheduleType,
    Schedule,
    ExecutionData,
)
from bamboo_engine.handlers.service_activity import ServiceActivityHandler


def test_execute__raise_not_ignore():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="",
    )

    node = ServiceActivity(
        id="nid",
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        code="test_service",
        version="legacy",
        error_ignorable=False,
        timeout=10,
    )

    data = Data({}, {})

    service = MagicMock()
    service.execute = MagicMock(side_effect=Exception)
    service.need_schedule = MagicMock(return_value=False)

    runtime = MagicMock()
    runtime.get_data = MagicMock(return_value=data)
    runtime.get_context_key_references = MagicMock(return_value=set())
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_service = MagicMock(return_value=service)

    handler = ServiceActivityHandler(node, runtime)
    result = handler.execute(pi, 1, "v1")

    assert result.should_sleep == True
    assert result.schedule_ready == False
    assert result.schedule_type == None
    assert result.schedule_after == -1
    assert result.dispatch_processes == []
    assert result.next_node_id == None
    assert result.should_die == False

    runtime.get_data.assert_called_once_with(node.id)
    runtime.get_data_inputs.assert_called_once_with(pi.root_pipeline_id)
    runtime.get_context_key_references.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set()
    )
    runtime.get_context_values.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set()
    )
    runtime.get_service.assert_called_once_with(code=node.code, version=node.version)
    runtime.start_timeout_monitor.assert_called_once_with(
        process_id=pi.process_id,
        node_id=node.id,
        version="v1",
        timeout=node.timeout,
    )
    runtime.set_state.assert_called_once_with(
        node_id=node.id, version="v1", to_state=states.FAILED, set_archive_time=True
    )
    runtime.stop_timeout_monitor.assert_called_once_with(
        process_id=pi.process_id,
        node_id=node.id,
        version="v1",
        timeout=node.timeout,
    )
    runtime.set_execution_data.assert_called_once()
    assert runtime.set_execution_data.call_args.kwargs["node_id"] == node.id
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {"_loop": 1}
    assert "ex_data" in runtime.set_execution_data.call_args.kwargs["data"].outputs

    service.setup_runtime_attributes.assert_called_once_with(
        id=node.id,
        version="v1",
        root_pipeline_id=pi.root_pipeline_id,
        top_pipeline_id=pi.top_pipeline_id,
        loop=1,
    )
    assert service.pre_execute.call_args.kwargs["data"].inputs == {"_loop": 1}
    assert "ex_data" in service.pre_execute.call_args.kwargs["data"].outputs
    assert service.pre_execute.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.pre_execute.call_args.kwargs["root_pipeline_data"].outputs == {}
    assert service.execute.call_args.kwargs["data"].inputs == {"_loop": 1}
    assert "ex_data" in service.execute.call_args.kwargs["data"].outputs
    assert service.execute.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.execute.call_args.kwargs["root_pipeline_data"].outputs == {}


def test_execute__raise_ignore():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="",
    )

    node = ServiceActivity(
        id="nid",
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        code="test_service",
        version="legacy",
        error_ignorable=True,
        timeout=None,
    )

    data = Data({}, {})

    service = MagicMock()
    service.execute = MagicMock(side_effect=Exception)
    service.need_schedule = MagicMock(return_value=True)

    runtime = MagicMock()
    runtime.get_data = MagicMock(return_value=data)
    runtime.get_context_key_references = MagicMock(return_value=set())
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_service = MagicMock(return_value=service)

    handler = ServiceActivityHandler(node, runtime)
    result = handler.execute(pi, 1, "v1")

    assert result.should_sleep == False
    assert result.schedule_ready == False
    assert result.schedule_type == None
    assert result.schedule_after == -1
    assert result.dispatch_processes == []
    assert result.next_node_id == node.target_nodes[0]
    assert result.should_die == False

    runtime.get_data.assert_called_once_with(node.id)
    runtime.get_data_inputs.assert_called_once_with(pi.root_pipeline_id)
    runtime.get_context_key_references.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set()
    )
    runtime.get_context_values.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set()
    )
    runtime.get_service.assert_called_once_with(code=node.code, version=node.version)
    runtime.start_timeout_monitor.assert_not_called()
    runtime.set_state.assert_called_once_with(
        node_id=node.id,
        version="v1",
        to_state=states.FINISHED,
        set_archive_time=True,
        error_ignored=True,
    )
    runtime.stop_timeout_monitor.assert_not_called()
    runtime.set_execution_data.assert_called_once()
    assert runtime.set_execution_data.call_args.kwargs["node_id"] == node.id
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {"_loop": 1}
    assert "ex_data" in runtime.set_execution_data.call_args.kwargs["data"].outputs

    service.setup_runtime_attributes.assert_called_once_with(
        id=node.id,
        version="v1",
        root_pipeline_id=pi.root_pipeline_id,
        top_pipeline_id=pi.top_pipeline_id,
        loop=1,
    )
    assert service.pre_execute.call_args.kwargs["data"].inputs == {"_loop": 1}
    assert "ex_data" in service.pre_execute.call_args.kwargs["data"].outputs
    assert service.pre_execute.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.pre_execute.call_args.kwargs["root_pipeline_data"].outputs == {}
    assert service.execute.call_args.kwargs["data"].inputs == {"_loop": 1}
    assert "ex_data" in service.execute.call_args.kwargs["data"].outputs
    assert service.execute.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.execute.call_args.kwargs["root_pipeline_data"].outputs == {}


def test_execute__success_and_schedule():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="",
    )

    node = ServiceActivity(
        id="nid",
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        code="test_service",
        version="legacy",
        error_ignorable=False,
        timeout=10,
    )

    data = Data({}, {})

    service = MagicMock()
    service.need_schedule = MagicMock(return_value=True)
    service.schedule_type = MagicMock(return_value=ScheduleType.POLL)
    service.schedule_after = MagicMock(return_value=5)
    service.execute = MagicMock(return_value=True)

    runtime = MagicMock()
    runtime.get_data = MagicMock(return_value=data)
    runtime.get_context_key_references = MagicMock(return_value=set())
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_service = MagicMock(return_value=service)

    handler = ServiceActivityHandler(node, runtime)
    result = handler.execute(pi, 1, "v1")

    assert result.should_sleep == True
    assert result.schedule_ready == True
    assert result.schedule_type == ScheduleType.POLL
    assert result.schedule_after == 5
    assert result.dispatch_processes == []
    assert result.next_node_id == None
    assert result.should_die == False

    runtime.get_data.assert_called_once_with(node.id)
    runtime.get_data_inputs.assert_called_once_with(pi.root_pipeline_id)
    runtime.get_context_key_references.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set()
    )
    runtime.get_context_values.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set()
    )
    runtime.get_service.assert_called_once_with(code=node.code, version=node.version)
    runtime.start_timeout_monitor.assert_called_once_with(
        process_id=pi.process_id,
        node_id=node.id,
        version="v1",
        timeout=node.timeout,
    )
    runtime.set_state.assert_not_called()
    runtime.stop_timeout_monitor.assert_not_called()
    runtime.set_execution_data.assert_called_once()
    assert runtime.set_execution_data.call_args.kwargs["node_id"] == node.id
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {"_loop": 1}
    assert runtime.set_execution_data.call_args.kwargs["data"].outputs == {
        "_result": True
    }

    service.setup_runtime_attributes.assert_called_once_with(
        id=node.id,
        version="v1",
        root_pipeline_id=pi.root_pipeline_id,
        top_pipeline_id=pi.top_pipeline_id,
        loop=1,
    )
    assert service.pre_execute.call_args.kwargs["data"].inputs == {"_loop": 1}
    assert service.pre_execute.call_args.kwargs["data"].outputs == {"_result": True}
    assert service.pre_execute.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.pre_execute.call_args.kwargs["root_pipeline_data"].outputs == {}

    assert service.execute.call_args.kwargs["data"].inputs == {"_loop": 1}
    assert service.execute.call_args.kwargs["data"].outputs == {"_result": True}
    assert service.execute.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.execute.call_args.kwargs["root_pipeline_data"].outputs == {}


def test_execute__success_and_no_schedule():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="",
    )

    node = ServiceActivity(
        id="nid",
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        code="test_service",
        version="legacy",
        error_ignorable=False,
        timeout=10,
    )

    data = Data(
        {
            "k1": DataInput(need_render=True, value="${k4}"),
            "k2": DataInput(need_render=True, value="2"),
            "k3": DataInput(need_render=False, value="${k5}"),
        },
        {},
    )

    service = MagicMock()
    service.need_schedule = MagicMock(return_value=False)
    service.schedule_type = MagicMock(return_value=None)
    service.schedule_after = MagicMock(return_value=-1)
    service.execute = MagicMock(return_value=True)

    runtime = MagicMock()
    runtime.get_data = MagicMock(return_value=data)
    runtime.get_context_key_references = MagicMock(return_value=set(["${k6}"]))
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_service = MagicMock(return_value=service)

    handler = ServiceActivityHandler(node, runtime)
    result = handler.execute(pi, 1, "v1")

    assert result.should_sleep == False
    assert result.schedule_ready == False
    assert result.schedule_type == None
    assert result.schedule_after == -1
    assert result.dispatch_processes == []
    assert result.next_node_id == node.target_nodes[0]
    assert result.should_die == False

    runtime.get_data.assert_called_once_with(node.id)
    runtime.get_data_inputs.assert_called_once_with(pi.root_pipeline_id)
    runtime.get_context_key_references.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set(["${k4}"])
    )
    runtime.get_context_values.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set(["${k4}", "${k6}"])
    )
    runtime.get_service.assert_called_once_with(code=node.code, version=node.version)
    runtime.start_timeout_monitor.assert_called_once_with(
        process_id=pi.process_id,
        node_id=node.id,
        version="v1",
        timeout=node.timeout,
    )
    runtime.set_state.assert_called_once_with(
        node_id=node.id,
        version="v1",
        to_state=states.FINISHED,
        set_archive_time=True,
    )
    runtime.stop_timeout_monitor.assert_called_once_with(
        process_id=pi.process_id,
        node_id=node.id,
        version="v1",
        timeout=node.timeout,
    )
    runtime.set_execution_data.assert_called_once()
    assert runtime.set_execution_data.call_args.kwargs["node_id"] == node.id
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {
        "k1": "${k4}",
        "k2": "2",
        "k3": "${k5}",
        "_loop": 1,
    }
    assert runtime.set_execution_data.call_args.kwargs["data"].outputs == {
        "_result": True
    }

    service.setup_runtime_attributes.assert_called_once_with(
        id=node.id,
        version="v1",
        root_pipeline_id=pi.root_pipeline_id,
        top_pipeline_id=pi.top_pipeline_id,
        loop=1,
    )
    assert service.pre_execute.call_args.kwargs["data"].inputs == {
        "k1": "${k4}",
        "k2": "2",
        "k3": "${k5}",
        "_loop": 1,
    }
    assert service.pre_execute.call_args.kwargs["data"].outputs == {"_result": True}
    assert service.pre_execute.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.pre_execute.call_args.kwargs["root_pipeline_data"].outputs == {}

    assert service.execute.call_args.kwargs["data"].inputs == {
        "k1": "${k4}",
        "k2": "2",
        "k3": "${k5}",
        "_loop": 1,
    }
    assert service.execute.call_args.kwargs["data"].outputs == {"_result": True}
    assert service.execute.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.execute.call_args.kwargs["root_pipeline_data"].outputs == {}


def test_execute__fail_and_schedule():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="",
    )

    node = ServiceActivity(
        id="nid",
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        code="test_service",
        version="legacy",
        error_ignorable=False,
        timeout=10,
    )

    data = Data({}, {})

    service = MagicMock()
    service.execute = MagicMock(return_value=False)
    service.need_schedule = MagicMock(return_value=True)
    service.schedule_type = MagicMock(return_value=ScheduleType.POLL)
    service.schedule_after = MagicMock(return_value=5)

    runtime = MagicMock()
    runtime.get_data = MagicMock(return_value=data)
    runtime.get_context_key_references = MagicMock(return_value=set())
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_service = MagicMock(return_value=service)

    handler = ServiceActivityHandler(node, runtime)
    result = handler.execute(pi, 1, "v1")

    assert result.should_sleep == True
    assert result.schedule_ready == False
    assert result.schedule_type == None
    assert result.schedule_after == -1
    assert result.dispatch_processes == []
    assert result.next_node_id == None
    assert result.should_die == False

    runtime.get_data.assert_called_once_with(node.id)
    runtime.get_data_inputs.assert_called_once_with(pi.root_pipeline_id)
    runtime.get_context_key_references.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set()
    )
    runtime.get_context_values.assert_called_once_with(
        pipeline_id=pi.top_pipeline_id, keys=set()
    )
    runtime.get_service.assert_called_once_with(code=node.code, version=node.version)
    runtime.start_timeout_monitor.assert_called_once_with(
        process_id=pi.process_id,
        node_id=node.id,
        version="v1",
        timeout=node.timeout,
    )
    runtime.set_state.assert_called_once_with(
        node_id=node.id, version="v1", to_state=states.FAILED, set_archive_time=True
    )
    runtime.stop_timeout_monitor.assert_called_once_with(
        process_id=pi.process_id,
        node_id=node.id,
        version="v1",
        timeout=node.timeout,
    )
    runtime.set_execution_data.assert_called_once()
    assert runtime.set_execution_data.call_args.kwargs["node_id"] == node.id
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {"_loop": 1}
    assert runtime.set_execution_data.call_args.kwargs["data"].outputs == {
        "_result": False
    }

    service.setup_runtime_attributes.assert_called_once_with(
        id=node.id,
        version="v1",
        root_pipeline_id=pi.root_pipeline_id,
        top_pipeline_id=pi.top_pipeline_id,
        loop=1,
    )
    assert service.pre_execute.call_args.kwargs["data"].inputs == {"_loop": 1}
    assert service.pre_execute.call_args.kwargs["data"].outputs == {"_result": False}
    assert service.pre_execute.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.pre_execute.call_args.kwargs["root_pipeline_data"].outputs == {}

    assert service.execute.call_args.kwargs["data"].inputs == {"_loop": 1}
    assert service.execute.call_args.kwargs["data"].outputs == {"_result": False}
    assert service.execute.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.execute.call_args.kwargs["root_pipeline_data"].outputs == {}


def test_schedule__raise_not_ignore():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="",
    )

    node = ServiceActivity(
        id="nid",
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        code="test_service",
        version="legacy",
        error_ignorable=False,
        timeout=10,
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node.id,
        finished=False,
        expired=False,
        version="v1",
        times=1,
    )

    service_data = ExecutionData({}, {})
    data_outputs = {}

    service = MagicMock()
    service.schedule = MagicMock(side_effect=Exception)

    runtime = MagicMock()
    runtime.get_data_outputs = MagicMock(return_value=data_outputs)
    runtime.get_execution_data = MagicMock(return_value=service_data)
    runtime.get_data_inputs = MagicMock(return_value={})
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_service = MagicMock(return_value=service)

    handler = ServiceActivityHandler(node, runtime)
    result = handler.schedule(pi, 1, schedule, None)

    assert result.has_next_schedule == False
    assert result.schedule_after == -1
    assert result.schedule_done == False
    assert result.next_node_id == None

    runtime.get_data_outputs.assert_called_once_with(node.id)
    runtime.get_execution_data.assert_called_once_with(node.id)
    runtime.get_data_inputs.assert_called_once_with(pi.root_pipeline_id)
    runtime.get_service.assert_called_once_with(code=node.code, version=node.version)
    runtime.add_schedule_times.assert_called_once_with(schedule.id)
    runtime.set_execution_data.assert_called_once()
    assert runtime.set_execution_data.call_args.kwargs["node_id"] == node.id
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {}
    assert "ex_data" in runtime.set_execution_data.call_args.kwargs["data"].outputs
    runtime.stop_timeout_monitor.assert_called_once_with(
        process_id=pi.process_id,
        node_id=node.id,
        version=schedule.version,
        timeout=node.timeout,
    )
    runtime.set_state.assert_called_once_with(
        node_id=node.id, version="v1", to_state=states.FAILED, set_archive_time=True
    )

    service.setup_runtime_attributes.assert_called_once_with(
        id=node.id,
        version="v1",
        root_pipeline_id=pi.root_pipeline_id,
        top_pipeline_id=pi.top_pipeline_id,
        loop=1,
    )
    assert service.schedule.call_args.kwargs["schedule"] == schedule
    assert service.schedule.call_args.kwargs["data"] == service_data
    assert service.schedule.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.schedule.call_args.kwargs["root_pipeline_data"].outputs == {}
    assert service.schedule.call_args.kwargs["callback_data"] == None


def test_schedule__raise_ignore():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="",
    )

    node = ServiceActivity(
        id="nid",
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        code="test_service",
        version="legacy",
        error_ignorable=True,
        timeout=None,
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node.id,
        finished=False,
        expired=False,
        version="v1",
        times=1,
    )

    service_data = ExecutionData({}, {})
    data_outputs = {}

    service = MagicMock()
    service.schedule = MagicMock(side_effect=Exception)

    runtime = MagicMock()
    runtime.get_data_outputs = MagicMock(return_value=data_outputs)
    runtime.get_execution_data = MagicMock(return_value=service_data)
    runtime.get_data_inputs = MagicMock(return_value={})
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_service = MagicMock(return_value=service)

    handler = ServiceActivityHandler(node, runtime)
    result = handler.schedule(pi, 1, schedule, None)

    assert result.has_next_schedule == False
    assert result.schedule_after == -1
    assert result.schedule_done == True
    assert result.next_node_id == node.target_nodes[0]

    runtime.get_data_outputs.assert_called_once_with(node.id)
    runtime.get_execution_data.assert_called_once_with(node.id)
    runtime.get_data_inputs.assert_called_once_with(pi.root_pipeline_id)
    runtime.get_service.assert_called_once_with(code=node.code, version=node.version)
    runtime.add_schedule_times.assert_called_once_with(schedule.id)
    runtime.set_execution_data.assert_called_once()
    assert runtime.set_execution_data.call_args.kwargs["node_id"] == node.id
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {}
    assert "ex_data" in runtime.set_execution_data.call_args.kwargs["data"].outputs
    runtime.stop_timeout_monitor.assert_not_called()
    runtime.set_state.assert_called_once_with(
        node_id=node.id,
        version=schedule.version,
        to_state=states.FINISHED,
        set_archive_time=True,
        error_ignored=True,
    )

    service.setup_runtime_attributes.assert_called_once_with(
        id=node.id,
        version="v1",
        root_pipeline_id=pi.root_pipeline_id,
        top_pipeline_id=pi.top_pipeline_id,
        loop=1,
    )
    assert service.schedule.call_args.kwargs["schedule"] == schedule
    assert service.schedule.call_args.kwargs["data"] == service_data
    assert service.schedule.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.schedule.call_args.kwargs["root_pipeline_data"].outputs == {}
    assert service.schedule.call_args.kwargs["callback_data"] == None


def test_schedule__poll_success_and_not_done():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="",
    )

    node = ServiceActivity(
        id="nid",
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        code="test_service",
        version="legacy",
        error_ignorable=True,
        timeout=10,
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node.id,
        finished=False,
        expired=False,
        version="v1",
        times=1,
    )

    service_data = ExecutionData({}, {})
    data_outputs = {}

    service = MagicMock()
    service.schedule = MagicMock(return_value=True)
    service.schedule_after = MagicMock(return_value=5)
    service.is_schedule_done = MagicMock(return_value=False)

    runtime = MagicMock()
    runtime.get_data_outputs = MagicMock(return_value=data_outputs)
    runtime.get_execution_data = MagicMock(return_value=service_data)
    runtime.get_data_inputs = MagicMock(return_value={})
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_service = MagicMock(return_value=service)

    handler = ServiceActivityHandler(node, runtime)
    result = handler.schedule(pi, 1, schedule, None)

    assert result.has_next_schedule == False
    assert result.schedule_after == 5
    assert result.schedule_done == False
    assert result.next_node_id == None

    runtime.get_data_outputs.assert_called_once_with(node.id)
    runtime.get_execution_data.assert_called_once_with(node.id)
    runtime.get_data_inputs.assert_called_once_with(pi.root_pipeline_id)
    runtime.get_service.assert_called_once_with(code=node.code, version=node.version)
    runtime.add_schedule_times.assert_called_once_with(schedule.id)
    runtime.set_execution_data.assert_called_once()
    assert runtime.set_execution_data.call_args.kwargs["node_id"] == node.id
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {}
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {}
    runtime.stop_timeout_monitor.assert_not_called()
    runtime.set_state.assert_not_called()

    service.setup_runtime_attributes.assert_called_once_with(
        id=node.id,
        version="v1",
        root_pipeline_id=pi.root_pipeline_id,
        top_pipeline_id=pi.top_pipeline_id,
        loop=1,
    )
    service.is_schedule_done.assert_called_once()
    service.schedule_after.call_args.kwargs["schedule"] == schedule
    service.schedule_after.call_args.kwargs["data"] == service_data
    service.schedule_after.call_args.kwargs["root_pipeline_data"].inputs == {}
    service.schedule_after.call_args.kwargs["root_pipeline_data"].outputs == {}
    assert service.schedule.call_args.kwargs["schedule"] == schedule
    assert service.schedule.call_args.kwargs["data"] == service_data
    assert service.schedule.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.schedule.call_args.kwargs["root_pipeline_data"].outputs == {}
    assert service.schedule.call_args.kwargs["callback_data"] == None


def test_schedule__poll_success_and_done():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="",
    )

    node = ServiceActivity(
        id="nid",
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        code="test_service",
        version="legacy",
        error_ignorable=True,
        timeout=10,
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node.id,
        finished=False,
        expired=False,
        version="v1",
        times=1,
    )

    service_data = ExecutionData({}, {})
    data_outputs = {}

    service = MagicMock()
    service.schedule = MagicMock(return_value=True)
    service.is_schedule_done = MagicMock(return_value=True)

    runtime = MagicMock()
    runtime.get_data_outputs = MagicMock(return_value=data_outputs)
    runtime.get_execution_data = MagicMock(return_value=service_data)
    runtime.get_data_inputs = MagicMock(return_value={})
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_service = MagicMock(return_value=service)

    handler = ServiceActivityHandler(node, runtime)
    result = handler.schedule(pi, 1, schedule, None)

    assert result.has_next_schedule == False
    assert result.schedule_after == -1
    assert result.schedule_done == True
    assert result.next_node_id == node.target_nodes[0]

    runtime.get_data_outputs.assert_called_once_with(node.id)
    runtime.get_execution_data.assert_called_once_with(node.id)
    runtime.get_data_inputs.assert_called_once_with(pi.root_pipeline_id)
    runtime.get_service.assert_called_once_with(code=node.code, version=node.version)
    runtime.add_schedule_times.assert_called_once_with(schedule.id)
    runtime.set_execution_data.assert_called_once()
    assert runtime.set_execution_data.call_args.kwargs["node_id"] == node.id
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {}
    assert runtime.set_execution_data.call_args.kwargs["data"].outputs == {
        "_result": True
    }
    runtime.stop_timeout_monitor.assert_called_once_with(
        process_id=pi.process_id,
        node_id=node.id,
        version="v1",
        timeout=node.timeout,
    )
    runtime.set_state.assert_called_once_with(
        node_id=node.id,
        version=schedule.version,
        to_state=states.FINISHED,
        set_archive_time=True,
        error_ignored=False,
    )

    service.setup_runtime_attributes.assert_called_once_with(
        id=node.id,
        version="v1",
        root_pipeline_id=pi.root_pipeline_id,
        top_pipeline_id=pi.top_pipeline_id,
        loop=1,
    )
    service.is_schedule_done.assert_called_once()
    service.schedule_after.assert_not_called()
    assert service.schedule.call_args.kwargs["schedule"] == schedule
    assert service.schedule.call_args.kwargs["data"] == service_data
    assert service.schedule.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.schedule.call_args.kwargs["root_pipeline_data"].outputs == {}
    assert service.schedule.call_args.kwargs["callback_data"] == None


def test_schedule__callback_success():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="",
    )

    node = ServiceActivity(
        id="nid",
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        code="test_service",
        version="legacy",
        error_ignorable=True,
        timeout=10,
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.CALLBACK,
        process_id=pi.process_id,
        node_id=node.id,
        finished=False,
        expired=False,
        version="v1",
        times=1,
    )

    service_data = ExecutionData({}, {})
    data_outputs = {}

    service = MagicMock()
    service.schedule = MagicMock(return_value=True)
    service.is_schedule_done = MagicMock(return_value=True)

    runtime = MagicMock()
    runtime.get_data_outputs = MagicMock(return_value=data_outputs)
    runtime.get_execution_data = MagicMock(return_value=service_data)
    runtime.get_data_inputs = MagicMock(return_value={})
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_service = MagicMock(return_value=service)

    handler = ServiceActivityHandler(node, runtime)
    result = handler.schedule(pi, 1, schedule, None)

    assert result.has_next_schedule == False
    assert result.schedule_after == -1
    assert result.schedule_done == True
    assert result.next_node_id == node.target_nodes[0]

    runtime.get_data_outputs.assert_called_once_with(node.id)
    runtime.get_execution_data.assert_called_once_with(node.id)
    runtime.get_data_inputs.assert_called_once_with(pi.root_pipeline_id)
    runtime.get_service.assert_called_once_with(code=node.code, version=node.version)
    runtime.add_schedule_times.assert_called_once_with(schedule.id)
    runtime.set_execution_data.assert_called_once()
    assert runtime.set_execution_data.call_args.kwargs["node_id"] == node.id
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {}
    assert runtime.set_execution_data.call_args.kwargs["data"].outputs == {
        "_result": True
    }
    runtime.stop_timeout_monitor.assert_called_once_with(
        process_id=pi.process_id,
        node_id=node.id,
        version="v1",
        timeout=node.timeout,
    )
    runtime.set_state.assert_called_once_with(
        node_id=node.id,
        version=schedule.version,
        to_state=states.FINISHED,
        set_archive_time=True,
        error_ignored=False,
    )

    service.setup_runtime_attributes.assert_called_once_with(
        id=node.id,
        version="v1",
        root_pipeline_id=pi.root_pipeline_id,
        top_pipeline_id=pi.top_pipeline_id,
        loop=1,
    )
    service.is_schedule_done.assert_called_once()
    service.schedule_after.assert_not_called()
    assert service.schedule.call_args.kwargs["schedule"] == schedule
    assert service.schedule.call_args.kwargs["data"] == service_data
    assert service.schedule.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.schedule.call_args.kwargs["root_pipeline_data"].outputs == {}
    assert service.schedule.call_args.kwargs["callback_data"] == None


def test_schedule__multi_callback_success_and_not_done():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="",
    )

    node = ServiceActivity(
        id="nid",
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        code="test_service",
        version="legacy",
        error_ignorable=True,
        timeout=10,
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.MULTIPLE_CALLBACK,
        process_id=pi.process_id,
        node_id=node.id,
        finished=False,
        expired=False,
        version="v1",
        times=1,
    )

    service_data = ExecutionData({}, {})
    data_outputs = {}

    service = MagicMock()
    service.schedule = MagicMock(return_value=True)
    service.schedule_after = MagicMock(return_value=5)
    service.is_schedule_done = MagicMock(return_value=False)

    runtime = MagicMock()
    runtime.get_data_outputs = MagicMock(return_value=data_outputs)
    runtime.get_execution_data = MagicMock(return_value=service_data)
    runtime.get_data_inputs = MagicMock(return_value={})
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_service = MagicMock(return_value=service)

    handler = ServiceActivityHandler(node, runtime)
    result = handler.schedule(pi, 1, schedule, None)

    assert result.has_next_schedule == False
    assert result.schedule_after == 5
    assert result.schedule_done == False
    assert result.next_node_id == None

    runtime.get_data_outputs.assert_called_once_with(node.id)
    runtime.get_execution_data.assert_called_once_with(node.id)
    runtime.get_data_inputs.assert_called_once_with(pi.root_pipeline_id)
    runtime.get_service.assert_called_once_with(code=node.code, version=node.version)
    runtime.add_schedule_times.assert_called_once_with(schedule.id)
    runtime.set_execution_data.assert_called_once()
    assert runtime.set_execution_data.call_args.kwargs["node_id"] == node.id
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {}
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {}
    runtime.stop_timeout_monitor.assert_not_called()
    runtime.set_state.assert_not_called()

    service.setup_runtime_attributes.assert_called_once_with(
        id=node.id,
        version="v1",
        root_pipeline_id=pi.root_pipeline_id,
        top_pipeline_id=pi.top_pipeline_id,
        loop=1,
    )
    service.is_schedule_done.assert_called_once()
    service.schedule_after.call_args.kwargs["schedule"] == schedule
    service.schedule_after.call_args.kwargs["data"] == service_data
    service.schedule_after.call_args.kwargs["root_pipeline_data"].inputs == {}
    service.schedule_after.call_args.kwargs["root_pipeline_data"].outputs == {}
    assert service.schedule.call_args.kwargs["schedule"] == schedule
    assert service.schedule.call_args.kwargs["data"] == service_data
    assert service.schedule.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.schedule.call_args.kwargs["root_pipeline_data"].outputs == {}
    assert service.schedule.call_args.kwargs["callback_data"] == None


def test_schedule__multi_callback_success_and_done():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="",
    )

    node = ServiceActivity(
        id="nid",
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        code="test_service",
        version="legacy",
        error_ignorable=True,
        timeout=10,
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node.id,
        finished=False,
        expired=False,
        version="v1",
        times=1,
    )

    service_data = ExecutionData({}, {})
    data_outputs = {}

    service = MagicMock()
    service.schedule = MagicMock(return_value=True)
    service.is_schedule_done = MagicMock(return_value=True)

    runtime = MagicMock()
    runtime.get_data_outputs = MagicMock(return_value=data_outputs)
    runtime.get_execution_data = MagicMock(return_value=service_data)
    runtime.get_data_inputs = MagicMock(return_value={})
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_service = MagicMock(return_value=service)

    handler = ServiceActivityHandler(node, runtime)
    result = handler.schedule(pi, 1, schedule, None)

    assert result.has_next_schedule == False
    assert result.schedule_after == -1
    assert result.schedule_done == True
    assert result.next_node_id == node.target_nodes[0]

    runtime.get_data_outputs.assert_called_once_with(node.id)
    runtime.get_execution_data.assert_called_once_with(node.id)
    runtime.get_data_inputs.assert_called_once_with(pi.root_pipeline_id)
    runtime.get_service.assert_called_once_with(code=node.code, version=node.version)
    runtime.add_schedule_times.assert_called_once_with(schedule.id)
    runtime.set_execution_data.assert_called_once()
    assert runtime.set_execution_data.call_args.kwargs["node_id"] == node.id
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {}
    assert runtime.set_execution_data.call_args.kwargs["data"].outputs == {
        "_result": True
    }
    runtime.stop_timeout_monitor.assert_called_once_with(
        process_id=pi.process_id,
        node_id=node.id,
        version="v1",
        timeout=node.timeout,
    )
    runtime.set_state.assert_called_once_with(
        node_id=node.id,
        version=schedule.version,
        to_state=states.FINISHED,
        set_archive_time=True,
        error_ignored=False,
    )

    service.setup_runtime_attributes.assert_called_once_with(
        id=node.id,
        version="v1",
        root_pipeline_id=pi.root_pipeline_id,
        top_pipeline_id=pi.top_pipeline_id,
        loop=1,
    )
    service.is_schedule_done.assert_called_once()
    service.schedule_after.assert_not_called()
    assert service.schedule.call_args.kwargs["schedule"] == schedule
    assert service.schedule.call_args.kwargs["data"] == service_data
    assert service.schedule.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.schedule.call_args.kwargs["root_pipeline_data"].outputs == {}
    assert service.schedule.call_args.kwargs["callback_data"] == None


def test_schedule__fail():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="",
    )

    node = ServiceActivity(
        id="nid",
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        code="test_service",
        version="legacy",
        error_ignorable=False,
        timeout=None,
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node.id,
        finished=False,
        expired=False,
        version="v1",
        times=1,
    )

    service_data = ExecutionData({}, {})
    data_outputs = {}

    service = MagicMock()
    service.schedule = MagicMock(return_value=False)

    runtime = MagicMock()
    runtime.get_data_outputs = MagicMock(return_value=data_outputs)
    runtime.get_execution_data = MagicMock(return_value=service_data)
    runtime.get_data_inputs = MagicMock(return_value={})
    runtime.get_context_values = MagicMock(return_value=[])
    runtime.get_service = MagicMock(return_value=service)

    handler = ServiceActivityHandler(node, runtime)
    result = handler.schedule(pi, 1, schedule, None)

    assert result.has_next_schedule == False
    assert result.schedule_after == -1
    assert result.schedule_done == False
    assert result.next_node_id == None

    runtime.get_data_outputs.assert_called_once_with(node.id)
    runtime.get_execution_data.assert_called_once_with(node.id)
    runtime.get_data_inputs.assert_called_once_with(pi.root_pipeline_id)
    runtime.get_service.assert_called_once_with(code=node.code, version=node.version)
    runtime.add_schedule_times.assert_called_once_with(schedule.id)
    runtime.set_execution_data.assert_called_once()
    assert runtime.set_execution_data.call_args.kwargs["node_id"] == node.id
    assert runtime.set_execution_data.call_args.kwargs["data"].inputs == {}
    assert runtime.set_execution_data.call_args.kwargs["data"].outputs == {
        "_result": False
    }
    runtime.stop_timeout_monitor.assert_not_called()
    runtime.set_state.assert_called_once_with(
        node_id=node.id,
        version=schedule.version,
        to_state=states.FAILED,
        set_archive_time=True,
    )

    service.setup_runtime_attributes.assert_called_once_with(
        id=node.id,
        version="v1",
        root_pipeline_id=pi.root_pipeline_id,
        top_pipeline_id=pi.top_pipeline_id,
        loop=1,
    )
    assert service.schedule.call_args.kwargs["schedule"] == schedule
    assert service.schedule.call_args.kwargs["data"] == service_data
    assert service.schedule.call_args.kwargs["root_pipeline_data"].inputs == {}
    assert service.schedule.call_args.kwargs["root_pipeline_data"].outputs == {}
    assert service.schedule.call_args.kwargs["callback_data"] == None
