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
    ParallelGateway,
)
from bamboo_engine.handlers.parallel_gateway import (
    ParallelGatewayHandler,
)


def test_parallel_gateway_handler__execute_success():
    pi = ProcessInfo(
        process_id="pid",
        destination_id="",
        root_pipeline_id="root",
        pipeline_stack=["root"],
        parent_id="parent",
    )

    node = ParallelGateway(
        id="nid",
        type=NodeType.ParallelGateway,
        target_flows=["f1", "f2", "f3"],
        target_nodes=["t1", "t2", "t3"],
        targets={"f1": "t1", "f2": "t2", "f3": "t3"},
        root_pipeline_id="root",
        parent_pipeline_id="root",
        can_skip=True,
        converge_gateway_id="cg",
    )

    dispatch_processes = ["p1", "p2", "p3"]

    runtime = MagicMock()
    runtime.fork = MagicMock(return_value=dispatch_processes)

    handler = ParallelGatewayHandler(node, runtime)
    result = handler.execute(pi, 1, "v1")

    assert result.should_sleep == True
    assert result.schedule_ready == False
    assert result.schedule_type == None
    assert result.schedule_after == -1
    assert result.dispatch_processes == dispatch_processes
    assert result.next_node_id == None
    assert result.should_die == False

    runtime.fork.assert_called_once_with(
        parent_id=pi.process_id,
        root_pipeline_id=pi.root_pipeline_id,
        pipeline_stack=pi.pipeline_stack,
        from_to={
            "t1": "cg",
            "t2": "cg",
            "t3": "cg",
        },
    )

    runtime.set_state.assert_called_once_with(
        node_id=node.id, to_state=states.FINISHED, set_archive_time=True
    )
