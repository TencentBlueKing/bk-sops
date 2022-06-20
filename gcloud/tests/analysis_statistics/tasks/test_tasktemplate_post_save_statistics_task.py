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

from pipeline.models import PipelineTemplate

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.tests.test_data import *  # noqa
from gcloud.analysis_statistics.tasks import tasktemplate_post_save_statistics_task
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.analysis_statistics.models import TemplateNodeStatistics, TemplateStatistics

mock.mock._magics.add("__round__")

TEST_TASK_INSTANCE_ID = 1
TEST_COMPONENTS = [
    {"subprocess_stack": "[1,1,1]", "component_code": "component_code", "node_id": "node_id", "version": "version"}
]
TEST_COUNT_PIPELINE_TREE_NODES = (1, 1, 1)


class MockTemplateNodeStatisticsQuerySet(MockQuerySet):
    def values(self, *args, **kwargs):
        return TEST_COMPONENTS


class MockPipelineTmpl(MockPipelineTemplate):
    def values(self, *args, **kwargs):
        return [{"id": self.id}]


pipeline_tmpl = MockPipelineTmpl(id=1)
tasktmpl = MockTaskTemplate(id=1, pipeline_tree=TEST_PIPELINE_TREE, pipeline_template=pipeline_tmpl)
tmplnodestatistic = MockTemplateNodeStatisticsQuerySet()


class TestTaskTemplatePostSaveStatisticsTask(TestCase):
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=tasktmpl))
    @mock.patch(TEMPLATENODE_STATISTICS_FILTER, MagicMock(return_value=tmplnodestatistic))
    @mock.patch(COUNT_PIPELINE_TREE_NODES, MagicMock(return_value=TEST_COUNT_PIPELINE_TREE_NODES))
    @mock.patch(TEMPLATE_STATISTICS_UPDATE_OR_CREATE, MagicMock(return_value=MockQuerySet()))
    @mock.patch(PIPELINE_TEMPLATE_FILTER, MagicMock(return_value=pipeline_tmpl))
    def test_task_success_case(self):
        result = tasktemplate_post_save_statistics_task(TEST_TASK_INSTANCE_ID)
        TaskTemplate.objects.get.assert_called_once_with(id=TEST_TASK_INSTANCE_ID)
        PipelineTemplate.objects.filter.assert_called_once_with(template_id=TEST_ID_LIST[5])
        TemplateNodeStatistics.objects.filter.assert_called_with(template_id=tasktmpl.id)
        TemplateStatistics.objects.update_or_create.assert_called_once_with(
            task_template_id=tasktmpl.id,
            defaults={
                "template_id": tasktmpl.pipeline_template.id,
                "atom_total": 2,
                "subprocess_total": 1,
                "gateways_total": 0,
                "project_id": tasktmpl.project.id,
                "category": tasktmpl.category,
                "template_creator": tasktmpl.pipeline_template.creator,
                "template_create_time": tasktmpl.pipeline_template.create_time,
                "template_edit_time": tasktmpl.pipeline_template.edit_time,
                "output_count": 0,
                "input_count": 2,
            },
        )
        self.assertTrue(result)
