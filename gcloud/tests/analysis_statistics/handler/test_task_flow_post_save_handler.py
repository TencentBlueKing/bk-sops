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

from gcloud.constants import TaskCreateMethod
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tests.analysis_statistics.mock_settings import *  # noqa
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

TEST_DATA = "data"
TEST_APP_CODE = "app_code"
TEST_TEMPLATE_ID = "1"


class TestTaskFlowPostSaveHandler(TestCase):
    def test_task_call_success(self):
        with patch(TASKFLOWINSTANCE_POST_SAVE_STATISTICS_TASK, MagicMock()) as mocked_handler:
            pt = MockPipelineTemplate(id=1, name="pt")
            tmpl = MockTaskTemplate(id=1, pipeline_template=pt)
            self.taskflow = TaskFlowInstance.objects.create(
                category=tmpl.category,
                template_id=TEST_TEMPLATE_ID,
                template_source="project",
                create_method=TaskCreateMethod.API.value,
                create_info=TEST_APP_CODE,
                flow_type="common",
                current_flow="execute_task",
                engine_ver=1,
            )
            mocked_handler.assert_called_once_with(self.taskflow.id, True)
