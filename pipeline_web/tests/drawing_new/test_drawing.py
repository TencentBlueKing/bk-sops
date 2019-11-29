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

from pipeline_web.tests.drawing_new.data import (
    pipeline_without_gateways,
    pipeline_with_gateways,
    pipeline_with_circle
)

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

    def test_draw_pipeline_with_gateways(self):
        pipeline_tree = pipeline_with_gateways
        draw_pipeline(pipeline_tree)
        location = [
            {
                'status': '',
                'name': '',
                'x': START_X,
                'y': START_Y + EVENT_SHIFT_Y,
                'type': 'startpoint',
                'id': 'n7c985a50a8435b89e5daf3c618df732'
            },
            {
                'status': '',
                'name': 'node1',
                'x': START_X + SHIFT_X,
                'y': START_Y,
                'type': 'tasknode',
                'id': 'n9a17aecf7f232228e768152360564a3'
            },
            {
                'status': '',
                'name': '',
                'x': START_X + SHIFT_X * 2,
                'y': START_Y + GATEWAY_SHIFT_Y,
                'type': 'branchgateway',
                'id': 'n0244a7271a235219364f1377d230d04'
            },
            {
                'status': '',
                'name': 'node2',
                'x': START_X + SHIFT_X * 3,
                'y': START_Y,
                'type': 'tasknode',
                'id': 'n55c897bbc8c38cea18c99533348b1e3'
            },
            {
                'status': '',
                'name': '',
                'x': START_X + SHIFT_X * 3,
                'y': START_Y + GATEWAY_SHIFT_Y + SHIFT_Y,
                'type': 'parallelgateway',
                'id': 'nd97fecb12ed3c7a9047197e84c58549'
            },
            {
                'status': '',
                'name': 'node3',
                'x': START_X + SHIFT_X * 4,
                'y': START_Y + SHIFT_Y,
                'type': 'tasknode',
                'id': 'n3648618e4223512a8b7fc87b5112844'
            },
            {
                'status': '',
                'name': 'node4',
                'x': START_X + SHIFT_X * 4,
                'y': START_Y + SHIFT_Y * 2,
                'type': 'tasknode',
                'id': 'n8ea7e6e5d76308cb3d9b151e2c4d82c'
            },
            {
                'status': '',
                'name': '',
                'x': START_X + SHIFT_X * 5,
                'y': START_Y + GATEWAY_SHIFT_Y + SHIFT_Y,
                'type': 'convergegateway',
                'id': 'nbb53904ad35364f97ccaa37328d92d9'
            },
            {
                'status': '',
                'name': '',
                'x': START_X + SHIFT_X * 6,
                'y': START_Y + GATEWAY_SHIFT_Y,
                'type': 'convergegateway',
                'id': 'nfc24efd8fd13301a800f1040d492a8e'
            },
            {
                'status': '',
                'name': '',
                'x': START_X + SHIFT_X * 7,
                'y': START_Y + EVENT_SHIFT_Y,
                'type': 'endpoint',
                'id': 'n5b5605fe8293882915fdaa0f17ce8c6'
            }
        ]
        line = [
            {
                'source': {
                    'id': 'n7c985a50a8435b89e5daf3c618df732',
                    'arrow': 'Right'
                },
                'id': 'l3cef190dbd23a908d994f80897a53b3',
                'target': {
                    'id': 'n9a17aecf7f232228e768152360564a3',
                    'arrow': 'Left'
                }
            },
            {
                'source': {
                    'id': 'n9a17aecf7f232228e768152360564a3',
                    'arrow': 'Right'
                },
                'id': 'l12079c5e24a3b5eb22026a9a60a0638',
                'target': {
                    'id': 'n0244a7271a235219364f1377d230d04',
                    'arrow': 'Left'
                }
            },
            {
                'source': {
                    'id': 'n0244a7271a235219364f1377d230d04',
                    'arrow': 'Right'
                },
                'id': 'l33b08b83afd31fba746853a54c49cc0',
                'target': {
                    'id': 'n55c897bbc8c38cea18c99533348b1e3',
                    'arrow': 'Left'
                }
            },
            {
                'source': {
                    'id': 'n55c897bbc8c38cea18c99533348b1e3',
                    'arrow': 'Right'
                },
                'id': 'l774bb8683993b269005a0f13a38697a',
                'target': {
                    'id': 'nfc24efd8fd13301a800f1040d492a8e',
                    'arrow': 'Left'
                }
            },
            {
                'source': {
                    'id': 'n0244a7271a235219364f1377d230d04',
                    'arrow': 'Bottom'
                },
                'id': 'ld7b5d7c371036019a55810d0d961986',
                'target': {
                    'id': 'nd97fecb12ed3c7a9047197e84c58549',
                    'arrow': 'Left'
                }
            },
            {
                'source': {
                    'id': 'nd97fecb12ed3c7a9047197e84c58549',
                    'arrow': 'Right'
                },
                'id': 'lf6d76d6272c3bce84caf3d1113992d7',
                'target': {
                    'id': 'n3648618e4223512a8b7fc87b5112844',
                    'arrow': 'Left'
                }
            },
            {
                'source': {
                    'id': 'n3648618e4223512a8b7fc87b5112844',
                    'arrow': 'Right'
                },
                'id': 'lf477bb3adc43f71ad2c353e7da18b57',
                'target': {
                    'id': 'nbb53904ad35364f97ccaa37328d92d9',
                    'arrow': 'Left'
                }
            },
            {
                'source': {
                    'id': 'nd97fecb12ed3c7a9047197e84c58549',
                    'arrow': 'Bottom'
                },
                'id': 'l74a1d2d3a4d30be8d53452f639616bd',
                'target': {
                    'id': 'n8ea7e6e5d76308cb3d9b151e2c4d82c',
                    'arrow': 'Left'
                }
            },
            {
                'source': {
                    'id': 'n8ea7e6e5d76308cb3d9b151e2c4d82c',
                    'arrow': 'Right'
                },
                'id': 'la4c31c646483507a0af4704bfc9a05d',
                'target': {
                    'id': 'nbb53904ad35364f97ccaa37328d92d9',
                    'arrow': 'Bottom'
                }
            },
            {
                'source': {
                    'id': 'nbb53904ad35364f97ccaa37328d92d9',
                    'arrow': 'Right'
                },
                'id': 'l1471a752c513955af4b6a0779ab3b1d',
                'target': {
                    'id': 'nfc24efd8fd13301a800f1040d492a8e',
                    'arrow': 'Bottom'
                }
            },
            {
                'source': {
                    'id': 'nfc24efd8fd13301a800f1040d492a8e',
                    'arrow': 'Right'
                },
                'id': 'l07b3c2e2f943fdd96401bd843a65ec0',
                'target': {
                    'id': 'n5b5605fe8293882915fdaa0f17ce8c6',
                    'arrow': 'Left'
                }
            }
        ]
        self.assertEqual(pipeline_tree['location'], location)
        self.assertEqual(pipeline_tree['line'], line)
