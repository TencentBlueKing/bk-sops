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
from abc import ABCMeta, abstractmethod

import yaml
import jsonschema

from pipeline.core.data import library
from pipeline.parser.utils import replace_all_id
from pipeline_web.drawing_new.drawing import draw_pipeline


class BaseSchemaConverter(metaclass=ABCMeta):
    @abstractmethod
    def convert(self, data: dict) -> dict:
        pass

    @abstractmethod
    def reconvert(self, data: dict) -> dict:
        pass


class YamlSchemaConverter(BaseSchemaConverter):
    VERSION = "v1"
    TEMPLATE_DEFAULT_META = {
        "description": "",
    }
    NODE_NECESSARY_FIELDS = {
        "ServiceActivity": ["id", "type", "name", "component"],
        "SubProcess": ["id", "type", "name", "template_id"],
        "EmptyEndEvent": ["id", "type"],
        "EmptyStartEvent": ["id", "type"],
        "ExclusiveGateway": ["id", "type", "conditions"],
        "ConditionalParallelGateway": ["id", "type", "conditions"],
        "ConvergeGateway": ["id", "type"],
        "ParallelGateway": ["id", "type", "converge_gateway_id"],
    }
    NODE_DEFAULT_FIELD_VALUE = {
        "ServiceActivity": {
            "error_ignorable": False,
            "labels": [],
            "loop": None,
            "optional": True,
            "retryable": True,
            "skippable": True,
            "stage_name": "",
        },
        "SubProcess": {
            "error_ignorable": False,
            "labels": [],
            "loop": None,
            "optional": True,
            "retryable": True,
            "isSkipped": True,
            "stage_name": "",
            "hooked_constants": [],
        },
        "Gateway": {"labels": [], "name": ""},
    }
    NODE_FIELD_MAPPING = {
        "error_ignorable": "ignore_error",
        "retryable": "can_retry",
        "skippable": "can_skip",
    }
    NODE_FIELD_ORDER = [
        "id",
        "type",
        "name",
        "component",
        "output",
        "ignore_error",
        "can_retry",
        "can_skip",
        "optional",
        "stage_name",
        "labels",
        "loop",
        "next",
    ]
    CONSTANT_DEFAULT_FIELD_VALUE = {
        "desc": "",
        "validation": "",
        "version": "legacy",
        "is_meta": False,
        "custom_type": "",
        "show_type": "show",
        "value": "",
        "source_tag": "",
    }
    CONSTANT_EXPORT_OPTION_FIELD = ["plugin_code"]
    YAML_DOC_SCHEMA = {
        "type": "object",
        "required": ["meta", "spec", "schema_version"],
        "properties": {
            "meta": {"type": "object", "required": ["name", "id"]},
            "spec": {"type": "object", "required": ["nodes"], "properties": {"nodes": {"type": "array"}}},
        },
    }
    NOT_HOOK_COMPONENT_INPUT_KEY = "dummy_component_inputs"

    def validate_data(self, yaml_docs: list):
        """检查导入yaml数据结构合法性"""
        yaml_data = {}
        try:
            for yaml_doc in yaml_docs:
                jsonschema.validate(yaml_doc, self.YAML_DOC_SCHEMA)
                template_id = yaml_doc["meta"].get("id")
                yaml_data[template_id] = yaml_doc
        except jsonschema.ValidationError as e:
            return {"result": False, "data": yaml_data, "message": {"file": ["YAML数据格式有误: {}".format(e)]}}
        # 检查流程间是否有环引用的情况

        errors = {}
        template_set = set()
        for template_id, template in yaml_data.items():
            error = []
            template_set.add(template_id)
            # template 必须字段检查
            if not template.get("meta", {}).get("name"):
                error.append("模版下meta字段需包含模版名称(name字段)")
            # nodes的类型必须是list
            if not isinstance(template.get("spec", {}).get("nodes"), list):
                error.append("模版spec下nodes字段必须为列表")
                continue
            template = template["spec"]
            # template 下 nodes字段 & 连接 检查
            nodes_set = set([node["id"] for node in template["nodes"] if "id" in node])
            for i, node in enumerate(template["nodes"]):
                if "id" not in node or "type" not in node:
                    error.append("模版下所有节点都必须包含id和type字段")
                    continue
                if not set(self.NODE_NECESSARY_FIELDS[node["type"]]).issubset(node.keys()):
                    error.append(
                        "节点{}所属的节点类型{}需缺少必须字段：{}".format(
                            node["id"], node["type"], set(self.NODE_NECESSARY_FIELDS[node["type"]]) - set(node.keys())
                        )
                    )
                    continue
                if node["type"] in ["ExclusiveGateway", "ConditionalParallelGateway"]:
                    for condition in node["conditions"].keys():
                        if condition not in nodes_set:
                            error.append("{}网关{} 条件{}无法找到对应节点".format(node["type"], node["id"], condition))
                if node.get("next"):
                    if (
                        isinstance(node["next"], list)
                        and len(node["next"]) > 1
                        and node["type"] not in ["ExclusiveGateway", "ParallelGateway", "ConditionalParallelGateway"]
                    ):
                        error.append("节点{}只能有一个next节点".format(node["id"]))
                    else:
                        for next_node in node["next"]:
                            if next_node not in nodes_set:
                                error.append("节点{}无法找到下一个节点{}".format(node["id"], next_node))
            if error:
                errors[template_id] = error
        if errors:
            return {"result": False, "data": yaml_data, "message": errors}
        return {"result": True, "data": yaml_data, "message": {}}

    def convert(self, full_data: dict):
        """将原始流程数据转换成只保留YAML字段的数据"""
        data = copy.deepcopy(full_data)
        template_data = {}
        templates = data["pipeline_template_data"]["template"]
        for _, template_meta in data["template"].items():
            templates[template_meta["pipeline_template_id"]].update(template_meta)
        for pipeline_id, template in templates.items():
            template_data[pipeline_id] = self._convert_template(template)
        self._generate_readable_id(template_data)
        yaml_docs = []
        for template_id, template in template_data.items():
            meta = template.pop("meta")
            meta["id"] = template_id
            yaml_docs.append({"schema_version": "v1", "meta": meta, "spec": template})
        return {"result": True, "data": yaml_docs, "message": ""}

    def reconvert(self, yaml_docs: list):
        """将YAML字段流程数据转换成原始字段"""
        validate_result = self.validate_data(yaml_docs)
        if not validate_result["result"]:
            return {"result": False, "data": [], "message": validate_result["message"]}
        yaml_data = validate_result["data"]
        data = copy.deepcopy(yaml_data)
        templates = {}
        template_order = self._calculate_template_orders(data)
        for template_id in template_order:
            templates[template_id] = self._reconvert_template(template_id, data, templates)
        return {"result": True, "data": {"templates": templates, "template_order": template_order}, "message": []}

    @staticmethod
    def dump_yaml_file(yaml_data: list, file_name: str):
        """将YAML格式数据保存为文件"""
        with open(file_name, "w") as yaml_file:
            yaml.dump_all(yaml_data, yaml_file, allow_unicode=True, sort_keys=False)
        return {"result": True, "data": "", "message": ""}

    def _reconvert_template(self, template_id: str, data: dict, cur_templates: dict):
        """将YAML字段单流程数据转换成原始字段"""
        template = data[template_id]
        reconverted_template = {**self.TEMPLATE_DEFAULT_META}
        reconverted_template.update(template["meta"])
        reconverted_template["tree"] = self._reconvert_tree(template["spec"], cur_templates)
        return reconverted_template

    def _reconvert_nodes_in_tree(self, nodes: dict, reconverted_tree: dict, cur_templates: dict):
        """reconvert某流程树中各个节点的字段"""
        for i, node in enumerate(nodes):
            for json_field, yaml_field in self.NODE_FIELD_MAPPING.items():
                if yaml_field in node:
                    node.update({json_field: node[yaml_field]})
                    node.pop(yaml_field)
            if node["type"] == "EmptyStartEvent":
                reconverted_tree["start_event"] = {
                    "id": node["id"],
                    "incoming": "",
                    "labels": [],
                    "name": "",
                    "outgoing": node.pop("next") if "next" in node else [nodes[i + 1]["id"]],
                    "type": "EmptyStartEvent",
                }
            elif node["type"] == "ServiceActivity":
                activity = {
                    **self.NODE_DEFAULT_FIELD_VALUE["ServiceActivity"],
                    "outgoing": node.pop("next") if "next" in node else [nodes[i + 1]["id"]],
                }
                outputs = node.pop("output") if "output" in node else {}
                activity.update(node)
                component_constants = {"component_inputs": activity["component"]["data"], "component_outputs": outputs}
                for source_type, data in component_constants.items():
                    for form_key, param in data.items():
                        if "key" in param:
                            source_info = (node["id"], form_key)
                            constant, is_create = self._reconvert_constant(
                                constant=param,
                                cur_constants=reconverted_tree["constants"],
                                source_info=source_info,
                                source_tag="{}.{}".format(activity["component"]["code"], form_key),
                                source_type=source_type,
                            )
                            if is_create:
                                reconverted_tree["constants"][param["key"]] = constant
                            param["value"] = param["key"]
                        param["hook"] = True if source_type == "component_inputs" and "key" in param else False
                        for key in list(param.keys()):
                            if key not in ["value", "hook"]:
                                param.pop(key)
                reconverted_tree["activities"][node["id"]] = activity
            elif node["type"] == "SubProcess":
                subprocess = {
                    **self.NODE_DEFAULT_FIELD_VALUE["SubProcess"],
                    "outgoing": node.pop("next") if "next" in node else [nodes[i + 1]["id"]],
                }
                inputs = node.pop("data") if "data" in node else {}
                hooked_inputs = {key: value for key, value in inputs.items() if "key" in value}
                outputs = node.pop("output") if "output" in node else {}
                subprocess.update(node)
                constants = dict(
                    [
                        (key, value)
                        for key, value in cur_templates[node["template_id"]]["tree"]["constants"].items()
                        if value["source_type"] != "component_outputs"
                    ]
                )
                constants = copy.deepcopy(constants)
                for key, constant in constants.items():
                    if key in hooked_inputs:
                        constant["value"] = hooked_inputs[key]["key"]
                    elif key in inputs:
                        constant["value"] = inputs[key]["value"]

                subprocess["constants"] = constants
                subprocess_constants = {"component_inputs": hooked_inputs, "component_outputs": outputs}
                for source_type, data in subprocess_constants.items():
                    for form_key, param in data.items():
                        source_info = (node["id"], form_key)
                        constant, is_create = self._reconvert_constant(
                            constant=param,
                            cur_constants=reconverted_tree["constants"],
                            source_tag=param.get("source_tag"),
                            source_info=source_info,
                            source_type=source_type,
                        )
                        if is_create:
                            reconverted_tree["constants"][param["key"]] = constant
                reconverted_tree["activities"][node["id"]] = subprocess
            elif node["type"].endswith("Gateway"):
                gateway = {
                    **self.NODE_DEFAULT_FIELD_VALUE["Gateway"],
                    "outgoing": node.pop("next") if "next" in node else [nodes[i + 1]["id"]],
                }
                gateway.update(node)
                reconverted_tree["gateways"][node["id"]] = gateway
            elif node["type"] == "EmptyEndEvent":
                reconverted_tree["end_event"] = {
                    "id": node["id"],
                    "incoming": [],
                    "labels": [],
                    "name": "",
                    "outgoing": [],
                    "type": "EmptyEndEvent",
                }

    @staticmethod
    def _reconvert_flows_in_tree(nodes: dict, reconverted_tree: dict):
        """reconvert单流程树中的flows字段"""
        flows = {}
        flow_idx = 1
        tid = reconverted_tree["start_event"]["id"].split("_")[0]
        for node_id, node in nodes.items():
            replace_outgoing = []
            for next_node_id in node["outgoing"]:
                line_id = "{}_line{}".format(tid, flow_idx)
                flow_idx += 1
                flows[line_id] = {
                    "id": line_id,
                    "is_default": False,
                    "source": node_id,
                    "target": next_node_id,
                }
                nodes[next_node_id].setdefault("incoming", []).append(line_id)
                replace_outgoing.append(line_id)
                if node["type"] in ["ExclusiveGateway", "ConditionalParallelGateway"]:
                    default_condition = node.get("default_condition")
                    if default_condition and default_condition.get(next_node_id, ""):
                        default_condition[next_node_id]["tag"] = "branch_{}_{}".format(node_id, next_node_id)
                        node["default_condition"] = default_condition[next_node_id]
                        node["default_condition"]["flow_id"] = line_id
                    else:
                        condition = node["conditions"].pop(next_node_id)
                        condition["tag"] = "branch_{}_{}".format(node_id, next_node_id)
                        node["conditions"][line_id] = condition

            node["outgoing"] = replace_outgoing
        reconverted_tree["flows"] = flows

        # 统一处理各种类型节点的incoming和outgoing类型
        incoming_str_types = ["EmptyStartEvent"]
        outgoing_str_types = ["EmptyStartEvent", "ServiceActivity", "SubProcess", "EmptyEndEvent", "ConvergeGateway"]
        for _, node in nodes.items():
            if node["type"] in incoming_str_types:
                node["incoming"] = node["incoming"][0] if node["incoming"] else ""
            if node["type"] in outgoing_str_types:
                node["outgoing"] = node["outgoing"][0] if node["outgoing"] else ""

    def _reconvert_tree(self, template: dict, cur_templates: dict):
        """对单流程树从YAML字段恢复为原始字段"""
        reconverted_tree = {
            "activities": {},
            "constants": {},
            "end_event": {},
            "flows": {},
            "gateways": {},
            "line": [],
            "location": [],
            "outputs": template.get("outputs") or [],
            "start_event": {},
        }
        # 恢复节点值
        self._reconvert_nodes_in_tree(template["nodes"], reconverted_tree, cur_templates)
        nodes = {
            **reconverted_tree["activities"],
            **reconverted_tree["gateways"],
            reconverted_tree["end_event"]["id"]: reconverted_tree["end_event"],
            reconverted_tree["start_event"]["id"]: reconverted_tree["start_event"],
        }
        # 生成flows，计算incoming
        self._reconvert_flows_in_tree(nodes, reconverted_tree)

        # 恢复constants格式
        if "constants" in template:
            for constant_key, constant_attrs in template["constants"].items():
                reconverted_constant, is_create = self._reconvert_constant(
                    constant={**constant_attrs, "key": constant_key}, cur_constants=reconverted_tree["constants"],
                )
                if is_create:
                    reconverted_tree["constants"][constant_key] = reconverted_constant
        if self.NOT_HOOK_COMPONENT_INPUT_KEY in template:
            for constant_key, constant_attrs in template[self.NOT_HOOK_COMPONENT_INPUT_KEY].items():
                reconverted_constant, is_create = self._reconvert_constant(
                    constant={**constant_attrs, "key": constant_key},
                    cur_constants=reconverted_tree["constants"],
                    source_tag=constant_attrs.get("source_tag"),
                    source_type="component_inputs",
                )
                if is_create:
                    reconverted_tree["constants"][constant_key] = reconverted_constant
        # constants添加index
        index_num = 0
        for _, constant in reconverted_tree["constants"].items():
            constant.update({"index": index_num})
            index_num += 1

        replace_all_id(reconverted_tree)
        draw_pipeline(reconverted_tree)
        return reconverted_tree

    def _reconvert_constant(
        self,
        constant: dict,
        cur_constants: dict,
        source_info: tuple = None,
        source_tag: str = None,
        source_type: str = None,
    ) -> (dict, bool):
        """reconvert单流程树中的constant字段"""
        if constant["key"] in cur_constants:
            if source_info:
                key, value = source_info
                cur_constants[constant["key"]]["source_info"].setdefault(key, []).append(value)
            return cur_constants[constant["key"]], False
        reconverted_constant = {
            **self.CONSTANT_DEFAULT_FIELD_VALUE,
            "source_info": {},
            "source_type": "custom" if not source_type else source_type,
        }
        if "type" in constant:
            reconverted_constant["custom_type"] = constant.pop("type")
        if "hide" in constant:
            reconverted_constant["show_type"] = "hide"
            constant.pop("hide")
        reconverted_constant.update(constant)
        if source_info:
            reconverted_constant["source_info"] = {source_info[0]: [source_info[1]]}
        var_cls = library.VariableLibrary.get_var_class(reconverted_constant["custom_type"])
        var_tag = (
            var_cls.tag
            if var_cls
            else "{}.{}".format(reconverted_constant["custom_type"], reconverted_constant["custom_type"])
        )
        reconverted_constant["source_tag"] = source_tag if source_tag else var_tag
        return reconverted_constant, True

    @staticmethod
    def _calculate_template_orders(templates: dict):
        """计算templates顺序，保证子流程会在父流程之前，拓扑排序"""
        children_templates = {key: [] for key in templates.keys()}
        for template_id, template in templates.items():
            for node in template["spec"]["nodes"]:
                if node["type"] == "SubProcess":
                    children_templates[template_id].append(node["template_id"])
        visited = set()
        orders = []

        def dfs(tid: str):
            if tid in visited:
                return
            for child_tid in children_templates[tid]:
                dfs(child_tid)
            visited.add(tid)
            orders.append(tid)

        for template_id in children_templates:
            dfs(template_id)

        return orders

    @staticmethod
    def _generate_readable_id(yaml_data: dict):
        """YAML数据中流程和节点id生成易读id"""
        template_idx = 1
        template_key_mapping = {}
        node_key_mapping = {}
        for key, data in yaml_data.items():
            if "nodes" in data:
                template_key_mapping[key] = "template{}".format(template_idx)
                node_idx = 1
                for node in data["nodes"]:
                    node_key_mapping[node["id"]] = "t{}_node{}".format(template_idx, node_idx)
                    node_idx += 1
                template_idx += 1
        for key, data in yaml_data.items():
            if key in template_key_mapping:
                for node in data["nodes"]:
                    node["id"] = node_key_mapping[node["id"]]
                    if node.get("next"):
                        node["next"] = [node_key_mapping[node_id] for node_id in node["next"]]
                    if node["type"] == "SubProcess":
                        node["template_id"] = template_key_mapping[node["template_id"]]
                    if node["type"] in ["ExclusiveGateway", "ConditionalParallelGateway"]:
                        if "default_condition" in node:
                            node["default_condition"] = dict(
                                [
                                    (node_key_mapping[node_id], data)
                                    for node_id, data in node["default_condition"].items()
                                ]
                            )
                        node["conditions"] = dict(
                            [(node_key_mapping[node_id], data) for node_id, data in node["conditions"].items()]
                        )
                    if node["type"] == "ParallelGateway":
                        node["converge_gateway_id"] = node_key_mapping[node["converge_gateway_id"]]

        for key in template_key_mapping:
            yaml_data[template_key_mapping[key]] = yaml_data[key]
            yaml_data.pop(key)
        return yaml_data

    def _convert_template(self, template: dict):
        """将单流程转换为YAML数据字段"""
        yaml_template = {"meta": {"name": template["name"]}}
        converted_tree = self._convert_tree(template["tree"])
        yaml_template.update(**converted_tree)
        return yaml_template

    def _convert_tree(self, tree: dict):
        """将单流程树转换为YAML数据字段"""
        nodes = {
            **tree["activities"],
            **tree["gateways"],
            tree["start_event"]["id"]: tree["start_event"],
            tree["end_event"]["id"]: tree["end_event"],
        }
        start_node_id = tree["start_event"]["id"]
        end_node_id = tree["end_event"]["id"]
        # 将边相关信息处理成节点信息
        flows = tree["flows"]
        for flow in flows.values():
            nodes[flow["source"]].setdefault("next", []).append(flow["target"])
            nodes[flow["target"]].setdefault("last", []).append(flow["source"])
            if nodes[flow["source"]]["type"] in ["ExclusiveGateway", "ConditionalParallelGateway"]:
                default_condition = nodes[flow["source"]].get("default_condition")
                if default_condition and default_condition.get("flow_id") == flow["id"]:
                    nodes[flow["source"]]["default_condition"] = {flow["target"]: default_condition}
                else:
                    condition = nodes[flow["source"]]["conditions"].pop(flow["id"])
                    nodes[flow["source"]]["conditions"][flow["target"]] = condition
        nodes[start_node_id]["last"] = []
        nodes[end_node_id]["next"] = []

        constants = tree["constants"]
        converted_constants, param_constants = self._convert_constants(constants)

        ordered_node_ids = self._calculate_nodes_orders(
            {node_id: {"next": node["next"], "last": node["last"]} for node_id, node in copy.deepcopy(nodes).items()},
            start_node_id,
        )
        result_nodes = []
        for node_id in ordered_node_ids:
            converted_node = self._convert_node(nodes[node_id], param_constants)
            if len(nodes[node_id]["next"]) > 1 or (
                len(nodes[node_id]["next"]) > 0 and len(nodes[nodes[node_id]["next"][0]]["last"]) > 1
            ):
                converted_node["next"] = nodes[node_id]["next"]
            result_nodes.append(converted_node)

        converted_tree = {"nodes": result_nodes}
        if converted_constants:
            converted_tree["constants"] = converted_constants
        if param_constants["component_inputs"].get(self.NOT_HOOK_COMPONENT_INPUT_KEY):
            converted_tree[self.NOT_HOOK_COMPONENT_INPUT_KEY] = param_constants["component_inputs"][
                self.NOT_HOOK_COMPONENT_INPUT_KEY
            ]
        if tree["outputs"]:
            converted_tree["outputs"] = tree["outputs"]
        return converted_tree

    def _convert_node(self, node: dict, param_constants: dict):
        """将节点数据从原始字段转换为YAML字段"""
        converted_node = {}
        for field in self.NODE_NECESSARY_FIELDS.get(node["type"], []):
            converted_field = field if field not in self.NODE_FIELD_MAPPING else self.NODE_FIELD_MAPPING[field]
            converted_node[converted_field] = node[field]
        if node["type"] == "ServiceActivity":
            # 处理component和outputs
            component_data = converted_node["component"]["data"]
            for form_key, data in component_data.items():
                is_hooked = data.pop("hook")
                if is_hooked:
                    input_constant = param_constants["component_inputs"][node["id"]][form_key]
                    component_data[form_key] = input_constant
            for form_key, constant in param_constants["component_outputs"].get(node["id"], {}).items():
                converted_node.setdefault("output", {})[form_key] = constant
        elif node["type"] == "SubProcess":
            for key, constant in node["constants"].items():
                converted_node.setdefault("data", {})[key] = {"value": constant["value"]}
            # 处理 对应勾选的constants
            for form_key, constant in param_constants["component_inputs"].get(node["id"], {}).items():
                converted_node.setdefault("data", {})[form_key] = constant
            for form_key, constant in param_constants["component_outputs"].get(node["id"], {}).items():
                converted_node.setdefault("output", {})[form_key] = constant
        elif node["type"] in ["ExclusiveGateway", "ConditionalParallelGateway"]:
            if "default_condition" in node:
                converted_node["default_condition"] = node.get("default_condition")
                for default_condition in node["default_condition"].values():
                    default_condition.pop("flow_id", None)
                    default_condition.pop("tag", None)
            for condition in node["conditions"].values():
                condition.pop("tag", None)
        sorted_node = dict(
            sorted(
                converted_node.items(),
                key=lambda pair: self.NODE_FIELD_ORDER.index(pair[0])
                if pair[0] in self.NODE_FIELD_ORDER
                else len(self.NODE_FIELD_ORDER),
            )
        )
        return sorted_node

    def _convert_constants(self, constants: dict, is_subprocess: bool = False) -> (dict, dict):
        """变量转换，会将用户变量和参数变量进行拆分"""
        converted_constants = {}
        param_constants = {"component_inputs": {}, "component_outputs": {}}
        for key, constant in constants.items():
            cur_constant = {"name": constant["name"], "value": constant["value"]}
            if constant["source_type"] in ["component_outputs", "component_inputs"]:
                if constant["source_type"] == "component_outputs":
                    cur_constant.pop("value")
                if not is_subprocess:
                    cur_constant.update({"key": key})
                    for node_id, form_keys in constant["source_info"].items():
                        for form_key in form_keys:
                            param_constants[constant["source_type"]].setdefault(node_id, {})[form_key] = cur_constant
                    # 勾选变量对应插件删掉但对应变量保留的情况
                    if not constant["source_info"]:
                        key = cur_constant.pop("key")
                        param_constants[constant["source_type"]].setdefault(self.NOT_HOOK_COMPONENT_INPUT_KEY, {})[
                            key
                        ] = cur_constant
                else:
                    cur_constant = {"used_by": constant["source_info"]}
                    param_constants[constant["source_type"]][key] = cur_constant
            else:
                converted_constants.update({key: cur_constant})
            for field, value in constant.items():
                if field in self.CONSTANT_DEFAULT_FIELD_VALUE and self.CONSTANT_DEFAULT_FIELD_VALUE[field] != value:
                    if field == "custom_type":
                        cur_constant["type"] = value
                    elif field == "show_type":
                        cur_constant["hide"] = True
                    elif field == "source_tag":
                        if not constant["custom_type"]:
                            cur_constant["source_tag"] = value
                    else:
                        cur_constant[field] = value
                if field in self.CONSTANT_EXPORT_OPTION_FIELD and value:
                    cur_constant[field] = value
        return converted_constants, param_constants

    @staticmethod
    def _remove_loop_by_bfs(nodes: dict, start_node_id: str):
        """去除环状的情况, 会直接修改nodes"""
        node_id_queue = [start_node_id]
        cur_path_queue = [[start_node_id]]
        visited_node_ids = set()
        # 通过bfs遍历，并记录从开始节点到当前节点的路径
        while len(node_id_queue) > 0:
            cur_node_id = node_id_queue.pop(0)
            cur_path = cur_path_queue.pop(0)
            visited_node_ids.add(cur_node_id)
            next_node_to_remove = []
            for next_node_id in nodes[cur_node_id]["next"]:
                if next_node_id not in visited_node_ids:
                    node_id_queue.append(next_node_id)
                    cur_path_queue.append(cur_path + [next_node_id])
                # 如果下一个节点已经出现在当前路径中，则说明成环，去掉当前节点对下一个节点的连接
                elif next_node_id in cur_path:
                    next_node_to_remove.append(next_node_id)
            for node_to_remove in next_node_to_remove:
                nodes[cur_node_id]["next"].remove(node_to_remove)
                nodes[node_to_remove]["last"].remove(cur_node_id)
        return nodes

    def _calculate_nodes_orders(self, nodes: dict, start_node_id: str):
        """根据节点关系计算出可读性较强的节点顺序列表，考虑分支情况和带环情况"""
        # 先去除可能成环的边
        nodes = self._remove_loop_by_bfs(nodes, start_node_id)
        multi_next_node_stack = []
        cur_node_id = start_node_id
        ordered_node_ids = []
        ordered_node_set = set()
        node_number = len(nodes)
        while len(ordered_node_ids) < node_number:
            node = nodes[cur_node_id]
            # 如果还有其他节点的出度是该节点，则从多出度栈中拿一个节点作为下一个节点
            if len(node["last"]) > 0:
                cur_node_id = multi_next_node_stack.pop()
                continue
            # 如果当前节点是新节点，则添加到顺序队列中
            if cur_node_id not in ordered_node_set:
                ordered_node_ids.append(cur_node_id)
                ordered_node_set.add(cur_node_id)
            # 如果当前节点有多个出度，则随机选择一个作为下一个节点
            if len(node["next"]) >= 1:
                next_node_id = node["next"].pop()
                # 如果pop完之后还有出度, 则放入多出度栈中
                if len(node["next"]) > 0:
                    multi_next_node_stack.append(cur_node_id)
                # 去除下一个节点的入度
                nodes[next_node_id]["last"].remove(cur_node_id)
                cur_node_id = next_node_id
        return ordered_node_ids
