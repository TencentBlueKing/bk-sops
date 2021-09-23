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

from django.utils.translation import ugettext_lazy as _


def format_component_name(components: list, components_list: list):
    """
    @summary: 插件名格式化
    @param: components: component对象列表
    @param: components_list: 插件数据列表
    return groups
    """
    groups = []
    for comp in components:
        version = comp["version"]
        # 插件名国际化
        name = comp["name"].split("-")
        name = "{}-{}-{}".format(_(name[0]), _(name[1]), version)
        code = "{}-{}".format(comp["code"], comp["version"])
        value = 0
        for oth_com_tmp in components_list:
            if comp["code"] == oth_com_tmp["component_code"] and comp["version"] == oth_com_tmp["version"]:
                value += oth_com_tmp["value"]
        groups.append({"code": code, "name": name, "value": value})
    return groups
