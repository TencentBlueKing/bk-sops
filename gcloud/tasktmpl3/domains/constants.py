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
import copy
import logging
import re
from typing import List

from bamboo_engine.context import Context
from bamboo_engine.eri import ContextValue, NodeType
from bamboo_engine.template import Template
from bamboo_engine.utils.constants import VAR_CONTEXT_MAPPING
from pipeline.component_framework.constant import ConstantPool
from pipeline.core.data import var
from pipeline.core.data.expression import ConstantTemplate
from pipeline.core.data.library import VariableLibrary
from pipeline.eri.runtime import BambooDjangoRuntime

from pipeline_web.parser.format import format_data_to_pipeline_inputs

var_pattern = re.compile(r"\${(\w+)}")

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


def get_references(constants: dict, inputs: dict) -> set:
    """
    获取某个变量在上下文中引用的其他变量
    @param constants: {"${ip_lisr}: {}"}
    @param inputs: {"${ip_lisr}": {"value": xxx}}
    @return: ["${ip_lisr}"]
    """
    referenced_keys = []
    while True:
        last_count = len(referenced_keys)
        cons_pool = ConstantPool(inputs, lazy=True)
        refs = cons_pool.get_reference_info(strict=False)

        for keys in list(refs.values()):
            for key in keys:
                # add outputs keys later
                if key in constants and key not in referenced_keys:
                    referenced_keys.append(key)
                    inputs.update({key: constants[key]})
        if len(referenced_keys) == last_count:
            break

    return set(referenced_keys)


def preview_node_inputs(
    runtime: BambooDjangoRuntime,
    pipeline: dict,
    node_id: str,
    subprocess_stack: List[str] = [],
    root_pipeline_data: dict = {},
    parent_params: dict = {},
    subprocess_simple_inputs: bool = False,
):
    def get_need_render_context_keys():
        # 如果遇到子流程，到最后一层才会实际去解析需要渲染的变量
        node_info = pipeline["activities"][node_id]
        node_inputs = copy.deepcopy(node_info.get("component", {}).get("inputs", {}))
        pipeline_inputs = copy.deepcopy(pipeline["data"].get("inputs", {}))
        pipeline_inputs.update(parent_params)
        keys = get_references(pipeline_inputs, node_inputs)
        return keys

    # 对于子流程内的节点，拿不到当前node_id的type和code
    node_type = pipeline["activities"].get(node_id, {}).get("type")
    node_code = pipeline["activities"].get(node_id, {}).get("component", {}).get("code")
    # 只优化普通节点的渲染过程
    if node_type == NodeType.ServiceActivity.value and node_code != "subprocess_plugin":
        need_render_context_keys = get_need_render_context_keys()
    else:
        need_render_context_keys = list(pipeline["data"].get("inputs", {}).keys()) + list(parent_params.keys())
    no_need_render_keys = {
        "${%s}" % key
        for key, val in pipeline["activities"].get(node_id, {}).get("component", {}).get("inputs", {}).items()
        if not val.get("need_render")
    }
    need_render_context_keys = need_render_context_keys.difference(no_need_render_keys)
    context_values = [
        ContextValue(key=key, type=VAR_CONTEXT_MAPPING[info["type"]], value=info["value"], code=info.get("custom_type"))
        for key, info in list(pipeline["data"].get("inputs", {}).items()) + list(parent_params.items())
        if key in need_render_context_keys
    ]

    context = Context(runtime, context_values, root_pipeline_data)

    if subprocess_stack:
        # 如果子流程依赖了父流程的变量，那么需要把父流程的变量传递到下一层子流程中
        subprocess = subprocess_stack[0]
        child_pipeline = pipeline["activities"][subprocess]["pipeline"]
        parent_hydrated_context = context.hydrate(deformat=True)
        # 子流程需要有选择的渲染父流程的变量
        param_data = {key: info["value"] for key, info in pipeline["activities"][subprocess]["params"].items()}
        # 获取子流程的参数
        hydrated_param_data = Template(param_data).render(parent_hydrated_context)
        formatted_param_data = {key: {"value": value, "type": "plain"} for key, value in hydrated_param_data.items()}

        return preview_node_inputs(
            runtime=runtime,
            pipeline=child_pipeline,
            node_id=node_id,
            subprocess_stack=subprocess_stack[1:],
            root_pipeline_data=root_pipeline_data,
            parent_params=formatted_param_data,
            subprocess_simple_inputs=subprocess_simple_inputs,
        )

    if node_type == NodeType.ServiceActivity.value:
        # 如果是独立子流程
        if node_code == "subprocess_plugin" and subprocess_simple_inputs:
            raw_inputs = pipeline["activities"][node_id]["component"]["inputs"]["subprocess"]["value"]["pipeline"][
                "constants"
            ]
        else:
            raw_inputs = pipeline["activities"][node_id]["component"]["inputs"]
    elif node_type == NodeType.SubProcess.value:
        raw_inputs = pipeline["activities"][node_id]["params"]
    else:
        raise Exception(f"can not preview inputs for node type: {node_type}")
    raw_inputs = {key: info["value"] for key, info in raw_inputs.items()}
    hydrated_context = context.hydrate(deformat=True)
    inputs = Template(raw_inputs).render(hydrated_context)
    return inputs


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
