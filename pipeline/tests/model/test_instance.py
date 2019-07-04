# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.test import TestCase

from pipeline.models import PipelineInstance, PipelineTemplate


class TestPipelineInstance(TestCase):
    def setUp(self):
        self.data = {'a': 1, 'b': [1, 2, 3], 'c': {'d': 'd'}}
        self.creator = 'start'
        self.template = PipelineTemplate.objects.create_template(self.data, creator=self.creator, template_id='1')
        self.instance = PipelineInstance.objects.create_instance(self.template, creator=self.creator, instance_id='1')
        self.instance_2 = PipelineInstance.objects.create_instance(self.template, creator=self.creator, instance_id='2')
        self.instance_3 = PipelineInstance.objects.create_instance(self.template, creator=self.creator, instance_id='3')

    def test_create_instance(self):
        data = self.data
        creator = self.creator
        instance = self.instance
        self.assertIsNotNone(instance.snapshot)
        self.assertEqual(data, instance.data)
        self.assertEqual(creator, instance.creator)
        self.assertFalse(instance.is_started)
        self.assertFalse(instance.is_finished)
        self.assertFalse(instance.is_deleted)

    def test_set_started(self):
        instance = PipelineInstance.objects.set_started(self.instance.instance_id)
        self.assertTrue(instance.is_started)

    def test_set_finished(self):
        instance = PipelineInstance.objects.set_finished(self.instance.instance_id)
        self.assertTrue(instance.is_finished)

    def test_delete_instance(self):
        PipelineInstance.objects.delete_model(self.instance.instance_id)
        i = PipelineInstance.objects.get(instance_id=self.instance.instance_id)
        self.assertTrue(i.is_deleted)
        PipelineInstance.objects.delete_model([self.instance_2.instance_id, self.instance_3.instance_id])
        i2 = PipelineInstance.objects.get(instance_id=self.instance_2.instance_id)
        i3 = PipelineInstance.objects.get(instance_id=self.instance_3.instance_id)
        self.assertTrue(i2.is_deleted)
        self.assertTrue(i3.is_deleted)


