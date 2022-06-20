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

from gcloud.taskflow3.models import TaskFlowInstance

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class ExecutorProxyTestCase(TestCase):
    def test_template_source_is_not_project(self):
        task_template = MagicMock()
        task_template.objects.filter = MagicMock()
        with patch(TASKFLOW_MODEL_TASK_TEMPLATE, task_template):

            taskflow = TaskFlowInstance()
            taskflow.template_source = "common"
            self.assertEqual(taskflow.executor_proxy, None)
            task_template.objects.filter.assert_not_called()

            taskflow = TaskFlowInstance()
            taskflow.template_source = "onetime"
            self.assertEqual(taskflow.executor_proxy, None)
            task_template.objects.filter.assert_not_called()

    def test_normal(self):
        task_template = MagicMock()
        values_list_return = MagicMock()
        values_list_return.first = MagicMock(return_value="dummy")
        _filter_return = MagicMock()
        _filter_return.values_list = MagicMock(return_value=values_list_return)
        _filter = MagicMock(return_value=_filter_return)
        task_template.objects.filter = _filter
        with patch(TASKFLOW_MODEL_TASK_TEMPLATE, task_template):

            taskflow = TaskFlowInstance()
            taskflow.template_source = "project"
            self.assertEqual(taskflow.executor_proxy, "dummy")

            taskflow = TaskFlowInstance()
            taskflow.template_source = "business"
            self.assertEqual(taskflow.executor_proxy, "dummy")

    @patch("gcloud.taskflow3.models.TaskFlowInstance.save", MagicMock(return_value=None))
    def test_recorded_executor_proxy(self):
        taskflow = TaskFlowInstance()
        ep = taskflow.record_and_get_executor_proxy("dummy")
        self.assertEqual(ep, "dummy")
        self.assertEqual(taskflow.recorded_executor_proxy, "dummy")

        taskflow2 = TaskFlowInstance(recorded_executor_proxy="recorded_one")
        ep = taskflow2.record_and_get_executor_proxy("dummy")
        self.assertEqual(ep, "recorded_one")
        self.assertEqual(taskflow2.recorded_executor_proxy, "recorded_one")
