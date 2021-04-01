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

from pipeline.core.flow.gateway import ConvergeGateway
from pipeline.engine.core import handlers
from pipeline.engine.exceptions import ChildDataSyncError
from pipeline.engine.models import Status
from pipeline.tests.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa

handlers.converge_gateway_handler = handlers.ConvergeGatewayHandler()


class ConvergeGatewayHandlerTestCase(TestCase):
    def test_element_cls(self):
        self.assertEqual(handlers.ConvergeGatewayHandler.element_cls(), ConvergeGateway)

    @patch(PIPELINE_STATUS_FINISH, MagicMock())
    def test_handle__normal_has_children(self):
        converge_gateway = MockConvergeGateway()
        process = MockPipelineProcess(children=[1, 2, 3])

        hdl_result = handlers.converge_gateway_handler(process, converge_gateway, MockStatus())

        process.sync_with_children.assert_called_once()

        Status.objects.finish.assert_called_once_with(converge_gateway)

        self.assertEqual(hdl_result.next_node, converge_gateway.next())
        self.assertFalse(hdl_result.should_return)
        self.assertFalse(hdl_result.should_sleep)

    @patch(PIPELINE_STATUS_FINISH, MagicMock())
    def test_handle__normal_without_children(self):
        converge_gateway = MockConvergeGateway()
        process = MockPipelineProcess(children=[])

        hdl_result = handlers.converge_gateway_handler(process, converge_gateway, MockStatus())

        process.sync_with_children.assert_not_called()

        Status.objects.finish.assert_called_once_with(converge_gateway)

        self.assertEqual(hdl_result.next_node, converge_gateway.next())
        self.assertFalse(hdl_result.should_return)
        self.assertFalse(hdl_result.should_sleep)

    @patch(PIPELINE_STATUS_FINISH, MagicMock())
    @patch(PIPELINE_STATUS_FAIL, MagicMock())
    def test_handle__sync_raise_exception(self):
        converge_gateway = MockConvergeGateway()
        e = ChildDataSyncError()
        process = MockPipelineProcess(children=[1, 2, 3], sync_exception=e)

        hdl_result = handlers.converge_gateway_handler(process, converge_gateway, MockStatus())

        process.sync_with_children.assert_called_once()

        Status.objects.fail.assert_called_once_with(
            converge_gateway, ex_data="Sync branch context error, check data backend status please."
        )

        Status.objects.finish.assert_not_called()

        self.assertIsNone(hdl_result.next_node)
        self.assertTrue(hdl_result.should_return)
        self.assertTrue(hdl_result.should_sleep)
