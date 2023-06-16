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

from gcloud.constants import Type

from .base import MakoTemplateOperation, MakoParam, MakoOperator

OPERATIONS = [
    MakoTemplateOperation(
        name=_("字符串分割后拼接"),
        operators=[MakoOperator(name="caller", type=Type.STRING)],
        params=[MakoParam(name="split_string", type=Type.STRING), MakoParam(name="join_string", type=Type.STRING)],
        template=[_("将 {caller}"), _("以 {split_string} 分割后"), _("以 {join_string} 拼接")],
        mako_template='${"{join_string}".join({caller}.split("{split_string}"))}',
    ),
    MakoTemplateOperation(
        name=_("替换字符串中的字符"),
        operators=[MakoOperator(name="caller", type=Type.STRING)],
        params=[MakoParam(name="old", type=Type.STRING), MakoParam(name="new", type=Type.STRING)],
        template=[_("将 {caller}"), _("中的 {old} 字符串"), _("替换为 {new} 字符串")],
        mako_template='${{caller}.replace("{old}", "{new}")}',
    ),
    MakoTemplateOperation(
        name=_("将首字母变成大写"),
        operators=[MakoOperator(name="caller", type=Type.STRING)],
        params=[],
        template=[_("将 {caller} 的首字母变成大写")],
        mako_template="${{caller}.capitalize()}",
    ),
    MakoTemplateOperation(
        name=_("将字符串变成大写"),
        operators=[MakoOperator(name="caller", type=Type.STRING)],
        params=[],
        template=[_("将 {caller} 变成大写")],
        mako_template="${{caller}.upper()}",
    ),
    MakoTemplateOperation(
        name=_("将字符串变成小写"),
        operators=[MakoOperator(name="caller", type=Type.STRING)],
        params=[],
        template=[_("将 {caller} 变成小写")],
        mako_template="${{caller}.lower()}",
    ),
    MakoTemplateOperation(
        name=_("获取子字符串出现的次数"),
        operators=[MakoOperator(name="caller", type=Type.STRING)],
        params=[MakoParam(name="sub", type=Type.STRING)],
        template=[_("获取 {caller} 中 {sub} 出现的次数")],
        mako_template='${{caller}.count("{sub}")}',
    ),
    MakoTemplateOperation(
        name=_("获取字符串的长度"),
        operators=[MakoOperator(name="caller", type=Type.STRING)],
        params=[],
        template=[_("获取 {caller} 的长度")],
        mako_template="${len({caller})}",
    ),
    MakoTemplateOperation(
        name=_("去除字符串头尾空格"),
        operators=[MakoOperator(name="caller", type=Type.STRING)],
        params=[],
        template=[_("去除 {caller} 头尾空格")],
        mako_template="${{caller}.strip()}",
    ),
    MakoTemplateOperation(
        name=_("去除字符串头部空格"),
        operators=[MakoOperator(name="caller", type=Type.STRING)],
        params=[],
        template=[_("去除 {caller} 头部空格")],
        mako_template="${{caller}.lstrip()}",
    ),
    MakoTemplateOperation(
        name=_("去除字符串尾部空格"),
        operators=[MakoOperator(name="caller", type=Type.STRING)],
        params=[],
        template=[_("去除 {caller} 尾部空格")],
        mako_template="${{caller}.rstrip()}",
    ),
    MakoTemplateOperation(
        name=_("将字符串中单词首字母改为大写"),
        operators=[MakoOperator(name="caller", type=Type.STRING)],
        params=[],
        template=[_("将 {caller} 中单词首字母改为大写")],
        mako_template="${{caller}.title()}",
    ),
    MakoTemplateOperation(
        name=_("返回路径的基本名称"),
        operators=[MakoOperator(name="path", type=Type.STRING)],
        params=[],
        template=[_("返回 {path} 的基本名称")],
        mako_template="${os.path.basename({path})}",
    ),
    MakoTemplateOperation(
        name=_("返回路径的目录名"),
        operators=[MakoOperator(name="path", type=Type.STRING)],
        params=[],
        template=[_("返回 {path} 的目录名")],
        mako_template="${os.path.dirname({path})}",
    ),
]
