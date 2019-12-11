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

from django.test import TestCase

from pipeline_web.drawing_new.constants import POSITION
from pipeline_web.drawing_new.drawing import draw_pipeline

from pipeline_web.tests.drawing_new.data import pipeline_without_gateways

START_X, START_Y = POSITION['start']
# 节点之间的平均距离
SHIFT_X = max(POSITION['activity_size'][0], POSITION['event_size'][0], POSITION['gateway_size'][0]) * 1.2
SHIFT_Y = max(POSITION['activity_size'][1], POSITION['event_size'][1], POSITION['gateway_size'][1]) * 2
# 开始/结束事件节点纵坐标偏差
EVENT_SHIFT_Y = (POSITION['activity_size'][1] - POSITION['event_size'][1]) * 0.5
GATEWAY_SHIFT_Y = (POSITION['activity_size'][1] - POSITION['gateway_size'][1]) * 0.5


class DrawingTest(TestCase):
    def test_draw_pipeline_without_gateways(self):
        pipeline_tree = pipeline_without_gateways
        location = [
            {
                'status': '',
                'name': '',
                'y': POSITION['start'][1] + EVENT_SHIFT_Y,
                'x': POSITION['start'][0],
                'type': 'startpoint',
                'id': 'nodeb200c52ea911f7a74cd478e5a7dd'
            },
            {
                'status': '',
                'name': 'node1',
                'y': START_Y,
                'x': START_X + SHIFT_X,
                'type': 'tasknode',
                'id': 'nodedd50630d1029bca78ad6efaf89d4'
            },
            {
                'status': '',
                'name': 'node2',
                'y': START_Y,
                'x': START_X + SHIFT_X * 2,
                'type': 'tasknode',
                'id': 'nodeed4e2b6a13801df5c9a95cf9a233'
            },
            {
                'status': '',
                'name': 'node3',
                'y': START_Y,
                'x': START_X + SHIFT_X * 3,
                'type': 'tasknode',
                'id': 'node28b5acddd6ddd48c8d7728b48931'
            },
            {
                'status': '',
                'name': '',
                'y': START_Y + EVENT_SHIFT_Y,
                'x': START_X + SHIFT_X * 4,
                'type': 'endpoint',
                'id': 'nodecf7ef57aef3cb6a412ae2ac10516'
            }
        ]
        line = [
            {
                'source': {
                    'id': 'nodeb200c52ea911f7a74cd478e5a7dd',
                    'arrow': 'Right'
                },
                'id': 'line3d44c1d88e8720f4be5f871c9d58',
                'target': {
                    'id': 'nodedd50630d1029bca78ad6efaf89d4',
                    'arrow': 'Left'
                }
            },
            {
                'source': {
                    'id': 'nodeed4e2b6a13801df5c9a95cf9a233',
                    'arrow': 'Right'
                },
                'id': 'line756f60ed487a3e62e0fe5f2f9e7a',
                'target': {
                    'id': 'node28b5acddd6ddd48c8d7728b48931',
                    'arrow': 'Left'
                }
            },
            {
                'source': {
                    'id': 'node28b5acddd6ddd48c8d7728b48931',
                    'arrow': 'Right'
                },
                'id': 'linecd908c241504aa274508bd116202',
                'target': {
                    'id': 'nodecf7ef57aef3cb6a412ae2ac10516',
                    'arrow': 'Left'
                }
            },
            {
                'source': {
                    'id': 'nodedd50630d1029bca78ad6efaf89d4',
                    'arrow': 'Right'
                },
                'id': 'line1b5f377dc55b244a30691f132086',
                'target': {
                    'id': 'nodeed4e2b6a13801df5c9a95cf9a233',
                    'arrow': 'Left'
                }
            }
        ]
        draw_pipeline(pipeline_tree)
        self.assertEqual(pipeline_tree['location'], location)
        self.assertEqual(pipeline_tree['line'], line)
