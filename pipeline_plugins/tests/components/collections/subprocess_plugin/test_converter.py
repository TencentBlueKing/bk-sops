# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json
from unittest.mock import MagicMock, patch

from django.test import TestCase

from gcloud.template_base.utils import inject_original_template_info
from pipeline_plugins.components.collections.subprocess_plugin.converter import (
    PipelineTreeSubprocessConverter,
)


class SubprocessPluginConverterTest(TestCase):
    SUBPROCESS_DATA = json.loads(
        """
    {
        "activities": {
            "n378d83bb3143087a0f9b85e836ad272": {
                "error_ignorable": false,
                "loop": null,
                "optional": true,
                "retryable": true,
                "isSkipped": true,
                "stage_name": "",
                "hooked_constants": [],
                "outgoing": "l6dc4991c19238dca668a325a34fd61a",
                "id": "n378d83bb3143087a0f9b85e836ad272",
                "type": "SubProcess",
                "name": "公共子流程",
                "template_id": "nc4aca9636503df1ae06cd32ec2a569f",
                "incoming": [
                    "l696528e3ac23ec19d555e84802e28df"
                ],
                "version": "82356c91cb1684a7c75bf86f0da5fe32",
                "pipeline": {
                    "activities": {
                        "nc2922e6a1403b558c057568c10a9043": {
                            "error_ignorable": false,
                            "loop": null,
                            "optional": true,
                            "retryable": true,
                            "skippable": true,
                            "stage_name": "",
                            "outgoing": "ld39800d68b2388b855d130e6bd89a7c",
                            "id": "nc2922e6a1403b558c057568c10a9043",
                            "type": "ServiceActivity",
                            "name": "定时",
                            "component": {
                                "code": "sleep_timer",
                                "data": {
                                    "bk_timing": {
                                        "value": "3",
                                        "hook": false
                                    },
                                    "force_check": {
                                        "value": true,
                                        "hook": false
                                    }
                                },
                                "version": "legacy"
                            },
                            "incoming": [
                                "ld872424403c3c50821324d084c71e54"
                            ],
                            "labels": []
                        }
                    },
                    "constants": {},
                    "end_event": {
                        "id": "n62d9f871f9536fe86c0547f61446725",
                        "incoming": [
                            "ld39800d68b2388b855d130e6bd89a7c"
                        ],
                        "name": "",
                        "outgoing": "",
                        "type": "EmptyEndEvent",
                        "labels": []
                    },
                    "flows": {
                        "ld39800d68b2388b855d130e6bd89a7c": {
                            "id": "ld39800d68b2388b855d130e6bd89a7c",
                            "is_default": false,
                            "source": "nc2922e6a1403b558c057568c10a9043",
                            "target": "n62d9f871f9536fe86c0547f61446725"
                        },
                        "ld872424403c3c50821324d084c71e54": {
                            "id": "ld872424403c3c50821324d084c71e54",
                            "is_default": false,
                            "source": "n4a9ee799589392ab34d719197d76b61",
                            "target": "nc2922e6a1403b558c057568c10a9043"
                        }
                    },
                    "gateways": {},
                    "line": [
                        {
                            "id": "ld39800d68b2388b855d130e6bd89a7c",
                            "source": {
                                "arrow": "Right",
                                "id": "nc2922e6a1403b558c057568c10a9043"
                            },
                            "target": {
                                "arrow": "Left",
                                "id": "n62d9f871f9536fe86c0547f61446725"
                            }
                        },
                        {
                            "id": "ld872424403c3c50821324d084c71e54",
                            "source": {
                                "arrow": "Right",
                                "id": "n4a9ee799589392ab34d719197d76b61"
                            },
                            "target": {
                                "arrow": "Left",
                                "id": "nc2922e6a1403b558c057568c10a9043"
                            }
                        }
                    ],
                    "location": [
                        {
                            "id": "n4a9ee799589392ab34d719197d76b61",
                            "type": "startpoint",
                            "name": "",
                            "status": "",
                            "x": 60,
                            "y": 105
                        },
                        {
                            "id": "nc2922e6a1403b558c057568c10a9043",
                            "type": "tasknode",
                            "name": "定时",
                            "status": "",
                            "x": 148,
                            "y": 100
                        },
                        {
                            "id": "n62d9f871f9536fe86c0547f61446725",
                            "type": "endpoint",
                            "name": "",
                            "status": "",
                            "x": 343,
                            "y": 105
                        }
                    ],
                    "outputs": [],
                    "start_event": {
                        "id": "n4a9ee799589392ab34d719197d76b61",
                        "incoming": "",
                        "name": "",
                        "outgoing": "ld872424403c3c50821324d084c71e54",
                        "type": "EmptyStartEvent",
                        "labels": []
                    },
                    "id": "n378d83bb3143087a0f9b85e836ad272"
                },
                "labels": []
            }
        },
        "constants": {},
        "end_event": {
            "id": "n8ab69a4132e34ff96e9ad4118000a7e",
            "incoming": [
                "l6dc4991c19238dca668a325a34fd61a"
            ],
            "name": "",
            "outgoing": "",
            "type": "EmptyEndEvent",
            "labels": []
        },
        "flows": {
            "l6dc4991c19238dca668a325a34fd61a": {
                "id": "l6dc4991c19238dca668a325a34fd61a",
                "is_default": false,
                "source": "n378d83bb3143087a0f9b85e836ad272",
                "target": "n8ab69a4132e34ff96e9ad4118000a7e"
            },
            "l696528e3ac23ec19d555e84802e28df": {
                "id": "l696528e3ac23ec19d555e84802e28df",
                "is_default": false,
                "source": "nd25a4981c1e3fe39ab17b9e81ea2259",
                "target": "n378d83bb3143087a0f9b85e836ad272"
            }
        },
        "gateways": {},
        "line": [
            {
                "id": "l6dc4991c19238dca668a325a34fd61a",
                "source": {
                    "arrow": "Right",
                    "id": "n378d83bb3143087a0f9b85e836ad272"
                },
                "target": {
                    "arrow": "Left",
                    "id": "n8ab69a4132e34ff96e9ad4118000a7e"
                }
            },
            {
                "id": "l696528e3ac23ec19d555e84802e28df",
                "source": {
                    "arrow": "Right",
                    "id": "nd25a4981c1e3fe39ab17b9e81ea2259"
                },
                "target": {
                    "arrow": "Left",
                    "id": "n378d83bb3143087a0f9b85e836ad272"
                }
            }
        ],
        "location": [
            {
                "id": "nd25a4981c1e3fe39ab17b9e81ea2259",
                "type": "startpoint",
                "name": "",
                "status": "",
                "x": 60,
                "y": 105
            },
            {
                "id": "n378d83bb3143087a0f9b85e836ad272",
                "type": "subflow",
                "name": "公共子流程",
                "status": "",
                "x": 148,
                "y": 100
            },
            {
                "id": "n8ab69a4132e34ff96e9ad4118000a7e",
                "type": "endpoint",
                "name": "",
                "status": "",
                "x": 343,
                "y": 105
            }
        ],
        "outputs": [],
        "start_event": {
            "id": "nd25a4981c1e3fe39ab17b9e81ea2259",
            "incoming": "",
            "name": "",
            "outgoing": "l696528e3ac23ec19d555e84802e28df",
            "type": "EmptyStartEvent",
            "labels": []
        },
        "id": "n4002b26081e34c585ec86ef1deb3e72"
    }
    """
    )

    CONVERTED_DATA = json.loads(
        """
    {
        "activities": {
            "n378d83bb3143087a0f9b85e836ad272": {
                "error_ignorable": false,
                "auto_retry": {
                    "enabled": false,
                    "interval": 0,
                    "times": 1
                },
                "timeout_config": {
                    "enabled": false,
                    "seconds": 10,
                    "action": "forced_fail"
                },
                "skippable": true,
                "retryable": true,
                "type": "ServiceActivity",
                "component": {
                    "code": "subprocess_plugin",
                    "data": {
                        "subprocess": {
                            "hook": false,
                            "need_render": false,
                            "value": {
                                "template_id": "nc4aca9636503df1ae06cd32ec2a569f",
                                "pipeline": {
                                    "activities": {
                                        "nc2922e6a1403b558c057568c10a9043": {
                                            "error_ignorable": false,
                                            "loop": null,
                                            "optional": true,
                                            "retryable": true,
                                            "skippable": true,
                                            "stage_name": "",
                                            "outgoing": "ld39800d68b2388b855d130e6bd89a7c",
                                            "id": "nc2922e6a1403b558c057568c10a9043",
                                            "type": "ServiceActivity",
                                            "name": "定时",
                                            "component": {
                                                "code": "sleep_timer",
                                                "data": {
                                                    "bk_timing": {
                                                        "value": "3",
                                                        "hook": false
                                                    },
                                                    "force_check": {
                                                        "value": true,
                                                        "hook": false
                                                    }
                                                },
                                                "version": "legacy"
                                            },
                                            "incoming": [
                                                "ld872424403c3c50821324d084c71e54"
                                            ],
                                            "labels": []
                                        }
                                    },
                                    "constants": {},
                                    "end_event": {
                                        "id": "n62d9f871f9536fe86c0547f61446725",
                                        "incoming": [
                                            "ld39800d68b2388b855d130e6bd89a7c"
                                        ],
                                        "name": "",
                                        "outgoing": "",
                                        "type": "EmptyEndEvent",
                                        "labels": []
                                    },
                                    "flows": {
                                        "ld39800d68b2388b855d130e6bd89a7c": {
                                            "id": "ld39800d68b2388b855d130e6bd89a7c",
                                            "is_default": false,
                                            "source": "nc2922e6a1403b558c057568c10a9043",
                                            "target": "n62d9f871f9536fe86c0547f61446725"
                                        },
                                        "ld872424403c3c50821324d084c71e54": {
                                            "id": "ld872424403c3c50821324d084c71e54",
                                            "is_default": false,
                                            "source": "n4a9ee799589392ab34d719197d76b61",
                                            "target": "nc2922e6a1403b558c057568c10a9043"
                                        }
                                    },
                                    "gateways": {},
                                    "line": [
                                        {
                                            "id": "ld39800d68b2388b855d130e6bd89a7c",
                                            "source": {
                                                "arrow": "Right",
                                                "id": "nc2922e6a1403b558c057568c10a9043"
                                            },
                                            "target": {
                                                "arrow": "Left",
                                                "id": "n62d9f871f9536fe86c0547f61446725"
                                            }
                                        },
                                        {
                                            "id": "ld872424403c3c50821324d084c71e54",
                                            "source": {
                                                "arrow": "Right",
                                                "id": "n4a9ee799589392ab34d719197d76b61"
                                            },
                                            "target": {
                                                "arrow": "Left",
                                                "id": "nc2922e6a1403b558c057568c10a9043"
                                            }
                                        }
                                    ],
                                    "location": [
                                        {
                                            "id": "n4a9ee799589392ab34d719197d76b61",
                                            "type": "startpoint",
                                            "name": "",
                                            "status": "",
                                            "x": 60,
                                            "y": 105
                                        },
                                        {
                                            "id": "nc2922e6a1403b558c057568c10a9043",
                                            "type": "tasknode",
                                            "name": "定时",
                                            "status": "",
                                            "x": 148,
                                            "y": 100
                                        },
                                        {
                                            "id": "n62d9f871f9536fe86c0547f61446725",
                                            "type": "endpoint",
                                            "name": "",
                                            "status": "",
                                            "x": 343,
                                            "y": 105
                                        }
                                    ],
                                    "outputs": [],
                                    "start_event": {
                                        "id": "n4a9ee799589392ab34d719197d76b61",
                                        "incoming": "",
                                        "name": "",
                                        "outgoing": "ld872424403c3c50821324d084c71e54",
                                        "type": "EmptyStartEvent",
                                        "labels": []
                                    },
                                    "id": "n378d83bb3143087a0f9b85e836ad272"
                                },
                                "subprocess_name": "公共子流程",
                                "template_source": "project"
                            }
                        }
                    },
                    "version": "1.0.0"
                },
                "optional": true,
                "stage_name": "",
                "outgoing": "l6dc4991c19238dca668a325a34fd61a",
                "id": "n378d83bb3143087a0f9b85e836ad272",
                "name": "公共子流程",
                "original_template_id": "123",
                "original_template_version": "tmpl_version",
                "incoming": [
                    "l696528e3ac23ec19d555e84802e28df"
                ],
                "labels": []
            }
        },
        "constants": {},
        "end_event": {
            "id": "n8ab69a4132e34ff96e9ad4118000a7e",
            "incoming": [
                "l6dc4991c19238dca668a325a34fd61a"
            ],
            "name": "",
            "outgoing": "",
            "type": "EmptyEndEvent",
            "labels": []
        },
        "flows": {
            "l6dc4991c19238dca668a325a34fd61a": {
                "id": "l6dc4991c19238dca668a325a34fd61a",
                "is_default": false,
                "source": "n378d83bb3143087a0f9b85e836ad272",
                "target": "n8ab69a4132e34ff96e9ad4118000a7e"
            },
            "l696528e3ac23ec19d555e84802e28df": {
                "id": "l696528e3ac23ec19d555e84802e28df",
                "is_default": false,
                "source": "nd25a4981c1e3fe39ab17b9e81ea2259",
                "target": "n378d83bb3143087a0f9b85e836ad272"
            }
        },
        "gateways": {},
        "line": [
            {
                "id": "l6dc4991c19238dca668a325a34fd61a",
                "source": {
                    "arrow": "Right",
                    "id": "n378d83bb3143087a0f9b85e836ad272"
                },
                "target": {
                    "arrow": "Left",
                    "id": "n8ab69a4132e34ff96e9ad4118000a7e"
                }
            },
            {
                "id": "l696528e3ac23ec19d555e84802e28df",
                "source": {
                    "arrow": "Right",
                    "id": "nd25a4981c1e3fe39ab17b9e81ea2259"
                },
                "target": {
                    "arrow": "Left",
                    "id": "n378d83bb3143087a0f9b85e836ad272"
                }
            }
        ],
        "location": [
            {
                "id": "nd25a4981c1e3fe39ab17b9e81ea2259",
                "type": "startpoint",
                "name": "",
                "status": "",
                "x": 60,
                "y": 105
            },
            {
                "id": "n378d83bb3143087a0f9b85e836ad272",
                "type": "tasknode",
                "name": "公共子流程",
                "status": "",
                "x": 148,
                "y": 100
            },
            {
                "id": "n8ab69a4132e34ff96e9ad4118000a7e",
                "type": "endpoint",
                "name": "",
                "status": "",
                "x": 343,
                "y": 105
            }
        ],
        "outputs": [],
        "start_event": {
            "id": "nd25a4981c1e3fe39ab17b9e81ea2259",
            "incoming": "",
            "name": "",
            "outgoing": "l696528e3ac23ec19d555e84802e28df",
            "type": "EmptyStartEvent",
            "labels": []
        },
        "id": "n4002b26081e34c585ec86ef1deb3e72"
    }
    """
    )

    def test_convert(self):
        tmpl_mocker = MagicMock()
        tmpl_mocker.id = "123"
        tmpl_mocker.version = "tmpl_version"
        cls_mocker = MagicMock()
        cls_mocker.objects = MagicMock()
        qs_mocker = MagicMock()
        qs_mocker.first = MagicMock(return_value=tmpl_mocker)
        cls_mocker.objects.filter = MagicMock(return_value=qs_mocker)

        get_model = MagicMock(return_value=cls_mocker)

        subprocess_data = self.SUBPROCESS_DATA
        with patch("gcloud.template_base.utils.apps.get_model", get_model):
            with patch("gcloud.template_base.utils.isinstance", MagicMock(return_value=False)):
                converter = PipelineTreeSubprocessConverter(subprocess_data)
                inject_original_template_info(subprocess_data)
                converter.convert()
                self.assertEqual(self.CONVERTED_DATA, subprocess_data)
