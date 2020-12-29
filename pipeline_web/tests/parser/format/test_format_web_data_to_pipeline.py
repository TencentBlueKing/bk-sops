# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import json

from django.test import TestCase

from pipeline_web.parser.format import format_web_data_to_pipeline

web_tree = json.loads(
    """
    {
        "activities": {
            "n635e9dbdd4731b7922d2285032e873f": {
                "can_retry": true,
                "hooked_constants": [],
                "id": "n635e9dbdd4731b7922d2285032e873f",
                "incoming": [
                    "l4cd41e1fb4e3c6bb76a9eaa927ec5bd"
                ],
                "isSkipped": true,
                "loop": null,
                "name": "父流程_clone",
                "optional": false,
                "outgoing": "lf8082727223366db7cce16284f86f31",
                "stage_name": "步骤1",
                "template_id": "n264da9b090d33fc8eda1b7ae6b0d029",
                "type": "SubProcess",
                "version": "d8d9229f5f11bf642845b5741007cce7",
                "pipeline": {
                    "activities": {
                        "nab4fa758628344f9d7c3435d62571f4": {
                            "can_retry": true,
                            "hooked_constants": [],
                            "id": "nab4fa758628344f9d7c3435d62571f4",
                            "incoming": [
                                "l62677c18c0234a88bdbd8aa4287b47b"
                            ],
                            "isSkipped": true,
                            "loop": null,
                            "name": "子流程_clone",
                            "optional": false,
                            "outgoing": "lb69586240d83096bfee3771617ea75c",
                            "stage_name": "步骤1",
                            "template_id": "nda2521e3f8c3ffe98b79917c23e5244",
                            "type": "SubProcess",
                            "version": "fe6048201cd56a2053ca2bbf6a3941a6",
                            "pipeline": {
                                "activities": {
                                    "n4361d55c49f3b8fbdae08ac24031547": {
                                        "can_retry": true,
                                        "hooked_constants": [],
                                        "id": "n4361d55c49f3b8fbdae08ac24031547",
                                        "incoming": [
                                            "l9e50b3f95a938bc867641e20aeb06fe"
                                        ],
                                        "isSkipped": true,
                                        "loop": null,
                                        "name": "孙子流程_clone",
                                        "optional": false,
                                        "outgoing": "lb6b6d7e77463d6cae1938c08a801153",
                                        "stage_name": "步骤1",
                                        "template_id": "nc6adee9b98f317e982323d8115d903a",
                                        "type": "SubProcess",
                                        "version": "ef0fcea2fbe8b74d97c58fda28ebeaff",
                                        "pipeline": {
                                            "activities": {
                                                "ne44c8349f1b3d48bc7c0f82d5ff40bd": {
                                                    "component": {
                                                        "code": "sleep_timer",
                                                        "data": {
                                                            "bk_timing": {
                                                                "hook": true,
                                                                "value": "${bk_timing}"
                                                            }
                                                        },
                                                        "version": "legacy"
                                                    },
                                                    "error_ignorable": false,
                                                    "id": "ne44c8349f1b3d48bc7c0f82d5ff40bd",
                                                    "incoming": [
                                                        "la86b08263d936f4a06020dff15b837d"
                                                    ],
                                                    "loop": null,
                                                    "name": "定时",
                                                    "optional": false,
                                                    "outgoing": "l535bcd46a3c350c956ce4bf5dd9d2cd",
                                                    "retryable": true,
                                                    "skippable": true,
                                                    "stage_name": "步骤1",
                                                    "type": "ServiceActivity"
                                                },
                                                "nde9240e471c3c978e4147fce1d3e711": {
                                                    "component": {
                                                        "code": "sleep_timer",
                                                        "data": {
                                                            "bk_timing": {
                                                                "hook": false,
                                                                "value": "${b}"
                                                            }
                                                        },
                                                        "version": "legacy"
                                                    },
                                                    "error_ignorable": false,
                                                    "id": "nde9240e471c3c978e4147fce1d3e711",
                                                    "incoming": [
                                                        "l535bcd46a3c350c956ce4bf5dd9d2cd"
                                                    ],
                                                    "loop": null,
                                                    "name": "定时",
                                                    "optional": false,
                                                    "outgoing": "l5dd7f60092432818b940018c7e4e4fc",
                                                    "retryable": true,
                                                    "skippable": true,
                                                    "stage_name": "步骤1",
                                                    "type": "ServiceActivity"
                                                }
                                            },
                                            "constants": {
                                                "${bk_timing}": {
                                                    "custom_type": "",
                                                    "desc": "",
                                                    "formSchema": {
                                                        "attrs": {
                                                            "hookable": true,
                                                            "name": "定时时间",
                                                            "placeholder": "秒(s) 或 时间(%Y-%m-%d %H:%M:%S)",
                                                            "validation": [
                                                                {
                                                                    "type": "required"
                                                                },
                                                                {
                                                                    "type": "custom"
                                                                }
                                                            ]
                                                        },
                                                        "type": "input"
                                                    },
                                                    "index": 0,
                                                    "key": "${bk_timing}",
                                                    "name": "定时时间",
                                                    "show_type": "show",
                                                    "source_info": {
                                                        "ne44c8349f1b3d48bc7c0f82d5ff40bd": [
                                                            "bk_timing"
                                                        ]
                                                    },
                                                    "source_tag": "sleep_timer.bk_timing",
                                                    "source_type": "component_inputs",
                                                    "validation": "",
                                                    "value": "${b}",
                                                    "version": "legacy"
                                                },
                                                "${b}": {
                                                    "custom_type": "input",
                                                    "desc": "",
                                                    "form_schema": {
                                                        "attrs": {
                                                            "hookable": true,
                                                            "name": "输入框",
                                                            "validation": []
                                                        },
                                                        "type": "input"
                                                    },
                                                    "index": 1,
                                                    "key": "${b}",
                                                    "name": "b",
                                                    "show_type": "hide",
                                                    "source_info": {},
                                                    "source_tag": "input.input",
                                                    "source_type": "custom",
                                                    "validation": "^.+$",
                                                    "validator": [],
                                                    "value": "xxx",
                                                    "version": "legacy"
                                                }
                                            },
                                            "end_event": {
                                                "id": "n5310fd055223ff99a1998df892edb54",
                                                "incoming": [
                                                    "l5dd7f60092432818b940018c7e4e4fc"
                                                ],
                                                "name": "",
                                                "outgoing": "",
                                                "type": "EmptyEndEvent"
                                            },
                                            "flows": {
                                                "l535bcd46a3c350c956ce4bf5dd9d2cd": {
                                                    "id": "l535bcd46a3c350c956ce4bf5dd9d2cd",
                                                    "is_default": false,
                                                    "source": "ne44c8349f1b3d48bc7c0f82d5ff40bd",
                                                    "target": "nde9240e471c3c978e4147fce1d3e711"
                                                },
                                                "la86b08263d936f4a06020dff15b837d": {
                                                    "id": "la86b08263d936f4a06020dff15b837d",
                                                    "is_default": false,
                                                    "source": "n1596cabb3313ae697e90a01abf600d3",
                                                    "target": "ne44c8349f1b3d48bc7c0f82d5ff40bd"
                                                },
                                                "l5dd7f60092432818b940018c7e4e4fc": {
                                                    "id": "l5dd7f60092432818b940018c7e4e4fc",
                                                    "is_default": false,
                                                    "source": "nde9240e471c3c978e4147fce1d3e711",
                                                    "target": "n5310fd055223ff99a1998df892edb54"
                                                }
                                            },
                                            "gateways": {},
                                            "line": [
                                                {
                                                    "id": "la86b08263d936f4a06020dff15b837d",
                                                    "source": {
                                                        "arrow": "Right",
                                                        "id": "n1596cabb3313ae697e90a01abf600d3"
                                                    },
                                                    "target": {
                                                        "arrow": "Left",
                                                        "id": "ne44c8349f1b3d48bc7c0f82d5ff40bd"
                                                    }
                                                },
                                                {
                                                    "id": "l535bcd46a3c350c956ce4bf5dd9d2cd",
                                                    "source": {
                                                        "arrow": "Right",
                                                        "id": "ne44c8349f1b3d48bc7c0f82d5ff40bd"
                                                    },
                                                    "target": {
                                                        "arrow": "Left",
                                                        "id": "nde9240e471c3c978e4147fce1d3e711"
                                                    }
                                                },
                                                {
                                                    "id": "l5dd7f60092432818b940018c7e4e4fc",
                                                    "source": {
                                                        "arrow": "Right",
                                                        "id": "nde9240e471c3c978e4147fce1d3e711"
                                                    },
                                                    "target": {
                                                        "arrow": "Left",
                                                        "id": "n5310fd055223ff99a1998df892edb54"
                                                    }
                                                }
                                            ],
                                            "location": [
                                                {
                                                    "id": "n1596cabb3313ae697e90a01abf600d3",
                                                    "type": "startpoint",
                                                    "x": 20,
                                                    "y": 150
                                                },
                                                {
                                                    "group": "蓝鲸服务(BK)",
                                                    "icon": "",
                                                    "id": "ne44c8349f1b3d48bc7c0f82d5ff40bd",
                                                    "name": "定时",
                                                    "stage_name": "步骤1",
                                                    "type": "tasknode",
                                                    "x": 130,
                                                    "y": 145
                                                },
                                                {
                                                    "id": "n5310fd055223ff99a1998df892edb54",
                                                    "type": "endpoint",
                                                    "x": 540,
                                                    "y": 150
                                                },
                                                {
                                                    "group": "蓝鲸服务(BK)",
                                                    "icon": "",
                                                    "id": "nde9240e471c3c978e4147fce1d3e711",
                                                    "name": "定时",
                                                    "stage_name": "步骤1",
                                                    "type": "tasknode",
                                                    "x": 330,
                                                    "y": 145
                                                }
                                            ],
                                            "outputs": [],
                                            "start_event": {
                                                "id": "n1596cabb3313ae697e90a01abf600d3",
                                                "incoming": "",
                                                "name": "",
                                                "outgoing": "la86b08263d936f4a06020dff15b837d",
                                                "type": "EmptyStartEvent"
                                            },
                                            "id": "n4361d55c49f3b8fbdae08ac24031547"
                                        }
                                    },
                                    "n451f37c09063febbd395b08621dacb6": {
                                        "component": {
                                            "code": "sleep_timer",
                                            "data": {
                                                "bk_timing": {
                                                    "hook": false,
                                                    "value": "${ip}"
                                                },
                                                "force_check": {
                                                    "hook": false,
                                                    "value": true
                                                }
                                            },
                                            "version": "legacy"
                                        },
                                        "error_ignorable": false,
                                        "id": "n451f37c09063febbd395b08621dacb6",
                                        "incoming": [
                                            "l501f6abcb753aed8d4f61e9aef2b084"
                                        ],
                                        "loop": null,
                                        "name": "定时",
                                        "optional": false,
                                        "outgoing": "l9e50b3f95a938bc867641e20aeb06fe",
                                        "stage_name": "",
                                        "type": "ServiceActivity",
                                        "retryable": true,
                                        "skippable": true
                                    }
                                },
                                "constants": {
                                    "${b}": {
                                        "custom_type": "input",
                                        "desc": "",
                                        "form_schema": {
                                            "attrs": {
                                                "hookable": true,
                                                "name": "输入框",
                                                "validation": []
                                            },
                                            "type": "input"
                                        },
                                        "index": 0,
                                        "key": "${b}",
                                        "name": "b",
                                        "show_type": "show",
                                        "source_info": {},
                                        "source_tag": "input.input",
                                        "source_type": "custom",
                                        "validation": "^.+$",
                                        "validator": [],
                                        "value": "${c}",
                                        "version": "legacy"
                                    },
                                    "${ip}": {
                                        "custom_type": "ip_selector",
                                        "desc": "",
                                        "form_schema": {
                                            "type": "ip_selector",
                                            "attrs": {
                                                "name": "选择服务器",
                                                "hookable": true,
                                                "isMultiple": false,
                                                "validation": [
                                                    {
                                                        "type": "required"
                                                    }
                                                ],
                                                "default": {
                                                    "selectors": [
                                                        "ip"
                                                    ],
                                                    "topo": [],
                                                    "ip": [],
                                                    "filters": [],
                                                    "excludes": [],
                                                    "with_cloud_id": false
                                                }
                                            }
                                        },
                                        "index": 2,
                                        "key": "${ip}",
                                        "name": "ip",
                                        "show_type": "show",
                                        "source_info": {},
                                        "source_tag": "var_cmdb_ip_selector.ip_selector",
                                        "source_type": "custom",
                                        "validation": "",
                                        "value": "${ip}",
                                        "version": "legacy",
                                        "is_meta": false
                                    }
                                },
                                "end_event": {
                                    "id": "n5814616524a3f9b97910acaf5ca3222",
                                    "incoming": [
                                        "lb6b6d7e77463d6cae1938c08a801153"
                                    ],
                                    "name": "",
                                    "outgoing": "",
                                    "type": "EmptyEndEvent"
                                },
                                "flows": {
                                    "lb6b6d7e77463d6cae1938c08a801153": {
                                        "id": "lb6b6d7e77463d6cae1938c08a801153",
                                        "is_default": false,
                                        "source": "n4361d55c49f3b8fbdae08ac24031547",
                                        "target": "n5814616524a3f9b97910acaf5ca3222"
                                    },
                                    "l501f6abcb753aed8d4f61e9aef2b084": {
                                        "id": "l501f6abcb753aed8d4f61e9aef2b084",
                                        "is_default": false,
                                        "source": "n1c17515f81c3eb896561678e17c7b9e",
                                        "target": "n451f37c09063febbd395b08621dacb6"
                                    },
                                    "l9e50b3f95a938bc867641e20aeb06fe": {
                                        "id": "l9e50b3f95a938bc867641e20aeb06fe",
                                        "is_default": false,
                                        "source": "n451f37c09063febbd395b08621dacb6",
                                        "target": "n4361d55c49f3b8fbdae08ac24031547"
                                    }
                                },
                                "gateways": {},
                                "line": [
                                    {
                                        "id": "lb6b6d7e77463d6cae1938c08a801153",
                                        "source": {
                                            "arrow": "Right",
                                            "id": "n4361d55c49f3b8fbdae08ac24031547"
                                        },
                                        "target": {
                                            "arrow": "Left",
                                            "id": "n5814616524a3f9b97910acaf5ca3222"
                                        }
                                    },
                                    {
                                        "id": "l501f6abcb753aed8d4f61e9aef2b084",
                                        "source": {
                                            "arrow": "Right",
                                            "id": "n1c17515f81c3eb896561678e17c7b9e"
                                        },
                                        "target": {
                                            "arrow": "Left",
                                            "id": "n451f37c09063febbd395b08621dacb6"
                                        }
                                    },
                                    {
                                        "id": "l9e50b3f95a938bc867641e20aeb06fe",
                                        "source": {
                                            "arrow": "Right",
                                            "id": "n451f37c09063febbd395b08621dacb6"
                                        },
                                        "target": {
                                            "arrow": "Left",
                                            "id": "n4361d55c49f3b8fbdae08ac24031547"
                                        }
                                    }
                                ],
                                "location": [
                                    {
                                        "id": "n1c17515f81c3eb896561678e17c7b9e",
                                        "type": "startpoint",
                                        "x": 20,
                                        "y": 155
                                    },
                                    {
                                        "id": "n451f37c09063febbd395b08621dacb6",
                                        "type": "tasknode",
                                        "name": "定时",
                                        "stage_name": "",
                                        "x": 108,
                                        "y": 150,
                                        "group": "蓝鲸服务(BK)",
                                        "icon": ""
                                    },
                                    {
                                        "id": "n4361d55c49f3b8fbdae08ac24031547",
                                        "type": "subflow",
                                        "name": "孙子流程_clone",
                                        "stage_name": "步骤1",
                                        "x": 303,
                                        "y": 150
                                    },
                                    {
                                        "id": "n5814616524a3f9b97910acaf5ca3222",
                                        "type": "endpoint",
                                        "x": 498,
                                        "y": 155
                                    }
                                ],
                                "outputs": [],
                                "start_event": {
                                    "id": "n1c17515f81c3eb896561678e17c7b9e",
                                    "incoming": "",
                                    "name": "",
                                    "outgoing": "l501f6abcb753aed8d4f61e9aef2b084",
                                    "type": "EmptyStartEvent"
                                },
                                "id": "nab4fa758628344f9d7c3435d62571f4"
                            }
                        }
                    },
                    "constants": {
                        "${c}": {
                            "custom_type": "input",
                            "desc": "",
                            "form_schema": {
                                "attrs": {
                                    "hookable": true,
                                    "name": "输入框",
                                    "validation": []
                                },
                                "type": "input"
                            },
                            "index": 0,
                            "key": "${c}",
                            "name": "c",
                            "show_type": "show",
                            "source_info": {},
                            "source_tag": "input.input",
                            "source_type": "custom",
                            "validation": "^.+$",
                            "validator": [],
                            "value": "${d}",
                            "version": "legacy"
                        },
                        "${ip}": {
                            "name": "ip",
                            "key": "${ip}",
                            "desc": "",
                            "custom_type": "ip_selector",
                            "source_info": {
                                "nab4fa758628344f9d7c3435d62571f4": [
                                    "${ip}"
                                ]
                            },
                            "source_tag": "var_cmdb_ip_selector.ip_selector",
                            "value": {
                                "selectors": [
                                    "ip"
                                ],
                                "topo": [],
                                "ip": [
                                    {
                                        "bk_cloud_id": 0,
                                        "bk_host_name": "jobdev-1",
                                        "bk_host_id": 4,
                                        "bk_host_innerip": "1.1.1.1",
                                        "cloud": [
                                            {
                                                "id": "0",
                                                "bk_inst_name": "default area"
                                            }
                                        ],
                                        "agent": 1
                                    },
                                    {
                                        "bk_cloud_id": 0,
                                        "bk_host_name": "",
                                        "bk_host_id": 9,
                                        "bk_host_innerip": "2.2.2.2",
                                        "cloud": [
                                            {
                                                "id": "0",
                                                "bk_inst_name": "default area"
                                            }
                                        ],
                                        "agent": 0
                                    }
                                ],
                                "filters": [],
                                "excludes": [],
                                "with_cloud_id": false
                            },
                            "show_type": "show",
                            "source_type": "component_inputs",
                            "validation": "",
                            "index": 1,
                            "version": "legacy",
                            "form_schema": {
                                "type": "ip_selector",
                                "attrs": {
                                    "name": "ip",
                                    "hookable": true,
                                    "isMultiple": false,
                                    "validation": [
                                        {
                                            "type": "required"
                                        }
                                    ],
                                    "default": {
                                        "selectors": [
                                            "ip"
                                        ],
                                        "topo": [],
                                        "ip": [],
                                        "filters": [],
                                        "excludes": [],
                                        "with_cloud_id": false
                                    }
                                }
                            }
                        }
                    },
                    "end_event": {
                        "id": "na2f2993757832c59fd6ce21b992db56",
                        "incoming": [
                            "lb69586240d83096bfee3771617ea75c"
                        ],
                        "name": "",
                        "outgoing": "",
                        "type": "EmptyEndEvent"
                    },
                    "flows": {
                        "lb69586240d83096bfee3771617ea75c": {
                            "id": "lb69586240d83096bfee3771617ea75c",
                            "is_default": false,
                            "source": "nab4fa758628344f9d7c3435d62571f4",
                            "target": "na2f2993757832c59fd6ce21b992db56"
                        },
                        "l62677c18c0234a88bdbd8aa4287b47b": {
                            "id": "l62677c18c0234a88bdbd8aa4287b47b",
                            "is_default": false,
                            "source": "ndd32b3de7143cd2acd4b3e260882ab9",
                            "target": "nab4fa758628344f9d7c3435d62571f4"
                        }
                    },
                    "gateways": {},
                    "line": [
                        {
                            "id": "l62677c18c0234a88bdbd8aa4287b47b",
                            "source": {
                                "arrow": "Right",
                                "id": "ndd32b3de7143cd2acd4b3e260882ab9"
                            },
                            "target": {
                                "arrow": "Left",
                                "id": "nab4fa758628344f9d7c3435d62571f4"
                            }
                        },
                        {
                            "id": "lb69586240d83096bfee3771617ea75c",
                            "source": {
                                "arrow": "Right",
                                "id": "nab4fa758628344f9d7c3435d62571f4"
                            },
                            "target": {
                                "arrow": "Left",
                                "id": "na2f2993757832c59fd6ce21b992db56"
                            }
                        }
                    ],
                    "location": [
                        {
                            "id": "ndd32b3de7143cd2acd4b3e260882ab9",
                            "type": "startpoint",
                            "x": 20,
                            "y": 150
                        },
                        {
                            "id": "na2f2993757832c59fd6ce21b992db56",
                            "type": "endpoint",
                            "x": 540,
                            "y": 150
                        },
                        {
                            "id": "nab4fa758628344f9d7c3435d62571f4",
                            "type": "subflow",
                            "name": "子流程_clone",
                            "stage_name": "步骤1",
                            "x": 220,
                            "y": 145
                        }
                    ],
                    "outputs": [],
                    "start_event": {
                        "id": "ndd32b3de7143cd2acd4b3e260882ab9",
                        "incoming": "",
                        "name": "",
                        "outgoing": "l62677c18c0234a88bdbd8aa4287b47b",
                        "type": "EmptyStartEvent"
                    },
                    "id": "n635e9dbdd4731b7922d2285032e873f"
                }
            },
            "nac621f53104387ebc893f3063d4656b": {
                "component": {
                    "code": "sleep_timer",
                    "data": {
                        "bk_timing": {
                            "hook": false,
                            "value": "${time}"
                        },
                        "force_check": {
                            "hook": false,
                            "value": true
                        }
                    },
                    "version": "legacy"
                },
                "error_ignorable": false,
                "id": "nac621f53104387ebc893f3063d4656b",
                "incoming": [
                    "l9e5c0c3a3d73fad87ee077690f67546"
                ],
                "loop": null,
                "name": "定时",
                "optional": false,
                "outgoing": "l480639665a5360284dfeb8384f59d8c",
                "stage_name": "",
                "type": "ServiceActivity",
                "retryable": true,
                "skippable": true
            },
            "n465cfafc9723b14abfd93c20c15f101": {
                "component": {
                    "code": "sleep_timer",
                    "data": {
                        "bk_timing": {
                            "hook": false,
                            "value": "${1 if _result else 2}"
                        },
                        "force_check": {
                            "hook": false,
                            "value": true
                        }
                    },
                    "version": "legacy"
                },
                "error_ignorable": false,
                "id": "n465cfafc9723b14abfd93c20c15f101",
                "incoming": [
                    "l480639665a5360284dfeb8384f59d8c"
                ],
                "loop": null,
                "name": "定时",
                "optional": false,
                "outgoing": "l8a74b20b9ee366f8a521ee765da9259",
                "stage_name": "",
                "type": "ServiceActivity",
                "retryable": true,
                "skippable": true
            },
            "n67f91916e3036e39693910f9aa7635b": {
                "component": {
                    "code": "sleep_timer",
                    "data": {
                        "bk_timing": {
                            "hook": false,
                            "value": "${exp}"
                        },
                        "force_check": {
                            "hook": false,
                            "value": true
                        }
                    },
                    "version": "legacy"
                },
                "error_ignorable": false,
                "id": "n67f91916e3036e39693910f9aa7635b",
                "incoming": [
                    "l8a74b20b9ee366f8a521ee765da9259"
                ],
                "loop": null,
                "name": "定时",
                "optional": false,
                "outgoing": "l231ee42e8a63b7886f95b2df53c2325",
                "stage_name": "",
                "type": "ServiceActivity",
                "retryable": true,
                "skippable": true
            },
            "nb0186bd7c163a3d8919220e7004b3b2": {
                "component": {
                    "code": "sleep_timer",
                    "data": {
                        "bk_timing": {
                            "hook": false,
                            "value": "${exp1}"
                        },
                        "force_check": {
                            "hook": false,
                            "value": true
                        }
                    },
                    "version": "legacy"
                },
                "error_ignorable": false,
                "id": "nb0186bd7c163a3d8919220e7004b3b2",
                "incoming": [
                    "l231ee42e8a63b7886f95b2df53c2325"
                ],
                "loop": null,
                "name": "定时",
                "optional": false,
                "outgoing": "l5ff97b7195f30f4ab21b48f53ec3ccd",
                "stage_name": "",
                "type": "ServiceActivity",
                "retryable": true,
                "skippable": true
            },
            "na0f5f9f502e3a6e98322f1a2979e6b1": {
                "component": {
                    "code": "sleep_timer",
                    "data": {
                        "bk_timing": {
                            "hook": false,
                            "value": "${output_exp}"
                        },
                        "force_check": {
                            "hook": false,
                            "value": true
                        }
                    },
                    "version": "legacy"
                },
                "error_ignorable": false,
                "id": "na0f5f9f502e3a6e98322f1a2979e6b1",
                "incoming": [
                    "l5ff97b7195f30f4ab21b48f53ec3ccd"
                ],
                "loop": null,
                "name": "定时",
                "optional": false,
                "outgoing": "l4cd41e1fb4e3c6bb76a9eaa927ec5bd",
                "stage_name": "",
                "type": "ServiceActivity",
                "retryable": true,
                "skippable": true
            }
        },
        "constants": {
            "${d}": {
                "custom_type": "input",
                "desc": "",
                "form_schema": {
                    "attrs": {
                        "hookable": true,
                        "name": "输入框",
                        "validation": []
                    },
                    "type": "input"
                },
                "index": 0,
                "key": "${d}",
                "name": "d",
                "show_type": "show",
                "source_info": {},
                "source_tag": "input.input",
                "source_type": "custom",
                "validation": "^.+$",
                "validator": [],
                "value": "3",
                "version": "legacy"
            },
            "${time}": {
                "custom_type": "input",
                "desc": "",
                "form_schema": {
                    "type": "input",
                    "attrs": {
                        "name": "输入框",
                        "hookable": true,
                        "validation": []
                    }
                },
                "index": 1,
                "key": "${time}",
                "name": "time",
                "show_type": "hide",
                "source_info": {},
                "source_tag": "input.input",
                "source_type": "custom",
                "validation": "^.+$",
                "value": "${time2}",
                "version": "legacy"
            },
            "${time2}": {
                "custom_type": "input",
                "desc": "",
                "form_schema": {
                    "type": "input",
                    "attrs": {
                        "name": "输入框",
                        "hookable": true,
                        "validation": []
                    }
                },
                "index": 2,
                "key": "${time2}",
                "name": "time2",
                "show_type": "hide",
                "source_info": {},
                "source_tag": "input.input",
                "source_type": "custom",
                "validation": "^.+$",
                "value": "3",
                "version": "legacy"
            },
            "${_result}": {
                "name": "执行结果",
                "key": "${_result}",
                "desc": "",
                "custom_type": "",
                "source_info": {
                    "nac621f53104387ebc893f3063d4656b": [
                        "_result"
                    ]
                },
                "source_tag": "",
                "value": "",
                "show_type": "hide",
                "source_type": "component_outputs",
                "validation": "",
                "index": 3,
                "version": "legacy"
            },
            "${exp}": {
                "custom_type": "input",
                "desc": "",
                "form_schema": {
                    "type": "input",
                    "attrs": {
                        "name": "输入框",
                        "hookable": true,
                        "validation": []
                    }
                },
                "index": 4,
                "key": "${exp}",
                "name": "exp",
                "show_type": "show",
                "source_info": {},
                "source_tag": "input.input",
                "source_type": "custom",
                "validation": "^.+$",
                "value": "${10 if int(d) < 10 else d}",
                "version": "legacy"
            },
            "${exp1}": {
                "custom_type": "input",
                "desc": "",
                "form_schema": {
                    "type": "input",
                    "attrs": {
                        "name": "输入框",
                        "hookable": true,
                        "validation": []
                    }
                },
                "index": 5,
                "key": "${exp1}",
                "name": "exp1",
                "show_type": "hide",
                "source_info": {},
                "source_tag": "input.input",
                "source_type": "custom",
                "validation": "^.+$",
                "value": "${5 if int(d) < 10 else d}",
                "version": "legacy"
            },
            "${output_exp}": {
                "custom_type": "input",
                "desc": "",
                "form_schema": {
                    "type": "input",
                    "attrs": {
                        "name": "输入框",
                        "hookable": true,
                        "validation": []
                    }
                },
                "index": 6,
                "key": "${output_exp}",
                "name": "output_exp",
                "show_type": "hide",
                "source_info": {},
                "source_tag": "input.input",
                "source_type": "custom",
                "validation": "^.+$",
                "value": "${1 if _result else xxx}",
                "version": "legacy"
            }
        },
        "end_event": {
            "id": "nb503f6c50813da79441f16f40f2bf0d",
            "incoming": [
                "lf8082727223366db7cce16284f86f31"
            ],
            "name": "",
            "outgoing": "",
            "type": "EmptyEndEvent"
        },
        "flows": {
            "lf8082727223366db7cce16284f86f31": {
                "id": "lf8082727223366db7cce16284f86f31",
                "is_default": false,
                "source": "n635e9dbdd4731b7922d2285032e873f",
                "target": "nb503f6c50813da79441f16f40f2bf0d"
            },
            "l9e5c0c3a3d73fad87ee077690f67546": {
                "id": "l9e5c0c3a3d73fad87ee077690f67546",
                "is_default": false,
                "source": "nbf3cb0f30583b8d9fee415099ad625f",
                "target": "nac621f53104387ebc893f3063d4656b"
            },
            "l480639665a5360284dfeb8384f59d8c": {
                "id": "l480639665a5360284dfeb8384f59d8c",
                "is_default": false,
                "source": "nac621f53104387ebc893f3063d4656b",
                "target": "n465cfafc9723b14abfd93c20c15f101"
            },
            "l8a74b20b9ee366f8a521ee765da9259": {
                "id": "l8a74b20b9ee366f8a521ee765da9259",
                "is_default": false,
                "source": "n465cfafc9723b14abfd93c20c15f101",
                "target": "n67f91916e3036e39693910f9aa7635b"
            },
            "l231ee42e8a63b7886f95b2df53c2325": {
                "id": "l231ee42e8a63b7886f95b2df53c2325",
                "is_default": false,
                "source": "n67f91916e3036e39693910f9aa7635b",
                "target": "nb0186bd7c163a3d8919220e7004b3b2"
            },
            "l5ff97b7195f30f4ab21b48f53ec3ccd": {
                "id": "l5ff97b7195f30f4ab21b48f53ec3ccd",
                "is_default": false,
                "source": "nb0186bd7c163a3d8919220e7004b3b2",
                "target": "na0f5f9f502e3a6e98322f1a2979e6b1"
            },
            "l4cd41e1fb4e3c6bb76a9eaa927ec5bd": {
                "id": "l4cd41e1fb4e3c6bb76a9eaa927ec5bd",
                "is_default": false,
                "source": "na0f5f9f502e3a6e98322f1a2979e6b1",
                "target": "n635e9dbdd4731b7922d2285032e873f"
            }
        },
        "gateways": {},
        "line": [
            {
                "id": "lf8082727223366db7cce16284f86f31",
                "source": {
                    "arrow": "Right",
                    "id": "n635e9dbdd4731b7922d2285032e873f"
                },
                "target": {
                    "arrow": "Left",
                    "id": "nb503f6c50813da79441f16f40f2bf0d"
                }
            },
            {
                "source": {
                    "arrow": "Right",
                    "id": "nbf3cb0f30583b8d9fee415099ad625f"
                },
                "target": {
                    "id": "nac621f53104387ebc893f3063d4656b",
                    "arrow": "Left"
                },
                "id": "l9e5c0c3a3d73fad87ee077690f67546"
            },
            {
                "source": {
                    "arrow": "Right",
                    "id": "nac621f53104387ebc893f3063d4656b"
                },
                "target": {
                    "id": "n465cfafc9723b14abfd93c20c15f101",
                    "arrow": "Left"
                },
                "id": "l480639665a5360284dfeb8384f59d8c"
            },
            {
                "source": {
                    "arrow": "Right",
                    "id": "n465cfafc9723b14abfd93c20c15f101"
                },
                "target": {
                    "id": "n67f91916e3036e39693910f9aa7635b",
                    "arrow": "Left"
                },
                "id": "l8a74b20b9ee366f8a521ee765da9259"
            },
            {
                "source": {
                    "arrow": "Right",
                    "id": "n67f91916e3036e39693910f9aa7635b"
                },
                "target": {
                    "id": "nb0186bd7c163a3d8919220e7004b3b2",
                    "arrow": "Left"
                },
                "id": "l231ee42e8a63b7886f95b2df53c2325"
            },
            {
                "source": {
                    "arrow": "Right",
                    "id": "nb0186bd7c163a3d8919220e7004b3b2"
                },
                "target": {
                    "id": "na0f5f9f502e3a6e98322f1a2979e6b1",
                    "arrow": "Left"
                },
                "id": "l5ff97b7195f30f4ab21b48f53ec3ccd"
            },
            {
                "source": {
                    "arrow": "Right",
                    "id": "na0f5f9f502e3a6e98322f1a2979e6b1"
                },
                "target": {
                    "id": "n635e9dbdd4731b7922d2285032e873f",
                    "arrow": "Left"
                },
                "id": "l4cd41e1fb4e3c6bb76a9eaa927ec5bd"
            }
        ],
        "location": [
            {
                "id": "nbf3cb0f30583b8d9fee415099ad625f",
                "type": "startpoint",
                "x": 20,
                "y": 150
            },
            {
                "id": "nb503f6c50813da79441f16f40f2bf0d",
                "type": "endpoint",
                "x": 540,
                "y": 150
            },
            {
                "id": "n635e9dbdd4731b7922d2285032e873f",
                "type": "subflow",
                "name": "父流程_clone",
                "stage_name": "步骤1",
                "x": 220,
                "y": 145
            },
            {
                "id": "nac621f53104387ebc893f3063d4656b",
                "type": "tasknode",
                "name": "定时",
                "stage_name": "",
                "x": 110,
                "y": 365,
                "group": "蓝鲸服务(BK)",
                "icon": ""
            },
            {
                "id": "n465cfafc9723b14abfd93c20c15f101",
                "type": "tasknode",
                "name": "定时",
                "stage_name": "",
                "x": 310,
                "y": 365,
                "group": "蓝鲸服务(BK)",
                "icon": ""
            },
            {
                "id": "n67f91916e3036e39693910f9aa7635b",
                "type": "tasknode",
                "name": "定时",
                "stage_name": "",
                "x": 510,
                "y": 365,
                "group": "蓝鲸服务(BK)",
                "icon": ""
            },
            {
                "id": "nb0186bd7c163a3d8919220e7004b3b2",
                "type": "tasknode",
                "name": "定时",
                "stage_name": "",
                "x": 710,
                "y": 365,
                "group": "蓝鲸服务(BK)",
                "icon": ""
            },
            {
                "id": "na0f5f9f502e3a6e98322f1a2979e6b1",
                "type": "tasknode",
                "name": "定时",
                "stage_name": "",
                "x": 910,
                "y": 365,
                "group": "蓝鲸服务(BK)",
                "icon": ""
            }
        ],
        "outputs": [],
        "start_event": {
            "id": "nbf3cb0f30583b8d9fee415099ad625f",
            "incoming": "",
            "name": "",
            "outgoing": "l9e5c0c3a3d73fad87ee077690f67546",
            "type": "EmptyStartEvent"
        },
        "id": "n86d00b8416b3cfda9e5dcd7684bbc5a"
    }
    """
)

