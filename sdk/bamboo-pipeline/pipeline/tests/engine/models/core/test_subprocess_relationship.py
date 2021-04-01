# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase

from pipeline.engine.models import SubProcessRelationship
from pipeline.utils.uniqid import uniqid


class TestSubprocessRelationship(TestCase):
    def setUp(self):
        self.subprocess_id = uniqid()
        self.process_id = uniqid()

    def test_add_relation(self):
        rel_id = SubProcessRelationship.objects.add_relation(
            subprocess_id=self.subprocess_id, process_id=self.process_id
        ).id

        self.assertTrue(
            SubProcessRelationship.objects.filter(subprocess_id=self.subprocess_id, process_id=self.process_id).exists()
        )

        rel = SubProcessRelationship.objects.get(id=rel_id)
        self.assertEqual(rel.subprocess_id, self.subprocess_id)
        self.assertEqual(rel.process_id, self.process_id)

    def test_delete_relationship(self):
        SubProcessRelationship.objects.add_relation(subprocess_id=self.subprocess_id, process_id="1")
        SubProcessRelationship.objects.add_relation(subprocess_id=self.subprocess_id, process_id="2")
        SubProcessRelationship.objects.add_relation(subprocess_id=self.subprocess_id, process_id="3")
        SubProcessRelationship.objects.delete_relation(subprocess_id=self.subprocess_id, process_id=None)
        self.assertFalse(SubProcessRelationship.objects.filter(subprocess_id=self.subprocess_id))

        SubProcessRelationship.objects.add_relation(subprocess_id="1", process_id=self.process_id)
        SubProcessRelationship.objects.add_relation(subprocess_id="2", process_id=self.process_id)
        SubProcessRelationship.objects.add_relation(subprocess_id="3", process_id=self.process_id)
        SubProcessRelationship.objects.delete_relation(subprocess_id=None, process_id=self.process_id)
        self.assertFalse(SubProcessRelationship.objects.filter(process_id=self.process_id))

        SubProcessRelationship.objects.add_relation(subprocess_id=self.subprocess_id, process_id=self.process_id)
        SubProcessRelationship.objects.delete_relation(subprocess_id=self.subprocess_id, process_id=self.process_id)
        self.assertFalse(
            SubProcessRelationship.objects.filter(process_id=self.process_id, subprocess_id=self.subprocess_id)
        )
