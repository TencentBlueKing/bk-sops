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

from gcloud.constants import Type

from .base import MakoTemplateOperation, MakoParam, MakoOperator

OPERATIONS = [
    MakoTemplateOperation(
        name="字符串分割后拼接",
        operators=[MakoOperator(name="caller", type=Type.STRING)],
        params=[MakoParam(name="split_string", type=Type.STRING), MakoParam(name="join_string", type=Type.STRING)],
        template=["将 {caller}", "以 {split_string} 分割后", "以 {join_string} 拼接"],
        mako_template='${"{join_string}".join({caller}.split("{split_string}"))}',
    ),
    MakoTemplateOperation(
        name="替换字符串中的字符",
        operators=[MakoOperator(name="caller", type=Type.STRING)],
        params=[MakoParam(name="old", type=Type.STRING), MakoParam(name="new", type=Type.STRING)],
        template=["将 {caller}", "中的 {old} 字符串", "替换为 {new} 字符串"],
        mako_template='${caller}.replace("{old}", "{new}")}',
    ),
]
