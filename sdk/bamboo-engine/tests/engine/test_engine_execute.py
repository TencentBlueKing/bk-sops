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

import pytest
import mock
from mock import MagicMock, call

from bamboo_engine.eri import (
    ProcessInfo,
    ServiceActivity,
    State,
    NodeType,
    ExecutionData,
    ScheduleType,
    Schedule,
    DispatchProcess,
)
from bamboo_engine import states
from bamboo_engine.engine import Engine
from bamboo_engine.exceptions import StateVersionNotMatchError
from bamboo_engine.handler import HandlerFactory, ExecuteResult


def test_execute__reach_destination_and_wake_up_failed():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="nid",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.child_process_finish = MagicMock(return_value=False)

    engine = Engine(runtime=runtime)
    engine.execute(pi.process_id, node_id)

    runtime.get_process_info.assert_called_once_with(pi.process_id)
    runtime.wake_up.assert_called_once_with(pi.process_id)
    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.child_process_finish.assert_called_once_with(pi.parent_id, pi.process_id)
    runtime.execute.assert_not_called()


def test_execute__reach_destination_and_wake_up_success():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="nid",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.child_process_finish = MagicMock(return_value=True)

    engine = Engine(runtime=runtime)
    engine.execute(pi.process_id, node_id)

    runtime.get_process_info.assert_called_once_with(pi.process_id)
    runtime.wake_up.assert_called_once_with(pi.process_id)
    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.child_process_finish.assert_called_once_with(pi.parent_id, pi.process_id)
    runtime.execute.assert_called_once_with(pi.parent_id, pi.destination_id)


def test_execute__engine_frozen():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="d1",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.is_frozen = MagicMock(return_value=True)

    engine = Engine(runtime=runtime)
    engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.set_current_node.assert_called_once_with(pi.process_id, node_id)
    runtime.freeze.assert_called_once_with(pi.process_id)


def test_execute__root_pipeline_revoked():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="d1",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.is_frozen = MagicMock(return_value=False)
    runtime.batch_get_state_name = MagicMock(return_value={"root": states.REVOKED})

    engine = Engine(runtime=runtime)
    engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.die.assert_called_once_with(pi.process_id)


def test_execute__root_pipeline_suspended():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="d1",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.is_frozen = MagicMock(return_value=False)
    runtime.batch_get_state_name = MagicMock(return_value={"root": states.SUSPENDED})

    engine = Engine(runtime=runtime)
    engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.suspend.assert_called_once_with(pi.process_id, pi.root_pipeline_id)


def test_execute__suspended_in_pipeline_stack():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="d1",
        root_pipeline_id="root",
        pipeline_stack=["root", "s1", "s2"],
        parent_id="parent",
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.is_frozen = MagicMock(return_value=False)
    runtime.batch_get_state_name = MagicMock(
        return_value={
            "root": states.RUNNING,
            "s1": states.SUSPENDED,
            "s2": states.SUSPENDED,
        }
    )

    engine = Engine(runtime=runtime)
    engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.suspend.assert_called_once_with(pi.process_id, pi.pipeline_stack[1])


def test_execute__exceed_rerun_limit():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="d1",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )
    node = ServiceActivity(
        id=node_id,
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        code="",
        version="",
        timeout=None,
        error_ignorable=False,
    )
    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.FINISHED,
        version="v",
        loop=11,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.is_frozen = MagicMock(return_value=False)
    runtime.batch_get_state_name = MagicMock(return_value={"root": states.RUNNING})
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state_or_none = MagicMock(return_value=state)
    runtime.node_rerun_limit = MagicMock(return_value=10)
    runtime.get_execution_data_outputs = MagicMock(return_value={})

    engine = Engine(runtime=runtime)
    engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_state_or_none.assert_called_once_with(node_id)
    runtime.node_rerun_limit.assert_called_once_with(pi.root_pipeline_id, node_id)
    runtime.set_execution_data_outputs.assert_called_once_with(
        node_id, {"ex_data": "node execution exceed rerun limit 10"}
    )
    runtime.set_state.assert_called_once_with(
        node_id=node_id, to_state=states.FAILED, set_archive_time=True
    )
    runtime.sleep.assert_called_once_with(pi.process_id)


