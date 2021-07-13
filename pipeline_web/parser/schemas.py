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

KEY_PATTERN = r"^((\$\{[a-zA-Z0-9_]+\})|([a-zA-Z0-9_]+))$"
SYSTEM_KEY_PATTERN = r"^((\$\{[a-zA-Z0-9_\.]+\})|([a-zA-Z0-9_\.]+))$"
ACT_MAX_LENGTH = 50
CONSTANT_MAX_LENGTH = 30
ONE_FLOW = {
    "anyOf": [
        {"type": "string"},
        {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1, "maxItems": 1},
    ]
}
MULTIPLE_FLOW = {
    "anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1}]
}

WEB_PIPELINE_SCHEMA = {
    "definitions": {},
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$id": "http://example.com/example.json",
    "type": "object",
    "properties": {
        "start_event": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "type": {"type": "string", "enum": ["EmptyStartEvent"]},
                "outgoing": ONE_FLOW,
            },
            "required": ["id", "name", "type", "outgoing"],
        },
        "end_event": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "type": {"type": "string", "enum": ["EmptyEndEvent"]},
                "incoming": MULTIPLE_FLOW,
            },
            "required": ["id", "name", "type", "incoming"],
        },
        "flows": {
            "type": "object",
            "patternProperties": {
                "^\\w+$": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "source": {"type": "string"},
                        "target": {"type": "string"},
                    },
                    "required": ["id", "source", "target"],
                }
            },
        },
        "gateways": {
            "type": "object",
            "patternProperties": {
                "^\\w+$": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "type": {"type": "string", "enum": ["ConvergeGateway"]},
                                "name": {"type": "string", "maxLength": ACT_MAX_LENGTH},
                                "incoming": MULTIPLE_FLOW,
                                "outgoing": ONE_FLOW,
                            },
                            "required": ["id", "type", "name", "incoming", "outgoing"],
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "type": {"type": "string", "enum": ["ParallelGateway"]},
                                "name": {"type": "string", "maxLength": ACT_MAX_LENGTH},
                                "incoming": MULTIPLE_FLOW,
                                "outgoing": MULTIPLE_FLOW,
                            },
                            "required": ["id", "type", "name", "incoming", "outgoing"],
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "type": {"type": "string", "enum": ["ExclusiveGateway"]},
                                "name": {"type": "string", "maxLength": ACT_MAX_LENGTH},
                                "conditions": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^\\w+$": {
                                            "type": "object",
                                            "properties": {"evaluate": {"type": "string"}},
                                            "required": ["evaluate"],
                                        }
                                    },
                                },
                                "incoming": MULTIPLE_FLOW,
                                "outgoing": MULTIPLE_FLOW,
                            },
                            "required": ["id", "type", "name", "incoming", "outgoing", "conditions"],
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "type": {"type": "string", "enum": ["ConditionalParallelGateway"]},
                                "name": {"type": "string", "maxLength": ACT_MAX_LENGTH},
                                "conditions": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^\\w+$": {
                                            "type": "object",
                                            "properties": {"evaluate": {"type": "string"}},
                                            "required": ["evaluate"],
                                        }
                                    },
                                },
                                "incoming": MULTIPLE_FLOW,
                                "outgoing": MULTIPLE_FLOW,
                            },
                            "required": ["id", "type", "name", "incoming", "outgoing", "conditions"],
                        },
                    ]
                }
            },
        },
        "activities": {
            "type": "object",
            "patternProperties": {
                "^\\w+$": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "type": {"type": "string", "enum": ["ServiceActivity", "SubProcess"]},
                        "name": {"type": "string", "minLength": 1, "maxLength": ACT_MAX_LENGTH},
                        "incoming": MULTIPLE_FLOW,
                        "outgoing": ONE_FLOW,
                        "component": {
                            "type": "object",
                            "properties": {
                                "code": {"type": "string"},
                                "data": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^\\w+$": {
                                            "type": "object",
                                            "properties": {
                                                "hook": {"type": "boolean"},
                                                "value": {
                                                    "type": ["string", "boolean", "object", "null", "number", "array"]
                                                },
                                            },
                                            "required": ["hook", "value"],
                                        }
                                    },
                                },
                            },
                            "required": ["code", "data"],
                        },
                    },
                    "required": ["id", "name", "type", "incoming", "outgoing"],
                }
            },
        },
        "constants": {
            "type": "object",
            "patternProperties": {
                KEY_PATTERN: {
                    "type": "object",
                    "properties": {
                        "source_tag": {"type": "string"},
                        "name": {"type": "string", "minLength": 1, "maxLength": CONSTANT_MAX_LENGTH},
                        "custom_type": {"type": "string"},
                        "source_type": {
                            "type": "string",
                            "enum": ["component_inputs", "component_outputs", "custom", "system"],
                        },
                        "validation": {"type": "string"},
                        "source_info": {
                            "type": "object",
                            "patternProperties": {"^\\w+$": {"type": "array", "items": {"type": "string"}}},
                        },
                        "key": {"type": "string", "pattern": KEY_PATTERN},
                        "desc": {"type": "string"},
                        "show_type": {"type": "string", "enum": ["show", "hide"]},
                    },
                }
            },
        },
        "outputs": {"type": "array", "items": {"type": "string", "pattern": SYSTEM_KEY_PATTERN}},
    },
    "required": ["start_event", "end_event", "activities", "gateways", "outputs", "constants"],
}
