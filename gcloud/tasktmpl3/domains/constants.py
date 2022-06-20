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

import logging

from bamboo_engine.context import Context
from bamboo_engine.eri import ContextValue
from bamboo_engine.utils.constants import VAR_CONTEXT_MAPPING
from pipeline.eri.runtime import BambooDjangoRuntime

from pipeline.core.data.expression import ConstantTemplate

from pipeline.core.data import var
from pipeline.core.data.library import VariableLibrary
from pipeline_web.parser.format import format_data_to_pipeline_inputs

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
    classified_constants = format_data_to_pipeline_inputs(
        to_calculate_constants, classified_constants, change_pipeline_inputs=True
    )

    # 沿用V2引擎的变量渲染逻辑
    runtime = BambooDjangoRuntime()
    context_values = [
        ContextValue(key=key, type=VAR_CONTEXT_MAPPING[info["type"]], value=info["value"], code=info.get("custom_type"))
        for key, info in classified_constants.items()
    ]
    context = Context(runtime, context_values, extra_data)
    hydrated_context = context.hydrate(mute_error=True)
    return {**constant_values, **hydrated_context}


def _system_constants_to_mako_str(value):
    """
    将内置系统变量(_system.xxx)转换为可用于mako渲染统计的变量(_system点xxx)
    """
    if isinstance(value, dict):
        for k, v in value.items():
            value[k] = _system_constants_to_mako_str(v)

    if isinstance(value, list):
        for i, v in enumerate(value):
            value[i] = _system_constants_to_mako_str(v)

    if isinstance(value, str):
        return value.replace("_system.", "_system点") if "_system." in value else value

    return value


def _mako_str_to_system_constants(value):
    """
    将用于mako渲染统计的变量(_system点xxx)还原为内置系统变量(_system.xxx)
    """
    if isinstance(value, str):
        return value.replace("_system点", "_system.") if "_system点" in value else value

    return value


def analysis_pipeline_constants_ref(pipeline_tree):
    result = {key: {"activities": [], "conditions": [], "constants": []} for key in pipeline_tree.get("constants", {})}

    def ref_counter(key):
        return result.setdefault("${%s}" % key, {"activities": [], "conditions": [], "constants": []})

    for act_id, act in pipeline_tree.get("activities", {}).items():
        if act["type"] == "SubProcess":
            subproc_consts = act.get("constants", {})
            for key, info in subproc_consts.items():
                value = _system_constants_to_mako_str(info["value"])
                refs = ConstantTemplate(value).get_reference()
                for r in refs:
                    r = _mako_str_to_system_constants(r)
                    ref_counter(r)["activities"].append(act_id)

        elif act["type"] == "ServiceActivity":
            act_data = act.get("component", {}).get("data", {})
            for data_item in act_data.values():
                value = _system_constants_to_mako_str(data_item["value"])
                refs = ConstantTemplate(value).get_reference()
                for r in refs:
                    r = _mako_str_to_system_constants(r)
                    ref_counter(r)["activities"].append(act_id)

    for gateway in pipeline_tree.get("gateways", {}).values():
        if gateway["type"] not in ["ExclusiveGateway", "ConditionalParallelGateway"]:
            continue

        for condition_id, condition in gateway.get("conditions", {}).items():
            value = _system_constants_to_mako_str(condition["evaluate"])
            refs = ConstantTemplate(value).get_reference()
            for r in refs:
                r = _mako_str_to_system_constants(r)
                ref_counter(r)["conditions"].append(condition_id)

    for key, const in pipeline_tree.get("constants", {}).items():
        value = _system_constants_to_mako_str(const.get("value"))
        refs = ConstantTemplate(value).get_reference()
        for r in refs:
            r = _mako_str_to_system_constants(r)
            ref_counter(r)["constants"].append(key)

    return result
