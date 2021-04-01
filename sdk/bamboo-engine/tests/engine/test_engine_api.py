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
from mock import MagicMock, call, patch

from bamboo_engine.eri import SuspendedProcessInfo, NodeType
from bamboo_engine import states, exceptions
from bamboo_engine.engine import Engine


def test_run_pipeline():

    process_id = 1
    start_event_id = "token"
    options = {"priority": 100, "queue": "q"}

    runtime = MagicMock()
    runtime.prepare_run_pipeline = MagicMock(return_value=process_id)
    runtime.execute = MagicMock()
    validator = MagicMock()

    pipeline = {"start_event": {"id": start_event_id}}
    root_pipeline_data = {"k": "v"}

    engine = Engine(runtime=runtime)

    with patch("bamboo_engine.engine.validator", validator):
        engine.run_pipeline(
            pipeline=pipeline, root_pipeline_data=root_pipeline_data, **options
        )

    validator.validate_and_process_pipeline.assert_called_once_with(pipeline, False)
    runtime.pre_prepare_run_pipeline.assert_called_once_with(
        pipeline, root_pipeline_data, **options
    )
    runtime.prepare_run_pipeline.assert_called_once_with(
        pipeline, root_pipeline_data, **options
    )
    runtime.post_prepare_run_pipeline.assert_called_once_with(
        pipeline, root_pipeline_data, **options
    )
    runtime.execute.assert_called_once_with(process_id, start_event_id)


def test_pause_pipeline():
    pipeline_id = "pid"

    runtime = MagicMock()
    runtime.has_state = MagicMock(return_value=True)

    engine = Engine(runtime=runtime)
    engine.pause_pipeline(pipeline_id)

    runtime.has_state.assert_called_once_with(pipeline_id)
    runtime.pre_pause_pipeline.assert_called_once_with(pipeline_id)
    runtime.set_state.assert_called_once_with(
        node_id=pipeline_id, to_state=states.SUSPENDED
    )
    runtime.post_pause_pipeline.assert_called_once_with(pipeline_id)


def test_pause_pipeline__pipeline_not_exist():
    pipeline_id = "pid"

    runtime = MagicMock()
    runtime.has_state = MagicMock(return_value=False)
    runtime.pre_pause_pipeline = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)

    with pytest.raises(exceptions.NotFoundError):
        engine.pause_pipeline(pipeline_id)


def test_revoke_pipeline():
    pipeline_id = "pid"

    runtime = MagicMock()
    runtime.has_state = MagicMock(return_value=True)

    engine = Engine(runtime=runtime)
    engine.revoke_pipeline(pipeline_id)

    runtime.has_state.assert_called_once_with(pipeline_id)
    runtime.pre_revoke_pipeline.assert_called_once_with(pipeline_id)
    runtime.set_state.assert_called_once_with(
        node_id=pipeline_id, to_state=states.REVOKED
    )
    runtime.post_revoke_pipeline.assert_called_once_with(pipeline_id)


def test_revoke_pipeline__pipeline_not_exist():
    pipeline_id = "pid"

    runtime = MagicMock()
    runtime.has_state = MagicMock(return_value=False)
    runtime.pre_revoke_pipeline = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)

    with pytest.raises(exceptions.NotFoundError):
        engine.revoke_pipeline(pipeline_id)


def test_resume_pipeline():
    pipeline_id = "pid"
    suspended_process_info = [
        SuspendedProcessInfo(process_id=1, current_node=2),
        SuspendedProcessInfo(process_id=3, current_node=4),
    ]
    state = MagicMock()
    state.name = "SUSPENDED"

    runtime = MagicMock()
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_suspended_process_info = MagicMock(return_value=suspended_process_info)

    engine = Engine(runtime=runtime)
    engine.resume_pipeline(pipeline_id)

    runtime.get_state.assert_called_once_with(pipeline_id)
    runtime.get_suspended_process_info.assert_called_once_with(pipeline_id)
    runtime.pre_resume_pipeline.assert_called_once_with(pipeline_id)
    runtime.set_state.assert_called_once_with(
        node_id=pipeline_id, to_state=states.RUNNING
    )
    runtime.batch_resume.assert_called_once_with(
        process_id_list=[
            suspended_process_info[0].process_id,
            suspended_process_info[1].process_id,
        ]
    )
    runtime.execute.assert_has_calls(
        [
            call(
                suspended_process_info[0].process_id,
                suspended_process_info[0].current_node,
            ),
            call(
                suspended_process_info[1].process_id,
                suspended_process_info[1].current_node,
            ),
        ]
    )
    runtime.post_resume_pipeline.assert_called_once_with(pipeline_id)


