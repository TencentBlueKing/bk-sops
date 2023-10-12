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
from mock import MagicMock, call, patch

from gcloud.shortcuts.message import ATOM_FAILED
from gcloud.taskflow3.celery.tasks import send_taskflow_message
from gcloud.tests.mock_settings import *  # noqa


class SendTaskflowMessageTaskTestCase(TestCase):
    @classmethod
    def generate_taskflow(cls):
        root_taskflow = MagicMock()
        root_taskflow.id = 1
        root_taskflow.engine_ver = 1
        root_taskflow.pipeline_instance = {}
        root_taskflow.project_id = 1

        child_taskflow = MagicMock()
        child_taskflow.id = 2
        child_taskflow.is_child_taskflow = True

        return root_taskflow, child_taskflow

    def test_send_taskflow_message(self):

        get_task_status = MagicMock()
        taskflow = MagicMock()
        taskflow.id = 1
        taskflow_model = MagicMock()
        taskflow_model.objects.get = MagicMock(return_value=taskflow)

        send_task_flow_message = MagicMock()
        with patch(TASKFLOW_TASKS_TASKFLOW_INSTANCE, taskflow_model):
            with patch(TASKFLOW_TASKS_TASK_COMMAND_DISPATCHER_GET_STATUS, get_task_status):
                with patch(TASKFLOW_TASKS_SEND_TASK_FLOW_MESSAGE, send_task_flow_message):
                    send_taskflow_message(taskflow.id, ATOM_FAILED, node_name="test")

        send_task_flow_message.assert_called_once_with(taskflow, ATOM_FAILED, "test")
        get_task_status.assert_not_called()
        taskflow_model.objects.get.assert_called_once_with(id=taskflow.id)

    def test_send_taskflow_message__use_root(self):

        root_taskflow, child_taskflow = self.generate_taskflow()
        taskflow_model = MagicMock()
        taskflow_model.objects.get = MagicMock(side_effect=lambda id: {1: root_taskflow, 2: child_taskflow}[id])

        taskflow_relation = MagicMock()
        taskflow_relation.root_task_id = root_taskflow.id
        taskflow_relation_model = MagicMock()
        taskflow_relation_model.objects.get = MagicMock(return_value=taskflow_relation)
        send_task_flow_message = MagicMock()
        with patch(TASKFLOW_TASKS_TASKFLOW_RELATION, taskflow_relation_model):
            with patch(TASKFLOW_TASKS_TASKFLOW_INSTANCE, taskflow_model):
                with patch(TASKFLOW_TASKS_SEND_TASK_FLOW_MESSAGE, send_task_flow_message):
                    send_taskflow_message(
                        child_taskflow.id,
                        ATOM_FAILED,
                        node_name="test",
                        use_root=True,
                    )

        send_task_flow_message.assert_called_once_with(root_taskflow, ATOM_FAILED, "test")
        taskflow_model.objects.get.assert_has_calls(calls=[call(id=child_taskflow.id), call(id=root_taskflow.id)])
