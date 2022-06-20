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


from django.test import TestCase
from django.db.models import signals
from pipeline.contrib.statistics.models import ComponentInTemplate

from pipeline.models import PipelineTemplate, Snapshot
from pipeline.utils.uniqid import uniqid

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.analysis_statistics.data_migrate.tasks import migrate_component
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.analysis_statistics.models import TemplateNodeStatistics
from gcloud.core.models import Project


class TestMigrateComponent(TestCase):
    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def setUp(self):
        self.test_snapshot = Snapshot.objects.create_snapshot({})
        self.test_snapshot.save()
        self.test_project = Project.objects.create(
            name="proj",
            creator="creator",
        )
        self.test_project.save()
        # prepare test data
        template_id = uniqid()
        component_code = uniqid()
        node_id = uniqid()
        self.component_in_template = ComponentInTemplate.objects.create(
            component_code=component_code, template_id=template_id, node_id=node_id
        )
        self.pipeline_template = PipelineTemplate.objects.create(
            template_id=template_id, creator="creator", snapshot=self.test_snapshot
        )
        self.task_template = TaskTemplate.objects.create(
            project=self.test_project, pipeline_template=self.pipeline_template
        )

    def tearDown(self):
        ComponentInTemplate.objects.all().delete()
        PipelineTemplate.objects.all().delete()
        TaskTemplate.objects.all().delete()

    @patch(TEMPLATE_NODE_STATISTICS_FILTER, MagicMock())
    @patch(TEMPLATE_NODE_STATISTICS_CREATE, MagicMock())
    def test_migrate_component(self):
        test_start = self.component_in_template.id - 1
        test_end = self.component_in_template.id + 1
        result = migrate_component(test_start, test_end)
        kwargs = dict(
            component_code=self.component_in_template.component_code,
            template_id=self.pipeline_template.id,
            task_template_id=self.task_template.id,
            project_id=self.task_template.project.id,
            category=self.task_template.category,
            node_id=self.component_in_template.node_id,
            is_sub=self.component_in_template.is_sub,
            subprocess_stack=self.component_in_template.subprocess_stack,
            version=self.component_in_template.version,
            template_creator=self.pipeline_template.creator,
            template_create_time=self.pipeline_template.create_time,
            template_edit_time=self.pipeline_template.edit_time,
        )
        TemplateNodeStatistics.objects.filter.assert_called_once_with(
            task_template_id=kwargs["task_template_id"], node_id=kwargs["node_id"]
        )
        TemplateNodeStatistics.objects.create.assert_called_once_with(**kwargs)
        self.assertTrue(result)