def test_resume_pipeline__state_not_match():
    pipeline_id = "pid"
    suspended_process_info = []
    state = MagicMock()
    state.name = "RUNNING"

    runtime = MagicMock()
    runtime.get_state = MagicMock(return_value=state)

    engine = Engine(runtime=runtime)

    with pytest.raises(exceptions.InvalidOperationError):
        engine.resume_pipeline(pipeline_id)

    runtime.get_state.assert_called_once_with(pipeline_id)
    runtime.set_state.assert_not_called()


def test_resume_pipeline__can_not_find_suspended_process():
    pipeline_id = "pid"
    suspended_process_info = []
    state = MagicMock()
    state.name = "SUSPENDED"

    runtime = MagicMock()
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_suspended_process_info = MagicMock(return_value=suspended_process_info)

    engine = Engine(runtime=runtime)
    engine.resume_pipeline(pipeline_id)

    runtime.get_state.assert_called_once_with(pipeline_id)
    runtime.get_suspended_process_info.assert_called_once_with(pipeline_id)
    runtime.pre_resume_pipeline.assert_called_once_with(pipeline_id)
    runtime.set_state.assert_called_once_with(
        node_id=pipeline_id, to_state=states.RUNNING
    )
    runtime.batch_resume.assert_not_called()
    runtime.execute.assert_not_called()
    runtime.post_resume_pipeline.assert_called_once_with(pipeline_id)


def test_pause_node_appoint():
    node_id = "nid"
    node_type = NodeType.ServiceActivity

    node = MagicMock()
    node.type = node_type

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)

    engine = Engine(runtime=runtime)
    engine.pause_node_appoint(node_id)

    runtime.pre_pause_node.assert_called_once_with(node_id)
    runtime.set_state.assert_called_once_with(
        node_id=node_id, to_state=states.SUSPENDED
    )
    runtime.post_pause_node.assert_called_once_with(node_id)


def test_pause_node_appoint__node_type_is_subprocess():
    node_id = "nid"
    node_type = NodeType.SubProcess

    node = MagicMock()
    node.type = node_type

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.pre_pause_node = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)
    with pytest.raises(exceptions.InvalidOperationError):
        engine.pause_node_appoint(node_id)


def test_resume_node_appoint():
    node_id = "nid"
    node_type = NodeType.ServiceActivity

    node = MagicMock()
    node.type = node_type
    suspended_process_info_list = [
        SuspendedProcessInfo("1", "2"),
    ]

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_suspended_process_info = MagicMock(
        return_value=suspended_process_info_list
    )

    engine = Engine(runtime=runtime)
    engine.resume_node_appoint(node_id)

    runtime.get_node.assert_called_once_with(node_id)
    runtime.pre_resume_node.assert_called_once_with(node_id)
    runtime.set_state.assert_called_once_with(node_id=node_id, to_state=states.READY)
    runtime.get_suspended_process_info.assert_called_once_with(node_id)
    runtime.resume.assert_called_once_with(
        process_id=suspended_process_info_list[0].process_id
    )
    runtime.execute.assert_called_once_with(
        suspended_process_info_list[0].process_id,
        suspended_process_info_list[0].current_node,
    )
    runtime.post_resume_node.assert_called_once_with(node_id)


def test_resume_node_appoint__node_type_is_subprocess():
    node_id = "nid"
    node_type = NodeType.SubProcess

    node = MagicMock()
    node.type = node_type

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.pre_resume_node = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)
    with pytest.raises(exceptions.InvalidOperationError):
        engine.resume_node_appoint(node_id)


def test_resume_node_appoint__without_suspended_process():
    node_id = "nid"
    node_type = NodeType.ServiceActivity

    node = MagicMock()
    node.type = node_type
    suspended_process_info_list = []

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_suspended_process_info = MagicMock(
        return_value=suspended_process_info_list
    )
    runtime.resume = MagicMock(side_effect=Exception)
    runtime.execute = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)
    engine.resume_node_appoint(node_id)

    runtime.get_node.assert_called_once_with(node_id)
    runtime.pre_resume_node.assert_called_once_with(node_id)
    runtime.set_state.assert_called_once_with(node_id=node_id, to_state=states.READY)
    runtime.get_suspended_process_info.assert_called_once_with(node_id)
    runtime.resume.assert_not_called()
    runtime.execute.assert_not_called()
    runtime.post_resume_node.assert_called_once_with(node_id)


