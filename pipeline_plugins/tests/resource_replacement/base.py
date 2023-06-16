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
import typing

from pipeline_plugins.resource_replacement import base

FIRST_ACT_ID: str = "nodec5d2a1ba8df259c8dd4deeb0fc66"

PIPELINE_TREE_MOCK_DATA: typing.Dict[str, typing.Any] = {
    "name": "new20230418143711",
    "activities": {
        FIRST_ACT_ID: {
            "id": FIRST_ACT_ID,
            "incoming": ["line44cf9510e757d159328d64819435"],
            "name": "测试原子",
            "outgoing": "line7824dc9c613f9f4b82ae20f76e33",
            "type": "ServiceActivity",
        }
    },
    "end_event": {
        "id": "nodecf1085a27fe0fbf3020aca8ddc6f",
        "incoming": ["line7824dc9c613f9f4b82ae20f76e33"],
        "name": "",
        "outgoing": "",
        "type": "EmptyEndEvent",
    },
    "flows": {
        "line44cf9510e757d159328d64819435": {
            "id": "line44cf9510e757d159328d64819435",
            "is_default": False,
            "source": "node332f956ed5069aa5b316ea1a27e8",
            "target": FIRST_ACT_ID,
        },
        "line7824dc9c613f9f4b82ae20f76e33": {
            "id": "line7824dc9c613f9f4b82ae20f76e33",
            "is_default": False,
            "source": FIRST_ACT_ID,
            "target": "nodecf1085a27fe0fbf3020aca8ddc6f",
        },
    },
    "gateways": {},
    "line": [
        {
            "id": "line44cf9510e757d159328d64819435",
            "source": {"arrow": "Right", "id": "node332f956ed5069aa5b316ea1a27e8"},
            "target": {"arrow": "Left", "id": FIRST_ACT_ID},
        },
        {
            "id": "line7824dc9c613f9f4b82ae20f76e33",
            "source": {"arrow": "Right", "id": FIRST_ACT_ID},
            "target": {"arrow": "Left", "id": "nodecf1085a27fe0fbf3020aca8ddc6f"},
        },
    ],
    "outputs": [],
    "start_event": {
        "id": "node332f956ed5069aa5b316ea1a27e8",
        "incoming": "",
        "name": "",
        "outgoing": "line44cf9510e757d159328d64819435",
        "type": "EmptyStartEvent",
    },
    "template_id": "",
    "constants": {},
    "default_flow_type": "common",
}

OLD_BIZ_ID__NEW_BIZ_INFO_MAP = {
    2: {
        "bk_old_biz_name": "测试业务",
        "bk_old_biz_id": 2,
        "bk_new_biz_name": "测试业务_new",
        "bk_new_biz_id": 1002,
        "bk_env": "o",
    }
}


class DBMockHelper(base.DBHelper):
    def fetch_resource_id_map(
        self, resource_type: str, source_data: typing.List[typing.Union[int, str]], source_data_type: type
    ) -> typing.Dict[typing.Union[int, str], typing.Union[int, str]]:
        """
        获取资源新老关系映射
        :param resource_type:
        :param source_data:
        :param source_data_type:
        :return:
        """
        if source_data_type == str:
            return {source_id: f"{source_id}_new" for source_id in source_data}
        else:
            return {int(source_id): int(source_id) + 100000 for source_id in source_data}
