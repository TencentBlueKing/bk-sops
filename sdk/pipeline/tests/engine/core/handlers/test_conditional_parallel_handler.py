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

from pipeline.core.flow.gateway import ConditionalParallelGateway
from pipeline.engine.core import handlers
from pipeline.engine.core.handlers import conditional_parallel
from pipeline.engine.models import PipelineProcess, Status
from pipeline.exceptions import ConditionExhaustedException, PipelineException
from pipeline.tests.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa

handlers.conditional_parallel_handler = handlers.ConditionalParallelGatewayHandler()

hydrate_context = "hydrate_context"
targets = [IdentifyObject(), IdentifyObject(), IdentifyObject()]


class ConditionalParallelGatewayHandlerTestCase(TestCase):
    def test_element_cls(self):
        self.assertEqual(handlers.ConditionalParallelGatewayHandler.element_cls(), ConditionalParallelGateway)

    @patch(CPG_HYDRATE_DATA, MagicMock(return_value=hydrate_context))
    @patch(PIPELINE_STATUS_FAIL, MagicMock())
    def test_handle__get_targets_raise(self):
        e_message = "e_message"
        context_variables = "variables"

        cpg = MagicMock()
        cpg.targets_meet_condition = MagicMock(side_effect=ConditionExhaustedException(e_message))
        status = MockStatus(loop=0)
        process = MockPipelineProcess(top_pipeline_context=MockContext(variables=context_variables))

        result = handlers.conditional_parallel_handler(process, cpg, status)
        self.assertIsNone(result.next_node)
        self.assertTrue(result.should_return)
        self.assertTrue(result.should_sleep)

        conditional_parallel.hydrate_data.assert_called_once_with(context_variables)

        cpg.targets_meet_condition.assert_called_once_with(hydrate_context)

        Status.objects.fail.assert_called_once_with(cpg, ex_data=e_message)

        process.join.assert_not_called()

    @patch(CPG_HYDRATE_DATA, MagicMock(return_value=hydrate_context))
    @patch(PIPELINE_STATUS_FAIL, MagicMock())
    def test_handle__fork_child_raise(self):
        e_message = "e_message"
        context_variables = "variables"
        converge_gateway_id = "converge_gateway_id"

        cpg = MagicMock()
        cpg.targets_meet_condition = MagicMock(return_value=targets)
        cpg.converge_gateway_id = converge_gateway_id
        status = MockStatus(loop=0)
        process = MockPipelineProcess(top_pipeline_context=MockContext(variables=context_variables))

        with patch(PIPELINE_PROCESS_FORK_CHILD, MagicMock(side_effect=PipelineException(e_message))):
            result = handlers.conditional_parallel_handler(process, cpg, status)
            self.assertIsNone(result.next_node)
            self.assertTrue(result.should_return)
            self.assertTrue(result.should_sleep)

            conditional_parallel.hydrate_data.assert_called_once_with(context_variables)

            cpg.targets_meet_condition.assert_called_once_with(hydrate_context)

            Status.objects.fail.assert_called_once_with(cpg, ex_data=e_message)

            process.join.assert_not_called()

    @patch(CPG_HYDRATE_DATA, MagicMock(return_value=hydrate_context))
    @patch(PIPELINE_STATUS_FINISH, MagicMock())
    def test_handle__normal(self):
        context_variables = "variables"
        converge_gateway_id = "converge_gateway_id"
        children = [1, 2, 3]

        for loop in [0, 1, 2, 3]:
            cpg = MagicMock()
            cpg.targets_meet_condition = MagicMock(return_value=targets)
            cpg.converge_gateway_id = converge_gateway_id
            status = MockStatus(loop=loop)
            process = MockPipelineProcess(top_pipeline_context=MockContext(variables=context_variables))

            with patch(PIPELINE_PROCESS_FORK_CHILD, MagicMock(side_effect=children)):
                result = handlers.conditional_parallel_handler(process, cpg, status)
                self.assertIsNone(result.next_node)
                self.assertTrue(result.should_return)
                self.assertTrue(result.should_sleep)

                if loop > 1:
                    process.top_pipeline.context.recover_variable.assert_called_once()

                conditional_parallel.hydrate_data.assert_called_once_with(context_variables)

                cpg.targets_meet_condition.assert_called_once_with(hydrate_context)

                PipelineProcess.objects.fork_child.assert_has_calls(
                    [
                        mock.call(
                            parent=process, current_node_id=targets[0].id, destination_id=cpg.converge_gateway_id
                        ),
                        mock.call(
                            parent=process, current_node_id=targets[1].id, destination_id=cpg.converge_gateway_id
                        ),
                        mock.call(
                            parent=process, current_node_id=targets[2].id, destination_id=cpg.converge_gateway_id
                        ),
                    ]
                )

                process.join.assert_called_once_with(children)

                Status.objects.finish.assert_called_once_with(cpg)

                conditional_parallel.hydrate_data.reset_mock()

                Status.objects.finish.reset_mock()
