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
    CallbackData,
)
from bamboo_engine import states
from bamboo_engine.engine import Engine
from bamboo_engine.exceptions import StateVersionNotMatchError
from bamboo_engine.handler import HandlerFactory, ScheduleResult


def test_schedule__lock_get_failed():
    node_id = "nid"
    schedule_id = 1

    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.apply_schedule_lock = MagicMock(return_value=False)

    engine = Engine(runtime=runtime)
    engine.schedule(pi.process_id, node_id, schedule_id)

    runtime.get_process_info.assert_called_once_with(pi.process_id)
    runtime.apply_schedule_lock.assert_called_once_with(schedule_id)
    assert runtime.set_next_schedule.call_args.kwargs["process_id"] == pi.process_id
    assert runtime.set_next_schedule.call_args.kwargs["node_id"] == node_id
    assert runtime.set_next_schedule.call_args.kwargs["schedule_id"] == schedule_id
    assert runtime.set_next_schedule.call_args.kwargs["callback_data_id"] == None
    assert runtime.set_next_schedule.call_args.kwargs["schedule_after"] <= 5
    runtime.get_schedule.assert_not_called()


def test_schedule__schedule_is_finished():
    node_id = "nid"

    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node_id,
        finished=True,
        expired=False,
        version="v1",
        times=0,
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.apply_schedule_lock = MagicMock(return_value=True)
    runtime.get_schedule = MagicMock(return_value=schedule)

    engine = Engine(runtime=runtime)
    engine.schedule(pi.process_id, node_id, schedule.id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_process_info.assert_called_once_with(pi.process_id)
    runtime.apply_schedule_lock.assert_called_once_with(schedule.id)
    runtime.schedule.assert_not_called()
    runtime.get_schedule.assert_called_once_with(schedule.id)
    runtime.get_state.assert_not_called()


def test_schedule__schedule_version_not_match():
    node_id = "nid"

    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node_id,
        finished=False,
        expired=False,
        version="v1",
        times=0,
    )

    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.RUNNING,
        version="v2",
        loop=11,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.apply_schedule_lock = MagicMock(return_value=True)
    runtime.get_schedule = MagicMock(return_value=schedule)
    runtime.get_state = MagicMock(return_value=state)

    engine = Engine(runtime=runtime)
    engine.schedule(pi.process_id, node_id, schedule.id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_process_info.assert_called_once_with(pi.process_id)
    runtime.apply_schedule_lock.assert_called_once_with(schedule.id)
    runtime.schedule.assert_not_called()
    runtime.get_schedule.assert_called_once_with(schedule.id)
    runtime.get_state.assert_called_once_with(node_id)
    runtime.expire_schedule.assert_called_once_with(schedule.id)
    runtime.get_node.assert_not_called()


def test_schedule__schedule_node_state_is_not_running():
    node_id = "nid"

    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node_id,
        finished=False,
        expired=False,
        version="v1",
        times=0,
    )

    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.FAILED,
        version="v1",
        loop=11,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.apply_schedule_lock = MagicMock(return_value=True)
    runtime.get_schedule = MagicMock(return_value=schedule)
    runtime.get_state = MagicMock(return_value=state)

    engine = Engine(runtime=runtime)
    engine.schedule(pi.process_id, node_id, schedule.id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_process_info.assert_called_once_with(pi.process_id)
    runtime.apply_schedule_lock.assert_called_once_with(schedule.id)
    runtime.schedule.assert_not_called()
    runtime.get_schedule.assert_called_once_with(schedule.id)
    runtime.get_state.assert_called_once_with(node_id)
    runtime.expire_schedule.assert_called_once_with(schedule.id)
    runtime.get_node.assert_not_called()


def test_schedule__unexpect_raise():
    node_id = "nid"
    schedule_id = 1

    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.apply_schedule_lock = MagicMock(side_effect=Exception)
    runtime.get_execution_data_outputs = MagicMock(return_value={})

    engine = Engine(runtime=runtime)
    engine.schedule(pi.process_id, node_id, schedule_id)

    runtime.get_process_info.assert_called_once_with(pi.process_id)
    runtime.apply_schedule_lock.assert_called_once_with(schedule_id)
    runtime.set_state.assert_called_once_with(
        node_id=node_id, to_state=states.FAILED, set_archive_time=True
    )
    runtime.get_execution_data_outputs.assert_called_once_with(node_id)
    runtime.set_execution_data_outputs.assert_called_once()
    runtime.release_schedule_lock.assert_called_once_with(schedule_id)
    runtime.get_schedule.assert_not_called()


def test_schedule__raise_state_not_match():
    node_id = "nid"
    schedule_id = 1

    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.apply_schedule_lock = MagicMock(side_effect=StateVersionNotMatchError)
    runtime.get_execution_data_outputs = MagicMock(return_value={})

    engine = Engine(runtime=runtime)
    engine.schedule(pi.process_id, node_id, schedule_id)

    runtime.get_process_info.assert_called_once_with(pi.process_id)
    runtime.apply_schedule_lock.assert_called_once_with(schedule_id)
    runtime.set_state.assert_not_called()
    runtime.get_execution_data_outputs.assert_not_called()
    runtime.set_execution_data_outputs.assert_not_called()
    runtime.release_schedule_lock.assert_not_called()
    runtime.get_schedule.assert_not_called()


def test_schedule__has_callback_data():
    node_id = "nid"

    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node_id,
        finished=False,
        expired=False,
        version="v1",
        times=0,
    )

    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.RUNNING,
        version="v1",
        loop=11,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
    )

    callback_data = CallbackData(id=1, node_id=node_id, version="v1", data={})

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

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.apply_schedule_lock = MagicMock(return_value=True)
    runtime.get_schedule = MagicMock(return_value=schedule)
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_callback_data = MagicMock(return_value=callback_data)
    runtime.get_node = MagicMock(return_value=node)

    handler = MagicMock()
    handler.schedule = MagicMock(
        return_value=ScheduleResult(
            has_next_schedule=False,
            schedule_after=-1,
            schedule_done=False,
            next_node_id=None,
        )
    )
    get_handler = MagicMock(return_value=handler)

    engine = Engine(runtime=runtime)

    with mock.patch(
        "bamboo_engine.engine.HandlerFactory.get_handler",
        get_handler,
    ):
        engine.schedule(pi.process_id, node_id, schedule.id, callback_data.id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_process_info.assert_called_once_with(pi.process_id)
    runtime.apply_schedule_lock.assert_called_once_with(schedule.id)
    runtime.schedule.assert_not_called()
    runtime.get_schedule.assert_called_once_with(schedule.id)
    runtime.get_state.assert_called_once_with(node_id)
    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_callback_data.assert_called_once_with(callback_data.id)
    handler.schedule.assert_called_once_with(pi, state.loop, schedule, callback_data)


def test_schedule__without_callback_data():
    node_id = "nid"

    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node_id,
        finished=False,
        expired=False,
        version="v1",
        times=0,
    )

    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.RUNNING,
        version="v1",
        loop=11,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
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

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.apply_schedule_lock = MagicMock(return_value=True)
    runtime.get_schedule = MagicMock(return_value=schedule)
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_node = MagicMock(return_value=node)

    handler = MagicMock()
    handler.schedule = MagicMock(
        return_value=ScheduleResult(
            has_next_schedule=False,
            schedule_after=-1,
            schedule_done=False,
            next_node_id=None,
        )
    )
    get_handler = MagicMock(return_value=handler)

    engine = Engine(runtime=runtime)

    with mock.patch(
        "bamboo_engine.engine.HandlerFactory.get_handler",
        get_handler,
    ):
        engine.schedule(pi.process_id, node_id, schedule.id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_process_info.assert_called_once_with(pi.process_id)
    runtime.apply_schedule_lock.assert_called_once_with(schedule.id)
    runtime.schedule.assert_not_called()
    runtime.get_schedule.assert_called_once_with(schedule.id)
    runtime.get_state.assert_called_once_with(node_id)
    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_callback_data.assert_not_called()
    handler.schedule.assert_called_once_with(pi, state.loop, schedule, None)


def test_schedule__has_next_schedule():
    node_id = "nid"

    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node_id,
        finished=False,
        expired=False,
        version="v1",
        times=0,
    )

    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.RUNNING,
        version="v1",
        loop=11,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
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

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.apply_schedule_lock = MagicMock(return_value=True)
    runtime.get_schedule = MagicMock(return_value=schedule)
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_node = MagicMock(return_value=node)

    handler = MagicMock()
    handler.schedule = MagicMock(
        return_value=ScheduleResult(
            has_next_schedule=True,
            schedule_after=60,
            schedule_done=False,
            next_node_id=None,
        )
    )
    get_handler = MagicMock(return_value=handler)

    engine = Engine(runtime=runtime)

    with mock.patch(
        "bamboo_engine.engine.HandlerFactory.get_handler",
        get_handler,
    ):
        engine.schedule(pi.process_id, node_id, schedule.id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_process_info.assert_called_once_with(pi.process_id)
    runtime.apply_schedule_lock.assert_called_once_with(schedule.id)
    runtime.schedule.assert_not_called()
    runtime.get_schedule.assert_called_once_with(schedule.id)
    runtime.get_state.assert_called_once_with(node_id)
    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_callback_data.assert_not_called()
    handler.schedule.assert_called_once_with(pi, state.loop, schedule, None)
    runtime.set_next_schedule.assert_called_once_with(
        pi.process_id, node_id, schedule.id, 60
    )
    runtime.finish_schedule.assert_not_called()
    runtime.execute.assert_not_called()


def test_schedule__schedule_done():
    node_id = "nid"

    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    schedule = Schedule(
        id=1,
        type=ScheduleType.POLL,
        process_id=pi.process_id,
        node_id=node_id,
        finished=False,
        expired=False,
        version="v1",
        times=0,
    )

    state = State(
        node_id=node_id,
        root_id="root",
        parent_id="root",
        name=states.RUNNING,
        version="v1",
        loop=11,
        retry=0,
        skip=False,
        created_time=None,
        started_time=None,
        archived_time=None,
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

    runtime = MagicMock()
    runtime.get_process_info = MagicMock(return_value=pi)
    runtime.apply_schedule_lock = MagicMock(return_value=True)
    runtime.get_schedule = MagicMock(return_value=schedule)
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_node = MagicMock(return_value=node)

    handler = MagicMock()
    handler.schedule = MagicMock(
        return_value=ScheduleResult(
            has_next_schedule=False,
            schedule_after=-1,
            schedule_done=True,
            next_node_id="nid2",
        )
    )
    get_handler = MagicMock(return_value=handler)

    engine = Engine(runtime=runtime)

    with mock.patch(
        "bamboo_engine.engine.HandlerFactory.get_handler",
        get_handler,
    ):
        engine.schedule(pi.process_id, node_id, schedule.id)

    runtime.beat.assert_called_once_with(pi.process_id)
    runtime.get_process_info.assert_called_once_with(pi.process_id)
    runtime.apply_schedule_lock.assert_called_once_with(schedule.id)
    runtime.schedule.assert_not_called()
    runtime.get_schedule.assert_called_once_with(schedule.id)
    runtime.get_state.assert_called_once_with(node_id)
    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_callback_data.assert_not_called()
    handler.schedule.assert_called_once_with(pi, state.loop, schedule, None)
    runtime.set_next_schedule.assert_not_called()
    runtime.finish_schedule.assert_called_once_with(schedule.id)
    runtime.execute.assert_called_once_with(pi.process_id, "nid2")
