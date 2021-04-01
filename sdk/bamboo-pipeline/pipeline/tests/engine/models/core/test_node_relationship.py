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

from pipeline.engine.models import NodeRelationship


class TestNodeRelationship(TestCase):
    def test_build_relationship(self):
        NodeRelationship.objects.build_relationship("1", "1")
        NodeRelationship.objects.build_relationship("1", "2")
        NodeRelationship.objects.build_relationship("1", "3")
        NodeRelationship.objects.build_relationship("2", "4")
        NodeRelationship.objects.build_relationship("2", "5")
        NodeRelationship.objects.build_relationship("3", "6")

        def count(ancestor_id, descendant_id):
            return NodeRelationship.objects.filter(ancestor_id=ancestor_id, descendant_id=descendant_id).count()

        def distance(ancestor_id, descendant_id):
            return NodeRelationship.objects.get(ancestor_id=ancestor_id, descendant_id=descendant_id).distance

        def get(ancestor_id, descendant_id):
            return NodeRelationship.objects.get(ancestor_id=ancestor_id, descendant_id=descendant_id)

        # rebuild check
        NodeRelationship.objects.build_relationship("1", "2")
        self.assertEqual(count("1", "1"), 1)
        self.assertEqual(count("1", "2"), 1)
        self.assertEqual(count("1", "3"), 1)
        self.assertEqual(count("2", "4"), 1)
        self.assertEqual(count("2", "5"), 1)
        self.assertEqual(count("3", "6"), 1)

        # distance check
        self.assertEqual(distance("1", "1"), 0)
        self.assertEqual(distance("2", "2"), 0)
        self.assertEqual(distance("3", "3"), 0)
        self.assertEqual(distance("4", "4"), 0)
        self.assertEqual(distance("5", "5"), 0)
        self.assertEqual(distance("6", "6"), 0)
        self.assertEqual(distance("1", "2"), 1)
        self.assertEqual(distance("1", "3"), 1)
        self.assertEqual(distance("1", "4"), 2)
        self.assertEqual(distance("1", "5"), 2)
        self.assertEqual(distance("1", "6"), 2)
        self.assertEqual(distance("2", "4"), 1)
        self.assertEqual(distance("2", "5"), 1)
        self.assertEqual(distance("3", "6"), 1)

        # invalid descendant check
        self.assertRaises(NodeRelationship.DoesNotExist, get, "2", "6")
        self.assertRaises(NodeRelationship.DoesNotExist, get, "3", "4")
        self.assertRaises(NodeRelationship.DoesNotExist, get, "3", "5")
