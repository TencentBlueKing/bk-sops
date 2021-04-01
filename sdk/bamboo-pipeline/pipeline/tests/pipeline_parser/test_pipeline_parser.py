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

import unittest

from pipeline.core.pipeline import Pipeline
from pipeline.parser.pipeline_parser import PipelineParser

from .data import CONDITIONAL_PARALLEL, PIPELINE_DATA, PIPELINE_WITH_SUB_PROCESS


class TestPipelineParser(unittest.TestCase):
    def setUp(self):
        from pipeline.component_framework.component import Component
        from pipeline.core.flow.activity import Service

        class TestService(Service):
            def execute(self, data, parent_data):
                return True

            def outputs_format(self):
                return []

        class TestComponent(Component):
            name = "test"
            code = "test"
            bound_service = TestService
            form = "test.js"

    def test_pipeline_parser(self):
        parser_obj = PipelineParser(PIPELINE_DATA)
        self.assertIsInstance(parser_obj.parse(), Pipeline)

    def test_sub_process_parser(self):
        parser_obj = PipelineParser(PIPELINE_WITH_SUB_PROCESS)
        self.assertIsInstance(parser_obj.parse(), Pipeline)

    def test_conditional_parallel_parser(self):
        parser_obj = PipelineParser(CONDITIONAL_PARALLEL)
        self.assertIsInstance(parser_obj.parse(), Pipeline)
