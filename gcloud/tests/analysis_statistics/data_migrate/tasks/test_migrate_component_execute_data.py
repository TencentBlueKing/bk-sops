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
from datetime import datetime, timezone
from django.db.models import signals
from pipeline.contrib.statistics.models import ComponentExecuteData

from pipeline.models import PipelineTemplate, PipelineInstance, Snapshot
from pipeline.utils.uniqid import uniqid

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.analysis_statistics.data_migrate.tasks import migrate_component_execute_data
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.analysis_statistics.models import TaskflowExecutedNodeStatistics
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
        instance_id = uniqid()
        template_id = uniqid()
        component_code = uniqid()
        node_id = uniqid()
        self.component_execute_data = ComponentExecuteData.objects.create(
            component_code=component_code,
            instance_id=instance_id,
            node_id=node_id,
            started_time=datetime(2021, 9, 18, 14, 57, 18, 609564, tzinfo=timezone.utc),
        )
        self.pipeline_template = PipelineTemplate.objects.create(
            template_id=template_id, creator="creator", snapshot=self.test_snapshot
        )
        self.pipeline_instance = PipelineInstance.objects.create(
            instance_id=instance_id, creator="creator", snapshot=self.test_snapshot, template=self.pipeline_template
        )
        self.taskflow_instance = TaskFlowInstance.objects.create(
            project=self.test_project, pipeline_instance=self.pipeline_instance, template_id=template_id
        )
        self.task_template = TaskTemplate.objects.create(
            project=self.test_project, pipeline_template=self.pipeline_template
        )

    def tearDown(self):
        PipelineTemplate.objects.all().delete()
        ComponentExecuteData.objects.all().delete()
        PipelineInstance.objects.all().delete()
        TaskFlowInstance.objects.all().delete()
        TaskTemplate.objects.all().delete()

    @patch(TASKFLOW_EXECUTE_NODE_STATISTICS_FILTER, MagicMock())
    @patch(TASKFLOW_EXECUTE_NODE_STATISTICS_CREATE, MagicMock())
    def test_migrate_component(self):
        test_start = self.component_execute_data.id - 1
        test_end = self.component_execute_data.id + 1
        result = migrate_component_execute_data(test_start, test_end)
        kwargs = dict(
            component_code=self.component_execute_data.component_code,
            instance_id=self.pipeline_instance.id,
            task_instance_id=self.taskflow_instance.id,
            node_id=self.component_execute_data.node_id,
            is_sub=self.component_execute_data.is_sub,
            subprocess_stack=self.component_execute_data.subprocess_stack,
            started_time=self.component_execute_data.started_time,
            archived_time=self.component_execute_data.archived_time,
            elapsed_time=self.component_execute_data.elapsed_time,
            status=self.component_execute_data.status,
            is_skip=self.component_execute_data.is_skip,
            is_retry=self.component_execute_data.is_retry,
            version=self.component_execute_data.version,
            template_id=self.pipeline_template.id,
            task_template_id=self.task_template.id,
            project_id=self.taskflow_instance.project.id,
            instance_create_time=self.pipeline_instance.create_time,
            instance_start_time=self.pipeline_instance.start_time,
            instance_finish_time=self.pipeline_instance.finish_time,
        )
        TaskflowExecutedNodeStatistics.objects.filter.assert_called_once_with(
            task_instance_id=kwargs["task_instance_id"], node_id=kwargs["node_id"]
        )
        TaskflowExecutedNodeStatistics.objects.create.assert_called_once_with(**kwargs)
        self.assertTrue(result)
