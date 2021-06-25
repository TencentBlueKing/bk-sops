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

from gcloud import err_code
from gcloud.taskflow3.models import TaskFlowInstance

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class GetNodeDetailTestCase(TestCase):
    def test_node_does_not_exist(self):
        taskflow = TaskFlowInstance()
        taskflow.has_node = MagicMock(return_value=False)

        detail = taskflow.get_node_detail(node_id="node_id", username="username")
        self.assertFalse(detail["result"])
        self.assertEqual(detail["code"], err_code.REQUEST_PARAM_INVALID.code)

    def test_get_node_data_err(self):
        taskflow = TaskFlowInstance()
        taskflow.engine_ver = 2
        taskflow.has_node = MagicMock(return_value=True)
        dispatcher = MagicMock()
        get_node_data_return = {"result": False}
        dispatcher.get_node_data = MagicMock(return_value=get_node_data_return)

        with patch(TASKFLOW_MODEL_NODE_CMD_DISPATCHER, MagicMock(return_value=dispatcher)):
            detail = taskflow.get_node_detail(node_id="node_id", username="username")

        self.assertEqual(detail, get_node_data_return)

    def test_get_node_detail_err(self):
        taskflow = TaskFlowInstance()
        taskflow.engine_ver = 2
        taskflow.has_node = MagicMock(return_value=True)
        dispatcher = MagicMock()
        get_node_data_return = {"result": True, "data": {}}
        get_node_detail_return = {"result": False}
        dispatcher.get_node_data = MagicMock(return_value=get_node_data_return)
        dispatcher.get_node_detail = MagicMock(return_value=get_node_detail_return)

        with patch(TASKFLOW_MODEL_NODE_CMD_DISPATCHER, MagicMock(return_value=dispatcher)):
            detail = taskflow.get_node_detail(node_id="node_id", username="username")

        self.assertEqual(detail, get_node_detail_return)

    def test_include_data_is_false(self):
        taskflow = TaskFlowInstance()
        taskflow.engine_ver = 2
        taskflow.has_node = MagicMock(return_value=True)
        dispatcher = MagicMock()
        get_node_data_return = {"result": True, "data": {}}
        get_node_detail_return = {"result": True, "data": {}}
        dispatcher.get_node_data = MagicMock(return_value=get_node_data_return)
        dispatcher.get_node_detail = MagicMock(return_value=get_node_detail_return)
        dispatcher_init = MagicMock(return_value=dispatcher)

        node_id = "node_id"
        username = "username"
        component_code = "component_code"
        subprocess_stack = ["1"]
        loop = 1
        include_data = False

        with patch(TASKFLOW_MODEL_NODE_CMD_DISPATCHER, dispatcher_init):
            detail = taskflow.get_node_detail(
                node_id=node_id,
                username=username,
                component_code=component_code,
                subprocess_stack=subprocess_stack,
                loop=loop,
                include_data=include_data,
            )

        dispatcher_init.assert_called_once_with(engine_ver=taskflow.engine_ver, node_id=node_id)
        dispatcher.get_node_data.assert_not_called()
        dispatcher.get_node_detail.assert_called_once_with(
            username=username,
            component_code=component_code,
            subprocess_stack=subprocess_stack,
            pipeline_instance=taskflow.pipeline_instance,
            loop=loop,
        )
        self.assertEqual(detail, {"code": 0, "data": {}, "message": "", "result": True})

    def test_success(self):
        taskflow = TaskFlowInstance()
        taskflow.engine_ver = 2
        taskflow.has_node = MagicMock(return_value=True)
        dispatcher = MagicMock()
        get_node_data_return = {"result": True, "data": {"data": "data"}}
        get_node_detail_return = {"result": True, "data": {"detail": "detail"}}
        dispatcher.get_node_data = MagicMock(return_value=get_node_data_return)
        dispatcher.get_node_detail = MagicMock(return_value=get_node_detail_return)
        dispatcher_init = MagicMock(return_value=dispatcher)

        node_id = "node_id"
        username = "username"
        component_code = "component_code"
        subprocess_stack = ["1"]
        loop = 1
        include_data = True

        with patch(TASKFLOW_MODEL_NODE_CMD_DISPATCHER, dispatcher_init):
            detail = taskflow.get_node_detail(
                node_id=node_id,
                username=username,
                component_code=component_code,
                subprocess_stack=subprocess_stack,
                loop=loop,
                include_data=include_data,
            )

        dispatcher_init.assert_called_once_with(engine_ver=taskflow.engine_ver, node_id=node_id)
        dispatcher.get_node_data.assert_called_once_with(
            username=username,
            component_code=component_code,
            subprocess_stack=subprocess_stack,
            pipeline_instance=taskflow.pipeline_instance,
            loop=loop,
        )
        dispatcher.get_node_detail.assert_called_once_with(
            username=username,
            component_code=component_code,
            subprocess_stack=subprocess_stack,
            pipeline_instance=taskflow.pipeline_instance,
            loop=loop,
        )
        self.assertEqual(
            detail, {"code": 0, "data": {"data": "data", "detail": "detail"}, "message": "", "result": True}
        )
