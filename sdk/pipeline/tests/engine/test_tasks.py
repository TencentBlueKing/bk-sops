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

import itertools

from django.test import TestCase

from pipeline.core.pipeline import Pipeline
from pipeline.engine import api, signals, states, tasks
from pipeline.engine.core import runtime, schedule
from pipeline.engine.models import NodeCeleryTask, NodeRelationship, ProcessCeleryTask, Status
from pipeline.tests.engine.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa


class EngineTaskTestCase(TestCase):
    def setUp(self):
        self.alive_process = MockPipelineProcess(top_pipeline=PipelineObject(node=ServiceActObject(interval=None)))
        self.not_alive_process = MockPipelineProcess(is_alive=False)
        self.get_alive_process = mock.MagicMock(return_value=self.alive_process)
        self.get_not_alive_process = mock.MagicMock(return_value=self.not_alive_process)
        self.transit_success = mock.MagicMock(return_value=MockActionResult(result=True))
        self.transit_fail = mock.MagicMock(return_value=MockActionResult(result=False))
        self.transit_fail_and_return_suspended = mock.MagicMock(
            return_value=MockActionResult(result=False, extra=FancyDict({"state": states.SUSPENDED}))
        )
        self.transit_fail_and_return_blocked = MagicMock(
            return_value=MockActionResult(result=False, extra=FancyDict({"state": states.BLOCKED}))
        )

    @mock.patch(ENGINE_RUN_LOOP, mock.MagicMock())
    def test_process_unfreeze(self):
        # alive process
        with mock.patch(PIPELINE_PROCESS_GET, self.get_alive_process):
            tasks.process_unfreeze(self.alive_process.id)

            self.get_alive_process.assert_called_with(id=self.alive_process.id)

            runtime.run_loop.assert_called_with(self.alive_process)

        runtime.run_loop.reset_mock()

        # dead process
        with mock.patch(PIPELINE_PROCESS_GET, self.get_not_alive_process):
            tasks.process_unfreeze(self.not_alive_process.id)

            self.get_not_alive_process.assert_called_with(id=self.not_alive_process.id)

            runtime.run_loop.assert_not_called()

    @mock.patch(ENGINE_RUN_LOOP, mock.MagicMock())
    @mock.patch(PIPELINE_STATUS_TRANSIT, mock.MagicMock())
    @mock.patch(PIPELINE_NODE_RELATIONSHIP_BUILD, mock.MagicMock())
    def test_start(self):
        # dead process
        with mock.patch(PIPELINE_PROCESS_GET, self.get_not_alive_process):
            tasks.start(self.not_alive_process.id)

            self.get_not_alive_process.assert_called_with(id=self.not_alive_process.id)

            Status.objects.transit.assert_not_called()

            NodeRelationship.objects.build_relationship.assert_not_called()

            runtime.run_loop.assert_not_called()

        # alive process
        with mock.patch(PIPELINE_PROCESS_GET, self.get_alive_process):
            # transit success
            with mock.patch(PIPELINE_STATUS_TRANSIT, self.transit_success):
                tasks.start(self.alive_process.id)

                self.get_alive_process.assert_called_with(id=self.alive_process.id)

                self.transit_success.assert_called_with(
                    self.alive_process.root_pipeline.id, states.RUNNING, is_pipeline=True, start=True
                )

                NodeRelationship.objects.build_relationship.assert_called_with(
                    self.alive_process.root_pipeline.id, self.alive_process.root_pipeline.id
                )

                runtime.run_loop.assert_called_with(self.alive_process)

            self.get_alive_process.reset_mock()
            self.transit_success.reset_mock()
            NodeRelationship.objects.build_relationship.reset_mock()
            runtime.run_loop.reset_mock()

            # transit failed
            with mock.patch(PIPELINE_STATUS_TRANSIT, self.transit_fail):
                tasks.start(self.alive_process.id)

                self.get_alive_process.assert_called_with(id=self.alive_process.id)

                self.transit_fail.assert_called_with(
                    self.alive_process.root_pipeline.id, states.RUNNING, is_pipeline=True, start=True
                )

                NodeRelationship.objects.build_relationship.assert_not_called()

                runtime.run_loop.assert_not_called()

    @mock.patch(ENGINE_RUN_LOOP, mock.MagicMock())
    def test_dispatch(self):
        # alive process
        with mock.patch(PIPELINE_PROCESS_GET, self.get_alive_process):
            tasks.dispatch(self.alive_process.id)

            self.get_alive_process.assert_called_with(id=self.alive_process.id)

            runtime.run_loop.assert_called_with(self.alive_process)

        self.get_not_alive_process.reset_mock()
        runtime.run_loop.reset_mock()

        # dead process
        with mock.patch(PIPELINE_PROCESS_GET, self.get_not_alive_process):
            tasks.dispatch(self.not_alive_process.id)

            self.get_not_alive_process.assert_called_with(id=self.not_alive_process.id)

            runtime.run_loop.assert_not_called()

    @mock.patch(ENGINE_RUN_LOOP, mock.MagicMock())
    @mock.patch(PIPELINE_STATUS_TRANSIT, mock.MagicMock())
    def test_process_wake_up(self):
        # dead process
        with mock.patch(PIPELINE_PROCESS_GET, self.get_not_alive_process):
            for current_node_id, call_from_child in itertools.product((uniqid(), None), (True, False)):
                self.get_not_alive_process.reset_mock()
                tasks.process_wake_up(
                    self.not_alive_process.id, current_node_id=current_node_id, call_from_child=call_from_child
                )

                self.get_not_alive_process.assert_called_with(id=self.not_alive_process.id)

                Status.objects.transit.assert_not_called()

                self.not_alive_process.wake_up.assert_not_called()

                runtime.run_loop.assert_not_called()

        # alive process
        with mock.patch(PIPELINE_PROCESS_GET, self.get_alive_process):
            # call from child
            tasks.process_wake_up(self.alive_process.id, current_node_id=None, call_from_child=True)

            self.get_alive_process.assert_called_with(id=self.alive_process.id)

            Status.objects.transit.assert_not_called()

            self.alive_process.wake_up.assert_called()

            self.assertIsNone(self.alive_process.current_node_id)

            runtime.run_loop.assert_called_with(self.alive_process)

            self.get_alive_process.reset_mock()
            self.alive_process.wake_up.reset_mock()
            runtime.run_loop.reset_mock()

            # has current_node_id
            current_node_id = uniqid()
            tasks.process_wake_up(self.alive_process.id, current_node_id=current_node_id, call_from_child=True)

            self.get_alive_process.assert_called_with(id=self.alive_process.id)

            Status.objects.transit.assert_not_called()

            self.alive_process.wake_up.assert_called()

            self.assertEqual(self.alive_process.current_node_id, current_node_id)

            runtime.run_loop.assert_called_with(self.alive_process)

            self.get_alive_process.reset_mock()
            self.alive_process.wake_up.reset_mock()
            runtime.run_loop.reset_mock()
            self.alive_process.current_node_id = None

            # not call from child

            with mock.patch(PIPELINE_STATUS_TRANSIT, self.transit_success):
                # transit success
                tasks.process_wake_up(self.alive_process.id, current_node_id=None, call_from_child=False)

                self.get_alive_process.assert_called_with(id=self.alive_process.id)

                self.transit_success.assert_called_with(
                    self.alive_process.root_pipeline.id, to_state=states.RUNNING, is_pipeline=True, unchanged_pass=True
                )

                self.alive_process.wake_up.assert_called()

                self.assertIsNone(self.alive_process.current_node_id)

                runtime.run_loop.assert_called_with(self.alive_process)

            self.get_alive_process.reset_mock()
            self.alive_process.wake_up.reset_mock()
            runtime.run_loop.reset_mock()

            with mock.patch(PIPELINE_STATUS_TRANSIT, self.transit_fail_and_return_suspended):
                # transit failed
                tasks.process_wake_up(self.alive_process.id, current_node_id=None, call_from_child=False)

                self.get_alive_process.assert_called_with(id=self.alive_process.id)

                self.transit_fail_and_return_suspended.assert_called_with(
                    self.alive_process.root_pipeline.id, to_state=states.RUNNING, is_pipeline=True, unchanged_pass=True
                )

                self.alive_process.wake_up.assert_not_called()

                self.assertIsNone(self.alive_process.current_node_id)

                runtime.run_loop.assert_not_called()

            with mock.patch(PIPELINE_STATUS_TRANSIT, self.transit_fail_and_return_blocked):
                # transit failed but in blocked state
                tasks.process_wake_up(self.alive_process.id, current_node_id=None, call_from_child=False)

                self.get_alive_process.assert_called_with(id=self.alive_process.id)

                self.transit_fail_and_return_blocked.assert_called_with(
                    self.alive_process.root_pipeline.id, to_state=states.RUNNING, is_pipeline=True, unchanged_pass=True
                )

                self.alive_process.wake_up.assert_called()

                self.assertIsNone(self.alive_process.current_node_id)

                runtime.run_loop.assert_called_with(self.alive_process)

    @mock.patch(ENGINE_RUN_LOOP, mock.MagicMock())
    def test_wake_up(self):
        # alive process
        with mock.patch(PIPELINE_PROCESS_GET, self.get_alive_process):
            tasks.wake_up(self.alive_process.id)

            self.get_alive_process.assert_called_with(id=self.alive_process.id)

            self.alive_process.wake_up.assert_called()

            runtime.run_loop.assert_called_with(self.alive_process)

        self.get_not_alive_process.reset_mock()
        self.alive_process.wake_up.reset_mock()
        runtime.run_loop.reset_mock()

        # dead process
        with mock.patch(PIPELINE_PROCESS_GET, self.get_not_alive_process):
            tasks.wake_up(self.not_alive_process.id)

            self.get_not_alive_process.assert_called_with(id=self.not_alive_process.id)

            self.not_alive_process.wake_up.assert_not_called()

            runtime.run_loop.assert_not_called()

    @mock.patch(ENGINE_TASKS_WAKE_UP_APPLY, mock.MagicMock(return_value=IdentifyObject(id="task_id")))
    @mock.patch(PIPELINE_CELERYTASK_BIND, mock.MagicMock())
    def test_batch_wake_up(self):
        process_id_list = [uniqid() for _ in range(5)]

        # transit success
        with mock.patch(PIPELINE_STATUS_TRANSIT, self.transit_success):
            tasks.batch_wake_up(process_id_list, self.alive_process.root_pipeline.id)

            self.transit_success.assert_called_with(
                self.alive_process.root_pipeline.id, to_state=states.RUNNING, is_pipeline=True
            )

            tasks.wake_up.apply_async.assert_has_calls([mock.call(args=[pid]) for pid in process_id_list])

            ProcessCeleryTask.objects.bind.assert_has_calls([mock.call(pid, "task_id") for pid in process_id_list])

        tasks.wake_up.apply_async.reset_mock()
        ProcessCeleryTask.objects.bind.reset_mock()

        # transit fail
        with mock.patch(PIPELINE_STATUS_TRANSIT, self.transit_fail):
            tasks.batch_wake_up(process_id_list, self.alive_process.root_pipeline.id)

            self.transit_fail.assert_called_with(
                self.alive_process.root_pipeline.id, to_state=states.RUNNING, is_pipeline=True
            )

            tasks.wake_up.apply_async.assert_not_called()

            ProcessCeleryTask.objects.bind.assert_not_called()

    @mock.patch(ENGINE_RUN_LOOP, mock.MagicMock())
    def test_wake_from_schedule(self):
        with mock.patch(PIPELINE_PROCESS_GET, self.get_alive_process):
            tasks.wake_from_schedule(self.alive_process.id, None)

            self.get_alive_process.assert_called_with(id=self.alive_process.id)

            self.alive_process.wake_up.assert_called()

            self.assertEqual(self.alive_process.current_node_id, self.alive_process.top_pipeline.node(None).next().id)

            runtime.run_loop.assert_called_with(self.alive_process)

    @mock.patch(ENGINE_SCHEDULE, mock.MagicMock())
    def test_service_schedule(self):
        process_id = uniqid()
        schedule_id = uniqid()
        data_id = None
        tasks.service_schedule(process_id, schedule_id, data_id)
        schedule.schedule.assert_called_with(process_id, schedule_id, data_id)

    @mock.patch(PIPELINE_NODE_CELERYTASK_DESTROY, mock.MagicMock())
    @mock.patch(ENGINE_API_FORCED_FAIL, mock.MagicMock())
    @mock.patch(ENGINE_ACTIVITY_FAIL_SIGNAL, mock.MagicMock())
    def test_node_timeout_check(self):

        # state for return None
        with mock.patch(PIPELINE_STATUS_STATE_FOR, mock.MagicMock(return_value=None)):
            node_id = uniqid()
            version = uniqid()
            root_pipeline_id = uniqid()
            tasks.node_timeout_check(node_id, version, root_pipeline_id)

            NodeCeleryTask.objects.destroy.assert_called_with(node_id)

            Status.objects.state_for.assert_called_with(node_id, version=version, may_not_exist=True)

            api.forced_fail.assert_not_called()

        for state_not_running in states.ALL_STATES.difference({states.RUNNING}):
            NodeCeleryTask.objects.destroy.reset_mock()
            api.forced_fail.reset_mock()
            # state for return other values
            with mock.patch(PIPELINE_STATUS_STATE_FOR, mock.MagicMock(return_value=state_not_running)):
                node_id = uniqid()
                version = uniqid()
                root_pipeline_id = uniqid()
                tasks.node_timeout_check(node_id, version, root_pipeline_id)

                NodeCeleryTask.objects.destroy.assert_called_with(node_id)

                Status.objects.state_for.assert_called_with(node_id, version=version, may_not_exist=True)

                api.forced_fail.assert_not_called()

        NodeCeleryTask.objects.destroy.reset_mock()
        api.forced_fail.reset_mock()

        # state for return RUNNING
        with mock.patch(PIPELINE_STATUS_STATE_FOR, mock.MagicMock(return_value=states.RUNNING)):
            # force fail success
            with mock.patch(ENGINE_API_FORCED_FAIL, mock.MagicMock(return_value=MockActionResult(result=True))):
                node_id = uniqid()
                version = uniqid()
                root_pipeline_id = uniqid()
                tasks.node_timeout_check(node_id, version, root_pipeline_id)

                NodeCeleryTask.objects.destroy.assert_called_with(node_id)

                Status.objects.state_for.assert_called_with(node_id, version=version, may_not_exist=True)

                api.forced_fail.assert_called_with(node_id, kill=True, ex_data="node execution timeout")

                signals.activity_failed.send.assert_called_with(
                    sender=Pipeline, pipeline_id=root_pipeline_id, pipeline_activity_id=node_id
                )

            NodeCeleryTask.objects.destroy.reset_mock()
            Status.objects.state_for.reset_mock()
            api.forced_fail.reset_mock()
            signals.activity_failed.send.reset_mock()

            # force fail failed
            with mock.patch(ENGINE_API_FORCED_FAIL, mock.MagicMock(return_value=MockActionResult(result=False))):
                node_id = uniqid()
                version = uniqid()
                root_pipeline_id = uniqid()
                tasks.node_timeout_check(node_id, version, root_pipeline_id)

                NodeCeleryTask.objects.destroy.assert_called_with(node_id)

                Status.objects.state_for.assert_called_with(node_id, version=version, may_not_exist=True)

                api.forced_fail.assert_called_with(node_id, kill=True, ex_data="node execution timeout")

                signals.activity_failed.send.assert_not_called()
