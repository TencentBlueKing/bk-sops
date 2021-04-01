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

from pipeline.conf import default_settings
from pipeline.core.flow.activity import ServiceActivity
from pipeline.django_signal_valve import valve
from pipeline.engine import signals
from pipeline.engine.core import handlers
from pipeline.engine.core.handlers import service_activity as service_act_h
from pipeline.engine.models import Data, ScheduleService, Status
from pipeline.tests.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa

handlers.service_activity_handler = handlers.ServiceActivityHandler()


class ServiceActivityHandlerTestCase(TestCase):
    def test_element_cls(self):
        self.assertEqual(handlers.ServiceActivityHandler.element_cls(), ServiceActivity)

    @patch(PIPELINE_STATUS_FAIL, MagicMock())
    @patch(SERVICE_ACT_HYDRATE_NODE_DATA, MagicMock())
    @patch(ENGINE_SIGNAL_TIMEOUT_START_SEND, MagicMock())
    @patch(ENGINE_SIGNAL_TIMEOUT_END_SEND, MagicMock())
    @patch(SIGNAL_VALVE_SEND, MagicMock())
    def test_handle__execute_raise_exception_and_not_ignore_error(self):

        for loop, timeout in itertools.product((1, 2), (5, None)):
            root_pipeline_data = "root_pipeline_data"
            ex_data = "ex_data"
            top_context = MockContext()

            process = MockPipelineProcess(root_pipeline_data=root_pipeline_data, top_pipeline_context=top_context)
            service_act = ServiceActObject(
                interval=None,
                execute_exception=Exception(),
                error_ignorable=False,
                timeout=timeout,
                data=MockData(get_one_of_outputs_return=ex_data),
            )
            status = MockStatus(loop=loop)

            with patch(PIPELINE_STATUS_GET, MagicMock(return_value=status)):

                hdl_result = handlers.service_activity_handler(process, service_act, status)

                if loop > 1:
                    service_act.prepare_rerun_data.assert_called_once()
                    top_context.recover_variable.assert_called_once()
                else:
                    service_act.prepare_rerun_data.assert_not_called()

                self.assertEqual(
                    service_act.data.inputs._loop, status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET
                )
                self.assertEqual(
                    service_act.data.outputs._loop, status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET
                )

                top_context.extract_output.assert_called_once_with(service_act, set_miss=False)

                service_act_h.hydrate_node_data.assert_called_once()

                if timeout:
                    signals.service_activity_timeout_monitor_start.send.assert_called_once_with(
                        sender=service_act.__class__,
                        node_id=service_act.id,
                        version=status.version,
                        root_pipeline_id=process.root_pipeline.id,
                        countdown=service_act.timeout,
                    )
                else:
                    signals.service_activity_timeout_monitor_start.send.assert_not_called()

                service_act.setup_runtime_attrs.assert_called_once_with(
                    id=service_act.id, root_pipeline_id=process.root_pipeline_id
                )
                service_act.execute.assert_called_once_with(root_pipeline_data)

                self.assertIsNotNone(service_act.data.outputs.ex_data)

                service_act.data.get_one_of_outputs.assert_called_once_with("ex_data")

                Status.objects.fail.assert_called_once_with(service_act, ex_data)

                service_act.failure_handler.assert_called_once_with(process.root_pipeline.data)

                if timeout:
                    signals.service_activity_timeout_monitor_end.send.assert_called_once_with(
                        sender=service_act.__class__, node_id=service_act.id, version=status.version
                    )
                else:
                    signals.service_activity_timeout_monitor_end.send.assert_not_called()

                valve.send.assert_called_once_with(
                    signals,
                    "activity_failed",
                    sender=process.root_pipeline,
                    pipeline_id=process.root_pipeline.id,
                    pipeline_activity_id=service_act.id,
                    subprocess_id_stack=process.subprocess_stack,
                )

                self.assertIsNone(hdl_result.next_node)
                self.assertFalse(hdl_result.should_return)
                self.assertTrue(hdl_result.should_sleep)

                # reset mock
                service_act_h.hydrate_node_data.reset_mock()
                signals.service_activity_timeout_monitor_start.send.reset_mock()
                Status.objects.fail.reset_mock()
                signals.service_activity_timeout_monitor_end.send.reset_mock()
                valve.send.reset_mock()

    @patch(PIPELINE_SCHEDULE_SERVICE_SET_SCHEDULE, MagicMock())
    @patch(SERVICE_ACT_HYDRATE_NODE_DATA, MagicMock())
    @patch(ENGINE_SIGNAL_TIMEOUT_START_SEND, MagicMock())
    @patch(ENGINE_SIGNAL_TIMEOUT_END_SEND, MagicMock())
    @patch(SIGNAL_VALVE_SEND, MagicMock())
    def test_handle__execute_raise_exception_and_ignore_error(self):
        for loop, timeout, need_schedule, finish_call_success in itertools.product(
            (1, 2), (5, None), (True, False), (True, False)
        ):
            root_pipeline_data = "root_pipeline_data"
            ex_data = "ex_data"
            top_context = MockContext()

            process = MockPipelineProcess(root_pipeline_data=root_pipeline_data, top_pipeline_context=top_context)
            service_act = ServiceActObject(
                interval=None,
                execute_exception=Exception(),
                error_ignorable=True,
                timeout=timeout,
                need_schedule=need_schedule,
                result_bit=False,
                data=MockData(get_one_of_outputs_return={"ex_data": ex_data, ServiceActivity.result_bit: False}),
            )
            status = MockStatus(loop=loop)

            with patch(PIPELINE_STATUS_GET, MagicMock(return_value=status)):
                with patch(PIPELINE_STATUS_FINISH, MagicMock(return_value=finish_call_success)):

                    hdl_result = handlers.service_activity_handler(process, service_act, status)

                    if loop > 1:
                        service_act.prepare_rerun_data.assert_called_once()
                        top_context.recover_variable.assert_called_once()
                    else:
                        service_act.prepare_rerun_data.assert_not_called()

                    self.assertEqual(
                        service_act.data.inputs._loop, status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET
                    )
                    self.assertEqual(
                        service_act.data.outputs._loop, status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET
                    )

                    service_act_h.hydrate_node_data.assert_called_once()

                    if timeout:
                        signals.service_activity_timeout_monitor_start.send.assert_called_once_with(
                            sender=service_act.__class__,
                            node_id=service_act.id,
                            version=status.version,
                            root_pipeline_id=process.root_pipeline.id,
                            countdown=service_act.timeout,
                        )
                    else:
                        signals.service_activity_timeout_monitor_start.send.assert_not_called()

                    service_act.setup_runtime_attrs.assert_called_once_with(
                        id=service_act.id, root_pipeline_id=process.root_pipeline_id
                    )

                    service_act.execute.assert_called_once_with(root_pipeline_data)

                    service_act.ignore_error.assert_called_once()

                    self.assertIsNotNone(service_act.data.outputs.ex_data)

                    ScheduleService.objects.set_schedule.assert_not_called()

                    top_context.extract_output.assert_has_calls(
                        [mock.call(service_act, set_miss=False), mock.call(service_act)]
                    )

                    if timeout:
                        signals.service_activity_timeout_monitor_end.send.assert_called_once_with(
                            sender=service_act.__class__, node_id=service_act.id, version=status.version
                        )
                    else:
                        signals.service_activity_timeout_monitor_end.send.assert_not_called()

                    Status.objects.finish.assert_called_once_with(service_act, True)

                    if finish_call_success:
                        self.assertEqual(hdl_result.next_node, service_act.next())
                        self.assertFalse(hdl_result.should_return)
                        self.assertFalse(hdl_result.should_sleep)
                    else:
                        self.assertIsNone(hdl_result.next_node)
                        self.assertFalse(hdl_result.should_return)
                        self.assertTrue(hdl_result.should_sleep)

                    # reset mock
                    service_act_h.hydrate_node_data.reset_mock()
                    signals.service_activity_timeout_monitor_start.send.reset_mock()
                    Status.objects.finish.reset_mock()
                    signals.service_activity_timeout_monitor_end.send.reset_mock()
                    valve.send.reset_mock()

    @patch(PIPELINE_SCHEDULE_SERVICE_SET_SCHEDULE, MagicMock())
    @patch(PIPELINE_STATUS_FAIL, MagicMock())
    @patch(SERVICE_ACT_HYDRATE_NODE_DATA, MagicMock())
    @patch(ENGINE_SIGNAL_TIMEOUT_START_SEND, MagicMock())
    @patch(ENGINE_SIGNAL_TIMEOUT_END_SEND, MagicMock())
    @patch(SIGNAL_VALVE_SEND, MagicMock())
    def test_handle__execute_return_false_and_not_ignore_error(self):
        for loop, timeout in itertools.product((1, 2), (5, None)):
            root_pipeline_data = "root_pipeline_data"
            ex_data = "ex_data"
            top_context = MockContext()

            process = MockPipelineProcess(root_pipeline_data=root_pipeline_data, top_pipeline_context=top_context)
            service_act = ServiceActObject(
                interval=None,
                execute_return=False,
                error_ignorable=False,
                timeout=timeout,
                data=MockData(get_one_of_outputs_return=ex_data),
            )
            status = MockStatus(loop=loop)

            with patch(PIPELINE_STATUS_GET, MagicMock(return_value=status)):

                hdl_result = handlers.service_activity_handler(process, service_act, status)

                if loop > 1:
                    service_act.prepare_rerun_data.assert_called_once()
                    top_context.recover_variable.assert_called_once()
                else:
                    service_act.prepare_rerun_data.assert_not_called()

                self.assertEqual(
                    service_act.data.inputs._loop, status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET
                )
                self.assertEqual(
                    service_act.data.outputs._loop, status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET
                )

                top_context.extract_output.assert_called_once_with(service_act, set_miss=False)

                service_act_h.hydrate_node_data.assert_called_once()

                if timeout:
                    signals.service_activity_timeout_monitor_start.send.assert_called_once_with(
                        sender=service_act.__class__,
                        node_id=service_act.id,
                        version=status.version,
                        root_pipeline_id=process.root_pipeline.id,
                        countdown=service_act.timeout,
                    )
                else:
                    signals.service_activity_timeout_monitor_start.send.assert_not_called()

                service_act.setup_runtime_attrs.assert_called_once_with(
                    id=service_act.id, root_pipeline_id=process.root_pipeline_id
                )

                service_act.execute.assert_called_once_with(root_pipeline_data)

                service_act.data.get_one_of_outputs.assert_called_once_with("ex_data")

                Status.objects.fail.assert_called_once_with(service_act, ex_data)

                service_act.failure_handler.assert_called_once_with(process.root_pipeline.data)

                if timeout:
                    signals.service_activity_timeout_monitor_end.send.assert_called_once_with(
                        sender=service_act.__class__, node_id=service_act.id, version=status.version
                    )
                else:
                    signals.service_activity_timeout_monitor_end.send.assert_not_called()

                valve.send.assert_called_once_with(
                    signals,
                    "activity_failed",
                    sender=process.root_pipeline,
                    pipeline_id=process.root_pipeline.id,
                    pipeline_activity_id=service_act.id,
                    subprocess_id_stack=process.subprocess_stack,
                )

                self.assertIsNone(hdl_result.next_node)
                self.assertFalse(hdl_result.should_return)
                self.assertTrue(hdl_result.should_sleep)

                # reset mock
                service_act_h.hydrate_node_data.reset_mock()
                signals.service_activity_timeout_monitor_start.send.reset_mock()
                Status.objects.fail.reset_mock()
                signals.service_activity_timeout_monitor_end.send.reset_mock()
                valve.send.reset_mock()

    @patch(PIPELINE_SCHEDULE_SERVICE_SET_SCHEDULE, MagicMock())
    @patch(SERVICE_ACT_HYDRATE_NODE_DATA, MagicMock())
    @patch(ENGINE_SIGNAL_TIMEOUT_START_SEND, MagicMock())
    @patch(ENGINE_SIGNAL_TIMEOUT_END_SEND, MagicMock())
    @patch(SIGNAL_VALVE_SEND, MagicMock())
    def test_handle__execute_return_true_and_is_ignore_error(self):
        for loop, timeout, need_schedule, finish_call_success in itertools.product(
            (1, 2), (5, None), (True, False), (True, False)
        ):
            root_pipeline_data = "root_pipeline_data"
            ex_data = "ex_data"
            top_context = MockContext()

            process = MockPipelineProcess(root_pipeline_data=root_pipeline_data, top_pipeline_context=top_context)
            service_act = ServiceActObject(
                interval=None,
                execute_return=True,
                error_ignorable=True,
                timeout=timeout,
                need_schedule=need_schedule,
                result_bit=False,
                data=MockData(get_one_of_outputs_return={"ex_data": ex_data, ServiceActivity.result_bit: False}),
            )
            status = MockStatus(loop=loop)

            with patch(PIPELINE_STATUS_GET, MagicMock(return_value=status)):
                with patch(PIPELINE_STATUS_FINISH, MagicMock(return_value=finish_call_success)):

                    hdl_result = handlers.service_activity_handler(process, service_act, status)

                    if loop > 1:
                        service_act.prepare_rerun_data.assert_called_once()
                        top_context.recover_variable.assert_called_once()
                    else:
                        service_act.prepare_rerun_data.assert_not_called()

                    self.assertEqual(
                        service_act.data.inputs._loop, status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET
                    )
                    self.assertEqual(
                        service_act.data.outputs._loop, status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET
                    )

                    service_act_h.hydrate_node_data.assert_called_once()

                    if timeout:
                        signals.service_activity_timeout_monitor_start.send.assert_called_once_with(
                            sender=service_act.__class__,
                            node_id=service_act.id,
                            version=status.version,
                            root_pipeline_id=process.root_pipeline.id,
                            countdown=service_act.timeout,
                        )
                    else:
                        signals.service_activity_timeout_monitor_start.send.assert_not_called()

                    service_act.setup_runtime_attrs.assert_called_once_with(
                        id=service_act.id, root_pipeline_id=process.root_pipeline_id
                    )

                    service_act.execute.assert_called_once_with(root_pipeline_data)

                    service_act.ignore_error.assert_not_called()

                    service_act.data.set_outputs.assert_not_called()

                    ScheduleService.objects.set_schedule.assert_not_called()

                    top_context.extract_output.assert_has_calls(
                        [mock.call(service_act, set_miss=False), mock.call(service_act)]
                    )

                    if timeout:
                        signals.service_activity_timeout_monitor_end.send.assert_called_once_with(
                            sender=service_act.__class__, node_id=service_act.id, version=status.version
                        )
                    else:
                        signals.service_activity_timeout_monitor_end.send.assert_not_called()

                    Status.objects.finish.assert_called_once_with(service_act, True)

                    if finish_call_success:
                        self.assertEqual(hdl_result.next_node, service_act.next())
                        self.assertFalse(hdl_result.should_return)
                        self.assertFalse(hdl_result.should_sleep)
                    else:
                        self.assertIsNone(hdl_result.next_node)
                        self.assertFalse(hdl_result.should_return)
                        self.assertTrue(hdl_result.should_sleep)

                    # reset mock
                    service_act_h.hydrate_node_data.reset_mock()
                    signals.service_activity_timeout_monitor_start.send.reset_mock()
                    Status.objects.finish.reset_mock()
                    signals.service_activity_timeout_monitor_end.send.reset_mock()
                    valve.send.reset_mock()

    @patch(PIPELINE_SCHEDULE_SERVICE_SET_SCHEDULE, MagicMock())
    @patch(PIPELINE_DATA_WRITE_NODE_DATA, MagicMock())
    @patch(PIPELINE_STATUS_FINISH, MagicMock())
    @patch(SERVICE_ACT_HYDRATE_NODE_DATA, MagicMock())
    @patch(ENGINE_SIGNAL_TIMEOUT_START_SEND, MagicMock())
    @patch(ENGINE_SIGNAL_TIMEOUT_END_SEND, MagicMock())
    def test_handle__execute_return_true_and_need_schedule(self):
        for loop, timeout, error_ignore in itertools.product((1, 2), (5, None), (True, False)):
            root_pipeline_data = "root_pipeline_data"
            ex_data = "ex_data"
            top_context = MockContext()

            process = MockPipelineProcess(root_pipeline_data=root_pipeline_data, top_pipeline_context=top_context)
            service_act = ServiceActObject(
                interval=None,
                execute_return=True,
                error_ignorable=error_ignore,
                timeout=timeout,
                need_schedule=True,
                result_bit=True,
                data=MockData(get_one_of_outputs_return={"ex_data": ex_data, ServiceActivity.result_bit: False}),
            )

            status = MockStatus(loop=loop)

            with patch(PIPELINE_STATUS_GET, MagicMock(return_value=status)):

                hdl_result = handlers.service_activity_handler(process, service_act, status)

                if loop > 1:
                    service_act.prepare_rerun_data.assert_called_once()
                    top_context.recover_variable.assert_called_once()
                else:
                    service_act.prepare_rerun_data.assert_not_called()

                self.assertEqual(
                    service_act.data.inputs._loop, status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET
                )
                self.assertEqual(
                    service_act.data.outputs._loop, status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET
                )

                service_act_h.hydrate_node_data.assert_called_once()

                if timeout:
                    signals.service_activity_timeout_monitor_start.send.assert_called_once_with(
                        sender=service_act.__class__,
                        node_id=service_act.id,
                        version=status.version,
                        root_pipeline_id=process.root_pipeline.id,
                        countdown=service_act.timeout,
                    )
                else:
                    signals.service_activity_timeout_monitor_start.send.assert_not_called()

                service_act.setup_runtime_attrs.assert_called_once_with(
                    id=service_act.id, root_pipeline_id=process.root_pipeline_id
                )

                service_act.execute.assert_called_once_with(root_pipeline_data)

                service_act.ignore_error.assert_not_called()

                service_act.data.set_outputs.assert_not_called()

                Data.objects.write_node_data.assert_called_once_with(service_act)

                top_context.extract_output.assert_called_once_with(service_act, set_miss=False)

                signals.service_activity_timeout_monitor_end.send.assert_not_called()

                Status.objects.finish.assert_not_called()

                self.assertIsNone(hdl_result.next_node)
                self.assertTrue(hdl_result.should_return)
                self.assertTrue(hdl_result.should_sleep)
                self.assertEqual(hdl_result.after_sleep_call, ScheduleService.objects.set_schedule)
                self.assertEqual(hdl_result.args, [])
                self.assertEqual(
                    hdl_result.kwargs,
                    dict(
                        activity_id=service_act.id,
                        service_act=service_act.shell(),
                        process_id=process.id,
                        version=status.version,
                        parent_data=process.top_pipeline.data,
                    ),
                )

                # reset mock
                service_act_h.hydrate_node_data.reset_mock()
                signals.service_activity_timeout_monitor_start.send.reset_mock()
                Status.objects.finish.reset_mock()
                Data.objects.write_node_data.reset_mock()
                ScheduleService.objects.set_schedule.reset_mock()
                signals.service_activity_timeout_monitor_end.send.reset_mock()

    @patch(PIPELINE_SCHEDULE_SERVICE_SET_SCHEDULE, MagicMock())
    @patch(PIPELINE_DATA_WRITE_NODE_DATA, MagicMock())
    @patch(PIPELINE_STATUS_FINISH, MagicMock())
    @patch(SERVICE_ACT_HYDRATE_NODE_DATA, MagicMock())
    @patch(ENGINE_SIGNAL_TIMEOUT_START_SEND, MagicMock())
    @patch(ENGINE_SIGNAL_TIMEOUT_END_SEND, MagicMock())
    def test_handle__execute_return_true_and_do_not_need_schedule(self):
        for loop, timeout, error_ignore, finish_call_success, on_retry in itertools.product(
            (1, 2), (5, None), (True, False), (True, False), (True, False)
        ):
            root_pipeline_data = "root_pipeline_data"
            ex_data = "ex_data"
            top_context = MockContext()

            process = MockPipelineProcess(root_pipeline_data=root_pipeline_data, top_pipeline_context=top_context)
            service_act = ServiceActObject(
                interval=None,
                execute_return=True,
                error_ignorable=error_ignore,
                timeout=timeout,
                need_schedule=False,
                result_bit=True,
                data=MockData(get_one_of_outputs_return={"ex_data": ex_data, ServiceActivity.result_bit: False}),
                on_retry=on_retry,
            )
            status = MockStatus(loop=loop)

            with patch(PIPELINE_STATUS_GET, MagicMock(return_value=status)):
                with patch(PIPELINE_STATUS_FINISH, MagicMock(return_value=finish_call_success)):

                    hdl_result = handlers.service_activity_handler(process, service_act, status)

                    if loop > 1 and not on_retry:
                        service_act.prepare_rerun_data.assert_called_once()
                        top_context.recover_variable.assert_called_once()
                        service_act.retry_at_current_exec.assert_not_called()
                    else:
                        service_act.prepare_rerun_data.assert_not_called()

                    if on_retry:
                        service_act.retry_at_current_exec.assert_called_once()

                    self.assertEqual(
                        service_act.data.inputs._loop, status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET
                    )
                    self.assertEqual(
                        service_act.data.outputs._loop, status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET
                    )

                    service_act_h.hydrate_node_data.assert_called_once()

                    if timeout:
                        signals.service_activity_timeout_monitor_start.send.assert_called_once_with(
                            sender=service_act.__class__,
                            node_id=service_act.id,
                            version=status.version,
                            root_pipeline_id=process.root_pipeline.id,
                            countdown=service_act.timeout,
                        )
                    else:
                        signals.service_activity_timeout_monitor_start.send.assert_not_called()

                    service_act.setup_runtime_attrs.assert_called_once_with(
                        id=service_act.id, root_pipeline_id=process.root_pipeline_id
                    )

                    service_act.execute.assert_called_once_with(root_pipeline_data)

                    service_act.ignore_error.assert_not_called()

                    service_act.data.set_outputs.assert_not_called()

                    ScheduleService.objects.set_schedule.assert_not_called()

                    top_context.extract_output.assert_has_calls(
                        [mock.call(service_act, set_miss=False), mock.call(service_act)]
                    )

                    if timeout:
                        signals.service_activity_timeout_monitor_end.send.assert_called_once_with(
                            sender=service_act.__class__, node_id=service_act.id, version=status.version
                        )
                    else:
                        signals.service_activity_timeout_monitor_end.send.assert_not_called()

                    Status.objects.finish.assert_called_once_with(service_act, False)

                    if finish_call_success:
                        self.assertEqual(hdl_result.next_node, service_act.next())
                        self.assertFalse(hdl_result.should_return)
                        self.assertFalse(hdl_result.should_sleep)
                    else:
                        self.assertIsNone(hdl_result.next_node)
                        self.assertFalse(hdl_result.should_return)
                        self.assertTrue(hdl_result.should_sleep)

                    service_act_h.hydrate_node_data.reset_mock()
                    signals.service_activity_timeout_monitor_start.send.reset_mock()
                    signals.service_activity_timeout_monitor_end.send.reset_mock()
                    Status.objects.finish.reset_mock()
