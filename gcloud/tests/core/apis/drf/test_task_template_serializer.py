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
import factory
from django.db.models import signals
from django.test import TestCase
from pipeline.models import PipelineTemplate, Snapshot

from gcloud.core.apis.drf.serilaziers.task_template import CreateTaskTemplateSerializer
from gcloud.core.models import Project
from gcloud.tasktmpl3.models import TaskTemplate


class TestCreateTaskTemplateSerializerProjectCheck(TestCase):
    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def setUp(self):
        self.project_a = Project.objects.create(name="project-a", creator="tester", bk_biz_id=1)
        self.project_b = Project.objects.create(name="project-b", creator="tester", bk_biz_id=2)
        self.snapshot = Snapshot.objects.create_snapshot({})
        self.pipeline_template = PipelineTemplate.objects.create(
            template_id="test_template_id", creator="tester", snapshot=self.snapshot
        )
        self.template = TaskTemplate.objects.create(
            project=self.project_a, category="Default", pipeline_template=self.pipeline_template
        )

    @staticmethod
    def build_data(project_id):
        return {
            "name": "test-template",
            "category": "Default",
            "default_flow_type": "common",
            "pipeline_tree": '{"activities": {}}',
            "notify_type": {"success": [], "fail": []},
            "project": project_id,
        }

    def test_update_with_same_project(self):
        serializer = CreateTaskTemplateSerializer(instance=self.template, data=self.build_data(self.project_a.id))
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_update_with_different_project(self):
        serializer = CreateTaskTemplateSerializer(instance=self.template, data=self.build_data(self.project_b.id))
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "流程所属项目与请求项目不一致，不允许更新",
            [str(error) for error in serializer.errors["non_field_errors"]],
        )

    def test_create_is_not_affected(self):
        serializer = CreateTaskTemplateSerializer(data=self.build_data(self.project_b.id))
        self.assertTrue(serializer.is_valid(), serializer.errors)