def test_retry_node():
    node_id = "nid"
    process_id = "pid"
    data = {}

    state = MagicMock()
    state.node_id = node_id
    state.name = states.FAILED
    state.started_time = "started_time"
    state.archived_time = "archived_time"
    state.loop = 1
    state.skip = True
    state.retry = 0
    state.version = "version"

    execution_data = MagicMock()
    execution_data.inputs = "inputs"
    execution_data.outputs = "outputs"

    runtime = MagicMock()
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_sleep_process_with_current_node_id = MagicMock(return_value=process_id)
    runtime.get_execution_data = MagicMock(return_value=execution_data)

    engine = Engine(runtime=runtime)
    engine.retry_node(node_id, data)

    runtime.pre_retry_node.assert_called_once_with(node_id, data)
    runtime.get_state.assert_called_once_with(node_id)
    runtime.get_sleep_process_with_current_node_id.assert_called_once_with(node_id)
    runtime.set_data_inputs.assert_called_once_with(node_id, data)
    runtime.add_history.assert_called_once_with(
        node_id=node_id,
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
        node_id=node_id,
        to_state=states.READY,
        is_retry=True,
        refresh_version=True,
        clear_started_time=True,
        clear_archived_time=True,
    )
    runtime.execute.assert_called_once_with(process_id, node_id)
    runtime.post_retry_node.assert_called_once_with(node_id, data)


def test_retry_node__state_is_not_failed():
    node_id = "nid"
    data = {}

    state = MagicMock()
    state.name = states.RUNNING

    runtime = MagicMock()
    runtime.get_state = MagicMock(return_value=state)
    runtime.pre_retry_node = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)
    with pytest.raises(exceptions.InvalidOperationError):
        engine.retry_node(node_id, data)


def test_retry_node__can_retry_is_false():
    node_id = "nid"
    process_id = "pid"
    data = {}

    state = MagicMock()
    state.node_id = node_id
    state.name = states.FAILED

    node = MagicMock()
    node.can_retry = False

    runtime = MagicMock()
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_node = MagicMock(return_value=node)

    engine = Engine(runtime=runtime)
    with pytest.raises(exceptions.InvalidOperationError):
        engine.retry_node(node_id, data)


def test_retry_node__can_not_find_sleep_process():
    node_id = "nid"
    data = {}

    state = MagicMock()
    state.node_id = node_id
    state.name = states.FAILED

    runtime = MagicMock()
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_sleep_process_with_current_node_id = MagicMock(return_value=None)
    runtime.pre_retry_node = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)
    with pytest.raises(exceptions.InvalidOperationError):
        engine.retry_node(node_id, data)


def test_retry_node__with_none_data():
    node_id = "nid"
    process_id = "pid"

    state = MagicMock()
    state.node_id = node_id
    state.name = states.FAILED
    state.started_time = "started_time"
    state.archived_time = "archived_time"
    state.loop = 1
    state.skip = True
    state.retry = 0
    state.version = "version"

    execution_data = MagicMock()
    execution_data.inputs = "inputs"
    execution_data.outputs = "outputs"

    runtime = MagicMock()
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_sleep_process_with_current_node_id = MagicMock(return_value=process_id)
    runtime.get_execution_data = MagicMock(return_value=execution_data)

    engine = Engine(runtime=runtime)
    engine.retry_node(node_id)

    runtime.pre_retry_node.assert_called_once_with(node_id, None)
    runtime.get_state.assert_called_once_with(node_id)
    runtime.get_sleep_process_with_current_node_id.assert_called_once_with(node_id)
    runtime.set_data_inputs.assert_not_called()
    runtime.add_history.assert_called_once_with(
        node_id=node_id,
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
        node_id=node_id,
        to_state=states.READY,
        is_retry=True,
        refresh_version=True,
        clear_started_time=True,
        clear_archived_time=True,
    )
    runtime.execute.assert_called_once_with(process_id, node_id)
    runtime.post_retry_node.assert_called_once_with(node_id, None)


