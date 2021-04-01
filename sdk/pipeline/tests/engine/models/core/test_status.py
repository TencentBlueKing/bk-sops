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

import copy

from django.test import TestCase

from pipeline.engine import states
from pipeline.engine.models import Data, LogEntry, Status, SubProcessRelationship
from pipeline.tests.mock_settings import *  # noqa

from ..mock import *  # noqa


class TestStatus(TestCase):
    def test_transit(self):
        mock_record = MagicMock()
        mock_record.return_value = IdentifyObject()

        mock_link_history = MagicMock()

        # start test
        id_1 = uniqid()
        result = Status.objects.transit(id=id_1, to_state=states.RUNNING, start=True, name=id_1)
        state = Status.objects.get(id=id_1)
        self.assertTrue(result.result)
        self.assertEqual(state.state, states.RUNNING)
        self.assertEqual(state.name, id_1)
        self.assertIsNotNone(state.started_time)

        # transit test
        with patch(PIPELINE_HISTORY_RECORD, mock_record):
            with patch(PIPELINE_HISTORY_LINK_HISTORY, mock_link_history):
                for is_pipeline, appoint_map in list(states.TRANSITION_MAP.items()):
                    for is_appoint, state_map in list(appoint_map.items()):
                        for from_state, to_state_set in list(state_map.items()):

                            # valid transit
                            for to_state in to_state_set:
                                state_id = uniqid()
                                result = Status.objects.transit(id=state_id, to_state=from_state, start=True)
                                self.assertTrue(result.result)
                                state = Status.objects.get(id=state_id)
                                self.assertIsNotNone(state.state_refresh_at)
                                state.state_refresh_at = None
                                state.save()
                                result = Status.objects.transit(
                                    id=state_id, is_pipeline=is_pipeline, appoint=is_appoint, to_state=to_state
                                )
                                self.assertTrue(result.result, "valid: from {} to {}".format(from_state, to_state))
                                state.refresh_from_db()
                                self.assertIsNotNone(state.state_refresh_at)
                                self.assertEqual(state.state, to_state)
                                if to_state in states.ARCHIVED_STATES:
                                    self.assertIsNotNone(state.archived_time)
                                else:
                                    self.assertIsNone(state.archived_time)

                            # invalid transit
                            invalid_to_state_set = states.ALL_STATES.difference(to_state_set)
                            for invalid_to_state in invalid_to_state_set:
                                state_id = uniqid()
                                Status.objects.transit(id=state_id, to_state=from_state, start=True)
                                result = Status.objects.transit(
                                    id=state_id, is_pipeline=is_pipeline, appoint=is_appoint, to_state=invalid_to_state
                                )
                                self.assertFalse(
                                    result.result, "invalid: from {} to {}".format(from_state, invalid_to_state)
                                )
                                state = Status.objects.get(id=state_id)
                                self.assertEqual(state.state, from_state)

        # transit when process is frozen
        def return_a_frozen_process(*args, **kwargs):
            obj = Object()
            obj.is_frozen = True
            return obj

        with patch(PIPELINE_PROCESS_GET, return_a_frozen_process):
            id_2 = uniqid()
            SubProcessRelationship.objects.create(process_id=uniqid(), subprocess_id=id_2)
            result = Status.objects.transit(id=id_2, to_state=states.RUNNING, start=True)
            self.assertTrue(result.result)
            result = Status.objects.transit(id=id_2, to_state=states.FINISHED, is_pipeline=True)
            self.assertFalse(result.result)
            result = Status.objects.transit(id=id_2, to_state=states.FINISHED, is_pipeline=False)
            self.assertTrue(result.result)

        def return_a_frozen_process_list(*args, **kwargs):
            obj = Object()
            obj.is_frozen = True
            return [obj]

        with patch(PIPELINE_PROCESS_FILTER, return_a_frozen_process_list):
            id_3 = uniqid()
            result = Status.objects.transit(id=id_3, to_state=states.RUNNING, start=True)
            self.assertTrue(result.result)
            result = Status.objects.transit(id=id_3, to_state=states.FINISHED, is_pipeline=True)
            self.assertFalse(result.result)
            result = Status.objects.transit(id=id_3, to_state=states.FINISHED, is_pipeline=False)
            self.assertTrue(result.result)

        # test special treat when transit from FINISHED to RUNNING

        mock_record.reset_mock()
        mock_link_history.reset_mock()

        with patch(PIPELINE_HISTORY_RECORD, mock_record):
            with patch(PIPELINE_HISTORY_LINK_HISTORY, mock_link_history):
                id_4 = uniqid()
                version = uniqid()
                result = Status.objects.transit(id=id_4, to_state=states.FINISHED, start=True, version=version)
                self.assertTrue(result.result)
                result = Status.objects.transit(id=id_4, to_state=states.RUNNING, appoint=True)
                self.assertFalse(result.result)
                result = Status.objects.transit(id=id_4, to_state=states.RUNNING)
                self.assertTrue(result.result)
                mock_record.assert_called()
                mock_link_history.assert_called()
                state = Status.objects.get(id=id_4)
                self.assertNotEqual(state.version, version)
                self.assertEqual(state.loop, 2)

        # test transit old version state

        id_6 = uniqid()
        result = Status.objects.transit(id=id_6, to_state=states.RUNNING, start=True)
        self.assertTrue(result.result)
        result = Status.objects.transit(id=id_6, to_state=states.FINISHED, version=uniqid())
        self.assertFalse(result.result)
        state = Status.objects.get(id=id_6)
        self.assertEqual(state.state, states.RUNNING)

        # test unchanged_pass is true
        id_7 = uniqid()
        result = Status.objects.transit(id=id_7, to_state=states.RUNNING, start=True)
        self.assertTrue(result.result)
        result = Status.objects.transit(id=id_7, to_state=states.RUNNING, unchanged_pass=True)
        self.assertTrue(result.result)
        state = Status.objects.get(id=id_7)
        self.assertEqual(state.state, states.RUNNING)

        # test unchanged_pass is false
        id_8 = uniqid()
        result = Status.objects.transit(id=id_8, to_state=states.RUNNING, start=True)
        self.assertTrue(result.result)
        result = Status.objects.transit(id=id_8, to_state=states.RUNNING)
        self.assertFalse(result.result)
        state = Status.objects.get(id=id_8)
        self.assertEqual(state.state, states.RUNNING)

    def test_batch_transit(self):
        status_id_list = {uniqid() for _ in range(5)}
        for sid in status_id_list:
            result = Status.objects.transit(id=sid, to_state=states.RUNNING, start=True)
            self.assertTrue(result.result)

        Status.objects.batch_transit(id_list=status_id_list, state=states.BLOCKED)
        for sid in status_id_list:
            self.assertEqual(Status.objects.state_for(sid), states.BLOCKED)

        # test exclude param
        status_id_list = [uniqid() for _ in range(3)]
        exclude = [uniqid() for _ in range(2)]
        all_id_list = copy.deepcopy(status_id_list)
        all_id_list.extend(exclude)
        for sid in all_id_list:
            result = Status.objects.transit(id=sid, to_state=states.RUNNING, start=True)
            self.assertTrue(result.result)

        Status.objects.batch_transit(id_list=status_id_list, state=states.BLOCKED, exclude=exclude)
        for sid in status_id_list:
            self.assertEqual(Status.objects.state_for(sid), states.BLOCKED)
        for sid in exclude:
            self.assertEqual(Status.objects.state_for(sid), states.RUNNING)

    def test_state_for(self):
        status_id = uniqid()
        result = Status.objects.transit(id=status_id, to_state=states.RUNNING, start=True)
        self.assertTrue(result.result)

        self.assertEqual(Status.objects.state_for(status_id), states.RUNNING)
        self.assertIsNone(Status.objects.state_for(uniqid(), may_not_exist=True))
        self.assertRaises(Status.DoesNotExist, Status.objects.state_for, id=uniqid())

        # test version param
        status_id = uniqid()
        result = Status.objects.transit(id=status_id, to_state=states.RUNNING, start=True)
        self.assertTrue(result.result)
        status = Status.objects.get(id=status_id)
        version = status.version

        self.assertEqual(Status.objects.state_for(status_id, version=version), states.RUNNING)
        self.assertIsNone(Status.objects.state_for(uniqid(), may_not_exist=True, version=version))
        self.assertIsNone(Status.objects.state_for(status_id, may_not_exist=True, version=uniqid()))
        self.assertRaises(Status.DoesNotExist, Status.objects.state_for, id=uniqid(), version=version)
        self.assertRaises(Status.DoesNotExist, Status.objects.state_for, id=uniqid(), version=uniqid())

    def test_version_for(self):
        status_id = uniqid()
        result = Status.objects.transit(id=status_id, to_state=states.RUNNING, start=True)
        self.assertTrue(result.result)
        status = Status.objects.get(id=status_id)
        self.assertEqual(Status.objects.version_for(status_id), status.version)

    def test_states_for(self):
        status_id_list = {uniqid() for _ in range(5)}
        for sid in status_id_list:
            result = Status.objects.transit(id=sid, to_state=states.RUNNING, start=True)
            self.assertTrue(result.result)

        state_list = Status.objects.states_for(status_id_list)
        self.assertEqual(len(status_id_list), len(state_list))
        for s in state_list:
            self.assertEqual(s, states.RUNNING)

        # test not exist id
        status_id_list = [uniqid() for _ in range(3)]
        not_exist = [uniqid() for _ in range(2)]
        for sid in status_id_list:
            result = Status.objects.transit(id=sid, to_state=states.RUNNING, start=True)
            self.assertTrue(result.result)

        status_id_list.extend(not_exist)
        state_list = Status.objects.states_for(status_id_list)
        self.assertEqual(len(status_id_list) - len(not_exist), len(state_list))
        for s in state_list:
            self.assertEqual(s, states.RUNNING)

    def test_prepare_for_pipeline(self):
        pipeline = PipelineObject()
        Status.objects.prepare_for_pipeline(pipeline)
        status = Status.objects.get(id=pipeline.id)
        self.assertEqual(status.state, states.READY)

        cls_str = str(pipeline.__class__)
        cls_name = pipeline.__class__.__name__[:64]
        self.assertEqual(status.name, cls_str if len(cls_str) <= 64 else cls_name)

    @patch(PIPELINE_DATA_WRITE_NODE_DATA, MagicMock())
    def test_fail(self):

        # success call test
        node = IdentifyObject()
        result = Status.objects.transit(id=node.id, to_state=states.RUNNING, start=True)
        self.assertTrue(result.result)
        result = Status.objects.fail(node, "ex_data")
        self.assertTrue(result.result)
        Data.objects.write_node_data.assert_called_with(node, "ex_data")
        status = Status.objects.get(id=node.id)
        self.assertEqual(status.state, states.FAILED)

        Data.objects.write_node_data.reset_mock()

        # test call failed
        node = IdentifyObject()
        result = Status.objects.transit(id=node.id, to_state=states.BLOCKED, start=True)
        self.assertTrue(result.result)
        result = Status.objects.fail(node, "ex_data")
        self.assertFalse(result.result)
        Data.objects.write_node_data.assert_not_called()
        status = Status.objects.get(id=node.id)
        self.assertEqual(status.state, states.BLOCKED)

    @patch(PIPELINE_DATA_WIRTE_EX_DATA, MagicMock())
    def test_raw_fail(self):
        # success call test
        node = IdentifyObject()
        result = Status.objects.transit(id=node.id, to_state=states.RUNNING, start=True)
        self.assertTrue(result.result)
        result = Status.objects.raw_fail(node.id, "ex_data")
        self.assertTrue(result.result)
        Data.objects.write_ex_data.assert_called_with(node.id, "ex_data")
        status = Status.objects.get(id=node.id)
        self.assertEqual(status.state, states.FAILED)

        Data.objects.write_ex_data.reset_mock()

        # test call failed
        node = IdentifyObject()
        result = Status.objects.transit(id=node.id, to_state=states.BLOCKED, start=True)
        self.assertTrue(result.result)
        result = Status.objects.raw_fail(node.id, "ex_data")
        self.assertFalse(result.result)
        Data.objects.write_ex_data.assert_not_called()
        status = Status.objects.get(id=node.id)
        self.assertEqual(status.state, states.BLOCKED)

    @patch(PIPELINE_DATA_WRITE_NODE_DATA, MagicMock())
    def test_finish(self):

        node = IdentifyObject()
        result = Status.objects.transit(id=node.id, to_state=states.RUNNING, start=True)
        self.assertTrue(result.result)
        result = Status.objects.finish(node)
        self.assertTrue(result.result)
        Data.objects.write_node_data.assert_called_with(node)
        status = Status.objects.get(id=node.id)
        self.assertFalse(status.error_ignorable)
        self.assertEqual(status.state, states.FINISHED)

        # test error_ignorable param
        Data.objects.write_node_data.reset_mock()
        node = IdentifyObject()
        result = Status.objects.transit(id=node.id, to_state=states.RUNNING, start=True)
        self.assertTrue(result.result)
        result = Status.objects.finish(node, error_ignorable=True)
        self.assertTrue(result.result)
        Data.objects.write_node_data.assert_called_with(node)
        status = Status.objects.get(id=node.id)
        self.assertTrue(status.error_ignorable)
        self.assertEqual(status.state, states.FINISHED)

        # test call failed
        Data.objects.write_node_data.reset_mock()
        node = IdentifyObject()
        result = Status.objects.transit(id=node.id, to_state=states.READY, start=True)
        self.assertTrue(result.result)
        result = Status.objects.finish(node)
        self.assertFalse(result.result)
        Data.objects.write_node_data.assert_not_called()
        status = Status.objects.get(id=node.id)
        self.assertFalse(status.error_ignorable)
        self.assertEqual(status.state, states.READY)

        Data.objects.write_node_data.reset_mock()
        node = IdentifyObject()
        result = Status.objects.transit(id=node.id, to_state=states.READY, start=True)
        self.assertTrue(result.result)
        result = Status.objects.finish(node, error_ignorable=True)
        self.assertFalse(result.result)
        Data.objects.write_node_data.assert_not_called()
        status = Status.objects.get(id=node.id)
        self.assertFalse(status.error_ignorable)
        self.assertEqual(status.state, states.READY)

    @patch(PIPELINE_DATA_WRITE_NODE_DATA, MagicMock())
    @patch(PIPELINE_HISTORY_LINK_HISTORY, MagicMock())
    @patch(PIPELINE_STATUS_RECOVER_FROM_BLOCK, MagicMock())
    @patch(ENGINE_SIGNAL_NODE_SKIP_CALL, MagicMock())
    def test_skip(self):

        from pipeline.engine.signals import node_skip_call

        mock_record = MagicMock()
        mock_record.return_value = IdentifyObject()
        node_skip_call.send = MagicMock()

        node = IdentifyObject()
        node.skip = MagicMock()
        process = Object()
        process.root_pipeline = IdentifyObject()
        process.subprocess_stack = "subprocess_stack"
        result = Status.objects.transit(id=node.id, to_state=states.FAILED, start=True)
        self.assertTrue(result.result)

        with patch(PIPELINE_HISTORY_RECORD, mock_record):
            result = Status.objects.skip(process, node)
            self.assertTrue(result.result)
            mock_record.assert_called()
            LogEntry.objects.link_history.assert_called_with(node_id=node.id, history_id=mock_record.return_value.id)
            status = Status.objects.get(id=node.id)
            self.assertTrue(status.skip)
            self.assertEqual(status.started_time, status.archived_time)
            self.assertEqual(status.state, states.FINISHED)
            node.skip.assert_called()
            Data.objects.write_node_data.assert_called_with(node)
            Status.objects.recover_from_block.assert_called_with(process.root_pipeline.id, process.subprocess_stack)
            node_skip_call.send.assert_called_once()

        mock_record.reset_mock()
        LogEntry.objects.link_history.reset_mock()
        node.skip.reset_mock()
        Data.objects.write_node_data.reset_mock()
        Status.objects.recover_from_block.reset_mock()
        node_skip_call.send.reset_mock()
        node.id = uniqid()
        result = Status.objects.transit(id=node.id, to_state=states.RUNNING, start=True)
        self.assertTrue(result.result)

        # test skip failed
        with patch(PIPELINE_HISTORY_RECORD, mock_record):
            result = Status.objects.skip(process, node)
            self.assertFalse(result.result)
            mock_record.assert_not_called()
            LogEntry.objects.link_history.assert_not_called()
            status = Status.objects.get(id=node.id)
            self.assertFalse(status.skip)
            self.assertNotEqual(status.started_time, status.archived_time)
            self.assertEqual(status.state, states.RUNNING)
            node.skip.assert_not_called()
            Data.objects.write_node_data.assert_not_called()
            Status.objects.recover_from_block.assert_not_called()
            node_skip_call.send.assert_not_called()

    @patch(PIPELINE_DATA_WRITE_NODE_DATA, MagicMock())
    @patch(PIPELINE_HISTORY_LINK_HISTORY, MagicMock())
    @patch(PIPELINE_STATUS_RECOVER_FROM_BLOCK, MagicMock())
    @patch(ENGINE_SIGNAL_NODE_RETRY_READY, MagicMock())
    def test_retry(self):

        from pipeline.engine.signals import node_retry_ready

        mock_record = MagicMock()
        mock_record.return_value = IdentifyObject()
        node_retry_ready.send = MagicMock()

        node = IdentifyObject()
        node.skip = MagicMock()
        node.next_exec_is_retry = MagicMock()
        process = Object()
        process.root_pipeline = IdentifyObject()
        process.subprocess_stack = "subprocess_stack"
        process.save = MagicMock()
        result = Status.objects.transit(id=node.id, to_state=states.FAILED, start=True)
        self.assertTrue(result.result)

        with patch(PIPELINE_HISTORY_RECORD, mock_record):
            status = Status.objects.get(id=node.id)
            result = Status.objects.retry(process, node, None)
            self.assertTrue(result.result)
            self.assertNotEqual(status.version, Status.objects.version_for(node.id))
            status.refresh_from_db()
            self.assertEqual(status.retry, 1)
            self.assertEqual(status.state, states.READY)
            mock_record.assert_called()
            LogEntry.objects.link_history.assert_called_with(node_id=node.id, history_id=mock_record.return_value.id)
            Status.objects.recover_from_block.assert_called_with(process.root_pipeline.id, process.subprocess_stack)
            Data.objects.write_node_data.assert_not_called()
            node_retry_ready.send.assert_called_once()
            process.save.assert_called_once()
            node.next_exec_is_retry.assert_called()

        process.save.reset_mock()
        mock_record.reset_mock()
        LogEntry.objects.link_history.reset_mock()
        node.skip.reset_mock()
        node.next_exec_is_retry = MagicMock()
        Data.objects.write_node_data.reset_mock()
        Status.objects.recover_from_block.reset_mock()
        node_retry_ready.send.reset_mock()
        node.id = uniqid()
        inputs = {"key": "value"}
        result = Status.objects.transit(id=node.id, to_state=states.FAILED, start=True)
        self.assertTrue(result.result)

        # test retry with inputs
        with patch(PIPELINE_HISTORY_RECORD, mock_record):
            status = Status.objects.get(id=node.id)
            result = Status.objects.retry(process, node, inputs)
            self.assertTrue(result.result)
            self.assertNotEqual(status.version, Status.objects.version_for(node.id))
            status.refresh_from_db()
            self.assertEqual(status.retry, 1)
            self.assertEqual(status.state, states.READY)
            mock_record.assert_called()
            node.next_exec_is_retry.assert_called()
            LogEntry.objects.link_history.assert_called_with(node_id=node.id, history_id=mock_record.return_value.id)
            Status.objects.recover_from_block.assert_called_with(process.root_pipeline.id, process.subprocess_stack)
            Data.objects.write_node_data.assert_called_with(node)
            node_retry_ready.send.assert_called_once()
            process.save.assert_called_once()

        process.save.reset_mock()
        mock_record.reset_mock()
        LogEntry.objects.link_history.reset_mock()
        node.skip.reset_mock()
        Data.objects.write_node_data.reset_mock()
        Status.objects.recover_from_block.reset_mock()
        node_retry_ready.send.reset_mock()
        node.id = uniqid()
        result = Status.objects.transit(id=node.id, to_state=states.FINISHED, start=True)
        self.assertTrue(result.result)

        # test retry failed
        with patch(PIPELINE_HISTORY_RECORD, mock_record):
            status = Status.objects.get(id=node.id)
            result = Status.objects.retry(process, node, inputs)
            self.assertFalse(result.result)
            self.assertEqual(status.version, Status.objects.version_for(node.id))
            status.refresh_from_db()
            self.assertEqual(status.retry, 0)
            self.assertEqual(status.state, states.FINISHED)
            mock_record.assert_not_called()
            LogEntry.objects.link_history.assert_not_called()
            Status.objects.recover_from_block.assert_not_called()
            Data.objects.write_node_data.assert_not_called()
            node_retry_ready.send.assert_not_called()
            process.save.assert_not_called()

        # test retry node reach max run limit
        Status.objects.filter(id=node.id).update(loop=11)
        with patch("pipeline.engine.models.core.RERUN_MAX_LIMIT", 10):
            result = Status.objects.retry(process, node, inputs)
            self.assertFalse(result.result)
            self.assertEqual(result.message, "rerun times exceed max limit: 10, can not retry")

    @patch(PIPELINE_STATUS_BATCH_TRANSIT, MagicMock())
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock())
    def test_recover_from_block(self):
        root_pipeline_id = uniqid()
        subprocess_stack = []

        Status.objects.recover_from_block(root_pipeline_id, [])
        Status.objects.batch_transit.assert_called_with(
            id_list=subprocess_stack, state=states.RUNNING, from_state=states.BLOCKED
        )
        Status.objects.transit.assert_called_with(id=root_pipeline_id, to_state=states.READY, is_pipeline=True)
