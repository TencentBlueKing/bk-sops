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
from gcloud.taskflow3.domains.context import TaskContext


MockSettings = "gcloud.taskflow3.domains.context.settings"


class TestSettings:
    BK_SOPS_HOST = "host"


class TestTaskUrl(TestCase):
    def test_taskurl(self):
        with patch(MockSettings, TestSettings):
            with patch(PROJECT_GET, MagicMock(return_value=MockProject(time_zone="UTC"))):
                project = MockProject(id="projid")
                taskflow = MockTaskFlowInstance(project=project, id="taskid")
                context = TaskContext(taskflow=taskflow, username="user")
                self.assertEqual(
                    context.task_url,
                    TestSettings.BK_SOPS_HOST.rstrip("/")
                    + f"/taskflow/execute/{taskflow.project.id}/?instance_id={taskflow.id}",
                )
