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

import factory


from django.test import TestCase
from django.db.models import signals

from pipeline.models import PipelineInstance, PipelineTemplate, Snapshot
from pipeline.utils.uniqid import uniqid

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.core.models import Project

TEST_TOTAL = 15
TEST_PAGE = 1
TEST_LIMIT = 10


class TestGroupByInstanceNode(TestCase):
    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def setUp(self):
        self.test_project = Project.objects.create(
            name="proj",
            creator="creator",
        )
        self.test_project.save()
        self.test_snapshot = Snapshot.objects.create_snapshot({})
        self.test_snapshot.save()
        # prepare test data
        template_id = uniqid()
        instance_id = uniqid()
        self.pipeline_template = PipelineTemplate.objects.create(
            template_id=template_id, creator="creator", snapshot=self.test_snapshot
        )
        self.pipeline_instance = PipelineInstance.objects.create(
            instance_id=instance_id, creator="creator", snapshot=self.test_snapshot, template=self.pipeline_template
        )
        for i in range(TEST_TOTAL):
            taskflow = TaskFlowInstance.objects.create(
                project=self.test_project, template_id=template_id, pipeline_instance=self.pipeline_instance
            )
            taskflow.save()
        self.taskflow = TaskFlowInstance.objects.all()

    def tearDown(self):
        Project.objects.all().delete()
        TaskFlowInstance.objects.all().delete()

    def test_group_by_instance_node(self):
        total, groups = TaskFlowInstance.objects.group_by_instance_node(
            taskflow=self.taskflow, filters=None, page=TEST_PAGE, limit=TEST_LIMIT
        )
        self.assertEqual(total, TEST_TOTAL)
