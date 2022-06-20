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
from pipeline.contrib.statistics.models import TemplateInPipeline

from pipeline.models import PipelineTemplate, Snapshot
from pipeline.utils.uniqid import uniqid

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.analysis_statistics.data_migrate.tasks import migrate_template
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.analysis_statistics.models import TemplateStatistics
from gcloud.core.models import Project


class TestMigrateTemplate(TestCase):
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
        self.template_in_pipeline = TemplateInPipeline.objects.create(
            template_id=template_id, atom_total=0, subprocess_total=0, gateways_total=0
        )
        self.pipeline_template = PipelineTemplate.objects.create(
            template_id=template_id, creator="creator", snapshot=self.test_snapshot
        )
        self.task_template = TaskTemplate.objects.create(
            project=self.test_project, pipeline_template=self.pipeline_template
        )

    def tearDown(self):
        TemplateInPipeline.objects.all().delete()
        PipelineTemplate.objects.all().delete()
        TaskTemplate.objects.all().delete()

    @patch(TEMPLATE_STATISTICS_FILTER, MagicMock())
    @patch(TEMPLATE_STATISTICS_CREATE, MagicMock())
    def test_migrate_template(self):
        test_start = self.template_in_pipeline.id - 1
        test_end = self.template_in_pipeline.id + 1
        result = migrate_template(test_start, test_end)
        kwargs = {
            "template_id": self.pipeline_template.id,
            "task_template_id": self.task_template.id,
            "atom_total": self.template_in_pipeline.atom_total,
            "subprocess_total": self.template_in_pipeline.subprocess_total,
            "gateways_total": self.template_in_pipeline.gateways_total,
            "project_id": self.task_template.project.id,
            "category": self.task_template.category,
            "template_creator": self.pipeline_template.creator,
            "template_create_time": self.pipeline_template.create_time,
            "template_edit_time": self.pipeline_template.edit_time,
            "input_count": 0,
            "output_count": 0,
        }
        TemplateStatistics.objects.filter.assert_called_once_with(template_id=kwargs["template_id"])
        TemplateStatistics.objects.create.assert_called_once_with(**kwargs)
        self.assertTrue(result)
