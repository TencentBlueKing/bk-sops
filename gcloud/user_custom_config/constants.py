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
from django.utils.translation import ugettext_lazy as _

TASKTMPL_ORDERBY_OPTIONS = [
    {"name": _("模板ID"), "value": "id"},
    {"name": _("创建时间"), "value": "pipeline_template__create_time"},
    {"name": _("更新时间"), "value": "pipeline_template__edit_time"},
    {"name": _("模板类型"), "value": "category"},
]

UserConfOption = {
    "task_template_ordering": TASKTMPL_ORDERBY_OPTIONS,
}

DEFAULT_PIPELINE_TREE = {
    "activities": {
        "node233c44ed19f816e75f47fa28ee9e": {
            "component": {
                "code": "bk_display",
                "data": {"bk_display_message": {"hook": False, "need_render": True, "value": ""}},
                "version": "1.0",
            },
            "error_ignorable": False,
            "id": "node233c44ed19f816e75f47fa28ee9e",
            "incoming": ["line93675a1e1fe437772fe3a9b71812"],
            "loop": None,
            "name": "消息展示",
            "optional": True,
            "outgoing": "line8d2551a42247463bfb31bc02f80c",
            "stage_name": "",
            "type": "ServiceActivity",
            "retryable": True,
            "skippable": True,
            "auto_retry": {"enable": False, "interval": 0, "times": 1},
            "timeout_config": {"enable": False, "seconds": 10, "action": "forced_fail"},
            "labels": [],
        }
    },
    "constants": {},
    "end_event": {
        "id": "noded8e797885448a9917a7ede435020",
        "incoming": ["line8d2551a42247463bfb31bc02f80c"],
        "name": "",
        "outgoing": "",
        "type": "EmptyEndEvent",
    },
    "flows": {
        "line93675a1e1fe437772fe3a9b71812": {
            "id": "line93675a1e1fe437772fe3a9b71812",
            "is_default": False,
            "source": "noded9effddb1a805561b925afdfc755",
            "target": "node233c44ed19f816e75f47fa28ee9e",
        },
        "line8d2551a42247463bfb31bc02f80c": {
            "id": "line8d2551a42247463bfb31bc02f80c",
            "is_default": False,
            "source": "node233c44ed19f816e75f47fa28ee9e",
            "target": "noded8e797885448a9917a7ede435020",
        },
    },
    "gateways": {},
    "line": [
        {
            "id": "line93675a1e1fe437772fe3a9b71812",
            "source": {"arrow": "Right", "id": "noded9effddb1a805561b925afdfc755"},
            "target": {"arrow": "Left", "id": "node233c44ed19f816e75f47fa28ee9e"},
        },
        {
            "id": "line8d2551a42247463bfb31bc02f80c",
            "source": {"arrow": "Right", "id": "node233c44ed19f816e75f47fa28ee9e"},
            "target": {"arrow": "Left", "id": "noded8e797885448a9917a7ede435020"},
        },
    ],
    "location": [
        {"id": "noded9effddb1a805561b925afdfc755", "type": "startpoint", "x": 40, "y": 150},
        {
            "id": "node233c44ed19f816e75f47fa28ee9e",
            "type": "tasknode",
            "name": "消息展示",
            "stage_name": "",
            "x": 240,
            "y": 140,
            "group": "蓝鲸服务(BK)",
            "icon": "",
        },
        {"id": "noded8e797885448a9917a7ede435020", "type": "endpoint", "x": 540, "y": 150},
    ],
    "outputs": [],
    "start_event": {
        "id": "noded9effddb1a805561b925afdfc755",
        "incoming": "",
        "name": "",
        "outgoing": "line93675a1e1fe437772fe3a9b71812",
        "type": "EmptyStartEvent",
    },
}


def get_options_by_fileds(configs=None):
    data = {}
    if not configs:
        return UserConfOption
    for key in configs:
        data[key] = UserConfOption[key]
    return data
