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

from __future__ import absolute_import

import mock
import copy
from django.test import TestCase
from django.db.models import signals
import factory

from pipeline.models import PipelineTemplate, Snapshot
from pipeline.contrib.periodic_task.models import PeriodicTask as PipelinePeriodicTask
from pipeline.utils.uniqid import uniqid

from gcloud.core.models import Business
from gcloud.periodictask.exceptions import InvalidOperationException
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.periodictask.models import PeriodicTask

WRAPPER_UNFOLD = 'pipeline_web.wrapper.PipelineTemplateWebWrapper.unfold_subprocess'


class PeriodicTaskTestCase(TestCase):

    @mock.patch(WRAPPER_UNFOLD, mock.MagicMock())
    def create_a_task(self):
        return PeriodicTask.objects.create(
            name='test',
            template=self.template,
            cron={},
            pipeline_tree=self.pipeline_tree,
            creator=self.creator,
            business=self.business
        )

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def setUp(self):
        self.name = 'test'
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
        self.business = Business.objects.create(
            cc_id=1,
            cc_name='mock business',
            cc_owner='tester',
            cc_company='',
            life_cycle='2',
            executor='',
        )
        self.invalid_business = Business.objects.create(
            cc_id=2,
            cc_name='mock business',
            cc_owner='tester',
            cc_company='',
            life_cycle='2',
            executor='',
        )
        self.snapshot, _ = Snapshot.objects.create_or_get_snapshot({})
        self.pipeline_template = PipelineTemplate.objects.create(
            template_id=uniqid(),
            name=self.name,
            creator=self.creator,
            snapshot=self.snapshot
        )
        task_template = TaskTemplate(
            business=self.business,
            pipeline_template=self.pipeline_template,
        )
        task_template.save()
        self.template = task_template
        self.task = self.create_a_task()

    def tearDown(self):
        if self.task:
            self.task = self.task.delete()
        self.template = self.template.delete()
        self.pipeline_template = self.pipeline_template.delete()
        self.snapshot = self.snapshot.delete()
        self.business = self.business.delete()

    def test_create_task(self):
        self.assertIsInstance(self.task, PeriodicTask)
        self.assertIsInstance(self.task.task, PipelinePeriodicTask)
        self.assertEqual(self.task.template_id, self.template.id)
        self.assertEqual(self.task.business.id, self.business.id)
        self.assertRaises(InvalidOperationException, PeriodicTask.objects.create,
                          name='test',
                          template=self.template,
                          cron={},
                          pipeline_tree=self.pipeline_tree,
                          creator=self.creator,
                          business=self.invalid_business
                          )

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

    def test_set_enabled(self):
        self.task.set_enabled(True)
        self.assertTrue(self.task.enabled)
        self.assertTrue(self.task.task.enabled)
        self.task.set_enabled(False)
        self.assertFalse(self.task.enabled)
        self.assertFalse(self.task.task.enabled)

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

    def test_form(self):
        expect_form = {k: v for k, v in self.pipeline_tree['constants'].items() if v['show_type'] == 'show'}
        self.assertEqual(self.task.form, expect_form)
