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

from pipeline.core.data.base import DataObject as RealDataObject
from pipeline.core.flow.activity import SubProcess
from pipeline.core.flow.event import EmptyEndEvent
from pipeline.engine import states
from pipeline.engine.core import handlers
from pipeline.engine.models import Data, Status
from pipeline.tests.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa

handlers.empty_end_event_handler = handlers.EmptyEndEventHandler()


class EmptyEndEventHandlerTestCase(TestCase):
    def test_element_cls(self):
        self.assertEqual(handlers.EmptyEndEventHandler.element_cls(), EmptyEndEvent)

    @patch(PIPELINE_STATUS_FINISH, MagicMock())
    def test_handle__is_subprocess(self):
        end_event = EndEventObject()
        context = MockContext()
        sub_pipeline = PipelineObject(context=MockContext())
        process = MockPipelineProcess(
            top_pipeline=PipelineObject(context=context, node=MockSubprocessActivity()),
            pipeline_stack=["root_pipeline", sub_pipeline],
        )

        hdl_result = handlers.empty_end_event_handler(process, end_event, MockStatus())

        sub_pipeline.context.write_output.assert_called_once_with(sub_pipeline)

        sub_process_node = process.top_pipeline.node(sub_pipeline.id)
        Status.objects.finish.assert_has_calls([mock.call(end_event), mock.call(sub_process_node)])

        process.top_pipeline.context.extract_output.assert_called_once_with(sub_process_node)

        self.assertEqual(hdl_result.next_node, sub_process_node.next())
        self.assertFalse(hdl_result.should_sleep)
        self.assertFalse(hdl_result.should_return)

    @patch(PIPELINE_STATUS_SELECT_FOR_UPDATE, MagicMock(return_value=MockQuerySet()))
    @patch(PIPELINE_STATUS_FINISH, MagicMock())
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock())
    @patch(PIPELINE_DATA_WRITE_NODE_DATA, MagicMock())
    def test_handle__is_not_subprocess(self):
        context = MockContext()
        subproc_1 = SubProcess(id=uniqid(), pipeline=PipelineObject(context=MockContext(), data=RealDataObject({})))
        subproc_2 = SubProcess(id=uniqid(), pipeline=PipelineObject(context=MockContext(), data=RealDataObject({})))
        spec = PipelineSpecObject(activities=[ServiceActObject(), subproc_1, subproc_2])
        process = MockPipelineProcess(top_pipeline_context=context, top_pipeline_spec=spec)
        top_pipeline = process.top_pipeline
        end_event = EndEventObject()

        hdl_result = handlers.empty_end_event_handler(process, end_event, MockStatus())

        top_pipeline.context.write_output.assert_called_once_with(top_pipeline)

        Data.objects.write_node_data.assert_called_once_with(top_pipeline)

        Status.objects.finish.assert_called_once_with(end_event)

        Status.objects.transit.assert_called_once_with(top_pipeline.id, to_state=states.FINISHED, is_pipeline=True)

        end_event.pipeline_finish.assert_called_once_with(process.root_pipeline.id)

        subproc_1.pipeline.context.clear.assert_called_once()

        subproc_2.pipeline.context.clear.assert_called_once()

        top_pipeline.context.clear.assert_called_once()

        process.destroy.assert_called_once()

        self.assertIsNone(hdl_result.next_node)
        self.assertTrue(hdl_result.should_return)
        self.assertFalse(hdl_result.should_sleep)
