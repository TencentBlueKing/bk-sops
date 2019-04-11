# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import absolute_import

import mock
from django.test import TestCase

from pipeline.models import PipelineInstance, PipelineTemplate
from pipeline.engine.models import Status, NodeRelationship
from pipeline.engine import states


class TestPipelineInstance(TestCase):
    def setUp(self):
        self.data = {
            u'activities': {
                u'act_1': {
                    u'outgoing': u'line_2',
                    u'incoming': u'line_1',
                    u'name': u'loop',
                    u'error_ignorable': False,
                    u'component': {
                        'global_outputs': {},
                        'inputs': {
                            u'i': {'type': 'splice',
                                   'value': '${loop_i}'}},
                        u'code': u'loop_test_comp'},
                    u'optional': False,
                    u'type': u'LoopServiceActivity',
                    u'loop_times': 4,
                    u'id': u'act_1',
                    u'loop': {}
                }
            },
            u'end_event': {
                u'incoming': u'line_2',
                u'outgoing': u'',
                u'type': u'EmptyEndEvent',
                u'id': u'end_event_id',
                u'name': u''
            },
            u'flows': {
                u'line_1': {
                    u'is_default': False,
                    u'source': u'start_event_id',
                    u'id': u'line_1',
                    u'target': u'act_1'
                },
                u'line_2': {
                    u'is_default': False,
                    u'source': u'act_1',
                    u'id': u'line_2',
                    u'target': u'end_event_id'
                }
            },
            u'id': u'pipeline_0',
            u'gateways': {},
            'data': {
                'inputs': {
                    u'${loop_i}': {'type': 'plain', 'value': 1},
                },
                'outputs': {}
            },
            u'start_event': {
                u'incoming': u'',
                u'outgoing': u'line_1',
                u'type': u'EmptyStartEvent',
                u'id': u'start_event_id',
                u'name': u''}
        }
        self.creator = 'start'
        self.template = PipelineTemplate.objects.create_model(self.data, creator=self.creator, template_id='1')
        self.instance = PipelineInstance.objects.create_instance(self.template, exec_data=self.data,
                                                                 creator=self.creator, instance_id='1')
        self.instance_2 = PipelineInstance.objects.create_instance(self.template, exec_data=self.data,
                                                                   creator=self.creator, instance_id='2')
        self.instance_3 = PipelineInstance.objects.create_instance(self.template, exec_data=self.data,
                                                                   creator=self.creator, instance_id='3')

    @mock.patch('pipeline.models.PipelineTemplate.objects.unfold_subprocess', mock.MagicMock())
    def test_create_instance(self):
        creator = self.creator
        instance = self.instance
        self.assertIsNotNone(instance.snapshot)
        self.assertEqual(instance.snapshot.data, instance.data)
        self.assertEqual(creator, instance.creator)
        self.assertFalse(instance.is_started)
        self.assertFalse(instance.is_finished)
        self.assertFalse(instance.is_deleted)

        # test spread
        PipelineInstance.objects.create_instance(self.template, exec_data=self.data,
                                                 creator=self.creator, instance_id='1')

        PipelineTemplate.objects.unfold_subprocess.assert_called_with(self.data)

        PipelineTemplate.objects.unfold_subprocess.reset_mock()

        PipelineInstance.objects.create_instance(self.template, exec_data=self.data,
                                                 creator=self.creator, instance_id='1', spread=True)

        PipelineTemplate.objects.unfold_subprocess.assert_not_called()

    def test_set_started(self):
        PipelineInstance.objects.set_started(self.instance.instance_id, self.creator)
        self.instance.refresh_from_db()
        self.assertTrue(self.instance.is_started)

    def test_set_finished(self):
        NodeRelationship.objects.build_relationship(self.instance.instance_id, self.instance.instance_id)
        Status.objects.create(id=self.instance.instance_id, state=states.FINISHED)
        for act_id in self.data[u'activities']:
            NodeRelationship.objects.build_relationship(self.instance.instance_id, act_id)
            Status.objects.create(id=act_id, state=states.FINISHED)
        NodeRelationship.objects.build_relationship(self.instance.instance_id, self.data[u'start_event']['id'])
        Status.objects.create(id=self.data[u'start_event']['id'], state=states.FINISHED)
        NodeRelationship.objects.build_relationship(self.instance.instance_id, self.data[u'end_event']['id'])
        Status.objects.create(id=self.data[u'end_event']['id'], state=states.FINISHED)
        print '###############################'
        print NodeRelationship.objects.filter(ancestor_id=self.instance.instance_id, distance__lte=99)
        PipelineInstance.objects.set_finished(self.instance.instance_id)

        self.instance.refresh_from_db()
        self.assertTrue(self.instance.is_finished)

    def test_delete_instance(self):
        PipelineInstance.objects.delete_model(self.instance.instance_id)
        i = PipelineInstance.objects.get(instance_id=self.instance.instance_id)
        self.assertTrue(i.is_deleted)
        PipelineInstance.objects.delete_model([self.instance_2.instance_id, self.instance_3.instance_id])
        i2 = PipelineInstance.objects.get(instance_id=self.instance_2.instance_id)
        i3 = PipelineInstance.objects.get(instance_id=self.instance_3.instance_id)
        self.assertTrue(i2.is_deleted)
        self.assertTrue(i3.is_deleted)
