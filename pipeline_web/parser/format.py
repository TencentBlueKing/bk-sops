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

from bamboo_engine.template import Template
from pipeline import exceptions
from pipeline.core.data import library, var
from pipeline.validators.utils import format_node_io_to_list

from pipeline_web.constants import PWE


def format_web_data_to_pipeline(web_pipeline: dict, is_subprocess: bool = False) -> dict:
    """
    更新或创建新的普通上下文数据

    :param web_pipeline: pipeline web tree
    :param is_subprocess: 是否是子流程的 tree
    :return: bamboo pipeline tree
    """
    pipeline_tree = copy.deepcopy(web_pipeline)
    constants = pipeline_tree.pop("constants")
    # classify inputs and outputs
    classification = classify_constants(constants, is_subprocess)

    pipeline_tree["data"] = {
        "inputs": classification["data_inputs"],
        "outputs": [key for key in pipeline_tree.pop("outputs")],
        "pre_render_keys": sorted(list(get_pre_render_mako_keys(constants))),
    }

    for act_id, act in list(pipeline_tree["activities"].items()):
        if act["type"] == "ServiceActivity":
            act_data = act["component"].pop("data")

            all_inputs = format_data_to_pipeline_inputs(act_data, classification["data_inputs"])
            act["component"]["inputs"] = {key: value for key, value in list(all_inputs.items()) if key in act_data}
            act["component"]["global_outputs"] = classification["acts_outputs"].get(act_id, {})

            # old web field process
            if "skippable" not in act:
                act["skippable"] = act.get("isSkipped", True)
            if "retryable" not in act:
                act["retryable"] = act.get("can_retry", True)

            # 检查节点配置冲突
            if act.get("timeout_config", {}).get("enable") and (
                act["error_ignorable"] or act.get("auto_retry", {}).get("enable")
            ):
                raise exceptions.InvalidOperationException(
                    "timeout_config can not be enabled with error_ignorable or auto_retry at the same time"
                )

            # 节点执行代理人配置
            if act.get("executor_proxy"):
                act["component"]["inputs"]["__executor_proxy"] = {
                    "type": "plain",
                    "value": act.get("executor_proxy"),
                    "is_param": False,
                    "need_render": False,
                }

        elif act["type"] == "SubProcess":
            parent_params = {}
            for key, info in list(act["pipeline"]["constants"].items()):
                # 为子流程设置 params 使得外层参数能够往子流程中传递
                if info["show_type"] == "show":
                    # lazy 变量
                    var_cls = library.VariableLibrary.get_var_class(info["custom_type"])
                    if var_cls and issubclass(var_cls, var.LazyVariable):
                        if (
                            var_cls.type == "meta"
                            and hasattr(var_cls, "process_meta_value")
                            and callable(var_cls.process_meta_value)
                        ):
                            value = var_cls.process_meta_value(info["meta"], info["value"])
                        else:
                            value = info["value"]

                        # 如果 lazy 类型的变量被勾选到了全局变量
                        # 则将 lazy 类型改为 splice 类型，避免两次解析 lazy 的值
                        # 用 value 从 constants 中检索是因为勾选时 key 可能会发生变化
                        if isinstance(value, str) and key in set(
                            constants.get(value, {}).get("source_info", {}).get(act["id"], [])
                        ):
                            parent_params[key] = {
                                "type": "splice",
                                "value": value,
                            }
                        else:
                            parent_params[key] = {
                                "type": "lazy",
                                "source_tag": info["source_tag"],
                                "custom_type": info["custom_type"],
                                "value": value,
                            }
                    else:
                        parent_params[key] = {"type": "splice", "value": info["value"]}
                    # 注入处理need_render
                    parent_params[key]["need_render"] = info.get("need_render", True)
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


def get_pre_render_mako_keys(constants: dict) -> set:
    """
    获取需要预渲染的变量的 keys

    :param constants: pipeline web tree 中的 constants 字段
    :return: 需要预渲染的变量的 keys
    """
    pre_render_inputs_keys = set()
    for key, info in list(constants.items()):
        if info["source_type"] == "component_outputs":
            continue

        if "pre_render_mako" in info:
            if info["pre_render_mako"]:
                pre_render_inputs_keys.add(key)

    return pre_render_inputs_keys


def classify_constants(constants: dict, is_subprocess: bool):
    """
    将 pipeline web tree 中的 constants 字段转换成
    bamboo pipeline tree 中的 data inputs 和节点输出的<节点ID:key -> data key>信息

    :param constants: pipeline web tree
    :param is_subprocess: 是否是子流程的 tree
    :return: bamboo pipeline tree 中的 data inputs 和节点输出的<节点ID:key -> data key>信息
    """
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
            if (
                var_cls.type == "meta"
                and hasattr(var_cls, "process_meta_value")
                and callable(var_cls.process_meta_value)
            ):
                value = var_cls.process_meta_value(info["meta"], info["value"])
            else:
                value = info["value"]
            data_inputs[key] = {
                "type": "lazy",
                "source_tag": info["source_tag"],
                "custom_type": info["custom_type"],
                "value": value,
                "is_param": info["is_param"],
            }
        else:
            ref = Template(info["value"]).get_reference()
            constant_type = "splice" if ref else "plain"
            is_param = info["show_type"] == "show" and is_subprocess
            data_inputs[key] = {"type": constant_type, "value": info["value"], "is_param": is_param}

    result = {"data_inputs": data_inputs, "acts_outputs": acts_outputs}
    return result


def format_data_to_pipeline_inputs(data: dict, pipeline_inputs: dict, change_pipeline_inputs: bool = False):
    """
    将 data 中的数据转换成 pipeline inputs 并添加到 pipeline_inputs 中

    :param data: 待计算的变量
    :param pipeline_inputs: 变量类型确定的，直接放入结果
    :param change_pipeline_inputs: 是否直接修改pipeline_inputs并作为结果返回
    :return:
    """
    ret = copy.deepcopy(pipeline_inputs) if not change_pipeline_inputs else pipeline_inputs
    for key, info in list(data.items()):
        ref = Template(info["value"]).get_reference()
        constant_type = "splice" if ref else "plain"
        # is_param和need_render禁止同时为True
        if info.get("is_param") and info.get("need_render"):
            raise exceptions.DataException("is_param and need_render cannot be selected at the same time")
        ret.setdefault(
            key,
            {
                "type": constant_type,
                "value": info["value"],
                "is_param": info.get("is_param", False),
                "need_render": info.get("need_render", True),
            },
        )

    return ret


def get_all_nodes(pipeline_tree: dict, with_subprocess: bool = False) -> dict:
    """
    获取 pipeline_tree 中所有 activity 的信息

    :param pipeline_tree: pipeline web tree
    :param with_subprocess: 是否是子流程的 tree
    :return: 包含 pipeline_tree 中所有 activity 的字典（包括子流程的 acitivity）
    """
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
