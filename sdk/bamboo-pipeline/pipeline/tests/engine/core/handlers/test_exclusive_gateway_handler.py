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

from pipeline.core.flow.gateway import ExclusiveGateway
from pipeline.engine.core import handlers
from pipeline.engine.core.handlers import exclusive_gateway as exg_h
from pipeline.engine.models import Status
from pipeline.exceptions import PipelineException
from pipeline.tests.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa

handlers.exclusive_gateway_handler = handlers.ExclusiveGatewayHandler()


class ExclusiveGatewayHandlerTestCase(TestCase):
    def test_element_cls(self):
        self.assertEqual(handlers.ExclusiveGatewayHandler.element_cls(), ExclusiveGateway)

    @patch(PIPELINE_STATUS_FINISH, MagicMock())
    def test_handle__normal(self):
        for loop in (1, 2, 3):
            hydrate_data_return = "hydrate_data_return"
            exclusive_gateway = MockExclusiveGateway()
            context = MockContext()
            process = MockPipelineProcess(top_pipeline_context=context)

            with patch(EXG_HYDRATE_DATA, MagicMock(return_value=hydrate_data_return)):
                hdl_result = handlers.exclusive_gateway_handler(process, exclusive_gateway, MockStatus(loop=loop))

                if loop > 1:
                    context.recover_variable.assert_called_once()
                else:
                    context.recover_variable.assert_not_called()

                exg_h.hydrate_data.assert_called_once_with(context.variables)

                exclusive_gateway.next.assert_called_once_with(hydrate_data_return)

                Status.objects.finish.assert_called_once_with(exclusive_gateway)

                self.assertEqual(hdl_result.next_node, exclusive_gateway.next())
                self.assertFalse(hdl_result.should_return)
                self.assertFalse(hdl_result.should_sleep)

            Status.objects.finish.reset_mock()

    @patch(PIPELINE_STATUS_FINISH, MagicMock())
    @patch(PIPELINE_STATUS_FAIL, MagicMock())
    def test_handle__next_raise_exception(self):
        hydrate_data_return = "hydrate_data_return"
        e = PipelineException("ex_data")
        exclusive_gateway = MockExclusiveGateway(next_exception=e)
        context = MockContext()
        process = MockPipelineProcess(top_pipeline_context=context)

        with patch(EXG_HYDRATE_DATA, MagicMock(return_value=hydrate_data_return)):
            hdl_result = handlers.exclusive_gateway_handler(process, exclusive_gateway, MockStatus())

            exg_h.hydrate_data.assert_called_once_with(context.variables)

            exclusive_gateway.next.assert_called_once_with(hydrate_data_return)

            Status.objects.fail.assert_called_once_with(exclusive_gateway, ex_data=str(e))

            Status.objects.finish.assert_not_called()

            self.assertIsNone(hdl_result.next_node)
            self.assertTrue(hdl_result.should_return)
            self.assertTrue(hdl_result.should_sleep)
