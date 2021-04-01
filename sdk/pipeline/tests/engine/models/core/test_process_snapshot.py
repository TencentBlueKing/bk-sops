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

from pipeline.engine.models.core import ProcessSnapshot
from pipeline.engine.utils import Stack


class TestProcessSnapshot(TestCase):
    def setUp(self):
        self.pipeline_stack = Stack(["pipeline1", "pipeline2"])
        self.subprocess_stack = Stack(["subprocess1", "subprocess2"])
        self.children = ["child1", "child2"]
        self.root_pipeline = "root_pipeline"
        self.snapshot = ProcessSnapshot.objects.create_snapshot(
            pipeline_stack=self.pipeline_stack,
            children=self.children,
            root_pipeline=self.root_pipeline,
            subprocess_stack=self.subprocess_stack,
        )

    def test_properties(self):
        self.assertEqual(self.snapshot.pipeline_stack, self.pipeline_stack)
        self.assertEqual(self.snapshot.children, self.children)
        self.assertEqual(self.snapshot.root_pipeline, self.root_pipeline)
        self.assertEqual(self.snapshot.subprocess_stack, self.subprocess_stack)

    def test_clean_children(self):
        self.snapshot.clean_children()
        self.assertEqual(len(self.snapshot.children), 0)