def test_execute__node_has_suspended_appoint():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="d1",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )
    node = ServiceActivity(
        id=node_id,
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        code="",
        version="",
        timeout=None,
        error_ignorable=False,
    )
    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.SUSPENDED,
        version="v",
        loop=1,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.is_frozen = MagicMock(return_value=False)
    runtime.batch_get_state_name = MagicMock(return_value={"root": states.RUNNING})
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state_or_none = MagicMock(return_value=state)
    runtime.node_rerun_limit = MagicMock(return_value=10)

    engine = Engine(runtime=runtime)
    engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_state_or_none.assert_called_once_with(node_id)
    runtime.node_rerun_limit.assert_called_once_with(pi.root_pipeline_id, node_id)
    runtime.set_state_root_and_parent.assert_called_once_with(
        node_id=node_id, root_id=pi.root_pipeline_id, parent_id=pi.top_pipeline_id
    )
    runtime.suspend.assert_called_once_with(pi.process_id, node_id)


def test_execute__node_can_not_transit_to_running():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="d1",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )
    node = ServiceActivity(
        id=node_id,
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        code="",
        version="",
        timeout=None,
        error_ignorable=False,
    )
    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.RUNNING,
        version="v",
        loop=1,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.is_frozen = MagicMock(return_value=False)
    runtime.batch_get_state_name = MagicMock(return_value={"root": states.RUNNING})
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state_or_none = MagicMock(return_value=state)
    runtime.node_rerun_limit = MagicMock(return_value=10)

    engine = Engine(runtime=runtime)
    engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_state_or_none.assert_called_once_with(node_id)
    runtime.node_rerun_limit.assert_called_once_with(pi.root_pipeline_id, node_id)
    runtime.set_state.assert_not_called()
    runtime.sleep.assert_called_once_with(pi.process_id)


def test_execute__rerun_and_have_to_sleep():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="d1",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )
    node = ServiceActivity(
        id=node_id,
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        code="",
        version="",
        timeout=None,
        error_ignorable=False,
    )
    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.FINISHED,
        version="v",
        loop=1,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
    )
    execution_data = ExecutionData(inputs={"1": "1"}, outputs={"2": "2"})

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.is_frozen = MagicMock(return_value=False)
    runtime.batch_get_state_name = MagicMock(return_value={"root": states.RUNNING})
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state_or_none = MagicMock(return_value=state)
    runtime.node_rerun_limit = MagicMock(return_value=10)
    runtime.get_execution_data = MagicMock(return_value=execution_data)
    runtime.set_state = MagicMock(return_value=state.version)

    handler = MagicMock()
    handler.execute = MagicMock(
        return_value=ExecuteResult(
            should_sleep=True,
            schedule_ready=False,
            schedule_type=None,
            schedule_after=-1,
            dispatch_processes=[],
            next_node_id=None,
            should_die=False,
        )
    )
    get_handler = MagicMock(return_value=handler)

    engine = Engine(runtime=runtime)

    with mock.patch(
        "bamboo_engine.engine.HandlerFactory.get_handler",
        get_handler,
    ):
        engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_state_or_none.assert_called_once_with(node_id)
    runtime.node_rerun_limit.assert_called_once_with(pi.root_pipeline_id, node_id)
    runtime.get_execution_data.assert_called_once_with(node.id)
    runtime.add_history.assert_called_once_with(
        node_id=node.id,
        started_time=state.started_time,
        archived_time=state.archived_time,
        loop=state.loop,
        skip=state.skip,
        retry=state.retry,
        version=state.version,
        inputs=execution_data.inputs,
        outputs=execution_data.outputs,
    )
    runtime.set_state.assert_called_once_with(
        node_id=node.id,
        to_state=states.RUNNING,
        loop=state.loop + 1,
        root_id=pi.root_pipeline_id,
        parent_id=pi.top_pipeline_id,
        set_started_time=True,
        reset_skip=True,
        reset_retry=True,
        reset_error_ignored=True,
        refresh_version=True,
    )
    runtime.sleep.assert_called_once_with(pi.process_id)
    runtime.set_schedule.assert_not_called()
    runtime.schedule.assert_not_called()
    runtime.execute.assert_not_called()
    runtime.die.assert_not_called()

    get_handler.assert_called_once_with(node, runtime)
    handler.execute.assert_called_once_with(pi, state.loop + 1, state.version)


