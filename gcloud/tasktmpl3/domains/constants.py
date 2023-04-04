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

from bamboo_engine.context import Context
from bamboo_engine.eri import ContextValue
from bamboo_engine.utils.boolrule import BoolRule
from bamboo_engine.utils.constants import VAR_CONTEXT_MAPPING
from pipeline.core.constants import PE
from pipeline.eri.runtime import BambooDjangoRuntime

from pipeline.core.data.expression import ConstantTemplate

from pipeline.core.data import var
from pipeline.core.data.library import VariableLibrary

from pipeline_web.graph import get_graph_from_pipeline_tree, get_ordered_necessary_nodes_and_paths_between_nodes
from pipeline_web.parser.format import format_data_to_pipeline_inputs
from pipeline_web.preview_base import PipelineTemplateWebPreviewer

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


def extract_unused_nodes_via_hydrated_constants(pipeline_tree: dict, hydrated_constants: dict) -> set:
    """
    @summary: 通过渲染后的变量，提取出未使用的节点
    @param pipeline_tree: 流程树
    @param hydrated_constants: 渲染后的常量
    @return: 未使用的节点列表
    """
    graph = get_graph_from_pipeline_tree(pipeline_tree)
    ordered_necessary_nodes, _ = get_ordered_necessary_nodes_and_paths_between_nodes(
        graph, pipeline_tree["start_event"]["id"], pipeline_tree["end_event"]["id"]
    )
    used_nodes = set(ordered_necessary_nodes)
    logger.info("[extract_unused_nodes_via_hydrated_constants] initial used_nodes: {}".format(used_nodes))

    gateways = pipeline_tree[PE.gateways]
    gateway_ids = set(gateways.keys())
    match_gateway_types = [PE.ExclusiveGateway, PE.ConditionalParallelGateway]
    runtime = BambooDjangoRuntime()
    hydrated_context = [
        ContextValue(key=key, type=VAR_CONTEXT_MAPPING["plain"], value=value)
        for key, value in hydrated_constants.items()
    ]

    def match_branch_nodes(candidate_nodes):
        """获取分支中匹配的节点"""
        for node_id, next_node_id in zip(candidate_nodes, candidate_nodes[1:]):
            if node_id in gateway_ids and gateways[node_id][PE.type] in match_gateway_types:
                context_values = [
                    ContextValue(key=flow_id, type=VAR_CONTEXT_MAPPING["splice"], value=condition[PE.evaluate])
                    for flow_id, condition in gateways[node_id][PE.conditions].items()
                ] + hydrated_context
                context = Context(runtime, context_values, {})
                hydrated_conditions = context.hydrate(mute_error=True)
                expressions = [
                    (flow_id, hydrated_conditions[flow_id]) for flow_id in gateways[node_id][PE.conditions].keys()
                ]
                expressions = list(filter(lambda exp: BoolRule(exp[1]).test(context=hydrated_constants), expressions))
                branch_start_node_ids = [pipeline_tree[PE.flows][exp[0]]["target"] for exp in expressions]
                for branch_start_node_id in branch_start_node_ids:
                    branch_nodes, _ = get_ordered_necessary_nodes_and_paths_between_nodes(
                        graph, branch_start_node_id, next_node_id
                    )
                    used_nodes.update(branch_nodes)
                    match_branch_nodes(branch_nodes)

    match_branch_nodes(ordered_necessary_nodes)
    logger.info("[extract_unused_nodes_via_hydrated_constants] after matching branch used_nodes: {}".format(used_nodes))
    return set(graph.nodes) - used_nodes


def get_task_referenced_constants(pipeline_tree: dict, constants: dict, extra_data: dict, *args, **kwargs) -> dict:
    """
    @summary: 基于当前变量参数，获取任务中被引用的变量
    """
    hydrated_constants = get_constant_values(constants, extra_data)
    logger.info("[get_task_referenced_constants] hydrated_constants: {}".format(hydrated_constants))
    unused_nodes = extract_unused_nodes_via_hydrated_constants(pipeline_tree, hydrated_constants)
    logger.info("[get_task_referenced_constants] unused_nodes: {}".format(unused_nodes))

    copy_pipeline_tree = copy.deepcopy(pipeline_tree)
    # 保留使用的节点
    for node_id in pipeline_tree[PE.activities].keys():
        if node_id in unused_nodes:
            copy_pipeline_tree[PE.activities].pop(node_id)
    for node_id in pipeline_tree[PE.gateways].keys():
        if node_id in unused_nodes:
            copy_pipeline_tree[PE.gateways].pop(node_id)
    PipelineTemplateWebPreviewer.remove_useless_constants(
        exclude_task_nodes_id=unused_nodes, pipeline_tree=copy_pipeline_tree,
    )
    referenced_constant_keys = set(copy_pipeline_tree["constants"].keys())
    logger.info("[get_task_referenced_constants] referenced_constant_keys: {}".format(referenced_constant_keys))
    # 获取这些变量引用到的变量
    for key in copy_pipeline_tree["constants"].keys():
        if key in constants:
            refs = ConstantTemplate(constants[key].get("value")).get_reference()
            referenced_constant_keys.update(["${%s}" % r for r in refs if "${%s}" % r in hydrated_constants])
    return {"referenced_constants": list(referenced_constant_keys)}
