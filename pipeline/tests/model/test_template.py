# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.test import TestCase

from pipeline.models import PipelineTemplate


class TestPipelineTemplate(TestCase):
    def setUp(self):
        self.data = {'a': 1, 'b': [1, 2, 3], 'c': {'d': 'd'}}
        self.creator = 'start'
        self.template = PipelineTemplate.objects.create_template(self.data, creator=self.creator, template_id='1')
        self.template_2 = PipelineTemplate.objects.create_template(self.data, creator=self.creator, template_id='2')
        self.template_3 = PipelineTemplate.objects.create_template(self.data, creator=self.creator, template_id='3')

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
