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
from mock import call

from pipeline.django_signal_valve import valve
from pipeline.engine import signals
from pipeline.engine.core import schedule
from pipeline.engine.models import Data, PipelineProcess, ScheduleService, Status
from pipeline.tests.engine.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa

PARENT_DATA = "PARENT_DATA"


class ScheduleTestCase(TestCase):
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock())
    @mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock())
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    def test_schedule_exception_handler__no_raise(self):
        # no raise
        process_id = uniqid()
        schedule_id = "{}{}".format(uniqid(), uniqid())
        with schedule.schedule_exception_handler(process_id, schedule_id):
            pass

        Status.objects.filter.assert_not_called()
        PipelineProcess.objects.get.assert_not_called()
        schedule.delete_parent_data.assert_not_called()

    @mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock())
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    def test_schedule_exception_handler__raise_and_find_corresponding_status(self):
        # raise and find corresponding status
        e = Exception()
        process = MockPipelineProcess()
        process_id = uniqid()
        schedule_id = "{}{}".format(uniqid(), uniqid())
        with mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock(return_value=process)):
            with schedule.schedule_exception_handler(process_id, schedule_id):
                raise e

            Status.objects.filter.assert_called_once_with(id=schedule_id[:32], version=schedule_id[32:])

            process.exit_gracefully.assert_called_once_with(e)

            schedule.delete_parent_data.assert_called_once_with(schedule_id)

            schedule.delete_parent_data.reset_mock()

    @mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock())
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=False)))
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    def test_schedule_exception_handler__raise_and_not_find_corresponding_status(self):
        e = Exception()
        process = MockPipelineProcess()
        process_id = uniqid()
        schedule_id = "{}{}".format(uniqid(), uniqid())
        with mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock(return_value=process)):
            with schedule.schedule_exception_handler(process_id, schedule_id):
                raise e

            Status.objects.filter.assert_called_once_with(id=schedule_id[:32], version=schedule_id[32:])

            PipelineProcess.objects.get.assert_not_called()

            process.exit_gracefully.assert_not_called()

            schedule.delete_parent_data.assert_called_once_with(schedule_id)

    @mock.patch(PIPELINE_SCHEDULE_SERVICE_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=False)))
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    def test_schedule_can_not_find_status(self):
        mock_ss = MockScheduleService()
        with mock.patch(PIPELINE_SCHEDULE_SERVICE_GET, mock.MagicMock(return_value=mock_ss)):
            process_id = uniqid()

            schedule.schedule(process_id, mock_ss.id)

            mock_ss.destroy.assert_called_once()

            schedule.delete_parent_data.assert_not_called()

            # reset mock
            mock_ss.destroy.reset_mock()

    @mock.patch(PIPELINE_SCHEDULE_SERVICE_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock(return_value=MockPipelineProcess()))
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    def test_schedule__can_not_get_schedule_parent_data(self):
        mock_ss = MockScheduleService()
        with mock.patch(PIPELINE_SCHEDULE_SERVICE_GET, mock.MagicMock(return_value=mock_ss)):
            with mock.patch(SCHEDULE_GET_SCHEDULE_PARENT_DATA, mock.MagicMock(return_value=None)):
                process_id = uniqid()

                schedule.schedule(process_id, mock_ss.id)

                mock_ss.destroy.assert_not_called()

                mock_ss.service_act.schedule.assert_not_called()

                schedule.delete_parent_data.assert_called_with(mock_ss.id)

    @mock.patch(PIPELINE_SCHEDULE_SERVICE_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_STATUS_TRANSIT, mock.MagicMock(return_value=MockActionResult(result=False)))
    @mock.patch(PIPELINE_DATA_WRITE_NODE_DATA, mock.MagicMock())
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    @mock.patch(SCHEDULE_GET_SCHEDULE_PARENT_DATA, mock.MagicMock(return_value=PARENT_DATA))
    @mock.patch(SCHEDULE_SET_SCHEDULE_DATA, mock.MagicMock())
    def test_schedule__schedule_return_fail_and_transit_fail(self):
        process = MockPipelineProcess()
        mock_ss = MockScheduleService(schedule_return=False)

        with mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock(return_value=process)):
            with mock.patch(PIPELINE_SCHEDULE_SERVICE_GET, mock.MagicMock(return_value=mock_ss)):
                process_id = uniqid()

                schedule.schedule(process_id, mock_ss.id)

                mock_ss.service_act.schedule.assert_called_with(PARENT_DATA, mock_ss.callback_data)

                self.assertEqual(mock_ss.schedule_times, 1)

                schedule.set_schedule_data.assert_called_once_with(mock_ss.id, PARENT_DATA)

                mock_ss.destroy.assert_called_once()

                Data.objects.write_node_data.assert_not_called()

    @mock.patch(PIPELINE_SCHEDULE_SERVICE_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_STATUS_TRANSIT, mock.MagicMock(return_value=MockActionResult(result=True)))
    @mock.patch(PIPELINE_DATA_WRITE_NODE_DATA, mock.MagicMock())
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    @mock.patch(SCHEDULE_GET_SCHEDULE_PARENT_DATA, mock.MagicMock(return_value=PARENT_DATA))
    @mock.patch(SCHEDULE_SET_SCHEDULE_DATA, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_TIMEOUT_END_SEND, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_ACT_SCHEDULE_FAIL_SEND, mock.MagicMock())
    @mock.patch(SIGNAL_VALVE_SEND, mock.MagicMock())
    @mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock(return_value=MockPipelineProcess()))
    def test_schedule__schedule_return_fail_and_transit_success(self):
        for timeout in (True, False):
            process = MockPipelineProcess()
            mock_ss = MockScheduleService(schedule_return=False, service_timeout=timeout)
            with mock.patch(
                PIPELINE_PROCESS_SELECT_FOR_UPDATE, mock.MagicMock(return_value=MockQuerySet(get_return=process))
            ):
                with mock.patch(PIPELINE_SCHEDULE_SERVICE_GET, mock.MagicMock(return_value=mock_ss)):
                    process_id = uniqid()

                    schedule.schedule(process_id, mock_ss.id)

                    mock_ss.service_act.schedule.assert_called_with(PARENT_DATA, mock_ss.callback_data)

                    self.assertEqual(mock_ss.schedule_times, 1)

                    schedule.set_schedule_data.assert_called_once_with(mock_ss.id, PARENT_DATA)

                    mock_ss.destroy.assert_not_called()

                    if timeout:
                        signals.service_activity_timeout_monitor_end.send.assert_called_once_with(
                            sender=mock_ss.service_act.__class__,
                            node_id=mock_ss.service_act.id,
                            version=mock_ss.version,
                        )
                    else:
                        signals.service_activity_timeout_monitor_end.send.assert_not_called()

                    Data.objects.write_node_data.assert_called_once_with(mock_ss.service_act, ex_data=None)

                    process.adjust_status.assert_called_once()

                    mock_ss.service_act.schedule_fail.assert_called_once()

                    signals.service_schedule_fail.send.assert_called_with(
                        sender=ScheduleService,
                        activity_shell=mock_ss.service_act,
                        schedule_service=mock_ss,
                        ex_data=None,
                    )

                    valve.send.assert_called_once_with(
                        signals,
                        "activity_failed",
                        sender=process.root_pipeline,
                        pipeline_id=process.root_pipeline_id,
                        pipeline_activity_id=mock_ss.service_act.id,
                        subprocess_id_stack=process.subprocess_stack,
                    )

                    # reset mock
                    schedule.set_schedule_data.reset_mock()
                    signals.service_activity_timeout_monitor_end.send.reset_mock()
                    Data.objects.write_node_data.reset_mock()
                    signals.service_schedule_fail.send.reset_mock()
                    valve.send.reset_mock()

    @mock.patch(PIPELINE_SCHEDULE_SERVICE_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_STATUS_TRANSIT, mock.MagicMock(return_value=MockActionResult(result=True)))
    @mock.patch(PIPELINE_DATA_WRITE_NODE_DATA, mock.MagicMock())
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock(return_value=MockPipelineProcess()))
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    @mock.patch(SCHEDULE_GET_SCHEDULE_PARENT_DATA, mock.MagicMock(return_value=PARENT_DATA))
    @mock.patch(SCHEDULE_SET_SCHEDULE_DATA, mock.MagicMock())
    def test_schedule__schedule_raise_exception_and_transit_fail(self):
        e = Exception()
        mock_ss = MockScheduleService(schedule_exception=e)
        with mock.patch(PIPELINE_SCHEDULE_SERVICE_GET, mock.MagicMock(return_value=mock_ss)):
            # 3.1.1. transit fail
            with mock.patch(PIPELINE_STATUS_TRANSIT, mock.MagicMock(return_value=MockActionResult(result=False))):
                process_id = uniqid()

                schedule.schedule(process_id, mock_ss.id)

                mock_ss.service_act.schedule.assert_called_once_with(PARENT_DATA, mock_ss.callback_data)

                self.assertEqual(mock_ss.schedule_times, 1)

                mock_ss.destroy.assert_called_once()

                Data.objects.write_node_data.assert_not_called()

    @mock.patch(PIPELINE_SCHEDULE_SERVICE_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_STATUS_TRANSIT, mock.MagicMock(return_value=MockActionResult(result=True)))
    @mock.patch(PIPELINE_DATA_WRITE_NODE_DATA, mock.MagicMock())
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    @mock.patch(SCHEDULE_GET_SCHEDULE_PARENT_DATA, mock.MagicMock(return_value=PARENT_DATA))
    @mock.patch(SCHEDULE_SET_SCHEDULE_DATA, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_TIMEOUT_END_SEND, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_ACT_SCHEDULE_FAIL_SEND, mock.MagicMock())
    @mock.patch(SIGNAL_VALVE_SEND, mock.MagicMock())
    @mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock(return_value=MockPipelineProcess()))
    def test_schedule__schedule_raise_exception_and_transit_success(self):
        for timeout in (True, False):
            e = Exception()
            mock_ss = MockScheduleService(schedule_exception=e, service_timeout=timeout)
            process = MockPipelineProcess()

            with mock.patch(
                PIPELINE_PROCESS_SELECT_FOR_UPDATE, mock.MagicMock(return_value=MockQuerySet(get_return=process))
            ):
                with mock.patch(PIPELINE_SCHEDULE_SERVICE_GET, mock.MagicMock(return_value=mock_ss)):
                    process_id = uniqid()

                    schedule.schedule(process_id, mock_ss.id)

                    mock_ss.service_act.schedule.assert_called_once_with(PARENT_DATA, mock_ss.callback_data)

                    self.assertEqual(mock_ss.schedule_times, 1)

                    mock_ss.destroy.assert_not_called()

                    if timeout:
                        signals.service_activity_timeout_monitor_end.send.assert_called_once_with(
                            sender=mock_ss.service_act.__class__,
                            node_id=mock_ss.service_act.id,
                            version=mock_ss.version,
                        )
                    else:
                        signals.service_activity_timeout_monitor_end.send.assert_not_called()

                    Data.objects.write_node_data.assert_called()

                    process.adjust_status.assert_called_once()

                    mock_ss.service_act.schedule_fail.assert_called_once()

                    signals.service_schedule_fail.send.assert_called()

                    valve.send.assert_called_once_with(
                        signals,
                        "activity_failed",
                        sender=process.root_pipeline,
                        pipeline_id=process.root_pipeline_id,
                        pipeline_activity_id=mock_ss.service_act.id,
                        subprocess_id_stack=process.subprocess_stack,
                    )

                    signals.service_activity_timeout_monitor_end.send.reset_mock()
                    Data.objects.write_node_data.reset_mock()
                    signals.service_schedule_fail.send.reset_mock()
                    valve.send.reset_mock()

    @mock.patch(PIPELINE_SCHEDULE_SERVICE_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_STATUS_TRANSIT, mock.MagicMock(return_value=MockActionResult(result=True)))
    @mock.patch(PIPELINE_DATA_WRITE_NODE_DATA, mock.MagicMock())
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    @mock.patch(SCHEDULE_GET_SCHEDULE_PARENT_DATA, mock.MagicMock(return_value=PARENT_DATA))
    @mock.patch(SCHEDULE_SET_SCHEDULE_DATA, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_TIMEOUT_END_SEND, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_ACT_SCHEDULE_FAIL_SEND, mock.MagicMock())
    @mock.patch(SIGNAL_VALVE_SEND, mock.MagicMock())
    @mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock(return_value=MockPipelineProcess()))
    def test_schedule__schedule_raise_exception_and_process_is_not_alive(self):
        for timeout in (True, False):
            e = Exception()
            mock_ss = MockScheduleService(schedule_exception=e, service_timeout=timeout)
            process = MockPipelineProcess(is_alive=False)

            with mock.patch(
                PIPELINE_PROCESS_SELECT_FOR_UPDATE, mock.MagicMock(return_value=MockQuerySet(get_return=process))
            ):
                with mock.patch(PIPELINE_SCHEDULE_SERVICE_GET, mock.MagicMock(return_value=mock_ss)):
                    process_id = uniqid()

                    schedule.schedule(process_id, mock_ss.id)

                    mock_ss.service_act.schedule.assert_called_once_with(PARENT_DATA, mock_ss.callback_data)

                    self.assertEqual(mock_ss.schedule_times, 1)

                    mock_ss.destroy.assert_not_called()

                    if timeout:
                        signals.service_activity_timeout_monitor_end.send.assert_called_once_with(
                            sender=mock_ss.service_act.__class__,
                            node_id=mock_ss.service_act.id,
                            version=mock_ss.version,
                        )
                    else:
                        signals.service_activity_timeout_monitor_end.send.assert_not_called()

                    Data.objects.write_node_data.assert_called()

                    process.adjust_status.assert_not_called()

                    mock_ss.service_act.schedule_fail.assert_not_called()

                    signals.service_schedule_fail.send.assert_not_called()

                    valve.send.assert_not_called()

                    signals.service_activity_timeout_monitor_end.send.reset_mock()
                    Data.objects.write_node_data.reset_mock()
                    signals.service_schedule_fail.send.reset_mock()
                    valve.send.reset_mock()

    @mock.patch(PIPELINE_SCHEDULE_SERVICE_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_STATUS_TRANSIT, mock.MagicMock(return_value=MockActionResult(result=True)))
    @mock.patch(PIPELINE_DATA_WRITE_NODE_DATA, mock.MagicMock())
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    @mock.patch(SCHEDULE_SET_SCHEDULE_DATA, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_TIMEOUT_END_SEND, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_ACT_SCHEDULE_FAIL_SEND, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_ACT_SCHEDULE_SUCCESS_SEND, mock.MagicMock())
    @mock.patch(SIGNAL_VALVE_SEND, mock.MagicMock())
    @mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock(return_value=MockPipelineProcess()))
    def test_schedule__schedule_raise_exception_and_ignore_error_and_transit_success(self):
        parent_data_return = "data"

        for timeout, process_alive in itertools.product((True, False), (True, False)):
            mock_ss = MockScheduleService(
                schedule_exception=Exception(),
                service_timeout=timeout,
                service_err_ignore=True,
                schedule_done=True,
                result_bit=False,
            )
            mock_context = MockContext()
            mock_status = MockEngineModelStatus(error_ignorable=False)
            mock_top_pipeline_data = MockData()
            process = MockPipelineProcess(
                is_alive=process_alive, top_pipeline_data=mock_top_pipeline_data, top_pipeline_context=mock_context
            )
            mock_parent_data = MockData(get_outputs_return=parent_data_return)

            with mock.patch(SCHEDULE_GET_SCHEDULE_PARENT_DATA, mock.MagicMock(return_value=mock_parent_data)):

                with mock.patch(PIPELINE_SCHEDULE_SERVICE_GET, mock.MagicMock(return_value=mock_ss)):

                    with mock.patch(PIPELINE_STATUS_GET, mock.MagicMock(return_value=mock_status)):

                        with mock.patch(
                            PIPELINE_PROCESS_GET, mock.MagicMock(return_value=process),
                        ):

                            process_id = uniqid()

                            schedule.schedule(process_id, mock_ss.id)

                            mock_ss.service_act.schedule.assert_called_once_with(
                                mock_parent_data, mock_ss.callback_data
                            )

                            mock_ss.service_act.ignore_error.assert_called_once()

                            mock_ss.service_act.finish_schedule.assert_called_once()

                            self.assertEqual(mock_ss.schedule_times, 1)

                            if timeout:
                                signals.service_activity_timeout_monitor_end.send.assert_called_once_with(
                                    sender=mock_ss.service_act.__class__,
                                    node_id=mock_ss.service_act.id,
                                    version=mock_ss.version,
                                )
                            else:
                                signals.service_activity_timeout_monitor_end.send.assert_not_called()

                            Data.objects.write_node_data.assert_called_once_with(mock_ss.service_act)

                            self.assertTrue(mock_status.error_ignorable)
                            mock_status.save.assert_called_once()

                            if not process_alive:
                                mock_ss.destroy.assert_called_once()

                                signals.service_activity_timeout_monitor_end.send.reset_mock()
                                Data.objects.write_node_data.reset_mock()

                                continue
                            else:
                                mock_ss.destroy.assert_not_called()

                            process.top_pipeline.data.update_outputs.assert_called_once_with(parent_data_return)

                            mock_context.extract_output.assert_called_once_with(mock_ss.service_act)

                            process.save.assert_called_once()

                            schedule.delete_parent_data.assert_called_once_with(mock_ss.id)

                            mock_ss.finish.assert_called_once()

                            signals.service_schedule_success.send.assert_called_once_with(
                                sender=ScheduleService, activity_shell=mock_ss.service_act, schedule_service=mock_ss
                            )

                            valve.send.assert_called_once_with(
                                signals,
                                "wake_from_schedule",
                                sender=ScheduleService,
                                process_id=mock_ss.process_id,
                                activity_id=mock_ss.activity_id,
                            )

                            # reset mock
                            signals.service_activity_timeout_monitor_end.send.reset_mock()
                            Data.objects.write_node_data.reset_mock()
                            schedule.delete_parent_data.reset_mock()
                            signals.service_schedule_success.send.reset_mock()
                            valve.send.reset_mock()

    @mock.patch(PIPELINE_SCHEDULE_SERVICE_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_STATUS_TRANSIT, mock.MagicMock(return_value=MockActionResult(result=False)))
    @mock.patch(PIPELINE_DATA_WRITE_NODE_DATA, mock.MagicMock())
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock(return_value=MockPipelineProcess()))
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    @mock.patch(SCHEDULE_GET_SCHEDULE_PARENT_DATA, mock.MagicMock(return_value=PARENT_DATA))
    @mock.patch(SCHEDULE_SET_SCHEDULE_DATA, mock.MagicMock())
    def test_schedule__schedule_return_success_and_wait_callback_but_transit_fail(self):
        for timeout in (True, False):
            mock_ss = MockScheduleService(
                schedule_return=True, service_timeout=timeout, wait_callback=True, result_bit=True
            )
            with mock.patch(PIPELINE_SCHEDULE_SERVICE_GET, mock.MagicMock(return_value=mock_ss)):
                process_id = uniqid()

                schedule.schedule(process_id, mock_ss.id)

                mock_ss.service_act.schedule.assert_called_once_with(PARENT_DATA, mock_ss.callback_data)

                self.assertEqual(mock_ss.schedule_times, 1)

                mock_ss.destroy.assert_called_once()

                Data.objects.write_node_data.assert_not_called()

    @mock.patch(PIPELINE_SCHEDULE_SERVICE_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_STATUS_TRANSIT, mock.MagicMock(return_value=MockActionResult(result=True)))
    @mock.patch(PIPELINE_DATA_WRITE_NODE_DATA, mock.MagicMock())
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    @mock.patch(SCHEDULE_SET_SCHEDULE_DATA, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_TIMEOUT_END_SEND, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_ACT_SCHEDULE_FAIL_SEND, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_ACT_SCHEDULE_SUCCESS_SEND, mock.MagicMock())
    @mock.patch(SIGNAL_VALVE_SEND, mock.MagicMock())
    @mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock(return_value=MockPipelineProcess()))
    def test_schedule__schedule_return_success_and_wait_callback_and_transit_success(self):
        parent_data_return = "data"

        for timeout, result_bit, process_alive, schedule_return in itertools.product(
            (True, False), (True, False), (True, False), (True, None)
        ):
            mock_ss = MockScheduleService(
                shcedule_return=schedule_return,
                service_timeout=timeout,
                wait_callback=True,
                multi_callback_enabled=False,
                result_bit=result_bit,
            )
            mock_context = MockContext()
            mock_status = MockEngineModelStatus(error_ignorable=False)
            mock_top_pipeline_data = MockData()
            process = MockPipelineProcess(
                is_alive=process_alive, top_pipeline_data=mock_top_pipeline_data, top_pipeline_context=mock_context
            )
            mock_parent_data = MockData(get_outputs_return=parent_data_return)

            with mock.patch(SCHEDULE_GET_SCHEDULE_PARENT_DATA, mock.MagicMock(return_value=mock_parent_data)):

                with mock.patch(PIPELINE_SCHEDULE_SERVICE_GET, mock.MagicMock(return_value=mock_ss)):

                    with mock.patch(PIPELINE_STATUS_GET, mock.MagicMock(return_value=mock_status)):

                        with mock.patch(
                            PIPELINE_PROCESS_GET, mock.MagicMock(return_value=process),
                        ):

                            process_id = uniqid()

                            schedule.schedule(process_id, mock_ss.id)

                            mock_ss.service_act.schedule.assert_called_once_with(
                                mock_parent_data, mock_ss.callback_data
                            )

                            self.assertEqual(mock_ss.schedule_times, 1)

                            if timeout:
                                signals.service_activity_timeout_monitor_end.send.assert_called_once_with(
                                    sender=mock_ss.service_act.__class__,
                                    node_id=mock_ss.service_act.id,
                                    version=mock_ss.version,
                                )
                            else:
                                signals.service_activity_timeout_monitor_end.send.assert_not_called()

                            Data.objects.write_node_data.assert_called_once_with(mock_ss.service_act)

                            if not result_bit:
                                self.assertTrue(mock_status.error_ignorable)
                                mock_status.save.assert_called_once()
                            else:
                                self.assertFalse(mock_status.error_ignorable)
                                mock_status.save.assert_not_called()

                            if not process_alive:
                                mock_ss.destroy.assert_called_once()

                                signals.service_activity_timeout_monitor_end.send.reset_mock()
                                Data.objects.write_node_data.reset_mock()

                                continue
                            else:
                                mock_ss.destroy.assert_not_called()

                            process.top_pipeline.data.update_outputs.assert_called_once_with(parent_data_return)

                            mock_context.extract_output.assert_called_once_with(mock_ss.service_act)

                            process.save.assert_called_once()

                            schedule.delete_parent_data.assert_called_once_with(mock_ss.id)

                            mock_ss.finish.assert_called_once()

                            signals.service_schedule_success.send.assert_called_once_with(
                                sender=ScheduleService, activity_shell=mock_ss.service_act, schedule_service=mock_ss
                            )

                            valve.send.assert_called_once_with(
                                signals,
                                "wake_from_schedule",
                                sender=ScheduleService,
                                process_id=mock_ss.process_id,
                                activity_id=mock_ss.activity_id,
                            )

                            # reset mock
                            signals.service_activity_timeout_monitor_end.send.reset_mock()
                            Data.objects.write_node_data.reset_mock()
                            schedule.delete_parent_data.reset_mock()
                            signals.service_schedule_success.send.reset_mock()
                            valve.send.reset_mock()

    @mock.patch(PIPELINE_SCHEDULE_SERVICE_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_STATUS_TRANSIT, mock.MagicMock(return_value=MockActionResult(result=True)))
    @mock.patch(PIPELINE_DATA_WRITE_NODE_DATA, mock.MagicMock())
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    @mock.patch(SCHEDULE_SET_SCHEDULE_DATA, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_TIMEOUT_END_SEND, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_ACT_SCHEDULE_FAIL_SEND, mock.MagicMock())
    @mock.patch(ENGINE_SIGNAL_ACT_SCHEDULE_SUCCESS_SEND, mock.MagicMock())
    @mock.patch(SIGNAL_VALVE_SEND, mock.MagicMock())
    def test_schedule__schedule_return_success_and_finished(self):
        parent_data_return = "data"

        for timeout, result_bit, process_alive in itertools.product((True, False), (True, False), (True, False)):
            mock_ss = MockScheduleService(
                schedule_return=True, service_timeout=timeout, schedule_done=True, result_bit=result_bit
            )
            mock_context = MockContext()
            mock_status = MockEngineModelStatus(error_ignorable=False)
            mock_top_pipeline_data = MockData()
            process = MockPipelineProcess(
                is_alive=process_alive, top_pipeline_data=mock_top_pipeline_data, top_pipeline_context=mock_context
            )

            mock_parent_data = MockData(get_outputs_return=parent_data_return)
            with mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock(return_value=process)):
                with mock.patch(SCHEDULE_GET_SCHEDULE_PARENT_DATA, mock.MagicMock(return_value=mock_parent_data)):

                    with mock.patch(PIPELINE_SCHEDULE_SERVICE_GET, mock.MagicMock(return_value=mock_ss)):

                        with mock.patch(PIPELINE_STATUS_GET, mock.MagicMock(return_value=mock_status)):

                            with mock.patch(
                                PIPELINE_PROCESS_GET, mock.MagicMock(return_value=process),
                            ):

                                schedule.schedule(process.id, mock_ss.id)

                                mock_ss.service_act.schedule.assert_called_once_with(
                                    mock_parent_data, mock_ss.callback_data
                                )

                                self.assertEqual(mock_ss.schedule_times, 1)

                                if timeout:
                                    signals.service_activity_timeout_monitor_end.send.assert_called_once_with(
                                        sender=mock_ss.service_act.__class__,
                                        node_id=mock_ss.service_act.id,
                                        version=mock_ss.version,
                                    )
                                else:
                                    signals.service_activity_timeout_monitor_end.send.assert_not_called()

                                Data.objects.write_node_data.assert_called_once_with(mock_ss.service_act)

                                if not result_bit:
                                    self.assertTrue(mock_status.error_ignorable)
                                    mock_status.save.assert_called_once()
                                else:
                                    self.assertFalse(mock_status.error_ignorable)
                                    mock_status.save.assert_not_called()

                                if not process_alive:
                                    mock_ss.destroy.assert_called_once()

                                    signals.service_activity_timeout_monitor_end.send.reset_mock()
                                    Data.objects.write_node_data.reset_mock()

                                    continue
                                else:
                                    mock_ss.destroy.assert_not_called()

                                process.top_pipeline.data.update_outputs.assert_called_once_with(parent_data_return)

                                mock_context.extract_output.assert_called_once_with(mock_ss.service_act)

                                process.save.assert_called_once()

                                schedule.delete_parent_data.assert_called_once_with(mock_ss.id)

                                mock_ss.finish.assert_called_once()

                                signals.service_schedule_success.send.assert_called_once_with(
                                    sender=ScheduleService, activity_shell=mock_ss.service_act, schedule_service=mock_ss
                                )

                                valve.send.assert_called_once_with(
                                    signals,
                                    "wake_from_schedule",
                                    sender=ScheduleService,
                                    process_id=mock_ss.process_id,
                                    activity_id=mock_ss.activity_id,
                                )

                                # reset mock
                                signals.service_activity_timeout_monitor_end.send.reset_mock()
                                Data.objects.write_node_data.reset_mock()
                                schedule.delete_parent_data.reset_mock()
                                signals.service_schedule_success.send.reset_mock()
                                valve.send.reset_mock()

    @mock.patch(PIPELINE_SCHEDULE_SERVICE_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_STATUS_TRANSIT, mock.MagicMock(return_value=MockActionResult(result=False)))
    @mock.patch(PIPELINE_DATA_WRITE_NODE_DATA, mock.MagicMock())
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock(return_value=MockPipelineProcess()))
    @mock.patch(SCHEDULE_DELETE_PARENT_DATA, mock.MagicMock())
    @mock.patch(SCHEDULE_GET_SCHEDULE_PARENT_DATA, mock.MagicMock(return_value=PARENT_DATA))
    @mock.patch(SCHEDULE_SET_SCHEDULE_DATA, mock.MagicMock())
    def test_schedule__schedule_return_success_and_need_next_schedule(self):
        mock_ss = MockScheduleService(schedule_return=True, result_bit=True)
        with mock.patch(PIPELINE_SCHEDULE_SERVICE_GET, mock.MagicMock(return_value=mock_ss)):
            process_id = uniqid()

            schedule.schedule(process_id, mock_ss.id)

            mock_ss.service_act.schedule.assert_called_once_with(PARENT_DATA, mock_ss.callback_data)

            self.assertEqual(mock_ss.schedule_times, 1)

            schedule.set_schedule_data.assert_called_once_with(mock_ss.id, PARENT_DATA)

            mock_ss.set_next_schedule.assert_called_once()

            Data.objects.write_node_data.assert_called_once()

    @mock.patch(PIPELINE_SCHEDULE_SERVICE_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_STATUS_FILTER, mock.MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(PIPELINE_PROCESS_GET, mock.MagicMock(return_value=MockPipelineProcess()))
    @mock.patch(SCHEDULE_GET_SCHEDULE_PARENT_DATA, mock.MagicMock(return_value=PARENT_DATA))
    @mock.patch(SCHEDULE_SET_SCHEDULE_DATA, mock.MagicMock())
    @mock.patch(PIPELINE_DATA_WRITE_NODE_DATA, mock.MagicMock())
    def test_schedule__schedule_return_success_and_wait_multi_callback(self):
        mock_ss = MockScheduleService(
            schedule_return=True, wait_callback=True, schedule_done=False, multi_callback_enabled=True, result_bit=True
        )

        with mock.patch(PIPELINE_SCHEDULE_SERVICE_GET, mock.MagicMock(return_value=mock_ss)):
            process_id = uniqid()

            schedule_calls, set_schedule_data_calls = [], []
            for schedule_times in range(1, 5):

                schedule.schedule(process_id, mock_ss.id)

                schedule_calls.append(call(PARENT_DATA, mock_ss.callback_data))
                mock_ss.service_act.schedule.assert_has_calls(schedule_calls)

                self.assertEqual(mock_ss.schedule_times, schedule_times)

                set_schedule_data_calls.append(call(mock_ss.id, PARENT_DATA))
                schedule.set_schedule_data.assert_has_calls(set_schedule_data_calls)

                mock_ss.save.assert_called()
                mock_ss.set_next_schedule.assert_not_called()
