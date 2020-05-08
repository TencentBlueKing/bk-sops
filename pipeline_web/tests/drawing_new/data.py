# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the 'License'); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


""" 
+------+        +------+        +------+        +------+        +------+
| afc8 |------->| c814 |------->| 4350 |------->| 8cca |------->| fb8b |
+------+        +------+        +------+        +------+        +------+
                    ↑              |
                    |              ↓
                    |           +------+
                     -----------| bb3d |
                                +------+
"""  # noqa
pipeline_with_circle = {
    'activities': {
        'nodeaf2161961809a91ebb00db88c814': {
            'component': {
                'code': 'pause_node',
                'data': {},
                'version': 'legacy'
            },
            'error_ignorable': False,
            'id': 'nodeaf2161961809a91ebb00db88c814',
            'incoming': ['linede15c52c74c1f5f566450d2c975a', 'line77a6cd587ff8476e75354c1d9469'],
            'loop': None,
            'name': 'pause1',
            'optional': False,
            'outgoing': 'line8602a85ef7e511765b77bc9f05e0',
            'type': 'ServiceActivity',
            'retryable': True,
            'skippable': True
        },
        'nodeeb9b2a00e46adacd9f57720e8cca': {
            'component': {
                'code': 'pause_node',
                'data': {},
                'version': 'legacy'
            },
            'error_ignorable': False,
            'id': 'nodeeb9b2a00e46adacd9f57720e8cca',
            'incoming': ['line5371f9df4afe9bb4351abdc19239'],
            'loop': None,
            'name': 'pause3',
            'optional': False,
            'outgoing': 'linecaddc6b1f1e421ce40456478dc6b',
            'type': 'ServiceActivity',
            'retryable': True,
            'skippable': True
        },
        'node0dfa73e80b9bf40aa05f2442bb3d': {
            'component': {
                'code': 'pause_node',
                'data': {},
                'version': 'legacy'
            },
            'error_ignorable': False,
            'id': 'node0dfa73e80b9bf40aa05f2442bb3d',
            'incoming': ['line7ac5fc7341c9ccbf773e9ca0c9cf'],
            'loop': None,
            'name': 'pause2',
            'optional': False,
            'outgoing': 'line77a6cd587ff8476e75354c1d9469',
            'type': 'ServiceActivity',
            'retryable': True,
            'skippable': True
        }
    },
    'constants': {},
    'end_event': {
        'id': 'nodea4bb3693dfb8d99d2084cee2fb8b',
        'incoming': ['linecaddc6b1f1e421ce40456478dc6b'],
        'name': '',
        'outgoing': '',
        'type': 'EmptyEndEvent'
    },
    'flows': {
        'linede15c52c74c1f5f566450d2c975a': {
            'id': 'linede15c52c74c1f5f566450d2c975a',
            'is_default': False,
            'source': 'node402bea676e660fab4cc643afafc8',
            'target': 'nodeaf2161961809a91ebb00db88c814'
        },
        'line8602a85ef7e511765b77bc9f05e0': {
            'id': 'line8602a85ef7e511765b77bc9f05e0',
            'is_default': False,
            'source': 'nodeaf2161961809a91ebb00db88c814',
            'target': 'node4149a8d446a7fc325b66a7ee4350'
        },
        'line5371f9df4afe9bb4351abdc19239': {
            'id': 'line5371f9df4afe9bb4351abdc19239',
            'is_default': False,
            'source': 'node4149a8d446a7fc325b66a7ee4350',
            'target': 'nodeeb9b2a00e46adacd9f57720e8cca'
        },
        'linecaddc6b1f1e421ce40456478dc6b': {
            'id': 'linecaddc6b1f1e421ce40456478dc6b',
            'is_default': False,
            'source': 'nodeeb9b2a00e46adacd9f57720e8cca',
            'target': 'nodea4bb3693dfb8d99d2084cee2fb8b'
        },
        'line7ac5fc7341c9ccbf773e9ca0c9cf': {
            'id': 'line7ac5fc7341c9ccbf773e9ca0c9cf',
            'is_default': False,
            'source': 'node4149a8d446a7fc325b66a7ee4350',
            'target': 'node0dfa73e80b9bf40aa05f2442bb3d'
        },
        'line77a6cd587ff8476e75354c1d9469': {
            'id': 'line77a6cd587ff8476e75354c1d9469',
            'is_default': False,
            'source': 'node0dfa73e80b9bf40aa05f2442bb3d',
            'target': 'nodeaf2161961809a91ebb00db88c814'
        }
    },
    'gateways': {
        'node4149a8d446a7fc325b66a7ee4350': {
            'id': 'node4149a8d446a7fc325b66a7ee4350',
            'incoming': ['line8602a85ef7e511765b77bc9f05e0'],
            'name': '',
            'outgoing': ['line5371f9df4afe9bb4351abdc19239', 'line7ac5fc7341c9ccbf773e9ca0c9cf'],
            'type': 'ExclusiveGateway',
            'conditions': {
                'line5371f9df4afe9bb4351abdc19239': {
                    'evaluate': '1 == 1',
                    'name': '1 == 1'
                },
                'line7ac5fc7341c9ccbf773e9ca0c9cf': {
                    'evaluate': '1 == 0',
                    'name': '1 == 0'
                }
            }
        }
    },
    'line': [
        {
            'id': 'linede15c52c74c1f5f566450d2c975a',
            'source': {
                'arrow': 'Right',
                'id': 'node402bea676e660fab4cc643afafc8'
            },
            'target': {
                'arrow': 'Left',
                'id': 'nodeaf2161961809a91ebb00db88c814'
            }
        },
        {
            'source': {
                'id': 'nodeaf2161961809a91ebb00db88c814',
                'arrow': 'Right'
            },
            'target': {
                'id': 'node4149a8d446a7fc325b66a7ee4350',
                'arrow': 'Left'
            },
            'id': 'line8602a85ef7e511765b77bc9f05e0'
        },
        {
            'source': {
                'id': 'node4149a8d446a7fc325b66a7ee4350',
                'arrow': 'Right'
            },
            'target': {
                'id': 'nodeeb9b2a00e46adacd9f57720e8cca',
                'arrow': 'Left'
            },
            'id': 'line5371f9df4afe9bb4351abdc19239'
        },
        {
            'source': {
                'id': 'nodeeb9b2a00e46adacd9f57720e8cca',
                'arrow': 'Right'
            },
            'target': {
                'id': 'nodea4bb3693dfb8d99d2084cee2fb8b',
                'arrow': 'Left'
            },
            'id': 'linecaddc6b1f1e421ce40456478dc6b'
        },
        {
            'source': {
                'id': 'node4149a8d446a7fc325b66a7ee4350',
                'arrow': 'Bottom'
            },
            'target': {
                'id': 'node0dfa73e80b9bf40aa05f2442bb3d',
                'arrow': 'Right'
            },
            'id': 'line7ac5fc7341c9ccbf773e9ca0c9cf'
        },
        {
            'source': {
                'id': 'node0dfa73e80b9bf40aa05f2442bb3d',
                'arrow': 'Left'
            },
            'target': {
                'id': 'nodeaf2161961809a91ebb00db88c814',
                'arrow': 'Bottom'
            },
            'id': 'line77a6cd587ff8476e75354c1d9469'
        }],
    'location': [
        {
            'id': 'node402bea676e660fab4cc643afafc8',
            'type': 'startpoint',
            'x': 80,
            'y': 150
        },
        {
            'id': 'nodeaf2161961809a91ebb00db88c814',
            'type': 'tasknode',
            'name': 'pause',
            'x': 205,
            'y': 150,
            'group': 'BK',
            'icon': ''
        },
        {
            'id': 'nodea4bb3693dfb8d99d2084cee2fb8b',
            'type': 'endpoint',
            'x': 840,
            'y': 150
        },
        {
            'id': 'node4149a8d446a7fc325b66a7ee4350',
            'type': 'branchgateway',
            'name': '',
            'x': 465,
            'y': 155
        },
        {
            'id': 'nodeeb9b2a00e46adacd9f57720e8cca',
            'type': 'tasknode',
            'name': 'pause',
            'x': 610,
            'y': 150,
            'group': 'BK',
            'icon': ''
        },
        {
            'id': 'node0dfa73e80b9bf40aa05f2442bb3d',
            'type': 'tasknode',
            'name': 'pause',
            'x': 290,
            'y': 260,
            'group': 'BK',
            'icon': ''
        }],
    'outputs': [],
    'start_event': {
        'id': 'node402bea676e660fab4cc643afafc8',
        'incoming': '',
        'name': '',
        'outgoing': 'linede15c52c74c1f5f566450d2c975a',
        'type': 'EmptyStartEvent'
    }
}

pipeline_without_gateways = {
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
            'name': '定时时间',
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

pipeline_with_gateways = pipeline_tree = {
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
