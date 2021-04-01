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

from django.test import TestCase

from pipeline.engine import states
from pipeline.engine.core import runtime
from pipeline.engine.models import FunctionSwitch, NodeRelationship, Status
from pipeline.tests.engine.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa

PIPELINE_BUILD_RELATIONSHIP = "pipeline.engine.models.NodeRelationship.objects.build_relationship"
PIPELINE_STATUS_TRANSIT = "pipeline.engine.models.Status.objects.transit"
PIPELINE_ENGINE_IS_FROZEN = "pipeline.engine.models.FunctionSwitch.objects.is_frozen"
PIPELINE_SETTING_RERUN_MAX_LIMIT = "pipeline.engine.core.runtime.RERUN_MAX_LIMIT"


class RuntimeTestCase(TestCase):
    def test_runtime_exception_handler(self):
        process = MockPipelineProcess()
        process.exit_gracefully = MagicMock()
        e = Exception()

        # raise case
        with runtime.runtime_exception_handler(process):
            raise e

        process.exit_gracefully.assert_called_with(e)

        process.exit_gracefully.reset_mock()

        # normal case
        with runtime.runtime_exception_handler(process):
            pass

        process.exit_gracefully.assert_not_called()

    @patch(PIPELINE_BUILD_RELATIONSHIP, MagicMock())
    @patch(PIPELINE_ENGINE_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=True)))
    @patch(PIPELINE_SETTING_RERUN_MAX_LIMIT, 0)
    def test_run_loop(self):
        # 1. test child meet destination
        destination_node = IdentifyObject()
        process = MockPipelineProcess(
            top_pipeline=PipelineObject(node=destination_node),
            destination_id=destination_node.id,
            current_node_id=destination_node.id,
        )
        runtime.run_loop(process)

        process.destroy_and_wake_up_parent.assert_called_with(destination_node.id)

        process.root_sleep_check.assert_not_called()

        process.sleep.assert_not_called()

        process.subproc_sleep_check.assert_not_called()

        FunctionSwitch.objects.is_frozen.assert_not_called()

        process.freeze.assert_not_called()

        Status.objects.transit.assert_not_called()

        process.refresh_current_node.assert_not_called()

        NodeRelationship.objects.build_relationship.assert_not_called()

        self.assertEqual(process.current_node_id, destination_node.id)

        # 2. test root sleep check return true、

        # 2.1. root pipeline is revoke
        current_node = IdentifyObject()
        process = MockPipelineProcess(
            top_pipeline=PipelineObject(node=current_node), destination_id=uniqid(), current_node_id=current_node.id
        )
        process.root_sleep_check = MagicMock(return_value=(True, states.REVOKED))

        runtime.run_loop(process)

        process.destroy_and_wake_up_parent.assert_not_called()

        process.root_sleep_check.assert_called()

        process.sleep.assert_called_once()
        process.sleep.assert_called_with(do_not_save=True)

        process.subproc_sleep_check.assert_not_called()

        FunctionSwitch.objects.is_frozen.assert_not_called()

        process.freeze.assert_not_called()

        Status.objects.transit.assert_not_called()

        process.refresh_current_node.assert_not_called()

        NodeRelationship.objects.build_relationship.assert_not_called()

        self.assertEqual(process.current_node_id, current_node.id)

        # 2.2. root pipeline is not revoke
        for state in states.SLEEP_STATES.difference({states.REVOKED}):
            current_node = IdentifyObject()
            process = MockPipelineProcess(
                top_pipeline=PipelineObject(node=current_node), destination_id=uniqid(), current_node_id=current_node.id
            )
            process.root_sleep_check = MagicMock(return_value=(True, state))

            runtime.run_loop(process)

            process.destroy_and_wake_up_parent.assert_not_called()

            process.root_sleep_check.assert_called()

            process.sleep.assert_called_once_with(do_not_save=False)

            process.subproc_sleep_check.assert_not_called()

            FunctionSwitch.objects.is_frozen.assert_not_called()

            process.freeze.assert_not_called()

            Status.objects.transit.assert_not_called()

            process.refresh_current_node.assert_not_called()

            NodeRelationship.objects.build_relationship.assert_not_called()

            self.assertEqual(process.current_node_id, current_node.id)

        # 3. test sub process sleep check return true
        current_node = IdentifyObject()
        subproc_above = uniqid()
        process = MockPipelineProcess(
            top_pipeline=PipelineObject(node=current_node), destination_id=uniqid(), current_node_id=current_node.id
        )
        process.root_sleep_check = MagicMock(return_value=(False, states.RUNNING))
        process.subproc_sleep_check = MagicMock(return_value=(True, subproc_above))

        runtime.run_loop(process)

        process.destroy_and_wake_up_parent.assert_not_called()

        process.root_sleep_check.assert_called()

        process.subproc_sleep_check.assert_called()

        process.sleep.assert_called_once_with(adjust_status=True, adjust_scope=subproc_above)

        FunctionSwitch.objects.is_frozen.assert_not_called()

        process.freeze.assert_not_called()

        Status.objects.transit.assert_not_called()

        process.refresh_current_node.assert_not_called()

        NodeRelationship.objects.build_relationship.assert_not_called()

        self.assertEqual(process.current_node_id, current_node.id)

        # 4. test engine is frozen
        with patch(PIPELINE_ENGINE_IS_FROZEN, MagicMock(return_value=True)):
            current_node = IdentifyObject()
            process = MockPipelineProcess(
                top_pipeline=PipelineObject(node=current_node), destination_id=uniqid(), current_node_id=current_node.id
            )
            process.root_sleep_check = MagicMock(return_value=(False, states.RUNNING))
            process.subproc_sleep_check = MagicMock(return_value=(False, []))

            runtime.run_loop(process)

            process.destroy_and_wake_up_parent.assert_not_called()

            process.root_sleep_check.assert_called()

            process.subproc_sleep_check.assert_called()

            process.sleep.assert_not_called()

            FunctionSwitch.objects.is_frozen.assert_called_once()

            process.freeze.assert_called_once()

            Status.objects.transit.assert_not_called()

            process.refresh_current_node.assert_not_called()

            NodeRelationship.objects.build_relationship.assert_not_called()

            self.assertEqual(process.current_node_id, current_node.id)

            FunctionSwitch.objects.is_frozen.reset_mock()

        # 5. test transit fail
        with patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=False))):
            current_node = IdentifyObject()
            process = MockPipelineProcess(
                top_pipeline=PipelineObject(node=current_node), destination_id=uniqid(), current_node_id=current_node.id
            )
            process.root_sleep_check = MagicMock(return_value=(False, states.RUNNING))
            process.subproc_sleep_check = MagicMock(return_value=(False, []))

            runtime.run_loop(process)

            process.destroy_and_wake_up_parent.assert_not_called()

            process.root_sleep_check.assert_called()

            process.subproc_sleep_check.assert_called()

            FunctionSwitch.objects.is_frozen.assert_called_once()

            process.freeze.assert_not_called()

            Status.objects.transit.assert_called_with(
                id=current_node.id, to_state=states.RUNNING, start=True, name=str(current_node.__class__)
            )

            process.sleep.assert_called_once_with(adjust_status=True)

            process.refresh_current_node.assert_not_called()

            NodeRelationship.objects.build_relationship.assert_not_called()

            self.assertEqual(process.current_node_id, current_node.id)

            FunctionSwitch.objects.is_frozen.reset_mock()
            Status.objects.transit.reset_mock()

        # 6. test normal
        hdl = MagicMock(return_value=MockHandlerResult(should_return=True, should_sleep=False))

        with patch("pipeline.engine.core.runtime.HandlersFactory.handlers_for", MagicMock(return_value=hdl)):
            # 6.1. test should return
            current_node = IdentifyObject(name="name")
            process = MockPipelineProcess(
                top_pipeline=PipelineObject(node=current_node), destination_id=uniqid(), current_node_id=current_node.id
            )
            process.root_sleep_check = MagicMock(return_value=(False, states.RUNNING))
            process.subproc_sleep_check = MagicMock(return_value=(False, []))

            runtime.run_loop(process)

            process.destroy_and_wake_up_parent.assert_not_called()

            process.root_sleep_check.assert_called()

            process.subproc_sleep_check.assert_called()

            FunctionSwitch.objects.is_frozen.assert_called_once()

            process.freeze.assert_not_called()

            Status.objects.transit.assert_called_with(
                id=current_node.id, to_state=states.RUNNING, start=True, name=current_node.name
            )

            process.refresh_current_node.assert_called_once_with(current_node.id)

            NodeRelationship.objects.build_relationship.assert_called_once_with(
                process.top_pipeline.id, current_node.id
            )

            hdl.assert_called_once_with(process, current_node, None)

            process.sleep.assert_not_called()

            self.assertEqual(process.current_node_id, current_node.id)

            FunctionSwitch.objects.is_frozen.reset_mock()
            Status.objects.transit.reset_mock()
            NodeRelationship.objects.build_relationship.reset_mock()
            hdl.reset_mock()

            # 6.2. test should sleep
            for should_return in (False, True):
                hdl.return_value = MockHandlerResult(
                    should_return=should_return,
                    should_sleep=True,
                    after_sleep_call=MagicMock(),
                    args=["token1", "token2"],
                    kwargs={"kwargs": "token3"},
                )

                current_node = IdentifyObject()
                process = MockPipelineProcess(
                    top_pipeline=PipelineObject(node=current_node),
                    destination_id=uniqid(),
                    current_node_id=current_node.id,
                )
                process.root_sleep_check = MagicMock(return_value=(False, states.RUNNING))
                process.subproc_sleep_check = MagicMock(return_value=(False, []))

                runtime.run_loop(process)

                process.destroy_and_wake_up_parent.assert_not_called()

                process.root_sleep_check.assert_called()

                process.subproc_sleep_check.assert_called()

                FunctionSwitch.objects.is_frozen.assert_called_once()

                process.freeze.assert_not_called()

                Status.objects.transit.assert_called_with(
                    id=current_node.id, to_state=states.RUNNING, start=True, name=str(current_node.__class__)
                )

                process.refresh_current_node.assert_called_once_with(current_node.id)

                NodeRelationship.objects.build_relationship.assert_called_once_with(
                    process.top_pipeline.id, current_node.id
                )

                hdl.assert_called_once_with(process, current_node, None)

                process.sleep.assert_called_once_with(adjust_status=True)

                hdl.return_value.after_sleep_call.assert_called_once_with("token1", "token2", kwargs="token3")

                self.assertEqual(process.current_node_id, current_node.id)

                FunctionSwitch.objects.is_frozen.reset_mock()
                Status.objects.transit.reset_mock()
                NodeRelationship.objects.build_relationship.reset_mock()
                hdl.reset_mock()

            # 6.3. test execute 3 node and return
            nodes = [IdentifyObject(), IdentifyObject(), IdentifyObject()]
            hdl.return_value = None
            hdl.side_effect = [
                MockHandlerResult(should_return=False, should_sleep=False, next_node=nodes[0]),
                MockHandlerResult(should_return=False, should_sleep=False, next_node=nodes[1]),
                MockHandlerResult(should_return=True, should_sleep=True, next_node=nodes[2]),
            ]

            current_node = IdentifyObject()
            process = MockPipelineProcess(
                top_pipeline=PipelineObject(
                    nodes={
                        current_node.id: current_node,
                        nodes[0].id: nodes[0],
                        nodes[1].id: nodes[1],
                        nodes[2].id: nodes[2],
                    }
                ),
                destination_id=uniqid(),
                current_node_id=current_node.id,
            )
            process.root_sleep_check = MagicMock(return_value=(False, states.RUNNING))
            process.subproc_sleep_check = MagicMock(return_value=(False, []))

            runtime.run_loop(process)

            process.destroy_and_wake_up_parent.assert_not_called()

            process.root_sleep_check.assert_has_calls([mock.call(), mock.call(), mock.call()])

            process.subproc_sleep_check.assert_has_calls([mock.call(), mock.call(), mock.call()])

            FunctionSwitch.objects.is_frozen.assert_has_calls([mock.call(), mock.call(), mock.call()])

            process.freeze.assert_not_called()

            Status.objects.transit.assert_has_calls(
                [
                    mock.call(
                        id=current_node.id, to_state=states.RUNNING, start=True, name=str(current_node.__class__)
                    ),
                    mock.call(id=nodes[0].id, to_state=states.RUNNING, start=True, name=str(current_node.__class__)),
                    mock.call(id=nodes[1].id, to_state=states.RUNNING, start=True, name=str(current_node.__class__)),
                ]
            )

            process.refresh_current_node.assert_has_calls(
                [mock.call(current_node.id), mock.call(nodes[0].id), mock.call(nodes[1].id)]
            )

            NodeRelationship.objects.build_relationship.assert_has_calls(
                [
                    mock.call(process.top_pipeline.id, current_node.id),
                    mock.call(process.top_pipeline.id, nodes[0].id),
                    mock.call(process.top_pipeline.id, nodes[1].id),
                ]
            )

            hdl.assert_has_calls(
                [
                    mock.call(process, current_node, None),
                    mock.call(process, nodes[0], None),
                    mock.call(process, nodes[1], None),
                ]
            )

            process.sleep.assert_called_once_with(adjust_status=True)

            self.assertEqual(process.current_node_id, nodes[1].id)

    @patch(PIPELINE_BUILD_RELATIONSHIP, MagicMock())
    @patch(PIPELINE_ENGINE_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=True, extra=MockStatus(loop=11))))
    @patch(PIPELINE_STATUS_FAIL, MagicMock())
    def __fail_with_node_reach_run_limit(self):
        with patch(PIPELINE_SETTING_RERUN_MAX_LIMIT, 10):
            current_node = IdentifyObject()
            process = MockPipelineProcess(
                top_pipeline=PipelineObject(node=current_node), destination_id=uniqid(), current_node_id=current_node.id
            )
            process.root_sleep_check = MagicMock(return_value=(False, states.RUNNING))
            process.subproc_sleep_check = MagicMock(return_value=(False, []))

            runtime.run_loop(process)

            process.destroy_and_wake_up_parent.assert_not_called()

            process.root_sleep_check.assert_called()

            process.subproc_sleep_check.assert_called()

            FunctionSwitch.objects.is_frozen.assert_called_once()

            process.freeze.assert_not_called()

            Status.objects.transit.assert_called_with(
                id=current_node.id, to_state=states.RUNNING, start=True, name=str(current_node.__class__)
            )

            Status.objects.fail.assert_called_once_with(current_node, "rerun times exceed max limit: 10")

            process.sleep.assert_called_once_with(adjust_status=True)

            process.refresh_current_node.assert_not_called()