def test_execute__have_to_sleep():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="d1",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )
    node = ServiceActivity(
        id=node_id,
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        code="",
        version="",
        timeout=None,
        error_ignorable=False,
    )
    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.FINISHED,
        version="v",
        loop=1,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
    )
    execution_data = ExecutionData(inputs={"1": "1"}, outputs={"2": "2"})

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.is_frozen = MagicMock(return_value=False)
    runtime.batch_get_state_name = MagicMock(return_value={"root": states.RUNNING})
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state_or_none = MagicMock(return_value=None)
    runtime.get_state = MagicMock(return_value=state)
    runtime.set_state = MagicMock(return_value=state.version)

    handler = MagicMock()
    handler.execute = MagicMock(
        return_value=ExecuteResult(
            should_sleep=True,
            schedule_ready=False,
            schedule_type=None,
            schedule_after=-1,
            dispatch_processes=[],
            next_node_id=None,
            should_die=False,
        )
    )
    get_handler = MagicMock(return_value=handler)

    engine = Engine(runtime=runtime)

    with mock.patch(
        "bamboo_engine.engine.HandlerFactory.get_handler",
        get_handler,
    ):
        engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_state_or_none.assert_called_once_with(node_id)
    runtime.node_rerun_limit.assert_not_called()
    runtime.set_state.assert_called_once_with(
        node_id=node.id,
        to_state=states.RUNNING,
        loop=1,
        root_id=pi.root_pipeline_id,
        parent_id=pi.top_pipeline_id,
        set_started_time=True,
        reset_skip=False,
        reset_retry=False,
        reset_error_ignored=False,
        refresh_version=False,
    )
    runtime.sleep.assert_called_once_with(pi.process_id)
    runtime.set_schedule.assert_not_called()
    runtime.schedule.assert_not_called()
    runtime.execute.assert_not_called()
    runtime.die.assert_not_called()

    get_handler.assert_called_once_with(node, runtime)
    handler.execute.assert_called_once_with(pi, state.loop, state.version)


