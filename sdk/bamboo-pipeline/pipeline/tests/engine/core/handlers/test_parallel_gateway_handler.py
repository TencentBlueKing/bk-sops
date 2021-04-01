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

from pipeline.core.flow.gateway import ParallelGateway
from pipeline.engine.core import handlers
from pipeline.engine.models import PipelineProcess, Status
from pipeline.exceptions import PipelineException
from pipeline.tests.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa

handlers.parallel_gateway_handler = handlers.ParallelGatewayHandler()


class ParallelGatewayHandlerTestCase(TestCase):
    def test_element_cls(self):
        self.assertEqual(handlers.ParallelGatewayHandler.element_cls(), ParallelGateway)

    @patch(PIPELINE_STATUS_FINISH, MagicMock())
    def test_handle__normal(self):
        process = MockPipelineProcess()
        parallel_gateway = MockParallelGateway()
        children = [MockPipelineProcess() for _ in range(len(parallel_gateway.outgoing.all_target_node()))]

        with patch(PIPELINE_PROCESS_FORK_CHILD, MagicMock(side_effect=children)):
            hdl_result = handlers.parallel_gateway_handler(process, parallel_gateway, MockStatus())

            fork_child_calls = [
                mock.call(
                    parent=process, current_node_id=target.id, destination_id=parallel_gateway.converge_gateway_id
                )
                for target in parallel_gateway.outgoing.all_target_node()
            ]
            PipelineProcess.objects.fork_child.assert_has_calls(fork_child_calls)

            process.join.assert_called_once_with(children)

            Status.objects.finish.assert_called_once_with(parallel_gateway)

            self.assertIsNone(hdl_result.next_node)
            self.assertTrue(hdl_result.should_return)
            self.assertTrue(hdl_result.should_sleep)

    @patch(PIPELINE_STATUS_FINISH, MagicMock())
    @patch(PIPELINE_STATUS_FAIL, MagicMock())
    def test_handle__fork_raise_exception(self):
        process = MockPipelineProcess()
        parallel_gateway = MockParallelGateway()
        e_msg = "e_msg"

        with patch(PIPELINE_PROCESS_FORK_CHILD, MagicMock(side_effect=PipelineException(e_msg))):
            hdl_result = handlers.parallel_gateway_handler(process, parallel_gateway, MockStatus())

            PipelineProcess.objects.fork_child.assert_called()

            Status.objects.fail.assert_called_once_with(parallel_gateway, e_msg)

            process.join.assert_not_called()

            Status.objects.finish.assert_not_called()

            self.assertIsNone(hdl_result.next_node)
            self.assertTrue(hdl_result.should_return)
            self.assertTrue(hdl_result.should_sleep)
