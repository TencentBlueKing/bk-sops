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

import logging

from django.utils.translation import ugettext_lazy as _

from pipeline.core.data.expression import ConstantTemplate

from pipeline.core.data import var
from pipeline.core.data.context import Context
from pipeline.core.data.converter import get_variable
from pipeline.core.data.library import VariableLibrary
from pipeline_web.parser.format import calculate_constants_type

logger = logging.getLogger("root")


def get_constant_values(constants, extra_data):
    constant_values = {}
    custom_constants = {}
    # 获取用户自定义变量
    for key, info in list(constants.items()):
        if info["source_type"] == "component_inputs":
            constant_values[key] = info["value"]
        elif info["source_type"] == "component_outputs":
            constant_values[key] = key
        elif info["custom_type"] and info.get("is_meta") is True:
            constant_values[key] = str(info["value"])
        else:
            custom_constants[key] = info
    # 获取变量类型
    classified_constants = {}
    to_calculate_constants = {}
    # 先计算lazy的情况
    for key, info in custom_constants.items():
        var_cls = VariableLibrary.get_var_class(info["custom_type"])
        if var_cls and issubclass(var_cls, var.LazyVariable):
            classified_constants[key] = {
                "type": "lazy",
                "source_tag": info["source_tag"],
                "custom_type": info["custom_type"],
                "value": info["value"],
            }
        else:
            to_calculate_constants[key] = info
    classified_constants = calculate_constants_type(
        to_calculate_constants, classified_constants, change_calculated=True
    )

    # 对变量进行第一次解析，放到context中
    context = Context({})
    for key, info in list(classified_constants.items()):
        variable = get_variable(key, info, context, extra_data)
        context.set_global_var(key, variable)
    # 变量值最终获取
    for key, info in list(classified_constants.items()):
        var_value = get_variable(key, info, context, extra_data).get()
        if var_value in ["", "[]", "{}"]:
            var_value = _("预览值为空，需要业务相关信息的变量不支持预览")
        constant_values[key] = str(var_value)
    return constant_values


def analysis_pipeline_constants_ref(pipeline_tree):

    result = {key: {"activities": [], "conditions": [], "constants": []} for key in pipeline_tree.get("constants", {})}

    def ref_counter(key):
        return result.setdefault("${%s}" % key, {"activities": [], "conditions": [], "constants": []})

    for act_id, act in pipeline_tree.get("activities", {}).items():
        if act["type"] == "SubProcess":
            subproc_consts = act.get("constants", {})
            for key, info in subproc_consts.items():
                refs = ConstantTemplate(info["value"]).get_reference()
                for r in refs:
                    ref_counter(r)["activities"].append(act_id)

        elif act["type"] == "ServiceActivity":
            act_data = act.get("component", {}).get("data", {})
            for data_item in act_data.values():
                refs = ConstantTemplate(data_item["value"]).get_reference()
                for r in refs:
                    ref_counter(r)["activities"].append(act_id)

    for gateway in pipeline_tree.get("gateways", {}).values():
        if gateway["type"] not in ["ExclusiveGateway", "ConditionalParallelGateway"]:
            continue

        for condition_id, condition in gateway.get("conditions", {}).items():
            refs = ConstantTemplate(condition["evaluate"]).get_reference()
            for r in refs:
                ref_counter(r)["conditions"].append(condition_id)

    for key, const in pipeline_tree.get("constants", {}).items():
        refs = ConstantTemplate(const.get("value")).get_reference()
        for r in refs:
            ref_counter(r)["constants"].append(key)

    return result