def test_skip_node():
    node_id = "nid"
    process_id = "pid"

    node = MagicMock()
    node.type = NodeType.ServiceActivity
    node.can_skip = True
    node.target_nodes = ["target_node"]

    state = MagicMock()
    state.node_id = node_id
    state.name = states.FAILED
    state.started_time = "started_time"
    state.archived_time = "archived_time"
    state.loop = 1
    state.skip = True
    state.retry = 0
    state.version = "version"

    execution_data = MagicMock()
    execution_data.inputs = "inputs"
    execution_data.outputs = "outputs"

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_sleep_process_with_current_node_id = MagicMock(return_value=process_id)
    runtime.get_execution_data = MagicMock(return_value=execution_data)

    engine = Engine(runtime=runtime)
    engine.skip_node(node_id)

    runtime.get_node.assert_called_once_with(node_id)
    runtime.pre_skip_node.assert_called_once_with(node_id)
    runtime.get_state.assert_called_once_with(node_id)
    runtime.get_sleep_process_with_current_node_id(node_id)
    runtime.add_history.assert_called_once_with(
        node_id=node_id,
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
        node_id=node_id,
        to_state=states.FINISHED,
        is_skip=True,
        refresh_version=True,
        set_archive_time=True,
    )
    runtime.execute.assert_called_once_with(process_id, node.target_nodes[0])
    runtime.post_skip_node.assert_called_once_with(node_id)


def test_skip_node__node_can_not_skip():
    node_id = "nid"
    process_id = "pid"

    node = MagicMock()
    node.type = NodeType.ServiceActivity
    node.can_skip = False

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.pre_skip_node = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)

    with pytest.raises(exceptions.InvalidOperationError):
        engine.skip_node(node_id)


def test_skip_node__node_type_not_fit():
    node_id = "nid"
    process_id = "pid"

    node = MagicMock()
    node.type = NodeType.SubProcess
    node.can_skip = True

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.pre_skip_node = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)

    with pytest.raises(exceptions.InvalidOperationError):
        engine.skip_node(node_id)


def test_skip_node__state_is_not_failed():
    node_id = "nid"
    process_id = "pid"

    node = MagicMock()
    node.type = NodeType.ServiceActivity
    node.can_skip = True
    node.target_nodes = ["target_node"]

    state = MagicMock()
    state.node_id = node_id
    state.name = states.RUNNING

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state = MagicMock(return_value=state)
    runtime.pre_skip_node = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)

    with pytest.raises(exceptions.InvalidOperationError):
        engine.skip_node(node_id)

    runtime.get_state.assert_called_once_with(node_id)


def test_skip_node__can_not_find_sleep_process():
    node_id = "nid"

    node = MagicMock()
    node.type = NodeType.ServiceActivity
    node.can_skip = True
    node.target_nodes = ["target_node"]

    state = MagicMock()
    state.node_id = node_id
    state.name = states.FAILED

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_sleep_process_with_current_node_id = MagicMock(return_value=None)
    runtime.pre_retry_node = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)
    with pytest.raises(exceptions.InvalidOperationError):
        engine.skip_node(node_id)

    runtime.get_state.assert_called_once_with(node_id)


def test_skip_exclusive_gateway():
    node_id = "nid"
    process_id = "pid"
    flow_id = "flow_1"

    node = MagicMock()
    node.id = node_id
    node.type = NodeType.ExclusiveGateway
    node.targets = {flow_id: "target_1"}

    state = MagicMock()
    state.node_id = node_id
    state.name = states.FAILED
    state.started_time = "started_time"
    state.archived_time = "archived_time"
    state.loop = 1
    state.skip = True
    state.retry = 0
    state.version = "version"

    execution_data = MagicMock()
    execution_data.inputs = "inputs"
    execution_data.outputs = "outputs"

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.pre_skip_exclusive_gateway = MagicMock()
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_sleep_process_with_current_node_id = MagicMock(return_value=process_id)
    runtime.get_execution_data = MagicMock(return_value=execution_data)

    engine = Engine(runtime=runtime)
    engine.skip_exclusive_gateway(node_id, flow_id)

    runtime.get_node.assert_called_once_with(node_id)
    runtime.pre_skip_exclusive_gateway.assert_called_once_with(node_id, flow_id)
    runtime.get_state.assert_called_once_with(node_id)
    runtime.get_sleep_process_with_current_node_id(node_id)
    runtime.add_history.assert_called_once_with(
        node_id=node_id,
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
        node_id=node_id,
        to_state=states.FINISHED,
        is_skip=True,
        refresh_version=True,
        set_archive_time=True,
    )
    runtime.execute.assert_called_once_with(process_id, node.targets[flow_id])
    runtime.post_skip_exclusive_gateway.assert_called_once_with(node_id, flow_id)


