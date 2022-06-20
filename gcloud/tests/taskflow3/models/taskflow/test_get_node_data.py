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
from pipeline.models import PipelineInstance

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class GetNodeDataTestCase(TestCase):
    def test_node_does_not_exist(self):
        taskflow = TaskFlowInstance()
        taskflow.id = 1
        taskflow.has_node = MagicMock(return_value=False)

        data = taskflow.get_node_data(node_id="node_id", username="username")
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)

    def test_success(self):
        taskflow = TaskFlowInstance()
        taskflow.id = 1
        taskflow.engine_ver = 2
        taskflow.has_node = MagicMock(return_value=True)
        taskflow.project_id = 3
        taskflow.pipeline_instance = PipelineInstance()
        dispatcher = MagicMock()
        get_node_data_return = {"code": 0, "data": {"data": "data"}, "message": "", "result": True}
        dispatcher.get_node_data = MagicMock(return_value=get_node_data_return)
        dispatcher_init = MagicMock(return_value=dispatcher)

        node_id = "node_id"
        username = "username"
        component_code = "component_code"
        subprocess_stack = ["1"]
        loop = 1

        with patch(TASKFLOW_MODEL_NODE_CMD_DISPATCHER, dispatcher_init):
            data = taskflow.get_node_data(
                node_id=node_id,
                username=username,
                component_code=component_code,
                subprocess_stack=subprocess_stack,
                loop=loop,
            )

        dispatcher_init.assert_called_once_with(engine_ver=taskflow.engine_ver, node_id=node_id, taskflow_id=1)
        dispatcher.get_node_data.assert_called_once_with(
            username=username,
            component_code=component_code,
            loop=loop,
            pipeline_instance=taskflow.pipeline_instance,
            subprocess_stack=subprocess_stack,
            project_id=taskflow.project_id,
        )
        self.assertEqual(data, get_node_data_return)