pipeline_tree = json.loads(
    """
    {
        "activities": {
            "n635e9dbdd4731b7922d2285032e873f": {
                "can_retry": true,
                "hooked_constants": [],
                "id": "n635e9dbdd4731b7922d2285032e873f",
                "incoming": [
                    "l4cd41e1fb4e3c6bb76a9eaa927ec5bd"
                ],
                "isSkipped": true,
                "loop": null,
                "name": "父流程_clone",
                "optional": false,
                "outgoing": "lf8082727223366db7cce16284f86f31",
                "stage_name": "步骤1",
                "template_id": "n264da9b090d33fc8eda1b7ae6b0d029",
                "type": "SubProcess",
                "version": "d8d9229f5f11bf642845b5741007cce7",
                "pipeline": {
                    "activities": {
                        "nab4fa758628344f9d7c3435d62571f4": {
                            "can_retry": true,
                            "hooked_constants": [],
                            "id": "nab4fa758628344f9d7c3435d62571f4",
                            "incoming": [
                                "l62677c18c0234a88bdbd8aa4287b47b"
                            ],
                            "isSkipped": true,
                            "loop": null,
                            "name": "子流程_clone",
                            "optional": false,
                            "outgoing": "lb69586240d83096bfee3771617ea75c",
                            "stage_name": "步骤1",
                            "template_id": "nda2521e3f8c3ffe98b79917c23e5244",
                            "type": "SubProcess",
                            "version": "fe6048201cd56a2053ca2bbf6a3941a6",
                            "pipeline": {
                                "activities": {
                                    "n4361d55c49f3b8fbdae08ac24031547": {
                                        "can_retry": true,
                                        "hooked_constants": [],
                                        "id": "n4361d55c49f3b8fbdae08ac24031547",
                                        "incoming": [
                                            "l9e50b3f95a938bc867641e20aeb06fe"
                                        ],
                                        "isSkipped": true,
                                        "loop": null,
                                        "name": "孙子流程_clone",
                                        "optional": false,
                                        "outgoing": "lb6b6d7e77463d6cae1938c08a801153",
                                        "stage_name": "步骤1",
                                        "template_id": "nc6adee9b98f317e982323d8115d903a",
                                        "type": "SubProcess",
                                        "version": "ef0fcea2fbe8b74d97c58fda28ebeaff",
                                        "pipeline": {
                                            "activities": {
                                                "ne44c8349f1b3d48bc7c0f82d5ff40bd": {
                                                    "component": {
                                                        "code": "sleep_timer",
                                                        "version": "legacy",
                                                        "inputs": {
                                                            "bk_timing": {
                                                                "type": "splice",
                                                                "value": "${bk_timing}",
                                                                "is_param": false
                                                            }
                                                        },
                                                        "global_outputs": {}
                                                    },
                                                    "error_ignorable": false,
                                                    "id": "ne44c8349f1b3d48bc7c0f82d5ff40bd",
                                                    "incoming": [
                                                        "la86b08263d936f4a06020dff15b837d"
                                                    ],
                                                    "loop": null,
                                                    "name": "定时",
                                                    "optional": false,
                                                    "outgoing": "l535bcd46a3c350c956ce4bf5dd9d2cd",
                                                    "retryable": true,
                                                    "skippable": true,
                                                    "stage_name": "步骤1",
                                                    "type": "ServiceActivity"
                                                },
                                                "nde9240e471c3c978e4147fce1d3e711": {
                                                    "component": {
                                                        "code": "sleep_timer",
                                                        "version": "legacy",
                                                        "inputs": {
                                                            "bk_timing": {
                                                                "type": "splice",
                                                                "value": "${b}",
                                                                "is_param": false
                                                            }
                                                        },
                                                        "global_outputs": {}
                                                    },
                                                    "error_ignorable": false,
                                                    "id": "nde9240e471c3c978e4147fce1d3e711",
                                                    "incoming": [
                                                        "l535bcd46a3c350c956ce4bf5dd9d2cd"
                                                    ],
                                                    "loop": null,
                                                    "name": "定时",
                                                    "optional": false,
                                                    "outgoing": "l5dd7f60092432818b940018c7e4e4fc",
                                                    "retryable": true,
                                                    "skippable": true,
                                                    "stage_name": "步骤1",
                                                    "type": "ServiceActivity"
                                                }
                                            },
                                            "end_event": {
                                                "id": "n5310fd055223ff99a1998df892edb54",
                                                "incoming": [
                                                    "l5dd7f60092432818b940018c7e4e4fc"
                                                ],
                                                "name": "",
                                                "outgoing": "",
                                                "type": "EmptyEndEvent"
                                            },
                                            "flows": {
                                                "l535bcd46a3c350c956ce4bf5dd9d2cd": {
                                                    "id": "l535bcd46a3c350c956ce4bf5dd9d2cd",
                                                    "is_default": false,
                                                    "source": "ne44c8349f1b3d48bc7c0f82d5ff40bd",
                                                    "target": "nde9240e471c3c978e4147fce1d3e711"
                                                },
                                                "la86b08263d936f4a06020dff15b837d": {
                                                    "id": "la86b08263d936f4a06020dff15b837d",
                                                    "is_default": false,
                                                    "source": "n1596cabb3313ae697e90a01abf600d3",
                                                    "target": "ne44c8349f1b3d48bc7c0f82d5ff40bd"
                                                },
                                                "l5dd7f60092432818b940018c7e4e4fc": {
                                                    "id": "l5dd7f60092432818b940018c7e4e4fc",
                                                    "is_default": false,
                                                    "source": "nde9240e471c3c978e4147fce1d3e711",
                                                    "target": "n5310fd055223ff99a1998df892edb54"
                                                }
                                            },
                                            "gateways": {},
                                            "line": [
                                                {
                                                    "id": "la86b08263d936f4a06020dff15b837d",
                                                    "source": {
                                                        "arrow": "Right",
                                                        "id": "n1596cabb3313ae697e90a01abf600d3"
                                                    },
                                                    "target": {
                                                        "arrow": "Left",
                                                        "id": "ne44c8349f1b3d48bc7c0f82d5ff40bd"
                                                    }
                                                },
                                                {
                                                    "id": "l535bcd46a3c350c956ce4bf5dd9d2cd",
                                                    "source": {
                                                        "arrow": "Right",
                                                        "id": "ne44c8349f1b3d48bc7c0f82d5ff40bd"
                                                    },
                                                    "target": {
                                                        "arrow": "Left",
                                                        "id": "nde9240e471c3c978e4147fce1d3e711"
                                                    }
                                                },
                                                {
                                                    "id": "l5dd7f60092432818b940018c7e4e4fc",
                                                    "source": {
                                                        "arrow": "Right",
                                                        "id": "nde9240e471c3c978e4147fce1d3e711"
                                                    },
                                                    "target": {
                                                        "arrow": "Left",
                                                        "id": "n5310fd055223ff99a1998df892edb54"
                                                    }
                                                }
                                            ],
                                            "location": [
                                                {
                                                    "id": "n1596cabb3313ae697e90a01abf600d3",
                                                    "type": "startpoint",
                                                    "x": 20,
                                                    "y": 150
                                                },
                                                {
                                                    "group": "蓝鲸服务(BK)",
                                                    "icon": "",
                                                    "id": "ne44c8349f1b3d48bc7c0f82d5ff40bd",
                                                    "name": "定时",
                                                    "stage_name": "步骤1",
                                                    "type": "tasknode",
                                                    "x": 130,
                                                    "y": 145
                                                },
                                                {
                                                    "id": "n5310fd055223ff99a1998df892edb54",
                                                    "type": "endpoint",
                                                    "x": 540,
                                                    "y": 150
                                                },
                                                {
                                                    "group": "蓝鲸服务(BK)",
                                                    "icon": "",
                                                    "id": "nde9240e471c3c978e4147fce1d3e711",
                                                    "name": "定时",
                                                    "stage_name": "步骤1",
                                                    "type": "tasknode",
                                                    "x": 330,
                                                    "y": 145
                                                }
                                            ],
                                            "start_event": {
                                                "id": "n1596cabb3313ae697e90a01abf600d3",
                                                "incoming": "",
                                                "name": "",
                                                "outgoing": "la86b08263d936f4a06020dff15b837d",
                                                "type": "EmptyStartEvent"
                                            },
                                            "id": "n4361d55c49f3b8fbdae08ac24031547",
                                            "data": {
                                                "inputs": {
                                                    "${bk_timing}": {
                                                        "type": "splice",
                                                        "value": "${b}",
                                                        "is_param": true
                                                    },
                                                    "${b}": {
                                                        "type": "plain",
                                                        "value": "xxx",
                                                        "is_param": false
                                                    }
                                                },
                                                "outputs": []
                                            }
                                        },
                                        "params": {
                                            "${bk_timing}": {
                                                "type": "splice",
                                                "value": "${b}"
                                            }
                                        }
                                    },
                                    "n451f37c09063febbd395b08621dacb6": {
                                        "component": {
                                            "code": "sleep_timer",
                                            "version": "legacy",
                                            "inputs": {
                                                "bk_timing": {
                                                    "type": "splice",
                                                    "value": "${ip}",
                                                    "is_param": false
                                                },
                                                "force_check": {
                                                    "type": "plain",
                                                    "value": true,
                                                    "is_param": false
                                                }
                                            },
                                            "global_outputs": {}
                                        },
                                        "error_ignorable": false,
                                        "id": "n451f37c09063febbd395b08621dacb6",
                                        "incoming": [
                                            "l501f6abcb753aed8d4f61e9aef2b084"
                                        ],
                                        "loop": null,
                                        "name": "定时",
                                        "optional": false,
                                        "outgoing": "l9e50b3f95a938bc867641e20aeb06fe",
                                        "stage_name": "",
                                        "type": "ServiceActivity",
                                        "retryable": true,
                                        "skippable": true
                                    }
                                },
                                "end_event": {
                                    "id": "n5814616524a3f9b97910acaf5ca3222",
                                    "incoming": [
                                        "lb6b6d7e77463d6cae1938c08a801153"
                                    ],
                                    "name": "",
                                    "outgoing": "",
                                    "type": "EmptyEndEvent"
                                },
                                "flows": {
                                    "lb6b6d7e77463d6cae1938c08a801153": {
                                        "id": "lb6b6d7e77463d6cae1938c08a801153",
                                        "is_default": false,
                                        "source": "n4361d55c49f3b8fbdae08ac24031547",
                                        "target": "n5814616524a3f9b97910acaf5ca3222"
                                    },
                                    "l501f6abcb753aed8d4f61e9aef2b084": {
                                        "id": "l501f6abcb753aed8d4f61e9aef2b084",
                                        "is_default": false,
                                        "source": "n1c17515f81c3eb896561678e17c7b9e",
                                        "target": "n451f37c09063febbd395b08621dacb6"
                                    },
                                    "l9e50b3f95a938bc867641e20aeb06fe": {
                                        "id": "l9e50b3f95a938bc867641e20aeb06fe",
                                        "is_default": false,
                                        "source": "n451f37c09063febbd395b08621dacb6",
                                        "target": "n4361d55c49f3b8fbdae08ac24031547"
                                    }
                                },
                                "gateways": {},
                                "line": [
                                    {
                                        "id": "lb6b6d7e77463d6cae1938c08a801153",
                                        "source": {
                                            "arrow": "Right",
                                            "id": "n4361d55c49f3b8fbdae08ac24031547"
                                        },
                                        "target": {
                                            "arrow": "Left",
                                            "id": "n5814616524a3f9b97910acaf5ca3222"
                                        }
                                    },
                                    {
                                        "id": "l501f6abcb753aed8d4f61e9aef2b084",
                                        "source": {
                                            "arrow": "Right",
                                            "id": "n1c17515f81c3eb896561678e17c7b9e"
                                        },
                                        "target": {
                                            "arrow": "Left",
                                            "id": "n451f37c09063febbd395b08621dacb6"
                                        }
                                    },
                                    {
                                        "id": "l9e50b3f95a938bc867641e20aeb06fe",
                                        "source": {
                                            "arrow": "Right",
                                            "id": "n451f37c09063febbd395b08621dacb6"
                                        },
                                        "target": {
                                            "arrow": "Left",
                                            "id": "n4361d55c49f3b8fbdae08ac24031547"
                                        }
                                    }
                                ],
                                "location": [
                                    {
                                        "id": "n1c17515f81c3eb896561678e17c7b9e",
                                        "type": "startpoint",
                                        "x": 20,
                                        "y": 155
                                    },
                                    {
                                        "id": "n451f37c09063febbd395b08621dacb6",
                                        "type": "tasknode",
                                        "name": "定时",
                                        "stage_name": "",
                                        "x": 108,
                                        "y": 150,
                                        "group": "蓝鲸服务(BK)",
                                        "icon": ""
                                    },
                                    {
                                        "id": "n4361d55c49f3b8fbdae08ac24031547",
                                        "type": "subflow",
                                        "name": "孙子流程_clone",
                                        "stage_name": "步骤1",
                                        "x": 303,
                                        "y": 150
                                    },
                                    {
                                        "id": "n5814616524a3f9b97910acaf5ca3222",
                                        "type": "endpoint",
                                        "x": 498,
                                        "y": 155
                                    }
                                ],
                                "start_event": {
                                    "id": "n1c17515f81c3eb896561678e17c7b9e",
                                    "incoming": "",
                                    "name": "",
                                    "outgoing": "l501f6abcb753aed8d4f61e9aef2b084",
                                    "type": "EmptyStartEvent"
                                },
                                "id": "nab4fa758628344f9d7c3435d62571f4",
                                "data": {
                                    "inputs": {
                                        "${b}": {
                                            "type": "splice",
                                            "value": "${c}",
                                            "is_param": true
                                        },
                                        "${ip}": {
                                            "type": "lazy",
                                            "source_tag": "var_cmdb_ip_selector.ip_selector",
                                            "custom_type": "ip_selector",
                                            "value": "${ip}",
                                            "is_param": true
                                        }
                                    },
                                    "outputs": []
                                }
                            },
                            "params": {
                                "${b}": {
                                    "type": "splice",
                                    "value": "${c}"
                                },
                                "${ip}": {
                                    "type": "lazy",
                                    "source_tag": "var_cmdb_ip_selector.ip_selector",
                                    "custom_type": "ip_selector",
                                    "value": "${ip}"
                                }
                            }
                        }
                    },
                    "end_event": {
                        "id": "na2f2993757832c59fd6ce21b992db56",
                        "incoming": [
                            "lb69586240d83096bfee3771617ea75c"
                        ],
                        "name": "",
                        "outgoing": "",
                        "type": "EmptyEndEvent"
                    },
                    "flows": {
                        "lb69586240d83096bfee3771617ea75c": {
                            "id": "lb69586240d83096bfee3771617ea75c",
                            "is_default": false,
                            "source": "nab4fa758628344f9d7c3435d62571f4",
                            "target": "na2f2993757832c59fd6ce21b992db56"
                        },
                        "l62677c18c0234a88bdbd8aa4287b47b": {
                            "id": "l62677c18c0234a88bdbd8aa4287b47b",
                            "is_default": false,
                            "source": "ndd32b3de7143cd2acd4b3e260882ab9",
                            "target": "nab4fa758628344f9d7c3435d62571f4"
                        }
                    },
                    "gateways": {},
                    "line": [
                        {
                            "id": "l62677c18c0234a88bdbd8aa4287b47b",
                            "source": {
                                "arrow": "Right",
                                "id": "ndd32b3de7143cd2acd4b3e260882ab9"
                            },
                            "target": {
                                "arrow": "Left",
                                "id": "nab4fa758628344f9d7c3435d62571f4"
                            }
                        },
                        {
                            "id": "lb69586240d83096bfee3771617ea75c",
                            "source": {
                                "arrow": "Right",
                                "id": "nab4fa758628344f9d7c3435d62571f4"
                            },
                            "target": {
                                "arrow": "Left",
                                "id": "na2f2993757832c59fd6ce21b992db56"
                            }
                        }
                    ],
                    "location": [
                        {
                            "id": "ndd32b3de7143cd2acd4b3e260882ab9",
                            "type": "startpoint",
                            "x": 20,
                            "y": 150
                        },
                        {
                            "id": "na2f2993757832c59fd6ce21b992db56",
                            "type": "endpoint",
                            "x": 540,
                            "y": 150
                        },
                        {
                            "id": "nab4fa758628344f9d7c3435d62571f4",
                            "type": "subflow",
                            "name": "子流程_clone",
                            "stage_name": "步骤1",
                            "x": 220,
                            "y": 145
                        }
                    ],
                    "start_event": {
                        "id": "ndd32b3de7143cd2acd4b3e260882ab9",
                        "incoming": "",
                        "name": "",
                        "outgoing": "l62677c18c0234a88bdbd8aa4287b47b",
                        "type": "EmptyStartEvent"
                    },
                    "id": "n635e9dbdd4731b7922d2285032e873f",
                    "data": {
                        "inputs": {
                            "${c}": {
                                "type": "splice",
                                "value": "${d}",
                                "is_param": true
                            },
                            "${ip}": {
                                "type": "lazy",
                                "source_tag": "var_cmdb_ip_selector.ip_selector",
                                "custom_type": "ip_selector",
                                "value": {
                                    "selectors": [
                                        "ip"
                                    ],
                                    "topo": [],
                                    "ip": [
                                        {
                                            "bk_cloud_id": 0,
                                            "bk_host_name": "jobdev-1",
                                            "bk_host_id": 4,
                                            "bk_host_innerip": "1.1.1.1",
                                            "cloud": [
                                                {
                                                    "id": "0",
                                                    "bk_inst_name": "default area"
                                                }
                                            ],
                                            "agent": 1
                                        },
                                        {
                                            "bk_cloud_id": 0,
                                            "bk_host_name": "",
                                            "bk_host_id": 9,
                                            "bk_host_innerip": "2.2.2.2",
                                            "cloud": [
                                                {
                                                    "id": "0",
                                                    "bk_inst_name": "default area"
                                                }
                                            ],
                                            "agent": 0
                                        }
                                    ],
                                    "filters": [],
                                    "excludes": [],
                                    "with_cloud_id": false
                                },
                                "is_param": true
                            }
                        },
                        "outputs": []
                    }
                },
                "params": {
                    "${c}": {
                        "type": "splice",
                        "value": "${d}"
                    },
                    "${ip}": {
                        "type": "lazy",
                        "source_tag": "var_cmdb_ip_selector.ip_selector",
                        "custom_type": "ip_selector",
                        "value": {
                            "selectors": [
                                "ip"
                            ],
                            "topo": [],
                            "ip": [
                                {
                                    "bk_cloud_id": 0,
                                    "bk_host_name": "jobdev-1",
                                    "bk_host_id": 4,
                                    "bk_host_innerip": "1.1.1.1",
                                    "cloud": [
                                        {
                                            "id": "0",
                                            "bk_inst_name": "default area"
                                        }
                                    ],
                                    "agent": 1
                                },
                                {
                                    "bk_cloud_id": 0,
                                    "bk_host_name": "",
                                    "bk_host_id": 9,
                                    "bk_host_innerip": "2.2.2.2",
                                    "cloud": [
                                        {
                                            "id": "0",
                                            "bk_inst_name": "default area"
                                        }
                                    ],
                                    "agent": 0
                                }
                            ],
                            "filters": [],
                            "excludes": [],
                            "with_cloud_id": false
                        }
                    }
                }
            },
            "nac621f53104387ebc893f3063d4656b": {
                "component": {
                    "code": "sleep_timer",
                    "version": "legacy",
                    "inputs": {
                        "bk_timing": {
                            "type": "splice",
                            "value": "${time}",
                            "is_param": false
                        },
                        "force_check": {
                            "type": "plain",
                            "value": true,
                            "is_param": false
                        }
                    },
                    "global_outputs": {
                        "_result": "${_result}"
                    }
                },
                "error_ignorable": false,
                "id": "nac621f53104387ebc893f3063d4656b",
                "incoming": [
                    "l9e5c0c3a3d73fad87ee077690f67546"
                ],
                "loop": null,
                "name": "定时",
                "optional": false,
                "outgoing": "l480639665a5360284dfeb8384f59d8c",
                "stage_name": "",
                "type": "ServiceActivity",
                "retryable": true,
                "skippable": true
            },
            "n465cfafc9723b14abfd93c20c15f101": {
                "component": {
                    "code": "sleep_timer",
                    "version": "legacy",
                    "inputs": {
                        "bk_timing": {
                            "type": "splice",
                            "value": "${1 if _result else 2}",
                            "is_param": false
                        },
                        "force_check": {
                            "type": "plain",
                            "value": true,
                            "is_param": false
                        }
                    },
                    "global_outputs": {}
                },
                "error_ignorable": false,
                "id": "n465cfafc9723b14abfd93c20c15f101",
                "incoming": [
                    "l480639665a5360284dfeb8384f59d8c"
                ],
                "loop": null,
                "name": "定时",
                "optional": false,
                "outgoing": "l8a74b20b9ee366f8a521ee765da9259",
                "stage_name": "",
                "type": "ServiceActivity",
                "retryable": true,
                "skippable": true
            },
            "n67f91916e3036e39693910f9aa7635b": {
                "component": {
                    "code": "sleep_timer",
                    "version": "legacy",
                    "inputs": {
                        "bk_timing": {
                            "type": "splice",
                            "value": "${exp}",
                            "is_param": false
                        },
                        "force_check": {
                            "type": "plain",
                            "value": true,
                            "is_param": false
                        }
                    },
                    "global_outputs": {}
                },
                "error_ignorable": false,
                "id": "n67f91916e3036e39693910f9aa7635b",
                "incoming": [
                    "l8a74b20b9ee366f8a521ee765da9259"
                ],
                "loop": null,
                "name": "定时",
                "optional": false,
                "outgoing": "l231ee42e8a63b7886f95b2df53c2325",
                "stage_name": "",
                "type": "ServiceActivity",
                "retryable": true,
                "skippable": true
            },
            "nb0186bd7c163a3d8919220e7004b3b2": {
                "component": {
                    "code": "sleep_timer",
                    "version": "legacy",
                    "inputs": {
                        "bk_timing": {
                            "type": "splice",
                            "value": "${exp1}",
                            "is_param": false
                        },
                        "force_check": {
                            "type": "plain",
                            "value": true,
                            "is_param": false
                        }
                    },
                    "global_outputs": {}
                },
                "error_ignorable": false,
                "id": "nb0186bd7c163a3d8919220e7004b3b2",
                "incoming": [
                    "l231ee42e8a63b7886f95b2df53c2325"
                ],
                "loop": null,
                "name": "定时",
                "optional": false,
                "outgoing": "l5ff97b7195f30f4ab21b48f53ec3ccd",
                "stage_name": "",
                "type": "ServiceActivity",
                "retryable": true,
                "skippable": true
            },
            "na0f5f9f502e3a6e98322f1a2979e6b1": {
                "component": {
                    "code": "sleep_timer",
                    "version": "legacy",
                    "inputs": {
                        "bk_timing": {
                            "type": "splice",
                            "value": "${output_exp}",
                            "is_param": false
                        },
                        "force_check": {
                            "type": "plain",
                            "value": true,
                            "is_param": false
                        }
                    },
                    "global_outputs": {}
                },
                "error_ignorable": false,
                "id": "na0f5f9f502e3a6e98322f1a2979e6b1",
                "incoming": [
                    "l5ff97b7195f30f4ab21b48f53ec3ccd"
                ],
                "loop": null,
                "name": "定时",
                "optional": false,
                "outgoing": "l4cd41e1fb4e3c6bb76a9eaa927ec5bd",
                "stage_name": "",
                "type": "ServiceActivity",
                "retryable": true,
                "skippable": true
            }
        },
        "end_event": {
            "id": "nb503f6c50813da79441f16f40f2bf0d",
            "incoming": [
                "lf8082727223366db7cce16284f86f31"
            ],
            "name": "",
            "outgoing": "",
            "type": "EmptyEndEvent"
        },
        "flows": {
            "lf8082727223366db7cce16284f86f31": {
                "id": "lf8082727223366db7cce16284f86f31",
                "is_default": false,
                "source": "n635e9dbdd4731b7922d2285032e873f",
                "target": "nb503f6c50813da79441f16f40f2bf0d"
            },
            "l9e5c0c3a3d73fad87ee077690f67546": {
                "id": "l9e5c0c3a3d73fad87ee077690f67546",
                "is_default": false,
                "source": "nbf3cb0f30583b8d9fee415099ad625f",
                "target": "nac621f53104387ebc893f3063d4656b"
            },
            "l480639665a5360284dfeb8384f59d8c": {
                "id": "l480639665a5360284dfeb8384f59d8c",
                "is_default": false,
                "source": "nac621f53104387ebc893f3063d4656b",
                "target": "n465cfafc9723b14abfd93c20c15f101"
            },
            "l8a74b20b9ee366f8a521ee765da9259": {
                "id": "l8a74b20b9ee366f8a521ee765da9259",
                "is_default": false,
                "source": "n465cfafc9723b14abfd93c20c15f101",
                "target": "n67f91916e3036e39693910f9aa7635b"
            },
            "l231ee42e8a63b7886f95b2df53c2325": {
                "id": "l231ee42e8a63b7886f95b2df53c2325",
                "is_default": false,
                "source": "n67f91916e3036e39693910f9aa7635b",
                "target": "nb0186bd7c163a3d8919220e7004b3b2"
            },
            "l5ff97b7195f30f4ab21b48f53ec3ccd": {
                "id": "l5ff97b7195f30f4ab21b48f53ec3ccd",
                "is_default": false,
                "source": "nb0186bd7c163a3d8919220e7004b3b2",
                "target": "na0f5f9f502e3a6e98322f1a2979e6b1"
            },
            "l4cd41e1fb4e3c6bb76a9eaa927ec5bd": {
                "id": "l4cd41e1fb4e3c6bb76a9eaa927ec5bd",
                "is_default": false,
                "source": "na0f5f9f502e3a6e98322f1a2979e6b1",
                "target": "n635e9dbdd4731b7922d2285032e873f"
            }
        },
        "gateways": {},
        "line": [
            {
                "id": "lf8082727223366db7cce16284f86f31",
                "source": {
                    "arrow": "Right",
                    "id": "n635e9dbdd4731b7922d2285032e873f"
                },
                "target": {
                    "arrow": "Left",
                    "id": "nb503f6c50813da79441f16f40f2bf0d"
                }
            },
            {
                "source": {
                    "arrow": "Right",
                    "id": "nbf3cb0f30583b8d9fee415099ad625f"
                },
                "target": {
                    "id": "nac621f53104387ebc893f3063d4656b",
                    "arrow": "Left"
                },
                "id": "l9e5c0c3a3d73fad87ee077690f67546"
            },
            {
                "source": {
                    "arrow": "Right",
                    "id": "nac621f53104387ebc893f3063d4656b"
                },
                "target": {
                    "id": "n465cfafc9723b14abfd93c20c15f101",
                    "arrow": "Left"
                },
                "id": "l480639665a5360284dfeb8384f59d8c"
            },
            {
                "source": {
                    "arrow": "Right",
                    "id": "n465cfafc9723b14abfd93c20c15f101"
                },
                "target": {
                    "id": "n67f91916e3036e39693910f9aa7635b",
                    "arrow": "Left"
                },
                "id": "l8a74b20b9ee366f8a521ee765da9259"
            },
            {
                "source": {
                    "arrow": "Right",
                    "id": "n67f91916e3036e39693910f9aa7635b"
                },
                "target": {
                    "id": "nb0186bd7c163a3d8919220e7004b3b2",
                    "arrow": "Left"
                },
                "id": "l231ee42e8a63b7886f95b2df53c2325"
            },
            {
                "source": {
                    "arrow": "Right",
                    "id": "nb0186bd7c163a3d8919220e7004b3b2"
                },
                "target": {
                    "id": "na0f5f9f502e3a6e98322f1a2979e6b1",
                    "arrow": "Left"
                },
                "id": "l5ff97b7195f30f4ab21b48f53ec3ccd"
            },
            {
                "source": {
                    "arrow": "Right",
                    "id": "na0f5f9f502e3a6e98322f1a2979e6b1"
                },
                "target": {
                    "id": "n635e9dbdd4731b7922d2285032e873f",
                    "arrow": "Left"
                },
                "id": "l4cd41e1fb4e3c6bb76a9eaa927ec5bd"
            }
        ],
        "location": [
            {
                "id": "nbf3cb0f30583b8d9fee415099ad625f",
                "type": "startpoint",
                "x": 20,
                "y": 150
            },
            {
                "id": "nb503f6c50813da79441f16f40f2bf0d",
                "type": "endpoint",
                "x": 540,
                "y": 150
            },
            {
                "id": "n635e9dbdd4731b7922d2285032e873f",
                "type": "subflow",
                "name": "父流程_clone",
                "stage_name": "步骤1",
                "x": 220,
                "y": 145
            },
            {
                "id": "nac621f53104387ebc893f3063d4656b",
                "type": "tasknode",
                "name": "定时",
                "stage_name": "",
                "x": 110,
                "y": 365,
                "group": "蓝鲸服务(BK)",
                "icon": ""
            },
            {
                "id": "n465cfafc9723b14abfd93c20c15f101",
                "type": "tasknode",
                "name": "定时",
                "stage_name": "",
                "x": 310,
                "y": 365,
                "group": "蓝鲸服务(BK)",
                "icon": ""
            },
            {
                "id": "n67f91916e3036e39693910f9aa7635b",
                "type": "tasknode",
                "name": "定时",
                "stage_name": "",
                "x": 510,
                "y": 365,
                "group": "蓝鲸服务(BK)",
                "icon": ""
            },
            {
                "id": "nb0186bd7c163a3d8919220e7004b3b2",
                "type": "tasknode",
                "name": "定时",
                "stage_name": "",
                "x": 710,
                "y": 365,
                "group": "蓝鲸服务(BK)",
                "icon": ""
            },
            {
                "id": "na0f5f9f502e3a6e98322f1a2979e6b1",
                "type": "tasknode",
                "name": "定时",
                "stage_name": "",
                "x": 910,
                "y": 365,
                "group": "蓝鲸服务(BK)",
                "icon": ""
            }
        ],
        "start_event": {
            "id": "nbf3cb0f30583b8d9fee415099ad625f",
            "incoming": "",
            "name": "",
            "outgoing": "l9e5c0c3a3d73fad87ee077690f67546",
            "type": "EmptyStartEvent"
        },
        "id": "n86d00b8416b3cfda9e5dcd7684bbc5a",
        "data": {
            "inputs": {
                "${d}": {
                    "type": "plain",
                    "value": "3",
                    "is_param": false
                },
                "${time}": {
                    "type": "splice",
                    "value": "${time2}",
                    "is_param": false
                },
                "${time2}": {
                    "type": "plain",
                    "value": "3",
                    "is_param": false
                },
                "${_result}": {
                    "type": "splice",
                    "source_act": "nac621f53104387ebc893f3063d4656b",
                    "source_key": "_result",
                    "value": "",
                    "is_param": false
                },
                "${exp}": {
                    "type": "splice",
                    "value": "${10 if int(d) < 10 else d}",
                    "is_param": false
                },
                "${exp1}": {
                    "type": "splice",
                    "value": "${5 if int(d) < 10 else d}",
                    "is_param": false
                },
                "${output_exp}": {
                    "type": "splice",
                    "value": "${1 if _result else xxx}",
                    "is_param": false
                }
            },
            "outputs": []
        }
    }
    """
)


class FormatWebDataToPipelineTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_normal(self):
        """
        正常情况的一种测试用例，包含以下情况:
        四层子流程变量传递
        子流程变量命名空间独立
        隐藏变量引用解析
        隐藏变量表达式解析
        输出变量引用解析
        全局变量引用输出变量解析
        """
        self.assertEqual(format_web_data_to_pipeline(web_tree), pipeline_tree)