def test_skip_exclusive_gateway__node_type_not_fit():
    node_id = "nid"
    flow_id = "flow_1"

    node = MagicMock()
    node.type = NodeType.ParallelGateway

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)

    with pytest.raises(exceptions.InvalidOperationError):
        engine.skip_exclusive_gateway(node_id, flow_id)


def test_skip_exclusive_gateway__node_is_not_failed():
    node_id = "nid"
    process_id = "pid"
    flow_id = "flow_1"

    node = MagicMock()
    node.type = NodeType.ExclusiveGateway
    node.can_skip = True
    node.targets = {flow_id: "target1"}

    state = MagicMock()
    state.node_id = node_id
    state.name = states.RUNNING

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state = MagicMock(return_value=state)
    runtime.pre_skip_exclusive_gateway = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)

    with pytest.raises(exceptions.InvalidOperationError):
        engine.skip_exclusive_gateway(node_id, flow_id)

    runtime.get_state.assert_called_once_with(node_id)


def test_skip_exclusive_gateway__can_not_find_sleep_proces():
    node_id = "nid"
    flow_id = "flow_1"

    node = MagicMock()
    node.type = NodeType.ExclusiveGateway
    node.targets = {flow_id: "target1"}

    state = MagicMock()
    state.node_id = node_id
    state.name = states.FAILED

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_sleep_process_with_current_node_id = MagicMock(return_value=None)
    runtime.pre_skip_exclusive_gateway = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)
    with pytest.raises(exceptions.InvalidOperationError):
        engine.skip_exclusive_gateway(node_id, flow_id)

    runtime.get_state.assert_called_once_with(node_id)


def test_forced_fail_activity():
    node_id = "nid"
    ex_data = "ex_msg"
    process_id = "pid"

    node = MagicMock()
    node.type = NodeType.ServiceActivity

    state = MagicMock()
    state.name = states.RUNNING

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_process_id_with_current_node_id = MagicMock(return_value=process_id)
    runtime.get_execution_data_outputs = MagicMock(return_value={})

    engine = Engine(runtime=runtime)
    engine.forced_fail_activity(node_id, ex_data)

    runtime.get_node.assert_called_once_with(node_id)
    runtime.get_state.assert_called_once_with(node_id)
    runtime.get_process_id_with_current_node_id.assert_called_once_with(node_id)
    runtime.pre_forced_fail_activity.assert_called_once_with(node_id, ex_data)
    runtime.get_execution_data_outputs.assert_called_once_with(node_id)
    runtime.set_state.assert_called_once_with(
        node_id=node_id,
        to_state=states.FAILED,
        refresh_version=True,
        set_archive_time=True,
    )
    runtime.set_execution_data_outputs.assert_called_once_with(
        node_id, {"ex_data": ex_data, "_forced_failed": True}
    )
    runtime.kill.assert_called_once_with(process_id)
    runtime.post_forced_fail_activity.assert_called_once_with(node_id, ex_data)


def test_forced_fail_activity__node_type_not_fit():
    node_id = "nid"
    ex_data = "ex_msg"

    node = MagicMock()
    node.type = NodeType.SubProcess

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)
    with pytest.raises(exceptions.InvalidOperationError):
        engine.forced_fail_activity(node_id, ex_data)


def test_forced_fail_activity__node_is_not_running():
    node_id = "nid"
    ex_data = "ex_msg"

    node = MagicMock()
    node.type = NodeType.ServiceActivity

    state = MagicMock()
    state.name = states.FINISHED

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_process_id_with_current_node_id = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)
    with pytest.raises(exceptions.InvalidOperationError):
        engine.forced_fail_activity(node_id, ex_data)

    runtime.get_state.assert_called_once_with(node_id)


