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

from pipeline_web.drawing import (
    draw_pipeline,
    START_X,
    START_Y,
    EVENT_OR_GATEWAY_SHIFT_Y,
    SHIFT_X,
    SHIFT_Y
)


class DrawingTest(TestCase):
    def test_draw_pipeline_without_gateways(self):
        pipeline_tree = {
            'activities': {
                'node28b5acddd6ddd48c8d7728b48931': {
                    'outgoing': 'linecd908c241504aa274508bd116202',
                    'incoming': 'line756f60ed487a3e62e0fe5f2f9e7a',
                    'name': 'node3',
                    'error_ignorable': False,
                    'component': {
                        'code': 'sleep_timer',
                        'data': {
                            'bk_timing': {
                                'hook': True,
                                'value': '${time3}'
                            }
                        }
                    },
                    'stage_name': 'stage3',
                    'retryable': True,
                    'skippable': True,
                    'type': 'ServiceActivity',
                    'id': 'node28b5acddd6ddd48c8d7728b48931'
                },
                'nodedd50630d1029bca78ad6efaf89d4': {
                    'outgoing': 'line1b5f377dc55b244a30691f132086',
                    'incoming': 'line3d44c1d88e8720f4be5f871c9d58',
                    'name': 'node1',
                    'error_ignorable': False,
                    'component': {
                        'code': 'sleep_timer',
                        'data': {
                            'bk_timing': {
                                'hook': True,
                                'value': '${bk_timing}'
                            }
                        }
                    },
                    'stage_name': 'stage1',
                    'retryable': True,
                    'skippable': True,
                    'type': 'ServiceActivity',
                    'id': 'nodedd50630d1029bca78ad6efaf89d4'
                },
                'nodeed4e2b6a13801df5c9a95cf9a233': {
                    'outgoing': 'line756f60ed487a3e62e0fe5f2f9e7a',
                    'incoming': 'line1b5f377dc55b244a30691f132086',
                    'name': 'node2',
                    'error_ignorable': False,
                    'component': {
                        'code': 'sleep_timer',
                        'data': {
                            'bk_timing': {
                                'hook': True,
                                'value': '${time2}'
                            }
                        }
                    },
                    'stage_name': 'stage2',
                    'retryable': True,
                    'skippable': True,
                    'type': 'ServiceActivity',
                    'id': 'nodeed4e2b6a13801df5c9a95cf9a233'
                }
            },
            'end_event': {
                'incoming': 'linecd908c241504aa274508bd116202',
                'outgoing': '',
                'type': 'EmptyEndEvent',
                'id': 'nodecf7ef57aef3cb6a412ae2ac10516',
                'name': ''
            },
            'outputs': [],
            'flows': {
                'line3d44c1d88e8720f4be5f871c9d58': {
                    'is_default': False,
                    'source': 'nodeb200c52ea911f7a74cd478e5a7dd',
                    'id': 'line3d44c1d88e8720f4be5f871c9d58',
                    'target': 'nodedd50630d1029bca78ad6efaf89d4'
                },
                'line756f60ed487a3e62e0fe5f2f9e7a': {
                    'is_default': False,
                    'source': 'nodeed4e2b6a13801df5c9a95cf9a233',
                    'id': 'line756f60ed487a3e62e0fe5f2f9e7a',
                    'target': 'node28b5acddd6ddd48c8d7728b48931'
                },
                'linecd908c241504aa274508bd116202': {
                    'is_default': False,
                    'source': 'node28b5acddd6ddd48c8d7728b48931',
                    'id': 'linecd908c241504aa274508bd116202',
                    'target': 'nodecf7ef57aef3cb6a412ae2ac10516'
                },
                'line1b5f377dc55b244a30691f132086': {
                    'is_default': False,
                    'source': 'nodedd50630d1029bca78ad6efaf89d4',
                    'id': 'line1b5f377dc55b244a30691f132086',
                    'target': 'nodeed4e2b6a13801df5c9a95cf9a233'
                }
            },
            'gateways': {},
            'start_event': {
                'incoming': '',
                'outgoing': 'line3d44c1d88e8720f4be5f871c9d58',
                'type': 'EmptyStartEvent',
                'id': 'nodeb200c52ea911f7a74cd478e5a7dd',
                'name': ''
            },
            'constants': {
                '${bk_timing}': {
                    'source_tag': 'sleep_timer.bk_timing',
                    'source_info': {
                        'nodedd50630d1029bca78ad6efaf89d4': ['bk_timing']
                    },
                    'name': '\u5b9a\u65f6\u65f6\u95f4',
                    'index': 0,
                    'custom_type': '',
                    'value': '3',
                    'show_type': 'show',
                    'source_type': 'component_inputs',
                    'key': '${bk_timing}',
                    'desc': ''
                },
                '${time3}': {
                    'source_tag': 'sleep_timer.bk_timing',
                    'source_info': {
                        'node28b5acddd6ddd48c8d7728b48931': ['bk_timing']
                    },
                    'name': 'time3',
                    'index': 2,
                    'custom_type': '',
                    'value': '',
                    'show_type': 'show',
                    'source_type': 'component_inputs',
                    'key': '${time3}',
                    'validation': '',
                    'desc': ''
                },
                '${time2}': {
                    'source_tag': 'sleep_timer.bk_timing',
                    'source_info': {
                        'nodeed4e2b6a13801df5c9a95cf9a233': ['bk_timing']
                    },
                    'name': 'time2',
                    'index': 1,
                    'custom_type': '',
                    'value': '2',
                    'show_type': 'show',
                    'source_type': 'component_inputs',
                    'key': '${time2}',
                    'validation': '',
                    'desc': ''
                }
            }
        }
        location = [
            {
                'status': '',
                'name': '',
                'y': START_Y + EVENT_OR_GATEWAY_SHIFT_Y,
                'x': START_X,
                'type': 'startpoint',
                'id': 'nodeb200c52ea911f7a74cd478e5a7dd'
            },
            {
                'status': '',
                'name': 'node1',
                'stage_name': 'stage1',
                'y': START_Y,
                'x': START_X + SHIFT_X,
                'type': 'tasknode',
                'id': 'nodedd50630d1029bca78ad6efaf89d4'
            },
            {
                'status': '',
                'name': 'node2',
                'stage_name': 'stage2',
                'y': START_Y,
                'x': START_X + SHIFT_X * 2,
                'type': 'tasknode',
                'id': 'nodeed4e2b6a13801df5c9a95cf9a233'
            },
            {
                'status': '',
                'name': 'node3',
                'stage_name': 'stage3',
                'y': START_Y,
                'x': START_X + SHIFT_X * 3,
                'type': 'tasknode',
                'id': 'node28b5acddd6ddd48c8d7728b48931'
            },
            {
                'status': '',
                'name': '',
                'y': START_Y + EVENT_OR_GATEWAY_SHIFT_Y,
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
                    'id': 'nodedd50630d1029bca78ad6efaf89d4',
                    'arrow': 'Right'
                },
                'id': 'line1b5f377dc55b244a30691f132086',
                'target': {
                    'id': 'nodeed4e2b6a13801df5c9a95cf9a233',
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
            }
        ]
        draw_pipeline(pipeline_tree, START_X, START_Y)
        self.assertEquals(pipeline_tree['location'], location)
        self.assertEquals(pipeline_tree['line'], line)

    def test_draw_gateways(self):
        pipeline_tree = {
            'activities': {
                'n55c897bbc8c38cea18c99533348b1e3': {
                    'outgoing': 'l774bb8683993b269005a0f13a38697a',
                    'incoming': 'l33b08b83afd31fba746853a54c49cc0',
                    'name': 'node2',
                    'error_ignorable': False,
                    'component': {
                        'code': 'sleep_timer',
                        'data': {
                            'bk_timing': {
                                'hook': True,
                                'value': '${bk_timing}'
                            }
                        }
                    },
                    'stage_name': 'stage2',
                    'retryable': True,
                    'type': 'ServiceActivity',
                    'id': 'n55c897bbc8c38cea18c99533348b1e3',
                    'skippable': True
                },
                'n3648618e4223512a8b7fc87b5112844': {
                    'outgoing': 'lf477bb3adc43f71ad2c353e7da18b57',
                    'incoming': 'lf6d76d6272c3bce84caf3d1113992d7',
                    'name': 'node3',
                    'error_ignorable': False,
                    'component': {
                        'code': 'sleep_timer',
                        'data': {
                            'bk_timing': {
                                'hook': False,
                                'value': '3'
                            }
                        }
                    },
                    'stage_name': 'stage3',
                    'retryable': True,
                    'type': 'ServiceActivity',
                    'id': 'n3648618e4223512a8b7fc87b5112844',
                    'skippable': True
                },
                'n8ea7e6e5d76308cb3d9b151e2c4d82c': {
                    'outgoing': 'la4c31c646483507a0af4704bfc9a05d',
                    'incoming': 'l74a1d2d3a4d30be8d53452f639616bd',
                    'name': 'node4',
                    'error_ignorable': False,
                    'component': {
                        'code': 'sleep_timer',
                        'data': {
                            'bk_timing': {
                                'hook': True,
                                'value': '${bk_timing}'
                            }
                        }
                    },
                    'stage_name': 'stage3',
                    'retryable': True,
                    'type': 'ServiceActivity',
                    'id': 'n8ea7e6e5d76308cb3d9b151e2c4d82c',
                    'skippable': True
                },
                'n9a17aecf7f232228e768152360564a3': {
                    'outgoing': 'l12079c5e24a3b5eb22026a9a60a0638',
                    'incoming': 'l3cef190dbd23a908d994f80897a53b3',
                    'name': 'node1',
                    'error_ignorable': False,
                    'component': {
                        'code': 'sleep_timer',
                        'data': {
                            'bk_timing': {
                                'hook': True,
                                'value': '${bk_timing}'
                            }
                        }
                    },
                    'stage_name': 'stage1',
                    'retryable': True,
                    'type': 'ServiceActivity',
                    'id': 'n9a17aecf7f232228e768152360564a3',
                    'skippable': True
                }
            },
            'end_event': {
                'incoming': 'l07b3c2e2f943fdd96401bd843a65ec0',
                'outgoing': '',
                'type': 'EmptyEndEvent',
                'id': 'n5b5605fe8293882915fdaa0f17ce8c6',
                'name': ''
            },
            'outputs': [
                '${bk_timing}'
            ],
            'flows': {
                'lf477bb3adc43f71ad2c353e7da18b57': {
                    'is_default': False,
                    'source': 'n3648618e4223512a8b7fc87b5112844',
                    'id': 'lf477bb3adc43f71ad2c353e7da18b57',
                    'target': 'nbb53904ad35364f97ccaa37328d92d9'
                },
                'lf6d76d6272c3bce84caf3d1113992d7': {
                    'is_default': False,
                    'source': 'nd97fecb12ed3c7a9047197e84c58549',
                    'id': 'lf6d76d6272c3bce84caf3d1113992d7',
                    'target': 'n3648618e4223512a8b7fc87b5112844'
                },
                'l74a1d2d3a4d30be8d53452f639616bd': {
                    'is_default': False,
                    'source': 'nd97fecb12ed3c7a9047197e84c58549',
                    'id': 'l74a1d2d3a4d30be8d53452f639616bd',
                    'target': 'n8ea7e6e5d76308cb3d9b151e2c4d82c'
                },
                'l33b08b83afd31fba746853a54c49cc0': {
                    'is_default': False,
                    'source': 'n0244a7271a235219364f1377d230d04',
                    'id': 'l33b08b83afd31fba746853a54c49cc0',
                    'target': 'n55c897bbc8c38cea18c99533348b1e3'
                },
                'ld7b5d7c371036019a55810d0d961986': {
                    'is_default': False,
                    'source': 'n0244a7271a235219364f1377d230d04',
                    'id': 'ld7b5d7c371036019a55810d0d961986',
                    'target': 'nd97fecb12ed3c7a9047197e84c58549'
                },
                'l3cef190dbd23a908d994f80897a53b3': {
                    'is_default': False,
                    'source': 'n7c985a50a8435b89e5daf3c618df732',
                    'id': 'l3cef190dbd23a908d994f80897a53b3',
                    'target': 'n9a17aecf7f232228e768152360564a3'
                },
                'l12079c5e24a3b5eb22026a9a60a0638': {
                    'is_default': False,
                    'source': 'n9a17aecf7f232228e768152360564a3',
                    'id': 'l12079c5e24a3b5eb22026a9a60a0638',
                    'target': 'n0244a7271a235219364f1377d230d04'
                },
                'l774bb8683993b269005a0f13a38697a': {
                    'is_default': False,
                    'source': 'n55c897bbc8c38cea18c99533348b1e3',
                    'id': 'l774bb8683993b269005a0f13a38697a',
                    'target': 'nfc24efd8fd13301a800f1040d492a8e'
                },
                'la4c31c646483507a0af4704bfc9a05d': {
                    'is_default': False,
                    'source': 'n8ea7e6e5d76308cb3d9b151e2c4d82c',
                    'id': 'la4c31c646483507a0af4704bfc9a05d',
                    'target': 'nbb53904ad35364f97ccaa37328d92d9'
                },
                'l07b3c2e2f943fdd96401bd843a65ec0': {
                    'is_default': False,
                    'source': 'nfc24efd8fd13301a800f1040d492a8e',
                    'id': 'l07b3c2e2f943fdd96401bd843a65ec0',
                    'target': 'n5b5605fe8293882915fdaa0f17ce8c6'
                },
                'l1471a752c513955af4b6a0779ab3b1d': {
                    'is_default': False,
                    'source': 'nbb53904ad35364f97ccaa37328d92d9',
                    'id': 'l1471a752c513955af4b6a0779ab3b1d',
                    'target': 'nfc24efd8fd13301a800f1040d492a8e'
                }
            },
            'gateways': {
                'nd97fecb12ed3c7a9047197e84c58549': {
                    'incoming': 'ld7b5d7c371036019a55810d0d961986',
                    'outgoing': [
                        'lf6d76d6272c3bce84caf3d1113992d7',
                        'l74a1d2d3a4d30be8d53452f639616bd'
                    ],
                    'type': 'ParallelGateway',
                    'id': 'nd97fecb12ed3c7a9047197e84c58549',
                    'name': ''
                },
                'nfc24efd8fd13301a800f1040d492a8e': {
                    'incoming': [
                        'l1471a752c513955af4b6a0779ab3b1d',
                        'l774bb8683993b269005a0f13a38697a'
                    ],
                    'outgoing': 'l07b3c2e2f943fdd96401bd843a65ec0',
                    'type': 'ConvergeGateway',
                    'id': 'nfc24efd8fd13301a800f1040d492a8e',
                    'name': ''
                },
                'nbb53904ad35364f97ccaa37328d92d9': {
                    'incoming': [
                        'la4c31c646483507a0af4704bfc9a05d',
                        'lf477bb3adc43f71ad2c353e7da18b57'
                    ],
                    'outgoing': 'l1471a752c513955af4b6a0779ab3b1d',
                    'type': 'ConvergeGateway',
                    'id': 'nbb53904ad35364f97ccaa37328d92d9',
                    'name': ''
                },
                'n0244a7271a235219364f1377d230d04': {
                    'outgoing': [
                        'l33b08b83afd31fba746853a54c49cc0',
                        'ld7b5d7c371036019a55810d0d961986'
                    ],
                    'incoming': 'l12079c5e24a3b5eb22026a9a60a0638',
                    'name': '',
                    'type': 'ExclusiveGateway',
                    'conditions': {
                        'l33b08b83afd31fba746853a54c49cc0': {
                            'evaluate': '${bk_timing} > 10'
                        },
                        'ld7b5d7c371036019a55810d0d961986': {
                            'evaluate': '${bk_timing} <= 10'
                        }
                    },
                    'id': 'n0244a7271a235219364f1377d230d04'
                }
            },
            'start_event': {
                'incoming': '',
                'outgoing': 'l3cef190dbd23a908d994f80897a53b3',
                'type': 'EmptyStartEvent',
                'id': 'n7c985a50a8435b89e5daf3c618df732',
                'name': ''
            },
            'id': 'n874625694473feebade4dc485d7397e',
            'constants': {
                '${bk_timing}': {
                    'source_tag': 'sleep_timer.bk_timing',
                    'source_info': {
                        'n55c897bbc8c38cea18c99533348b1e3': [
                            'bk_timing'
                        ],
                        'n8ea7e6e5d76308cb3d9b151e2c4d82c': [
                            'bk_timing'
                        ],
                        'n9a17aecf7f232228e768152360564a3': [
                            'bk_timing'
                        ]
                    },
                    'name': 'timing',
                    'index': 0,
                    'custom_type': '',
                    'value': '1',
                    'show_type': 'show',
                    'source_type': 'component_inputs',
                    'key': '${bk_timing}',
                    'desc': ''
                }
            }
        }
        location = [
            {
                'status': '',
                'name': '',
                'x': START_X,
                'y': START_Y + EVENT_OR_GATEWAY_SHIFT_Y,
                'type': 'startpoint',
                'id': 'n7c985a50a8435b89e5daf3c618df732'
            },
            {
                'status': '',
                'stage_name': 'stage1',
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
                'y': START_Y + EVENT_OR_GATEWAY_SHIFT_Y,
                'type': 'branchgateway',
                'id': 'n0244a7271a235219364f1377d230d04'
            },
            {
                'status': '',
                'stage_name': 'stage2',
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
                'y': START_Y + EVENT_OR_GATEWAY_SHIFT_Y + SHIFT_Y,
                'type': 'parallelgateway',
                'id': 'nd97fecb12ed3c7a9047197e84c58549'
            },
            {
                'status': '',
                'stage_name': 'stage3',
                'name': 'node3',
                'x': START_X + SHIFT_X * 4,
                'y': START_Y + SHIFT_Y,
                'type': 'tasknode',
                'id': 'n3648618e4223512a8b7fc87b5112844'
            },
            {
                'status': '',
                'stage_name': 'stage3',
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
                'y': START_Y + EVENT_OR_GATEWAY_SHIFT_Y + SHIFT_Y,
                'type': 'convergegateway',
                'id': 'nbb53904ad35364f97ccaa37328d92d9'
            },
            {
                'status': '',
                'name': '',
                'x': START_X + SHIFT_X * 6,
                'y': START_Y + EVENT_OR_GATEWAY_SHIFT_Y,
                'type': 'convergegateway',
                'id': 'nfc24efd8fd13301a800f1040d492a8e'
            },
            {
                'status': '',
                'name': '',
                'x': START_X + SHIFT_X * 7,
                'y': START_Y + EVENT_OR_GATEWAY_SHIFT_Y,
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
        draw_pipeline(pipeline_tree, START_X, START_Y)
        self.assertEquals(pipeline_tree['location'], location)
        self.assertEquals(pipeline_tree['line'], line)
