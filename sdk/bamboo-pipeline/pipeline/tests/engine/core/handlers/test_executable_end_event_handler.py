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

from pipeline.core.flow.event import ExecutableEndEvent
from pipeline.engine.core import handlers
from pipeline.engine.models import Status
from pipeline.tests.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa

handlers.executable_end_event_handler = handlers.ExecutableEndEventHandler()


class ExecutableEndEventHandlerTestCase(TestCase):
    def test_element_cls(self):
        self.assertEqual(handlers.ExecutableEndEventHandler.element_cls(), ExecutableEndEvent)

    @patch(ENGINE_HANDLERS_END_EVENT_HANDLE, MagicMock(return_value="token_1"))
    def test_handle__success(self):
        end_event = ExecutableEndEventObject()
        process = MockPipelineProcess(
            in_subprocess_return=True, root_pipeline=IdentifyObject(), top_pipeline=IdentifyObject()
        )
        status = MockStatus()

        hdl_result = handlers.executable_end_event_handler(process, end_event, status)

        self.assertEqual(hdl_result, "token_1")

        end_event.execute.assert_called_once_with(
            in_subprocess=process.in_subprocess,
            root_pipeline_id=process.root_pipeline.id,
            current_pipeline_id=process.top_pipeline.id,
        )

        super_handle = super(handlers.ExecutableEndEventHandler, handlers.executable_end_event_handler).handle
        super_handle.assert_called_once_with(process, end_event, status)

    @patch(ENGINE_HANDLERS_END_EVENT_HANDLE, MagicMock())
    @patch(PIPELINE_STATUS_FAIL, MagicMock())
    @patch(
        "pipeline.engine.core.handlers.endevent.executable_end_event.traceback.format_exc",
        MagicMock(return_value="token_2"),
    )
    def test_handle__raise_exception(self):
        end_event = ExecutableEndEventObject()
        end_event.execute = MagicMock(side_effect=Exception)
        process = MockPipelineProcess(
            in_subprocess_return=True, root_pipeline=IdentifyObject(), top_pipeline=IdentifyObject()
        )
        status = MockStatus()

        hdl_result = handlers.executable_end_event_handler(process, end_event, status)

        self.assertIsNone(hdl_result.next_node)
        self.assertFalse(hdl_result.should_return)
        self.assertTrue(hdl_result.should_sleep)

        end_event.execute.assert_called_once_with(
            in_subprocess=process.in_subprocess,
            root_pipeline_id=process.root_pipeline.id,
            current_pipeline_id=process.top_pipeline.id,
        )

        self.assertEqual(end_event.data.outputs.ex_data, "token_2")

        Status.objects.fail.assert_called_once_with(end_event, "token_2")

        super_handle = super(handlers.ExecutableEndEventHandler, handlers.executable_end_event_handler).handle
        super_handle.assert_not_called()
