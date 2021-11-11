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

from django.test import TestCase, override_settings

from pipeline.utils.uniqid import uniqid

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.core.models import Project

TEST_TOTAL = 15
TEST_PAGE = 1
TEST_LIMIT = 10


class TestGroupByInstanceNode(TestCase):
    def setUp(self):
        self.test_project = Project.objects.create(
            name="proj",
            creator="creator",
        )
        self.test_project.save()
        # prepare test data
        template_id = uniqid()
        for i in range(TEST_TOTAL):
            taskflow = TaskFlowInstance.objects.create(project=self.test_project, template_id=template_id)
            taskflow.save()
        self.taskflow = TaskFlowInstance.objects.all()

    def tearDown(self):
        Project.objects.all().delete()
        TaskFlowInstance.objects.all().delete()

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_group_by_instance_node(self):
        total, groups = TaskFlowInstance.objects.group_by_instance_node(
            taskflow=self.taskflow, filters=None, page=TEST_PAGE, limit=TEST_LIMIT
        )
        self.assertEqual(total, TEST_TOTAL)
