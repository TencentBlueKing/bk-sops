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

from django.test import TestCase

from pipeline.core.constants import PE
from pipeline.models import PipelineTemplate, Snapshot


class TestPipelineTemplate(TestCase):
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
        self.template_2 = PipelineTemplate.objects.create_model(self.data, creator=self.creator, template_id='2')
        self.template_3 = PipelineTemplate.objects.create_model(self.data, creator=self.creator, template_id='3')

    def test_create_template(self):
        template = self.template
        data = self.data
        creator = self.creator
        self.assertEqual(template.creator, creator)
        self.assertFalse(template.is_deleted)
        self.assertIsNotNone(template.snapshot)
        self.assertEqual(template.data, data)

    def test_delete_template(self):
        PipelineTemplate.objects.delete_model(self.template.template_id)
        t = PipelineTemplate.objects.get(template_id=self.template.template_id)
        self.assertTrue(t.is_deleted)
        PipelineTemplate.objects.delete_model([self.template_2.template_id, self.template_3.template_id])
        t2 = PipelineTemplate.objects.get(template_id=self.template_2.template_id)
        t3 = PipelineTemplate.objects.get(template_id=self.template_3.template_id)
        self.assertTrue(t2.is_deleted)
        self.assertTrue(t3.is_deleted)

    def test_set_has_subprocess_bit(self):
        template_do_not_has_subprocess = PipelineTemplate(snapshot=Snapshot(
            data={PE.activities: {'1': {'type': PE.ServiceActivity},
                                  '2': {'type': PE.ServiceActivity}}}))

        template_do_not_has_subprocess.set_has_subprocess_bit()
        self.assertFalse(template_do_not_has_subprocess.has_subprocess)

        template_has_1_subprocess = PipelineTemplate(snapshot=Snapshot(
            data={PE.activities: {'1': {'type': PE.SubProcess},
                                  '2': {'type': PE.ServiceActivity}}}))
        template_has_1_subprocess.set_has_subprocess_bit()
        self.assertTrue(template_has_1_subprocess.has_subprocess)

        template_has_3_subprocess = PipelineTemplate(snapshot=Snapshot(
            data={PE.activities: {'1': {'type': PE.SubProcess},
                                  '2': {'type': PE.SubProcess},
                                  '3': {'type': PE.SubProcess},
                                  '4': {'type': PE.ServiceActivity}}}))
        template_has_3_subprocess.set_has_subprocess_bit()
        self.assertTrue(template_has_3_subprocess.has_subprocess)
