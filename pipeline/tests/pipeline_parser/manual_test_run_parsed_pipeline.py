# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from pipeline.service.pipeline_engine_adapter.adapter_api import run_pipeline
from pipeline.parser.pipeline_parser import PipelineParser, WebPipelineAdapter
from pipeline.utils.uniqid import uniqid, node_uniqid
from .new_data_for_test import (
    PIPELINE_DATA,
    WEB_PIPELINE_WITH_SUB_PROCESS2
)


def test_run_serial_pipeline():
    pipeline = PIPELINE_DATA
    parser_obj = PipelineParser(pipeline)
    run_pipeline(parser_obj.parser())


def test_run_sub_pipeline2():
    pipeline = WEB_PIPELINE_WITH_SUB_PROCESS2
    parser_obj = WebPipelineAdapter(pipeline)
    run_pipeline(parser_obj.parser())


def main_test():
    id_list = [node_uniqid() for i in xrange(100)]
    pipe1 = {
        'id': id_list[0],
        'name': 'name',
        'start_event': {
            'id': id_list[1],
            'name': 'start',
            'type': 'EmptyStartEvent',
            'incoming': None,
            'outgoing': id_list[2]
        },
        'end_event': {
            'id': id_list[53],
            'name': 'end',
            'type': 'EmptyEndEvent',
            'incoming': id_list[52],
            'outgoing': None
        },
        'activities': {
        },
        'flows': {  # 存放该 Pipeline 中所有的线
        },
        'gateways': {  # 这里存放着网关的详细信息
        },
        'data': {
            'inputs': {
            },
            'outputs': {
            },
        }
    }
    for i in xrange(2, 51, 2):
        pipe1['flows'][id_list[i]] = {
            'id': id_list[i],
            'source': id_list[i - 1],
            'target': id_list[i + 1]
        }
        pipe1['activities'][id_list[i + 1]] = {
            'id': id_list[i + 1],
            'type': 'ServiceActivity',
            'name': 'first_task',
            'incoming': id_list[i],
            'outgoing': id_list[i + 2],
            'component': {
                'code': 'demo',
                'inputs': {
                    'input_test': {
                        'type': 'plain',
                        'value': '2',
                    },
                    'radio_test': {
                        'type': 'plain',
                        'value': '1',
                    },
                },
            }
        }
    pipe1['flows'][id_list[52]] = {
         'id': id_list[52],
         'source': id_list[52 - 1],
         'target': id_list[52 + 1]
    }
    parser_obj = PipelineParser(pipe1)
    run_pipeline(parser_obj.parser())
