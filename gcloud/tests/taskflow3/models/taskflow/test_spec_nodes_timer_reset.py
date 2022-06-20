# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase

from gcloud import err_code
from gcloud.taskflow3.models import TaskFlowInstance

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class SpecNodesTimerResetTestCase(TestCase):
    def test_node_does_not_exist(self):
        taskflow = TaskFlowInstance()
        taskflow.id = 1
        taskflow.has_node = MagicMock(return_value=False)

        detail = taskflow.spec_nodes_timer_reset(node_id="node_id", username="username", inputs="inputs")
        self.assertFalse(detail["result"])
        self.assertEqual(detail["code"], err_code.REQUEST_PARAM_INVALID.code)

    def test_forced_fail_fail(self):
        taskflow = TaskFlowInstance()
        taskflow.id = 1
        taskflow.engine_ver = 2
        taskflow.has_node = MagicMock(return_value=True)
        dispatcher = MagicMock()
        dispatch_return = {"result": False, "data": {"data": "data"}}
        dispatcher.dispatch = MagicMock(return_value=dispatch_return)
        dispatcher_init = MagicMock(return_value=dispatcher)

        node_id = "node_id"
        username = "username"
        inputs = "inputs"

        with patch(TASKFLOW_MODEL_NODE_CMD_DISPATCHER, dispatcher_init):
            detail = taskflow.spec_nodes_timer_reset(node_id=node_id, username=username, inputs=inputs)

        dispatcher_init.assert_called_once_with(engine_ver=taskflow.engine_ver, node_id=node_id, taskflow_id=1)
        dispatcher.dispatch.assert_called_once_with(
            command="forced_fail", operator=username, send_post_set_state_signal=False
        )
        self.assertEqual(detail, dispatch_return)

    def test_retry_fail(self):
        taskflow = TaskFlowInstance()
        taskflow.id = 1
        taskflow.engine_ver = 2
        taskflow.has_node = MagicMock(return_value=True)
        dispatcher = MagicMock()
        forced_fail_return = {"result": True, "data": {"data": "data"}}
        retry_return = {"result": False, "data": {"data": "data"}}
        dispatcher.dispatch = MagicMock(side_effect=[forced_fail_return, retry_return])
        dispatcher_init = MagicMock(return_value=dispatcher)

        node_id = "node_id"
        username = "username"
        inputs = "inputs"

        with patch(TASKFLOW_MODEL_NODE_CMD_DISPATCHER, dispatcher_init):
            detail = taskflow.spec_nodes_timer_reset(node_id=node_id, username=username, inputs=inputs)

        dispatcher_init.assert_called_once_with(engine_ver=taskflow.engine_ver, node_id=node_id, taskflow_id=1)
        dispatcher.dispatch.assert_has_calls(
            [
                call(command="forced_fail", operator=username, send_post_set_state_signal=False),
                call(command="retry", operator=username, inputs="inputs"),
            ]
        )
        self.assertEqual(detail, retry_return)

    def test_success(self):
        taskflow = TaskFlowInstance()
        taskflow.id = 1
        taskflow.engine_ver = 2
        taskflow.has_node = MagicMock(return_value=True)
        dispatcher = MagicMock()
        dispatch_return = {"result": True, "data": {"data": "data"}}
        dispatcher.dispatch = MagicMock(return_value=dispatch_return)
        dispatcher_init = MagicMock(return_value=dispatcher)

        node_id = "node_id"
        username = "username"
        inputs = "inputs"

        with patch(TASKFLOW_MODEL_NODE_CMD_DISPATCHER, dispatcher_init):
            detail = taskflow.spec_nodes_timer_reset(node_id=node_id, username=username, inputs=inputs)

        dispatcher_init.assert_called_once_with(engine_ver=taskflow.engine_ver, node_id=node_id, taskflow_id=1)
        dispatcher.dispatch.assert_has_calls(
            [
                call(command="forced_fail", operator=username, send_post_set_state_signal=False),
                call(command="retry", operator=username, inputs="inputs"),
            ]
        )
        self.assertEqual(detail, dispatch_return)
