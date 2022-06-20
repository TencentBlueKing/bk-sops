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


from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.taskflow3.context import TaskContext


def mock_init(self):
    self.project_id = "project_id"


class TaskExecutorTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.init = TaskContext.__init__
        TaskContext.__init__ = mock_init

    @classmethod
    def tearDownClass(cls):
        TaskContext.__init__ = cls.init

    def test_use_taskflow_executor_proxy(self):
        taskflow = MagicMock()
        taskflow.executor_proxy = "dummy"
        taskflow.record_and_get_executor_proxy = MagicMock(return_value="dummy")
        context = TaskContext()
        self.assertEqual(context.task_executor(taskflow, "operator"), "dummy")
        taskflow.record_and_get_executor_proxy.assert_called_once_with("dummy")

    def test_use_project_config_executor_proxy(self):
        project_config = MagicMock()
        project_config.objects.task_executor_for_project = MagicMock(return_value="proxy")
        with patch(TASKFLOW_CONTEXT_PROJECT_CONFIG, project_config):
            taskflow = MagicMock()
            taskflow.executor_proxy = ""
            taskflow.record_and_get_executor_proxy = MagicMock(return_value="proxy")
            context = TaskContext()
            self.assertEqual(context.task_executor(taskflow, "operator"), "proxy")
            taskflow.record_and_get_executor_proxy.assert_called_once_with("proxy")
