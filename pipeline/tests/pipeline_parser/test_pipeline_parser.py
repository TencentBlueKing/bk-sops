# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import unittest

from pipeline.parser.pipeline_parser import (
    PipelineParser,
    WebPipelineAdapter,
)
from pipeline.core.pipeline import Pipeline
from .new_data_for_test import (
    PIPELINE_DATA,
    PIPELINE_WITH_SUB_PROCESS,
    WEB_PIPELINE_DATA,
    WEB_PIPELINE_WITH_SUB_PROCESS,
    WEB_PIPELINE_WITH_SUB_PROCESS2,
    id_list2
)


class TestPipelineParser(unittest.TestCase):
    def test_pipeline_parser(self):
        parser_obj = PipelineParser(PIPELINE_DATA)
        self.assertIsInstance(parser_obj.parser(), Pipeline)

    def test_sub_process_parser(self):
        parser_obj = PipelineParser(PIPELINE_WITH_SUB_PROCESS)
        self.assertIsInstance(parser_obj.parser(), Pipeline)

    def test_web_pipeline_parser(self):
        parser_obj = WebPipelineAdapter(WEB_PIPELINE_DATA)
        self.assertIsInstance(parser_obj.parser(), Pipeline)

    def test_web_pipeline_parser(self):
        parser_obj = WebPipelineAdapter(WEB_PIPELINE_WITH_SUB_PROCESS)
        self.assertIsInstance(parser_obj.parser(), Pipeline)

    def test_web_pipeline_parser2(self):
        parser_obj = WebPipelineAdapter(WEB_PIPELINE_WITH_SUB_PROCESS2)
        self.assertIsInstance(parser_obj.parser(), Pipeline)

    def test_pipeline_get_act_inputs(self):
        parser_obj = WebPipelineAdapter(WEB_PIPELINE_WITH_SUB_PROCESS2)
        act_inputs = parser_obj.get_act_inputs(id_list2[3], [id_list2[10]])
        self.assertEqual(
            act_inputs,
            {
                'input_test': 'custom2',
                'radio_test': '1',
            }
        )