def test_execute__poll_schedule_ready():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="d1",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )
    node = ServiceActivity(
        id=node_id,
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        code="",
        version="",
        timeout=None,
        error_ignorable=False,
    )
    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.FINISHED,
        version="v",
        loop=1,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
    )
    execution_data = ExecutionData(inputs={"1": "1"}, outputs={"2": "2"})
    schedule = Schedule(
        id=2,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node_id,
        finished=False,
        expired=False,
        version=state.version,
        times=0,
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.is_frozen = MagicMock(return_value=False)
    runtime.batch_get_state_name = MagicMock(return_value={"root": states.RUNNING})
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state_or_none = MagicMock(return_value=None)
    runtime.get_state = MagicMock(return_value=state)
    runtime.set_schedule = MagicMock(return_value=schedule)
    runtime.set_state = MagicMock(return_value=state.version)

    handler = MagicMock()
    execute_result = ExecuteResult(
        should_sleep=True,
        schedule_ready=True,
        schedule_type=ScheduleType.POLL,
        schedule_after=5,
        dispatch_processes=[],
        next_node_id=None,
        should_die=False,
    )
    handler.execute = MagicMock(return_value=execute_result)
    get_handler = MagicMock(return_value=handler)

    engine = Engine(runtime=runtime)

    with mock.patch(
        "bamboo_engine.engine.HandlerFactory.get_handler",
        get_handler,
    ):
        engine.execute(pi.process_id, node_id)

    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_state_or_none.assert_called_once_with(node_id)
    runtime.node_rerun_limit.assert_not_called()
    runtime.set_state.assert_called_once_with(
        node_id=node.id,
        to_state=states.RUNNING,
        loop=1,
        root_id=pi.root_pipeline_id,
        parent_id=pi.top_pipeline_id,
        set_started_time=True,
        reset_skip=False,
        reset_retry=False,
        reset_error_ignored=False,
        refresh_version=False,
    )
    runtime.sleep.assert_called_once_with(pi.process_id)
    runtime.set_schedule.assert_called_once_with(
        process_id=pi.process_id,
        node_id=node.id,
        version=state.version,
        schedule_type=execute_result.schedule_type,
    )
    runtime.schedule.assert_called_once_with(pi.process_id, node.id, schedule.id)
    runtime.execute.assert_not_called()
    runtime.die.assert_not_called()

    get_handler.assert_called_once_with(node, runtime)
    handler.execute.assert_called_once_with(pi, state.loop, state.version)


def test_execute__callback_schedule_ready():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="d1",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )
    node = ServiceActivity(
        id=node_id,
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        code="",
        version="",
        timeout=None,
        error_ignorable=False,
    )
    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.FINISHED,
        version="v",
        loop=1,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
    )
    execution_data = ExecutionData(inputs={"1": "1"}, outputs={"2": "2"})
    schedule = Schedule(
        id=2,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node_id,
        finished=False,
        expired=False,
        version=state.version,
        times=0,
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.is_frozen = MagicMock(return_value=False)
    runtime.batch_get_state_name = MagicMock(return_value={"root": states.RUNNING})
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state_or_none = MagicMock(return_value=None)
    runtime.get_state = MagicMock(return_value=state)
    runtime.set_schedule = MagicMock(return_value=schedule)
    runtime.set_state = MagicMock(return_value=state.version)

    handler = MagicMock()
    execute_result = ExecuteResult(
        should_sleep=True,
        schedule_ready=True,
        schedule_type=ScheduleType.CALLBACK,
        schedule_after=5,
        dispatch_processes=[],
        next_node_id=None,
        should_die=False,
    )
    handler.execute = MagicMock(return_value=execute_result)
    get_handler = MagicMock(return_value=handler)

    engine = Engine(runtime=runtime)

    with mock.patch(
        "bamboo_engine.engine.HandlerFactory.get_handler",
        get_handler,
    ):
        engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_state_or_none.assert_called_once_with(node_id)
    runtime.node_rerun_limit.assert_not_called()
    runtime.set_state.assert_called_once_with(
        node_id=node.id,
        to_state=states.RUNNING,
        loop=1,
        root_id=pi.root_pipeline_id,
        parent_id=pi.top_pipeline_id,
        set_started_time=True,
        reset_skip=False,
        reset_retry=False,
        reset_error_ignored=False,
        refresh_version=False,
    )
    runtime.sleep.assert_called_once_with(pi.process_id)
    runtime.set_schedule.assert_called_once_with(
        process_id=pi.process_id,
        node_id=node.id,
        version=state.version,
        schedule_type=execute_result.schedule_type,
    )
    runtime.schedule.assert_not_called()
    runtime.execute.assert_not_called()
    runtime.die.assert_not_called()

    get_handler.assert_called_once_with(node, runtime)
    handler.execute.assert_called_once_with(pi, state.loop, state.version)


def test_execute__multi_callback_schedule_ready():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="d1",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )
    node = ServiceActivity(
        id=node_id,
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        code="",
        version="",
        timeout=None,
        error_ignorable=False,
    )
    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.FINISHED,
        version="v",
        loop=1,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
    )
    execution_data = ExecutionData(inputs={"1": "1"}, outputs={"2": "2"})
    schedule = Schedule(
        id=2,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node_id,
        finished=False,
        expired=False,
        version=state.version,
        times=0,
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.is_frozen = MagicMock(return_value=False)
    runtime.batch_get_state_name = MagicMock(return_value={"root": states.RUNNING})
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state_or_none = MagicMock(return_value=None)
    runtime.get_state = MagicMock(return_value=state)
    runtime.set_schedule = MagicMock(return_value=schedule)
    runtime.set_state = MagicMock(return_value=state.version)

    handler = MagicMock()
    execute_result = ExecuteResult(
        should_sleep=True,
        schedule_ready=True,
        schedule_type=ScheduleType.MULTIPLE_CALLBACK,
        schedule_after=5,
        dispatch_processes=[],
        next_node_id=None,
        should_die=False,
    )
    handler.execute = MagicMock(return_value=execute_result)
    get_handler = MagicMock(return_value=handler)

    engine = Engine(runtime=runtime)

    with mock.patch(
        "bamboo_engine.engine.HandlerFactory.get_handler",
        get_handler,
    ):
        engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_state_or_none.assert_called_once_with(node_id)
    runtime.node_rerun_limit.assert_not_called()
    runtime.set_state.assert_called_once_with(
        node_id=node.id,
        to_state=states.RUNNING,
        loop=1,
        root_id=pi.root_pipeline_id,
        parent_id=pi.top_pipeline_id,
        set_started_time=True,
        reset_skip=False,
        reset_retry=False,
        reset_error_ignored=False,
        refresh_version=False,
    )
    runtime.sleep.assert_called_once_with(pi.process_id)
    runtime.set_schedule.assert_called_once_with(
        process_id=pi.process_id,
        node_id=node.id,
        version=state.version,
        schedule_type=execute_result.schedule_type,
    )
    runtime.schedule.assert_not_called()
    runtime.execute.assert_not_called()
    runtime.die.assert_not_called()

    get_handler.assert_called_once_with(node, runtime)
    handler.execute.assert_called_once_with(pi, state.loop, state.version)


def test_execute__has_dispatch_processes():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="d1",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )
    node = ServiceActivity(
        id=node_id,
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        code="",
        version="",
        timeout=None,
        error_ignorable=False,
    )
    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.FINISHED,
        version="v",
        loop=1,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
    )
    execution_data = ExecutionData(inputs={"1": "1"}, outputs={"2": "2"})
    dispatch_processes = [
        DispatchProcess(process_id=3, node_id="n3"),
        DispatchProcess(process_id=4, node_id="n4"),
    ]

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.is_frozen = MagicMock(return_value=False)
    runtime.batch_get_state_name = MagicMock(return_value={"root": states.RUNNING})
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state_or_none = MagicMock(return_value=None)
    runtime.get_state = MagicMock(return_value=state)
    runtime.set_state = MagicMock(return_value=state.version)

    handler = MagicMock()
    handler.execute = MagicMock(
        return_value=ExecuteResult(
            should_sleep=True,
            schedule_ready=False,
            schedule_type=None,
            schedule_after=-1,
            dispatch_processes=dispatch_processes,
            next_node_id=None,
            should_die=False,
        )
    )
    get_handler = MagicMock(return_value=handler)

    engine = Engine(runtime=runtime)

    with mock.patch(
        "bamboo_engine.engine.HandlerFactory.get_handler",
        get_handler,
    ):
        engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_state_or_none.assert_called_once_with(node_id)
    runtime.node_rerun_limit.assert_not_called()
    runtime.set_state.assert_called_once_with(
        node_id=node.id,
        to_state=states.RUNNING,
        loop=1,
        root_id=pi.root_pipeline_id,
        parent_id=pi.top_pipeline_id,
        set_started_time=True,
        reset_skip=False,
        reset_retry=False,
        reset_error_ignored=False,
        refresh_version=False,
    )
    runtime.sleep.assert_called_once_with(pi.process_id)
    runtime.set_schedule.assert_not_called()
    runtime.schedule.assert_not_called()
    runtime.join.assert_called_once_with(
        pi.process_id, [d.process_id for d in dispatch_processes]
    )
    runtime.execute.assert_has_calls(
        [
            call(dispatch_processes[0].process_id, dispatch_processes[0].node_id),
            call(dispatch_processes[1].process_id, dispatch_processes[1].node_id),
        ]
    )
    runtime.die.assert_not_called()

    get_handler.assert_called_once_with(node, runtime)
    handler.execute.assert_called_once_with(pi, state.loop, state.version)


