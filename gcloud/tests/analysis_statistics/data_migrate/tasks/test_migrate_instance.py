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
from pipeline.contrib.statistics.models import InstanceInPipeline

from pipeline.models import PipelineInstance, PipelineTemplate, Snapshot
from pipeline.utils.uniqid import uniqid
from pipeline.engine.utils import calculate_elapsed_time

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.analysis_statistics.data_migrate.tasks import migrate_instance
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.analysis_statistics.models import TaskflowStatistics
from gcloud.core.models import Project


class TestMigrateInstance(TestCase):
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
        instance_id = uniqid()
        template_id = uniqid()
        self.instance_in_pipeline = InstanceInPipeline.objects.create(
            instance_id=instance_id, atom_total=0, subprocess_total=0, gateways_total=0
        )
        self.pipeline_template = PipelineTemplate.objects.create(
            template_id=template_id, creator="creator", snapshot=self.test_snapshot
        )
        self.pipeline_instance = PipelineInstance.objects.create(
            instance_id=instance_id, creator="creator", snapshot=self.test_snapshot, template=self.pipeline_template
        )
        self.task_template = TaskTemplate.objects.create(
            project=self.test_project, pipeline_template=self.pipeline_template
        )
        self.taskflow_instance = TaskFlowInstance.objects.create(
            project=self.test_project, pipeline_instance=self.pipeline_instance, template_id=template_id
        )

    def tearDown(self):
        InstanceInPipeline.objects.all().delete()
        PipelineTemplate.objects.all().delete()
        PipelineInstance.objects.all().delete()
        TaskFlowInstance.objects.all().delete()
        TaskTemplate.objects.all().delete()

    @patch(TASKFLOW_STATISTICS_FILTER, MagicMock())
    @patch(TASKFLOW_STATISTICS_CREATE, MagicMock())
    def test_migrate_instance(self):
        test_start = self.instance_in_pipeline.id - 1
        test_end = self.instance_in_pipeline.id + 1
        result = migrate_instance(test_start, test_end)
        kwargs = dict(
            instance_id=self.pipeline_instance.id,
            task_instance_id=self.taskflow_instance.id,
            atom_total=self.instance_in_pipeline.atom_total,
            subprocess_total=self.instance_in_pipeline.subprocess_total,
            gateways_total=self.instance_in_pipeline.gateways_total,
            project_id=self.taskflow_instance.project.id,
            category=self.task_template.category,
            template_id=self.pipeline_template.id,
            task_template_id=self.task_template.id,
            creator=self.pipeline_instance.creator,
            create_time=self.pipeline_instance.create_time,
            start_time=self.pipeline_instance.start_time,
            finish_time=self.pipeline_instance.finish_time,
            elapsed_time=calculate_elapsed_time(self.pipeline_instance.start_time, self.pipeline_instance.finish_time),
            create_method=self.taskflow_instance.create_method,
        )
        TaskflowStatistics.objects.filter.assert_called_once_with(instance_id=kwargs["instance_id"])
        TaskflowStatistics.objects.create.assert_called_once_with(**kwargs)
        self.assertTrue(result)
