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

from pipeline.models import PipelineInstance
from gcloud.taskflow3.models import TaskFlowInstance

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class CallbackTestCase(TestCase):
    def test_success(self):
        taskflow = TaskFlowInstance()
        taskflow.pk = 1
        old_pipeline = PipelineInstance()
        taskflow.pipeline_instance = old_pipeline
        taskflow.pipeline_instance.clone = MagicMock(return_value=PipelineInstance())
        username = "user"

        with patch(TASKINSTANCE_SAVE, MagicMock()):
            task = taskflow.clone(username)

            self.assertIsNone(task.id)
            self.assertFalse(task.is_deleted)
            taskflow.save.assert_called_once()
            old_pipeline.clone.assert_called_once_with(username)