def test_execute__have_to_die():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id="d1",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )
    node = ServiceActivity(
        id=node_id,
        type=NodeType.ServiceActivity,
        target_flows=["f1"],
        target_nodes=["t1"],
        targets={"f1": "t1"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        code="",
        version="",
        timeout=None,
        error_ignorable=False,
    )
    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.FINISHED,
        version="v",
        loop=1,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
    )
    execution_data = ExecutionData(inputs={"1": "1"}, outputs={"2": "2"})

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.is_frozen = MagicMock(return_value=False)
    runtime.batch_get_state_name = MagicMock(return_value={"root": states.RUNNING})
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state_or_none = MagicMock(return_value=None)
    runtime.get_state = MagicMock(return_value=state)
    runtime.set_state = MagicMock(return_value=state.version)

    handler = MagicMock()
    handler.execute = MagicMock(
        return_value=ExecuteResult(
            should_sleep=False,
            schedule_ready=False,
            schedule_type=None,
            schedule_after=-1,
            dispatch_processes=[],
            next_node_id=None,
            should_die=True,
        )
    )
    get_handler = MagicMock(return_value=handler)

    engine = Engine(runtime=runtime)

    with mock.patch(
        "bamboo_engine.engine.HandlerFactory.get_handler",
        get_handler,
    ):
        engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_state_or_none.assert_called_once_with(node_id)
    runtime.node_rerun_limit.assert_not_called()
    runtime.set_state.assert_called_once_with(
        node_id=node.id,
        to_state=states.RUNNING,
        loop=1,
        root_id=pi.root_pipeline_id,
        parent_id=pi.top_pipeline_id,
        set_started_time=True,
        reset_skip=False,
        reset_retry=False,
        reset_error_ignored=False,
        refresh_version=False,
    )
    runtime.sleep.assert_not_called()
    runtime.set_schedule.assert_not_called()
    runtime.schedule.assert_not_called()
    runtime.execute.assert_not_called()
    runtime.die.assert_called_once_with(pi.process_id)

    get_handler.assert_called_once_with(node, runtime)
    handler.execute.assert_called_once_with(pi, state.loop, state.version)


