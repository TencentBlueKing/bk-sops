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

from mock import patch, MagicMock

from django.test import TestCase

from gcloud.tests.mock_settings import *  # noqa
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.celery.tasks import prepare_and_start_task


class PrepareAndStartTaskTestCase(TestCase):
    def test_taskflow_not_exist(self):
        taskflow_instance = MagicMock()
        taskflow_instance.DoesNotExist = TaskFlowInstance.DoesNotExist
        taskflow_instance.objects.get = MagicMock(side_effect=TaskFlowInstance.DoesNotExist)
        with patch(TASKFLOW_TASKS_TASKFLOW_INSTANCE, taskflow_instance):
            prepare_and_start_task(task_id=1, project_id=2, username="3")

        taskflow_instance.objects.get.assert_called_once_with(id=1, project_id=2)

    def test_success(self):
        taskflow_instance = MagicMock()
        task = MagicMock()
        taskflow_instance.objects.get = MagicMock(return_value=task)

        with patch(TASKFLOW_TASKS_TASKFLOW_INSTANCE, taskflow_instance):
            prepare_and_start_task(task_id=1, project_id=2, username="3")

        taskflow_instance.objects.get.assert_called_once_with(id=1, project_id=2)
        task.task_action.assert_called_once_with("start", "3")