def test_forced_fail_activity__can_not_find_process_id():
    node_id = "nid"
    ex_data = "ex_msg"

    node = MagicMock()
    node.type = NodeType.ServiceActivity

    state = MagicMock()
    state.name = states.RUNNING

    runtime = MagicMock()
    runtime.get_node = MagicMock(return_value=node)
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_process_id_with_current_node_id = MagicMock(return_value=None)
    runtime.pre_forced_fail_activity = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)
    with pytest.raises(exceptions.InvalidOperationError):
        engine.forced_fail_activity(node_id, ex_data)

    runtime.get_state.get_process_id_with_current_node_id(node_id)


def test_callback():
    node_id = "nid"
    version = "v1"
    process_id = "pid"
    data = {"data": 1}
    data_id = 1

    state = MagicMock()
    state.version = version

    schedule = MagicMock()
    schedule_id = 2
    schedule.finished = False
    schedule.expired = False

    runtime = MagicMock()
    runtime.get_sleep_process_with_current_node_id = MagicMock(return_value=process_id)
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_schedule_with_node_and_version = MagicMock(return_value=schedule)
    runtime.set_callback_data = MagicMock(return_value=data_id)

    engine = Engine(runtime=runtime)
    engine.callback(node_id, version, data)

    runtime.get_sleep_process_with_current_node_id.assert_called_once_with(node_id)
    runtime.get_state.assert_called_once_with(node_id)
    runtime.get_schedule_with_node_and_version(node_id, version)
    runtime.pre_callback.assert_called_once_with(node_id, version, data)
    runtime.set_callback_data.assert_called_once_with(node_id, version, data)
    runtime.schedule.assert_called_once_with(process_id, node_id, schedule.id, data_id)
    runtime.post_callback.assert_called_once_with(node_id, version, data)


def test_callback__can_not_find_process_id():
    node_id = "nid"
    version = "v1"
    data = {"data": 1}

    runtime = MagicMock()
    runtime.get_sleep_process_with_current_node_id = MagicMock(return_value=None)
    runtime.get_state = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)
    with pytest.raises(exceptions.InvalidOperationError):
        engine.callback(node_id, version, data)


def test_callback__version_not_match():
    node_id = "nid"
    version = "v1"
    process_id = "pid"
    data = {"data": 1}

    state = MagicMock()
    state.version = "v2"

    schedule = MagicMock()
    schedule_id = 2

    runtime = MagicMock()
    runtime.get_sleep_process_with_current_node_id = MagicMock(return_value=process_id)
    runtime.get_schedule_with_node_and_version = MagicMock(return_value=schedule)
    runtime.get_state = MagicMock(return_value=state)
    runtime.pre_callback = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)
    with pytest.raises(exceptions.InvalidOperationError):
        engine.callback(node_id, version, data)

    runtime.expire_schedule.assert_called_once_with(schedule.id)


def test_callback__schedule_finished():
    node_id = "nid"
    version = "v1"
    process_id = "pid"
    data = {"data": 1}

    state = MagicMock()
    state.version = version

    schedule = MagicMock()
    schedule_id = 2
    schedule.finished = True
    schedule.expired = False

    runtime = MagicMock()
    runtime.get_sleep_process_with_current_node_id = MagicMock(return_value=process_id)
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_schedule_with_node_and_version = MagicMock(return_value=schedule)
    runtime.pre_callback = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)
    with pytest.raises(exceptions.InvalidOperationError):
        engine.callback(node_id, version, data)

    runtime.get_schedule_with_node_and_version.assert_called_once_with(node_id, version)
    runtime.expire_schedule.assert_not_called()


def test_callback__schedule_expired():
    node_id = "nid"
    version = "v1"
    process_id = "pid"
    data = {"data": 1}

    state = MagicMock()
    state.version = version

    schedule = MagicMock()
    schedule_id = 2
    schedule.finished = False
    schedule.expired = True

    runtime = MagicMock()
    runtime.get_sleep_process_with_current_node_id = MagicMock(return_value=process_id)
    runtime.get_state = MagicMock(return_value=state)
    runtime.get_schedule_with_node_and_version = MagicMock(return_value=schedule)
    runtime.pre_callback = MagicMock(side_effect=Exception)

    engine = Engine(runtime=runtime)
    with pytest.raises(exceptions.InvalidOperationError):
        engine.callback(node_id, version, data)

    runtime.get_schedule_with_node_and_version.assert_called_once_with(node_id, version)
    runtime.expire_schedule.assert_not_called()
