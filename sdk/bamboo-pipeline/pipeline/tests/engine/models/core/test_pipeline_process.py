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

import traceback

from django.test import TestCase

from pipeline.django_signal_valve import valve
from pipeline.engine import exceptions, signals, states
from pipeline.engine.models import Status
from pipeline.engine.models.core import PipelineModel, PipelineProcess, ProcessSnapshot, SubProcessRelationship
from pipeline.engine.utils import Stack
from pipeline.tests.mock_settings import *  # noqa

from ..mock import *  # noqa

valve.unload_valve_function()


class TestPipelineProcess(TestCase):
    def test_prepare_for_pipeline(self):
        pipeline = PipelineObject()

        process = PipelineProcess.objects.prepare_for_pipeline(pipeline)
        self.assertEqual(len(process.id), 32)
        self.assertEqual(process.root_pipeline_id, pipeline.id)
        self.assertEqual(process.current_node_id, pipeline.start_event.id)
        self.assertIsNotNone(process.snapshot)
        self.assertEqual(process.top_pipeline.id, pipeline.id)

    def test_fork_child(self):
        context = MockContext()
        context.clear_change_keys = MagicMock()
        pipeline = PipelineObject(context=context)
        current_node_id = uniqid()
        destination_id = uniqid()

        process = PipelineProcess.objects.prepare_for_pipeline(pipeline)
        child = PipelineProcess.objects.fork_child(
            parent=process, current_node_id=current_node_id, destination_id=destination_id
        )
        self.assertEqual(len(child.id), 32)
        self.assertEqual(process.root_pipeline_id, child.root_pipeline_id)
        self.assertEqual(len(child.pipeline_stack), 1)
        self.assertEqual(child.top_pipeline.id, process.top_pipeline.id)
        self.assertEqual(process.children, child.children)
        self.assertEqual(process.root_pipeline.id, child.root_pipeline.id)
        self.assertEqual(process.subprocess_stack, child.subprocess_stack)
        self.assertEqual(process.id, child.parent_id)
        self.assertEqual(child.current_node_id, current_node_id)
        self.assertEqual(child.destination_id, destination_id)
        self.assertEqual(context.clear_change_keys.call_count, 1)
        child.top_pipeline.prune.assert_called_once_with(current_node_id, destination_id)

    @patch(SIGNAL_VALVE_SEND, MagicMock())
    def test_process_ready(self):
        from pipeline.django_signal_valve.valve import send

        process_id = uniqid()
        current_node_id = uniqid()

        PipelineProcess.objects.process_ready(process_id)
        send.assert_called_with(
            signals,
            "process_ready",
            sender=PipelineProcess,
            process_id=process_id,
            current_node_id=None,
            call_from_child=False,
        )
        PipelineProcess.objects.process_ready(process_id, current_node_id, False)
        send.assert_called_with(
            signals,
            "process_ready",
            sender=PipelineProcess,
            process_id=process_id,
            current_node_id=current_node_id,
            call_from_child=False,
        )
        PipelineProcess.objects.process_ready(process_id, current_node_id, True)
        send.assert_called_with(
            signals,
            "process_ready",
            sender=PipelineProcess,
            process_id=process_id,
            current_node_id=current_node_id,
            call_from_child=True,
        )

    @patch(SIGNAL_VALVE_SEND, MagicMock())
    def test_batch_process_ready(self):
        from pipeline.django_signal_valve.valve import send

        process_id_list = [uniqid(), uniqid(), uniqid()]
        pipeline_id = uniqid()

        PipelineProcess.objects.batch_process_ready(process_id_list, pipeline_id)
        send.assert_called_with(
            signals,
            "batch_process_ready",
            sender=PipelineProcess,
            process_id_list=process_id_list,
            pipeline_id=pipeline_id,
        )

    @patch(SIGNAL_VALVE_SEND, MagicMock())
    def test_child_process_ready(self):
        from pipeline.django_signal_valve.valve import send

        child_id = uniqid()

        PipelineProcess.objects.child_process_ready(child_id)
        send.assert_called_with(signals, "child_process_ready", sender=PipelineProcess, child_id=child_id)

    def test_properties(self):
        process = PipelineProcess.objects.create()
        pipeline_stack = Stack(["pipeline1", "pipeline2"])
        subprocess_stack = Stack(["subprocess1", "subprocess2"])
        children = ["child1", "child2"]
        root_pipeline = "root_pipeline"
        mock_snapshot = ProcessSnapshot.objects.create_snapshot(
            pipeline_stack=pipeline_stack,
            children=children,
            root_pipeline=root_pipeline,
            subprocess_stack=subprocess_stack,
        )
        process.snapshot = mock_snapshot
        self.assertEqual(process.pipeline_stack, pipeline_stack)
        self.assertEqual(process.children, children)
        self.assertEqual(process.root_pipeline, root_pipeline)
        self.assertEqual(process.top_pipeline, pipeline_stack.top())
        self.assertEqual(process.subprocess_stack, subprocess_stack)

    def test_push_pipeline(self):
        pipeline = "pipeline_%s" % uniqid()
        subproc_pipeline = PipelineObject()
        process = PipelineProcess.objects.create()
        pipeline_stack = Stack(["pipeline1", "pipeline2"])
        subprocess_stack = Stack(["subprocess1", "subprocess2"])
        children = ["child1", "child2"]
        root_pipeline = "root_pipeline"
        mock_snapshot = ProcessSnapshot.objects.create_snapshot(
            pipeline_stack=pipeline_stack,
            children=children,
            root_pipeline=root_pipeline,
            subprocess_stack=subprocess_stack,
        )
        process.snapshot = mock_snapshot
        process.id = uniqid()

        process.push_pipeline(pipeline, is_subprocess=False)
        self.assertEqual(process.top_pipeline, pipeline)

        process.push_pipeline(subproc_pipeline, is_subprocess=True)
        self.assertEqual(process.top_pipeline, subproc_pipeline)
        self.assertTrue(
            SubProcessRelationship.objects.filter(subprocess_id=subproc_pipeline.id, process_id=process.id).exists()
        )

    def test_pop_pipeline(self):
        subproc_pipeline = PipelineObject()
        process = PipelineProcess.objects.create()
        pipeline_stack = Stack(["pipeline1", "pipeline2"])
        subprocess_stack = Stack(["subprocess1", "subprocess2"])
        children = ["child1", "child2"]
        root_pipeline = "root_pipeline"
        mock_snapshot = ProcessSnapshot.objects.create_snapshot(
            pipeline_stack=pipeline_stack,
            children=children,
            root_pipeline=root_pipeline,
            subprocess_stack=subprocess_stack,
        )
        process.snapshot = mock_snapshot
        process.id = uniqid()

        process.push_pipeline(subproc_pipeline, is_subprocess=True)
        self.assertEqual(process.top_pipeline, subproc_pipeline)
        self.assertTrue(
            SubProcessRelationship.objects.filter(subprocess_id=subproc_pipeline.id, process_id=process.id).exists()
        )

        pop_pipeline = process.pop_pipeline()
        self.assertEqual(pop_pipeline.id, subproc_pipeline.id)
        self.assertFalse(
            SubProcessRelationship.objects.filter(subprocess_id=subproc_pipeline.id, process_id=process.id).exists()
        )

        pop_pipeline = process.pop_pipeline()
        self.assertEqual(pop_pipeline, "pipeline2")

        pop_pipeline = process.pop_pipeline()
        self.assertEqual(pop_pipeline, "pipeline1")

    def test_join(self):
        children = [IdentifyObject(), IdentifyObject(), IdentifyObject()]
        mock_snapshot = ProcessSnapshot.objects.create_snapshot(
            pipeline_stack=Stack(), children=[], root_pipeline="root_pipeline", subprocess_stack=Stack()
        )
        process = PipelineProcess.objects.create()
        process.snapshot = mock_snapshot

        process.join(children)
        self.assertEqual(process.need_ack, len(children))
        for i in range(len(children)):
            self.assertEqual(process.children[i], children[i].id)

    def test_root_sleep_check(self):
        def return_suspended(*args, **kwargs):
            return states.SUSPENDED

        def return_revoked(*args, **kwargs):
            return states.REVOKED

        def return_blocked(*args, **kwargs):
            return states.BLOCKED

        another_status = MagicMock()
        status = [states.CREATED, states.READY, states.RUNNING, states.FINISHED, states.FAILED]
        another_status.side_effect = status

        mock_snapshot = ProcessSnapshot.objects.create_snapshot(
            pipeline_stack=Stack(), children=[], root_pipeline=IdentifyObject(), subprocess_stack=Stack()
        )
        process = PipelineProcess.objects.create()
        process.snapshot = mock_snapshot

        with mock.patch(PIPELINE_STATUS_STATE_FOR, return_suspended):
            self.assertEqual(process.root_sleep_check(), (True, states.SUSPENDED))

        with mock.patch(PIPELINE_STATUS_STATE_FOR, return_revoked):
            self.assertEqual(process.root_sleep_check(), (True, states.REVOKED))

        with mock.patch(PIPELINE_STATUS_STATE_FOR, return_blocked):
            self.assertEqual(process.root_sleep_check(), (True, states.BLOCKED))
            process.parent_id = "parent_id"
            self.assertEqual(process.root_sleep_check(), (False, states.BLOCKED))

        with mock.patch(PIPELINE_STATUS_STATE_FOR, another_status):
            for s in status:
                self.assertEqual(process.root_sleep_check(), (False, s))

    def test_subproc_sleep_check(self):
        mock_snapshot = ProcessSnapshot.objects.create_snapshot(
            pipeline_stack=Stack(), children=[], root_pipeline=IdentifyObject(), subprocess_stack=Stack([1, 2, 3, 4])
        )
        process = PipelineProcess.objects.create()
        process.snapshot = mock_snapshot

        def return_all_running(*args, **kwargs):
            return [
                StatusObject(id=1, state=states.RUNNING),
                StatusObject(id=2, state=states.RUNNING),
                StatusObject(id=3, state=states.RUNNING),
                StatusObject(id=4, state=states.RUNNING),
            ]

        def return_one_suspended(*args, **kwargs):
            return [
                StatusObject(id=1, state=states.RUNNING),
                StatusObject(id=2, state=states.SUSPENDED),
                StatusObject(id=3, state=states.RUNNING),
                StatusObject(id=4, state=states.RUNNING),
            ]

        def return_first_suspended(*args, **kwargs):
            return [
                StatusObject(id=1, state=states.SUSPENDED),
                StatusObject(id=2, state=states.RUNNING),
                StatusObject(id=3, state=states.RUNNING),
                StatusObject(id=4, state=states.RUNNING),
            ]

        def return_last_suspended(*args, **kwargs):
            return [
                StatusObject(id=1, state=states.RUNNING),
                StatusObject(id=2, state=states.RUNNING),
                StatusObject(id=3, state=states.RUNNING),
                StatusObject(id=4, state=states.SUSPENDED),
            ]

        with mock.patch(PIPELINE_STATUS_FILTER, return_all_running):
            self.assertEqual(process.subproc_sleep_check(), (False, [1, 2, 3, 4]))

        with mock.patch(PIPELINE_STATUS_FILTER, return_one_suspended):
            self.assertEqual(process.subproc_sleep_check(), (True, [1]))

        with mock.patch(PIPELINE_STATUS_FILTER, return_first_suspended):
            self.assertEqual(process.subproc_sleep_check(), (True, []))

        with mock.patch(PIPELINE_STATUS_FILTER, return_last_suspended):
            self.assertEqual(process.subproc_sleep_check(), (True, [1, 2, 3]))

    @patch(PIPELINE_CELERYTASK_UNBIND, MagicMock())
    def test_freeze(self):
        from pipeline.engine.models import ProcessCeleryTask

        pipeline = PipelineObject()

        process = PipelineProcess.objects.prepare_for_pipeline(pipeline)
        self.assertFalse(process.is_frozen)

        process.freeze()
        self.assertTrue(process.is_frozen)
        process.refresh_from_db()
        self.assertTrue(process.is_frozen)

        ProcessCeleryTask.objects.unbind.assert_called_with(process.id)

    @patch(SIGNAL_VALVE_SEND, MagicMock())
    def test_unfreeze(self):
        from pipeline.django_signal_valve.valve import send

        pipeline = PipelineObject()
        process = PipelineProcess.objects.prepare_for_pipeline(pipeline)

        process.freeze()
        process.unfreeze()
        self.assertFalse(process.is_frozen)
        process.refresh_from_db()
        self.assertFalse(process.is_frozen)

        send.assert_called_with(signals, "process_unfreeze", sender=PipelineProcess, process_id=process.id)

    @patch(PIPELINE_PROCESS_ADJUST_STATUS, MagicMock())
    @patch(PIPELINE_CELERYTASK_UNBIND, MagicMock())
    def test_sleep(self):
        from pipeline.engine.models import ProcessCeleryTask

        pipeline = PipelineObject()
        process = PipelineProcess.objects.prepare_for_pipeline(pipeline)

        process.sleep(do_not_save=True, adjust_status=True)
        process.adjust_status.assert_called_with(None)
        ProcessCeleryTask.objects.unbind.assert_not_called()
        process.adjust_status.reset_mock()

        process.sleep(do_not_save=True, adjust_status=True, adjust_scope=[1, 2, 3, 4])
        process.adjust_status.assert_called_with([1, 2, 3, 4])
        ProcessCeleryTask.objects.unbind.assert_not_called()
        process.adjust_status.reset_mock()

        process.sleep(do_not_save=False, adjust_status=False)
        process.adjust_status.assert_not_called()
        self.assertTrue(process.sleep)
        ProcessCeleryTask.objects.unbind.assert_called_with(process.id)

        with mock.patch(PIPELINE_PROCESS_CHILD_PROCESS_READY, MagicMock()):
            process = PipelineProcess.objects.prepare_for_pipeline(pipeline)
            mock_snapshot = ProcessSnapshot.objects.create_snapshot(
                pipeline_stack=Stack(),
                children=[1, 2, 3, 4],
                root_pipeline=IdentifyObject(),
                subprocess_stack=Stack([]),
            )
            process.snapshot = mock_snapshot
            process.sleep(do_not_save=False, adjust_status=False)
            PipelineProcess.objects.child_process_ready.assert_has_calls(
                [mock.call(1), mock.call(2), mock.call(3), mock.call(4)]
            )

    @patch(PIPELINE_STATUS_BATCH_TRANSIT, MagicMock())
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock())
    def test_adjust_status(self):
        process = PipelineProcess.objects.create()
        mock_snapshot = ProcessSnapshot.objects.create_snapshot(
            pipeline_stack=Stack(),
            children=[],
            root_pipeline=IdentifyObject(id="root_pipeline_id"),
            subprocess_stack=Stack([1, 2, 3, 4]),
        )
        process.snapshot = mock_snapshot
        process.current_node_id = "current_node_id"

        def return_suspended_for_node(id, may_not_exist=False):
            if id == "current_node_id":
                return states.SUSPENDED

        def return_failed_for_node(id, may_not_exist=False):
            if id == "current_node_id":
                return states.FAILED

        def return_suspended_for_root_pipeline(id, may_not_exist=False):
            if id == "root_pipeline_id":
                return states.SUSPENDED

        def return_none_for_node(*args, **kwargs):
            return None

        def return_empty_list_for_subproc(subprocess_stack):
            return []

        def return_all_running_for_subproc(subprocess_stack):
            return [states.RUNNING, states.RUNNING, states.RUNNING, states.RUNNING]

        def return_last_suspended_for_subproc(subprocess_stack):
            return [states.RUNNING, states.RUNNING, states.RUNNING, states.SUSPENDED]

        def return_one_suspended_for_subproc(subprocess_stack):
            return [states.RUNNING, states.SUSPENDED, states.RUNNING, states.RUNNING]

        node_state_possibility = [return_suspended_for_node, return_failed_for_node]

        with mock.patch(PIPELINE_STATUS_STATES_FOR, return_empty_list_for_subproc):
            for case in node_state_possibility:
                with mock.patch(PIPELINE_STATUS_STATE_FOR, case):
                    process.adjust_status()
                    Status.objects.batch_transit.assert_called_with(
                        id_list=[1, 2, 3, 4], state=states.BLOCKED, from_state=states.RUNNING
                    )
                    Status.objects.transit.assert_called_with(
                        "root_pipeline_id", to_state=states.BLOCKED, is_pipeline=True
                    )
                    Status.objects.batch_transit.reset_mock()
                    Status.objects.transit.reset_mock()

            with mock.patch(PIPELINE_STATUS_STATE_FOR, return_suspended_for_root_pipeline):
                process.adjust_status()
                Status.objects.batch_transit.assert_called_with(
                    id_list=[1, 2, 3, 4], state=states.SUSPENDED, from_state=states.RUNNING
                )
                Status.objects.batch_transit.reset_mock()

        with mock.patch(PIPELINE_STATUS_STATE_FOR, return_none_for_node):
            with mock.patch(PIPELINE_STATUS_STATES_FOR, return_all_running_for_subproc):
                process.adjust_status()
                Status.objects.batch_transit.assert_not_called()

            with mock.patch(PIPELINE_STATUS_STATES_FOR, return_last_suspended_for_subproc):
                process.adjust_status(adjust_scope=[1, 2, 3])
                Status.objects.batch_transit.assert_called_with(
                    id_list=[1, 2, 3], state=states.BLOCKED, from_state=states.RUNNING
                )
                Status.objects.batch_transit.reset_mock()

            with mock.patch(PIPELINE_STATUS_STATES_FOR, return_one_suspended_for_subproc):
                process.adjust_status(adjust_scope=[1])
                Status.objects.batch_transit.assert_called_with(
                    id_list=[1], state=states.BLOCKED, from_state=states.RUNNING
                )
                Status.objects.batch_transit.reset_mock()

    def test_wake_up(self):
        process = PipelineProcess.objects.create()
        process.is_sleep = True
        process.save()

        self.assertTrue(process.is_sleep)
        process.wake_up()
        self.assertFalse(process.is_sleep)

    @patch(PIPELINE_CELERYTASK_DESTROY, MagicMock())
    def test_destroy(self):
        from pipeline.engine.models import ProcessCeleryTask

        process = PipelineProcess.objects.create()
        process.id = uniqid()
        process.current_node_id = "current_node_id"

        mock_snapshot = ProcessSnapshot.objects.create_snapshot(
            pipeline_stack=Stack(), children=[1, 2, 3, 4], root_pipeline=IdentifyObject(), subprocess_stack=Stack([])
        )
        mock_snapshot.delete = MagicMock()
        process.snapshot = mock_snapshot

        process.destroy()
        self.assertFalse(process.is_alive)
        self.assertEqual(process.current_node_id, "")
        self.assertIsNone(process.snapshot)
        mock_snapshot.delete.assert_called()
        ProcessCeleryTask.objects.destroy.assert_called_with(process.id)

    def test_save(self):
        process = PipelineProcess.objects.create()
        mock_snapshot = ProcessSnapshot.objects.create_snapshot(
            pipeline_stack=Stack(), children=[1, 2, 3, 4], root_pipeline=IdentifyObject(), subprocess_stack=Stack([])
        )
        mock_snapshot.save = MagicMock()
        process.snapshot = mock_snapshot

        process.save(save_snapshot=False)
        mock_snapshot.save.assert_not_called()
        process.save(save_snapshot=True)
        mock_snapshot.save.assert_called()
        mock_snapshot.save.reset_mock()
        process.save()
        mock_snapshot.save.assert_called()

    def test_blocked_by_failure_or_suspended(self):
        process = PipelineProcess.objects.create()
        mock_snapshot = ProcessSnapshot.objects.create_snapshot(
            pipeline_stack=Stack(), children=[], root_pipeline=IdentifyObject(), subprocess_stack=Stack([])
        )
        process.snapshot = mock_snapshot

        def return_suspended(*args, **kwargs):
            return states.SUSPENDED

        def return_failed(*args, **kwargs):
            return states.FAILED

        def return_none(*args, **kwargs):
            return None

        class MockChild(object):
            def __init__(self, failed=False, suspended=False):
                self.failed = failed
                self.suspended = suspended

            def blocked_by_failure_or_suspended(self):
                return self.failed or self.suspended

        def return_child_no_anomaly(*args, **kwargs):
            return [MockChild(), MockChild(), MockChild()]

        def return_child_has_failed(*args, **kwargs):
            return [MockChild(), MockChild(), MockChild(failed=True)]

        def return_child_has_suspended(*args, **kwargs):
            return [MockChild(), MockChild(), MockChild(suspended=True)]

        process.is_sleep = False
        self.assertFalse(process.blocked_by_failure_or_suspended())

        # 当前节点已经执行失败
        with mock.patch(PIPELINE_STATUS_STATE_FOR, return_failed):
            process.is_sleep = True
            self.assertTrue(process.blocked_by_failure_or_suspended())

        # 当前节点被暂停
        with mock.patch(PIPELINE_STATUS_STATE_FOR, return_suspended):
            process.is_sleep = True
            self.assertTrue(process.blocked_by_failure_or_suspended())

        # 整个流程进入了 SUSPENDED 状态，未开始执行下一个节点
        with mock.patch(PIPELINE_STATUS_STATE_FOR, return_none):
            process.is_sleep = True
            self.assertFalse(process.blocked_by_failure_or_suspended())

            mock_snapshot = ProcessSnapshot.objects.create_snapshot(
                pipeline_stack=Stack(), children=[1, 2, 3], root_pipeline=IdentifyObject(), subprocess_stack=Stack([])
            )
            process.snapshot = mock_snapshot

            # 子进程都没有异常
            with mock.patch(PIPELINE_PROCESS_FILTER, return_child_no_anomaly):
                process.is_sleep = True
                self.assertFalse(process.blocked_by_failure_or_suspended())

            # 子进程中存在失败的进程
            with mock.patch(PIPELINE_PROCESS_FILTER, return_child_has_failed):
                process.is_sleep = True
                self.assertTrue(process.blocked_by_failure_or_suspended())

            # 子进程中存在暂停的进程
            with mock.patch(PIPELINE_PROCESS_FILTER, return_child_has_suspended):
                process.is_sleep = True
                self.assertTrue(process.blocked_by_failure_or_suspended())

    def test_sync_with_children(self):
        outputs = {"output_key": "output_value"}
        variables = {"variable_key": "varaiable_value"}

        process = PipelineProcess.objects.create()
        context = Object()
        context.update_global_var = MagicMock()
        context.sync_change = MagicMock()

        data = Object()
        data.update_outputs = MagicMock()

        mock_snapshot = ProcessSnapshot(
            data={
                "_pipeline_stack": Stack([PipelineObject(context=context, data=data)]),
                "_children": [1, 2, 3, 4],
                "_root_pipeline": IdentifyObject(),
                "_subprocess_stack": Stack([]),
            }
        )
        process.snapshot = mock_snapshot
        process.clean_children = MagicMock()

        def return_none(*args, **kwargs):
            return None

        def return_mock(id):
            if id.endswith("data"):
                return DataObject(outputs=outputs)
            if id.endswith("context"):
                return ContextObject(variables=variables)

        with mock.patch(PIPELINE_ENGINE_CORE_DATA_GET_OBJECT, return_none):
            self.assertRaises(exceptions.ChildDataSyncError, process.sync_with_children)

        with mock.patch(PIPELINE_ENGINE_CORE_DATA_GET_OBJECT, return_mock):
            process.sync_with_children()
            context.sync_change.assert_called()
            data.update_outputs.assert_called_with(outputs)
            process.clean_children.assert_called()

    @patch(PIPELINE_ENGINE_CORE_DATA_SET_OBJECT, MagicMock())
    @patch(PIPELINE_PROCESS_BLOCKED_BY_FAILURE, MagicMock())
    @patch(PIPELINE_PROCESS_DESTROY, MagicMock())
    @patch(PIPELINE_PROCESS_PROCESS_READY, MagicMock())
    @patch(PIPELINE_STATUS_BATCH_TRANSIT, MagicMock())
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock())
    def test_destroy_and_wake_up_parent(self):
        context = MockContext()
        context.clear_change_keys = MagicMock()
        pipeline = PipelineObject(context=context)

        process = PipelineProcess.objects.prepare_for_pipeline(pipeline)
        children = []
        for i in range(3):
            children.append(process.__class__.objects.fork_child(process, "current_node_id", "destination_id"))
        process.join(children)

        # def worker(child):
        #     child.destroy_and_wake_up_parent(child.destination_id)

        for child in children:
            child.destroy_and_wake_up_parent(child.destination_id)
            # sys_processes.append(Process(target=worker, args=(child,)))

        # for p in sys_processes:
        #     p.start()
        #
        # for p in sys_processes:
        #     p.join()

        process.refresh_from_db()
        self.assertEqual(process.need_ack, -1)
        self.assertEqual(process.ack_num, 0)
        self.assertEqual(PipelineProcess.blocked_by_failure_or_suspended.call_count, 2)
        PipelineProcess.objects.process_ready.assert_called_once()
        self.assertEqual(PipelineProcess.destroy.call_count, 3)

    def test__context_key(self):
        process = PipelineProcess.objects.create()
        process.id = uniqid()
        self.assertEqual(process._context_key(), "{}_context".format(process.id))
        self.assertEqual(process._context_key(process_id="another_id"), "{}_context".format("another_id"))

    def test__data_key(self):
        process = PipelineProcess.objects.create()
        process.id = uniqid()
        self.assertEqual(process._data_key(), "{}_data".format(process.id))
        self.assertEqual(process._data_key(process_id="another_id"), "{}_data".format("another_id"))

    def test_can_be_waked(self):
        process = PipelineProcess.objects.create()

        process.is_sleep = False
        process.is_alive = False
        self.assertFalse(process.can_be_waked())
        process.is_sleep = True
        process.is_alive = False
        self.assertFalse(process.can_be_waked())
        process.is_sleep = False
        process.is_alive = True
        self.assertFalse(process.can_be_waked())

        process.is_sleep = True
        process.is_alive = True
        process.need_ack = 3
        process.ack_num = 2
        self.assertFalse(process.can_be_waked())

        process.need_ack = 3
        process.ack_num = 3
        self.assertTrue(process.can_be_waked())
        process.need_ack = -1
        self.assertTrue(process.can_be_waked())

    @patch(PIPELINE_ENGINE_CORE_DATA_DEL_OBJECT, MagicMock())
    def test_clean_children(self):
        from pipeline.engine.core.data import del_object

        mock_snapshot = ProcessSnapshot(
            data={
                "_pipeline_stack": Stack(),
                "_children": ["1", "2", "3"],
                "_root_pipeline": IdentifyObject(),
                "_subprocess_stack": Stack([]),
            }
        )
        mock_snapshot.clean_children = MagicMock()
        mock_snapshot.save = MagicMock()

        process = PipelineProcess.objects.create()
        process.snapshot = mock_snapshot

        process.clean_children()
        del_object.assert_has_calls(
            [
                mock.call(process._context_key("1")),
                mock.call(process._data_key("1")),
                mock.call(process._context_key("2")),
                mock.call(process._data_key("2")),
                mock.call(process._context_key("3")),
                mock.call(process._data_key("3")),
            ]
        )
        mock_snapshot.clean_children.assert_called()
        mock_snapshot.save.assert_called()

    @patch(PIPELINE_STATUS_FAIL, MagicMock())
    @patch(PIPELINE_STATUS_RAW_FAIL, MagicMock())
    def test_exit_gracefully(self):
        mock_snapshot = ProcessSnapshot(
            data={
                "_pipeline_stack": Stack(),
                "_children": ["1", "2", "3"],
                "_root_pipeline": PipelineObject(),
                "_subprocess_stack": Stack([]),
            }
        )

        process = PipelineProcess.objects.create()
        process.snapshot = mock_snapshot
        process.sleep = MagicMock()
        e = Exception("test")

        process.current_node_id = uniqid()
        process.exit_gracefully(e)
        Status.objects.fail.assert_called_with(process.current_node_id, ex_data=traceback.format_exc())
        Status.objects.raw_fail.assert_not_called()
        process.sleep.assert_called_with(adjust_status=True)

        Status.objects.fail.reset_mock()
        process.sleep.reset_mock()

        # when stack is not empty
        mock_snapshot.data["_pipeline_stack"] = Stack([PipelineObject()])
        process.current_node_id = uniqid()
        process.exit_gracefully(e)
        Status.objects.fail.assert_called_with(process.current_node_id, ex_data=traceback.format_exc())
        Status.objects.raw_fail.assert_not_called()
        process.sleep.assert_called_with(adjust_status=True)

        Status.objects.fail.reset_mock()
        process.sleep.reset_mock()

        # when current_node is none
        top_pipeline = PipelineObject()
        top_pipeline.node = MagicMock(return_value=None)
        mock_snapshot.data["_pipeline_stack"] = Stack([top_pipeline])
        process.current_node_id = uniqid()
        process.exit_gracefully(e)
        Status.objects.fail.assert_not_called()
        Status.objects.raw_fail.assert_called_with(process.current_node_id, ex_data=traceback.format_exc())
        process.sleep.assert_called_with(adjust_status=True)

    def test_refresh_current_node(self):
        node_id = uniqid()
        process = PipelineProcess.objects.create()
        process.refresh_current_node(node_id)
        process.refresh_from_db()
        self.assertEqual(process.current_node_id, node_id)

    @patch(PIPELINE_STATUS_BATCH_TRANSIT, MagicMock())
    def test_revoke_subprocess(self):
        mock_snapshot = ProcessSnapshot(
            data={
                "_pipeline_stack": Stack(),
                "_children": [],
                "_root_pipeline": PipelineObject(),
                "_subprocess_stack": Stack([1, 2, 3, 4]),
            }
        )

        process = PipelineProcess.objects.create(id=uniqid())
        process.snapshot = mock_snapshot
        process.sleep = MagicMock()

        process.revoke_subprocess()
        Status.objects.batch_transit.assert_called_with(id_list=[1, 2, 3, 4], state=states.REVOKED)

        child_1 = Object()
        child_2 = Object()
        child_3 = Object()
        child_1.revoke_subprocess = MagicMock()
        child_2.revoke_subprocess = MagicMock()
        child_3.revoke_subprocess = MagicMock()

        def get_child(id):
            return {1: child_1, 2: child_2, 3: child_3}[id]

        mock_snapshot.data["_children"] = [1, 2, 3]

        with mock.patch(PIPELINE_PROCESS_GET, get_child):
            process.revoke_subprocess()
            Status.objects.batch_transit.assert_called_with(id_list=[1, 2, 3, 4], state=states.REVOKED)
            child_1.revoke_subprocess.assert_called()
            child_2.revoke_subprocess.assert_called()
            child_3.revoke_subprocess.assert_called()

        # test when subprocess_stack and children return None
        process = PipelineProcess.objects.create(id=uniqid())
        self.assertIsNone(process.subprocess_stack)
        self.assertIsNone(process.children)
        process.revoke_subprocess()

    @patch(PIPELINE_PROCESS_DESTROY, MagicMock())
    def test_destroy_all(self):
        mock_snapshot = ProcessSnapshot(
            data={
                "_pipeline_stack": Stack(),
                "_children": [],
                "_root_pipeline": PipelineObject(),
                "_subprocess_stack": Stack([]),
            }
        )
        process = PipelineProcess.objects.create()
        process.snapshot = mock_snapshot
        process.is_alive = False
        process.destroy_all()
        process.destroy.assert_not_called()

        process.is_alive = True
        process.destroy_all()
        process.destroy.assert_called()
        process.destroy.reset_mock()

        mock_snapshot.data["_children"] = [1, 2, 3]

        child_1 = Object()
        child_1.children = []
        child_1.destroy = MagicMock()
        child_1.is_alive = True
        child_2 = Object()
        child_2.children = []
        child_2.destroy = MagicMock()
        child_2.is_alive = False
        child_3 = Object()
        child_3.children = [1]
        child_3.destroy = MagicMock()
        child_3.is_alive = True

        def get_child(id):
            return {1: child_1, 2: child_2, 3: child_3}[id]

        with mock.patch(PIPELINE_PROCESS_GET, get_child):
            process.destroy_all()
            child_1.destroy.assert_called()
            child_2.destroy.assert_not_called()
            child_3.destroy.assert_called()
            self.assertEqual(child_1.destroy.call_count, 2)

    def test_in_subprocess__true(self):
        snapshot = ProcessSnapshot(data={"_pipeline_stack": Stack([1, 2])})
        process = PipelineProcess()
        process.snapshot = snapshot

        self.assertTrue(process.in_subprocess)

    def test_in_subprocess__false(self):
        snapshot = ProcessSnapshot(data={"_pipeline_stack": Stack([1])})
        process = PipelineProcess()
        process.snapshot = snapshot

        self.assertFalse(process.in_subprocess)

    def test_priority_for_process(self):
        pipeline = PipelineObject()
        process = PipelineProcess.objects.prepare_for_pipeline(pipeline)
        priority = 5
        PipelineModel.objects.prepare_for_pipeline(pipeline=pipeline, process=process, priority=priority)

        self.assertEqual(PipelineProcess.objects.priority_for_process(process.id), priority)
