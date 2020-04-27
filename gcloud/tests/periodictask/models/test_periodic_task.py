# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import copy
import factory

from django.test import TestCase
from django.db.models import signals

from pipeline.models import PipelineTemplate, Snapshot
from pipeline.utils.uniqid import uniqid
from pipeline_web.wrapper import PipelineTemplateWebWrapper

from gcloud.core.models import Project
from gcloud.periodictask.exceptions import InvalidOperationException
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.periodictask.models import PeriodicTask, PipelinePeriodicTask
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

WRAPPER_UNFOLD = 'pipeline_web.wrapper.PipelineTemplateWebWrapper.unfold_subprocess'


class PeriodicTaskTestCase(TestCase):

    @patch(WRAPPER_UNFOLD, MagicMock())
    def create_a_task(self):
        return PeriodicTask.objects.create(
            name='test',
            template=self.template,
            cron={},
            pipeline_tree=self.pipeline_tree,
            creator=self.creator,
            project=self.project
        )

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def setUp(self):
        self.name = 'test'
        self.task_template_name = 'task_template_name'
        self.creator = 'tester'
        self.extra_info = {'extra_info': 'val'}
        self.pipeline_tree = {'constants': {
            'key_1': {
                'value': 'val_1',
                'show_type': 'show',
            },
            'key_2': {
                'value': 'val_2',
                'show_type': 'hide',
            }
        }}
        self.project = Project.objects.create(
            name='test_project',
            time_zone='Asia/Shanghai',
            creator='test',
            desc=''
        )
        self.invalid_project = Project.objects.create(
            name='invalid_project',
            time_zone='Asia/Shanghai',
            creator='test',
            desc=''
        )
        self.snapshot, _ = Snapshot.objects.create_or_get_snapshot({})
        self.pipeline_template = PipelineTemplate.objects.create(
            template_id=uniqid(),
            name=self.task_template_name,
            creator=self.creator,
            snapshot=self.snapshot
        )
        task_template = TaskTemplate(
            project=self.project,
            pipeline_template=self.pipeline_template,
        )
        task_template.save()
        self.template = task_template
        self.task = self.create_a_task()

    @factory.django.mute_signals(signals.post_delete)
    def tearDown(self):
        if self.task:
            self.task = self.task.delete()
        self.template = self.template.delete()
        self.pipeline_template = self.pipeline_template.delete()
        self.snapshot = self.snapshot.delete()
        self.project = self.project.delete()

    def test_create_task(self):
        self.assertIsInstance(self.task, PeriodicTask)
        self.assertIsInstance(self.task.task, PipelinePeriodicTask)
        self.assertEqual(self.task.template_id, self.template.id)
        self.assertEqual(self.task.project.id, self.project.id)

    @patch(PIPELINE_TEMPLATE_WEB_WRAPPER_UNFOLD_SUBPROCESS, MagicMock())
    @patch(PERIODIC_TASK_PIPELINE_PERIODIC_TASK_CREATE_TASK, MagicMock())
    def test_create_pipeline_task(self):
        pipeline_tree = 'pipeline_tree_token'
        PeriodicTask.objects.create_pipeline_task(project=self.project,
                                                  template=self.template,
                                                  name=self.name,
                                                  cron={},
                                                  pipeline_tree=pipeline_tree,
                                                  creator=self.creator)

        PipelineTemplateWebWrapper.unfold_subprocess.assert_called_once_with(pipeline_tree)

        PipelinePeriodicTask.objects.create_task.assert_called_once_with(
            name=self.name,
            template=self.template.pipeline_template,
            cron={},
            data=pipeline_tree,
            creator=self.creator,
            timezone=self.project.time_zone,
            extra_info={
                'project_id': self.project.id,
                'category': self.template.category,
                'template_id': self.template.pipeline_template.template_id,
                'template_source': 'project',
                'template_num_id': self.template.id
            },
            spread=True
        )

    @patch(PIPELINE_TEMPLATE_WEB_WRAPPER_UNFOLD_SUBPROCESS, MagicMock())
    @patch(PERIODIC_TASK_PIPELINE_PERIODIC_TASK_CREATE_TASK, MagicMock())
    def test_create_pipeline_task__raise_invalid_operation(self):
        self.assertRaises(InvalidOperationException, PeriodicTask.objects.create_pipeline_task,
                          project=self.invalid_project,
                          template=self.template,
                          name=self.name,
                          cron={},
                          pipeline_tree=self.pipeline_tree,
                          creator=self.creator)

        PipelineTemplateWebWrapper.unfold_subprocess.assert_not_called()

        PipelinePeriodicTask.objects.create_task.assert_not_called()

    def test_enabled(self):
        self.assertEqual(self.task.enabled, self.task.task.enabled)

    def test_name(self):
        self.assertEqual(self.task.name, self.task.task.name)

    def test_cron(self):
        self.assertEqual(self.task.cron, self.task.task.cron)

    def test_total_run_count(self):
        self.assertEqual(self.task.total_run_count, self.task.task.total_run_count)

    def test_last_run_at(self):
        self.assertEqual(self.task.last_run_at, self.task.task.last_run_at)

    def test_creator(self):
        self.assertEqual(self.task.creator, self.task.task.creator)

    def test_pipeline_tree(self):
        self.assertEqual(self.task.pipeline_tree, self.task.task.execution_data)

    def test_form(self):
        self.assertEqual(self.task.form, self.task.task.form)

    def test_task_template_name(self):
        self.assertEqual(self.task.task_template_name, self.template.name)

    @patch(TASKTEMPLATE_GET, MagicMock(side_effect=TaskTemplate.DoesNotExist))
    def test_task_template_name__task_does_not_exist(self):
        self.assertEqual(self.task.task_template_name, '')

    def test_set_enabled(self):
        self.task.set_enabled(True)
        self.assertTrue(self.task.enabled)
        self.assertTrue(self.task.task.enabled)
        self.task.set_enabled(False)
        self.assertFalse(self.task.enabled)
        self.assertFalse(self.task.task.enabled)

    @factory.django.mute_signals(signals.post_delete)
    def test_delete(self):
        pipeline_periodic_task_id = self.task.task.id
        self.task = self.task.delete()
        self.assertRaises(
            PipelinePeriodicTask.DoesNotExist,
            PipelinePeriodicTask.objects.get,
            id=pipeline_periodic_task_id)

    def test_modify_constants(self):
        expect_constants = copy.deepcopy(self.task.task.execution_data['constants'])
        expect_constants['key_1']['value'] = 'val_3'
        new_constants = self.task.modify_constants({'key_1': 'val_3'})
        self.assertEqual(self.task.task.execution_data['constants'], expect_constants)
        self.assertEqual(new_constants, expect_constants)
