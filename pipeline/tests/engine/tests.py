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
from pipeline.utils.uniqid import uniqid


def main_test():
    pipe1 = {
        "id": uniqid(),
        "activities": {
            "d4b43834dbea0981f07db76d3c2d12ce": {
                "outgoing": "65085d5739b76b8c3c0152ca1e845a6f",
                "incoming": "30722fa74d29e61ce9289c5029a48a49",
                "name": "\u8282\u70b9_1",
                "error_ignorable": False,
                "component": {
                    "code": "job_fast_execute_script",
                    "data": {
                        "job_account": {
                            "hook": False,
                            "value": "root"
                        },
                        "job_script_timeout": {
                            "hook": False,
                            "value": "600"
                        },
                        "job_ip_list": {
                            "hook": False,
                            "value": "${ip}"
                        },
                        "job_content": {
                            "hook": False,
                            "value": "echo 1"
                        },
                        "job_script_type": {
                            "hook": False,
                            "value": "1"
                        },
                        "job_script_param": {
                            "hook": False,
                            "value": ""
                        }
                    }
                },
                "optional": False,
                "type": "ServiceActivity",
                "id": "d4b43834dbea0981f07db76d3c2d12ce",
                "loop": None
            }
        },
        "end_event": {
            "type": "EmptyEndEvent",
            "outgoing": "",
            "incoming": "65085d5739b76b8c3c0152ca1e845a6f",
            "id": "ad3d6364cbf1f3ff4b0a9d0c98a99d99",
            "name": ""
        },
        "outputs": [],
        "flows": {
            "65085d5739b76b8c3c0152ca1e845a6f": {
                "is_default": False,
                "source": "d4b43834dbea0981f07db76d3c2d12ce",
                "id": "65085d5739b76b8c3c0152ca1e845a6f",
                "target": "ad3d6364cbf1f3ff4b0a9d0c98a99d99"
            },
            "30722fa74d29e61ce9289c5029a48a49": {
                "is_default": False,
                "source": "3e8f33f335b6695201cc259fb5f365e0",
                "id": "30722fa74d29e61ce9289c5029a48a49",
                "target": "d4b43834dbea0981f07db76d3c2d12ce"
            }
        },
        "start_event": {
            "type": "EmptyStartEvent",
            "outgoing": "30722fa74d29e61ce9289c5029a48a49",
            "incoming": "",
            "id": "3e8f33f335b6695201cc259fb5f365e0",
            "name": ""
        },
        "constants": {
            "${ip}": {
                "source_tag": "var_ip_picker",
                "source_info": {},
                "name": "ip",
                "index": 0,
                "custom_type": "ip",
                "value": {
                    "var_ip_picker": {
                        "var_ip_custom_value": "",
                        "var_ip_select_module": ["111"],
                        "var_ip_input_set": "",
                        "var_ip_value_type": "ip",
                        "var_ip_select_set": ["2"],
                        "var_ip_input_module": "",
                        "var_ip_method": "select"
                    }
                },
                "show_type": "hide",
                "source_type": "custom",
                "key": "${ip}",
                "desc": ""
            }
        },
        "gateways": {}
    }
    parser_obj = WebPipelineAdapter(pipe1)
    run_pipeline(parser_obj.parser())