def test_execute__unexpect_raise():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id=None,
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.set_current_node = MagicMock(side_effect=Exception)
    runtime.get_execution_data_outputs = MagicMock(return_value={})

    engine = Engine(runtime=runtime)
    engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_process_info.assert_called_once_with(pi.process_id)
    runtime.get_execution_data_outputs.assert_called_once_with(node_id)
    runtime.set_state.assert_called_once_with(
        node_id=node_id,
        to_state=states.FAILED,
        root_id=pi.root_pipeline_id,
        parent_id=pi.top_pipeline_id,
        set_started_time=True,
        set_archive_time=True,
    )
    runtime.set_execution_data_outputs.assert_called_once()
    runtime.sleep.assert_called_once_with(pi.process_id)


def test_execute__raise_state_version_not_match():
    node_id = "nid"
    pi = ProcessInfo(
        process_id="pid",
        destination_id=None,
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.set_current_node = MagicMock(side_effect=StateVersionNotMatchError)
    runtime.get_execution_data_outputs = MagicMock(return_value={})

    engine = Engine(runtime=runtime)
    engine.execute(pi.process_id, node_id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_process_info.assert_called_once_with(pi.process_id)
    runtime.get_execution_data_outputs.assert_not_called()
    runtime.set_state.assert_not_called()
    runtime.set_execution_data_outputs.assert_not_called()
    runtime.sleep.assert_not_called()
