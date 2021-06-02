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

from gcloud.tasktmpl3.domains.constants import analysis_pipeline_constants_ref
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class AnalysisPipelineConstantsRefTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_defective_tree(self):
        self.assertEqual(analysis_pipeline_constants_ref({}), {})

    def test_without_constants(self):
        tree = {
            "name": "new20210104070848",
            "activities": {
                "nodec360d91ee7d67988b2a62264fd9f": {
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {"hook": False, "value": "2"},
                            "force_check": {"hook": False, "value": True},
                        },
                        "version": "legacy",
                    },
                    "error_ignorable": False,
                    "id": "nodec360d91ee7d67988b2a62264fd9f",
                    "incoming": ["line7399828179d271cdbb29ee133e8a"],
                    "loop": None,
                    "name": "定时",
                    "optional": False,
                    "outgoing": "line48a3b3062c11580ffbac27e4fc30",
                    "stage_name": "",
                    "type": "ServiceActivity",
                    "retryable": True,
                    "skippable": True,
                    "labels": [],
                },
                "node5a259597d556caa0688af3e53833": {
                    "constants": {
                        "${ip}": {
                            "custom_type": "select",
                            "desc": "",
                            "form_schema": {},
                            "index": 1,
                            "key": "${ip}",
                            "name": "ip",
                            "show_type": "show",
                            "source_info": {},
                            "source_tag": "select.select",
                            "source_type": "custom",
                            "validation": "",
                            "value": "123123",
                            "version": "legacy",
                            "is_meta": True,
                        }
                    },
                    "hooked_constants": [],
                    "id": "node5a259597d556caa0688af3e53833",
                    "incoming": ["linedbd96913fb3c5dfa596d537d4b5d"],
                    "loop": None,
                    "name": "BK审核",
                    "optional": False,
                    "outgoing": "line5982954e5f6326958588f00b16f3",
                    "stage_name": "",
                    "template_id": 4820,
                    "version": "27015c4a4892fe9e79fbcd3fa5245675",
                    "type": "SubProcess",
                    "labels": [],
                    "can_retry": True,
                    "isSkipped": True,
                },
                "node5a34e12af59450b003e7aeabb1ac": {
                    "constants": {},
                    "hooked_constants": [],
                    "id": "node5a34e12af59450b003e7aeabb1ac",
                    "incoming": ["lineb8761ba520675afdd03db1650370"],
                    "loop": None,
                    "name": "暂停节点测试",
                    "optional": False,
                    "outgoing": "line2c42806ce4ebb1df4cac76585ec8",
                    "stage_name": "",
                    "template_id": 3279,
                    "version": "b4f28a48ea215a7d9b5960f512cd3af9",
                    "type": "SubProcess",
                    "labels": [],
                },
            },
            "gateways": {
                "nodee90a33e783f5fe4e8b7ff46310a4": {
                    "id": "nodee90a33e783f5fe4e8b7ff46310a4",
                    "incoming": ["line28b774b87c4a6968b5ea3e296bc6"],
                    "name": "",
                    "outgoing": ["linecc134c88c3db75f3a20753c192c6"],
                    "type": "ExclusiveGateway",
                    "conditions": {
                        "linecc134c88c3db75f3a20753c192c6": {
                            "evaluate": "1 == 1",
                            "name": "1 == 1",
                            "tag": "branch_nodee90a33e783f5fe4e8b7ff46310a4_node095ea25e61e41fec3ab588453d3c",
                        }
                    },
                },
                "node75c689c611cb7669bc6acf2afef9": {
                    "id": "node75c689c611cb7669bc6acf2afef9",
                    "incoming": ["line8c77088acd3d7f54dfe3f87b2875"],
                    "name": "",
                    "outgoing": ["line7399828179d271cdbb29ee133e8a", "linedbd96913fb3c5dfa596d537d4b5d"],
                    "type": "ParallelGateway",
                },
                "node6173a49319fde2df4b922bcc3bdf": {
                    "id": "node6173a49319fde2df4b922bcc3bdf",
                    "incoming": ["line48a3b3062c11580ffbac27e4fc30", "line5982954e5f6326958588f00b16f3"],
                    "name": "",
                    "outgoing": "line28b774b87c4a6968b5ea3e296bc6",
                    "type": "ConvergeGateway",
                },
            },
            "constants": {},
        }
        self.assertEqual(analysis_pipeline_constants_ref(tree), {})

    def test_full_case(self):
        tree = {
            "name": "new20210104070848",
            "activities": {
                "nodec360d91ee7d67988b2a62264fd9f": {
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {
                                "hook": False,
                                "value": {"k1": "${c1}", "k2": "${c2}", "k3": "${c3}", "k4": "${c4}"},
                            },
                            "force_check": {"hook": False, "value": True},
                        },
                        "version": "legacy",
                    },
                    "error_ignorable": False,
                    "id": "nodec360d91ee7d67988b2a62264fd9f",
                    "incoming": ["line7399828179d271cdbb29ee133e8a"],
                    "loop": None,
                    "name": "定时",
                    "optional": False,
                    "outgoing": "line48a3b3062c11580ffbac27e4fc30",
                    "stage_name": "",
                    "type": "ServiceActivity",
                    "retryable": True,
                    "skippable": True,
                    "labels": [],
                },
                "node5a259597d556caa0688af3e53833": {
                    "constants": {
                        "${ip}": {
                            "custom_type": "select",
                            "desc": "",
                            "form_schema": {},
                            "index": 1,
                            "key": "${ip}",
                            "name": "ip",
                            "show_type": "show",
                            "source_info": {},
                            "source_tag": "select.select",
                            "source_type": "custom",
                            "validation": "",
                            "value": "${c1}, ${c3}",
                            "version": "legacy",
                            "is_meta": True,
                        }
                    },
                    "hooked_constants": [],
                    "id": "node5a259597d556caa0688af3e53833",
                    "incoming": ["linedbd96913fb3c5dfa596d537d4b5d"],
                    "loop": None,
                    "name": "BK审核",
                    "optional": False,
                    "outgoing": "line5982954e5f6326958588f00b16f3",
                    "stage_name": "",
                    "template_id": 4820,
                    "version": "27015c4a4892fe9e79fbcd3fa5245675",
                    "type": "SubProcess",
                    "labels": [],
                    "can_retry": True,
                    "isSkipped": True,
                },
                "node5a34e12af59450b003e7aeabb1ac": {
                    "constants": {},
                    "hooked_constants": [],
                    "id": "node5a34e12af59450b003e7aeabb1ac",
                    "incoming": ["lineb8761ba520675afdd03db1650370"],
                    "loop": None,
                    "name": "暂停节点测试",
                    "optional": False,
                    "outgoing": "line2c42806ce4ebb1df4cac76585ec8",
                    "stage_name": "",
                    "template_id": 3279,
                    "version": "b4f28a48ea215a7d9b5960f512cd3af9",
                    "type": "SubProcess",
                    "labels": [],
                },
            },
            "gateways": {
                "nodee90a33e783f5fe4e8b7ff46310a4": {
                    "id": "nodee90a33e783f5fe4e8b7ff46310a4",
                    "incoming": ["line28b774b87c4a6968b5ea3e296bc6"],
                    "name": "",
                    "outgoing": ["linecc134c88c3db75f3a20753c192c6"],
                    "type": "ExclusiveGateway",
                    "conditions": {
                        "linecc134c88c3db75f3a20753c192c6": {
                            "evaluate": "${c2} == ${c1}",
                            "name": "1 == 1",
                            "tag": "branch_nodee90a33e783f5fe4e8b7ff46310a4_node095ea25e61e41fec3ab588453d3c",
                        }
                    },
                },
                "node75c689c611cb7669bc6acf2afef9": {
                    "id": "node75c689c611cb7669bc6acf2afef9",
                    "incoming": ["line8c77088acd3d7f54dfe3f87b2875"],
                    "name": "",
                    "outgoing": ["line7399828179d271cdbb29ee133e8a", "linedbd96913fb3c5dfa596d537d4b5d"],
                    "type": "ParallelGateway",
                },
                "node6173a49319fde2df4b922bcc3bdf": {
                    "id": "node6173a49319fde2df4b922bcc3bdf",
                    "incoming": ["line48a3b3062c11580ffbac27e4fc30", "line5982954e5f6326958588f00b16f3"],
                    "name": "",
                    "outgoing": "line28b774b87c4a6968b5ea3e296bc6",
                    "type": "ConvergeGateway",
                },
            },
            "constants": {
                "${c1}": {
                    "custom_type": "input",
                    "desc": "",
                    "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
                    "index": 1,
                    "key": "${c1}",
                    "name": "c1",
                    "show_type": "show",
                    "source_info": {},
                    "source_tag": "input.input",
                    "source_type": "custom",
                    "validation": "^.+$",
                    "value": "",
                    "version": "legacy",
                },
                "${c2}": {
                    "custom_type": "input",
                    "desc": "",
                    "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
                    "index": 1,
                    "key": "${c1}",
                    "name": "c1",
                    "show_type": "show",
                    "source_info": {},
                    "source_tag": "input.input",
                    "source_type": "custom",
                    "validation": "^.+$",
                    "value": "${c1}_${c3}",
                    "version": "legacy",
                },
                "${c3}": {
                    "custom_type": "input",
                    "desc": "",
                    "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
                    "index": 1,
                    "key": "${c1}",
                    "name": "c1",
                    "show_type": "show",
                    "source_info": {},
                    "source_tag": "input.input",
                    "source_type": "custom",
                    "validation": "^.+$",
                    "value": "${c1}",
                    "version": "legacy",
                },
            },
        }
        expect = {
            "${c1}": {
                "activities": ["nodec360d91ee7d67988b2a62264fd9f", "node5a259597d556caa0688af3e53833"],
                "conditions": ["linecc134c88c3db75f3a20753c192c6"],
                "constants": ["${c2}", "${c3}"],
            },
            "${c2}": {
                "activities": ["nodec360d91ee7d67988b2a62264fd9f"],
                "conditions": ["linecc134c88c3db75f3a20753c192c6"],
                "constants": [],
            },
            "${c3}": {
                "activities": ["nodec360d91ee7d67988b2a62264fd9f", "node5a259597d556caa0688af3e53833"],
                "conditions": [],
                "constants": ["${c2}"],
            },
            "${c4}": {"activities": ["nodec360d91ee7d67988b2a62264fd9f"], "conditions": [], "constants": []},
        }
        result = analysis_pipeline_constants_ref(tree)
        self.assertEqual(expect, result)
