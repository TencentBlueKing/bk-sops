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

import copy

from pipeline import exceptions
from pipeline.core.data import library, var
from pipeline.core.data.expression import ConstantTemplate
from pipeline.validators.utils import format_node_io_to_list

from pipeline_web.constants import PWE


def format_web_data_to_pipeline(web_pipeline, is_subprocess=False):
    """
    @summary:
    @param web_pipeline: pipeline 前端数据
    @param is_subprocess: 是否子流程
    @return:
    """
    pipeline_tree = copy.deepcopy(web_pipeline)
    constants = pipeline_tree.pop("constants")
    classification = classify_constants(constants, is_subprocess)
    pipeline_tree["data"] = {
        "inputs": classification["data_inputs"],
        "outputs": [key for key in pipeline_tree.pop("outputs")],
    }

    for act_id, act in list(pipeline_tree["activities"].items()):
        if act["type"] == "ServiceActivity":
            act_data = act["component"].pop("data")

            all_inputs = calculate_constants_type(act_data, classification["data_inputs"])
            act["component"]["inputs"] = {key: value for key, value in list(all_inputs.items()) if key in act_data}
            act["component"]["global_outputs"] = classification["acts_outputs"].get(act_id, {})
        elif act["type"] == "SubProcess":
            parent_params = {}
            for key, info in list(act["pipeline"]["constants"].items()):
                # 为子流程设置 params 使得外层参数能够往子流程中传递
                if info["show_type"] == "show":
                    # lazy 变量
                    var_cls = library.VariableLibrary.get_var_class(info["custom_type"])
                    if var_cls and issubclass(var_cls, var.LazyVariable):
                        parent_params[key] = {
                            "type": "lazy",
                            "source_tag": info["source_tag"],
                            "custom_type": info["custom_type"],
                            "value": info["value"],
                        }
                    else:
                        parent_params[key] = {"type": "splice", "value": info["value"]}
            act["params"] = parent_params
            act["pipeline"] = format_web_data_to_pipeline(act["pipeline"], is_subprocess=True)
        else:
            raise exceptions.FlowTypeError("Unknown Activity type: %s" % act["type"])

    for act in list(pipeline_tree["activities"].values()):
        format_node_io_to_list(act, o=False)

    for gateway in list(pipeline_tree["gateways"].values()):
        format_node_io_to_list(gateway, o=False)

    format_node_io_to_list(pipeline_tree["end_event"], o=False)

    return pipeline_tree


def classify_constants(constants, is_subprocess):
    # pipeline tree inputs
    data_inputs = {}
    # pipeline act outputs
    acts_outputs = {}
    for key, info in list(constants.items()):
        # 显示的变量可以引用父流程 context，通过 param 传参
        if info["show_type"] == "show":
            info["is_param"] = True
        else:
            info["is_param"] = False

        if info["custom_type"]:
            var_cls = library.VariableLibrary.get_var_class(info["custom_type"])

        # 输出参数
        if info["source_type"] == "component_outputs":
            if info["source_info"].values():
                source_key = list(info["source_info"].values())[0][0]
                source_step = list(info["source_info"].keys())[0]
                # 生成 pipeline 层需要的 pipeline input
                data_inputs[key] = {
                    "type": "splice",
                    "source_act": source_step,
                    "source_key": source_key,
                    "value": info["value"],
                    "is_param": info["is_param"],
                }
                # 生成 pipeline 层需要的 acts_output
                acts_outputs.setdefault(source_step, {}).update({source_key: key})
        # 自定义的Lazy类型变量
        elif info["custom_type"] and var_cls and issubclass(var_cls, var.LazyVariable):
            data_inputs[key] = {
                "type": "lazy",
                "source_tag": info["source_tag"],
                "custom_type": info["custom_type"],
                "value": info["value"],
                "is_param": info["is_param"],
            }
        else:
            ref = ConstantTemplate(info["value"]).get_reference()
            constant_type = "splice" if ref else "plain"
            is_param = info["show_type"] == "show" and is_subprocess
            data_inputs[key] = {"type": constant_type, "value": info["value"], "is_param": is_param}

    result = {"data_inputs": data_inputs, "acts_outputs": acts_outputs}
    return result


def calculate_constants_type(to_calculate, calculated):
    """
    @summary:
    @param to_calculate: 待计算的变量
    @param calculated: 变量类型确定的，直接放入结果
    @return:
    """
    data = copy.deepcopy(calculated)
    for key, info in list(to_calculate.items()):
        ref = ConstantTemplate(info["value"]).get_reference()
        constant_type = "splice" if ref else "plain"
        data.setdefault(key, {"type": constant_type, "value": info["value"], "is_param": info.get("is_param", False)})

    return data


def get_all_nodes(pipeline_tree, with_subprocess=False):
    all_nodes = {}
    all_nodes.update(pipeline_tree[PWE.activities])
    all_nodes.update(pipeline_tree[PWE.gateways])
    all_nodes.update(
        {
            pipeline_tree[PWE.start_event][PWE.id]: pipeline_tree[PWE.start_event],
            pipeline_tree[PWE.end_event][PWE.id]: pipeline_tree[PWE.end_event],
        }
    )
    if with_subprocess:
        for act in pipeline_tree[PWE.activities].values():
            if act[PWE.type] == PWE.SubProcess:
                all_nodes.update(get_all_nodes(act[PWE.pipeline], with_subprocess=True))
    return all_nodes
