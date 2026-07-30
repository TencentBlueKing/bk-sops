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
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class AINotifyConfigTestCase(TestCase):
    def test_onetime_task_has_no_ai_notify_config(self):
        taskflow = TaskFlowInstance(template_source="onetime")
        self.assertIsNone(taskflow.get_ai_notify_type())
        self.assertIsNone(taskflow.get_ai_notify_group())

    def test_template_deleted(self):
        task_template = MagicMock()
        task_template.DoesNotExist = TaskTemplate.DoesNotExist
        task_template.objects.get = MagicMock(side_effect=TaskTemplate.DoesNotExist())
        with patch(TASKFLOW_MODEL_TASK_TEMPLATE, task_template):
            taskflow = TaskFlowInstance(template_source="project", template_id="404")
            self.assertIsNone(taskflow.get_ai_notify_type())
            self.assertIsNone(taskflow.get_ai_notify_group())

    def test_template_id_is_blank(self):
        taskflow = TaskFlowInstance(template_source="project", template_id="")
        self.assertIsNone(taskflow.get_ai_notify_type())
        self.assertIsNone(taskflow.get_ai_notify_group())

    def test_normal(self):
        task_template = MagicMock()
        task_template.objects.get = MagicMock(
            return_value=MagicMock(ai_notify_type=["weixin"], ai_notify_group=["group_id"])
        )
        with patch(TASKFLOW_MODEL_TASK_TEMPLATE, task_template):
            taskflow = TaskFlowInstance(template_source="project", template_id="1")
            self.assertEqual(taskflow.get_ai_notify_type(), ["weixin"])
            self.assertEqual(taskflow.get_ai_notify_group(), ["group_id"])
