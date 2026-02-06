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
import re
import uuid

from pipeline.component_framework.models import ComponentModel

logger = logging.getLogger("root")


class SimpleFlowConverter:
    """
    将前端简化流程格式转换为标准运维 pipeline_tree

    输入格式示例:
    [
        {"type": "StartEvent", "id": "start", "name": "流程开始"},
        {"type": "Activity", "id": "n1", "name": "数据库备份", "code": "job_fast_execute_script"},
        {"type": "Link", "source": "start", "target": "n1"},
        {"type": "Variable", "key": "${db_server}", "name": "数据库IP"},
        ...
    ]
    """

    DEFAULT_ACTIVITY_CONFIG = {
        "auto_retry": {"enable": False, "interval": 0, "times": 1},
        "timeout_config": {"action": "forced_fail", "enable": False, "seconds": 10},
        "error_ignorable": False,
        "retryable": True,
        "skippable": True,
        "optional": True,
        "labels": [],
        "loop": None,
    }

    PROJECT_BASE_INFO = {
        "task_categories": [
            {"value": "OpsTools", "name": "运维工具"},
            {"value": "MonitorAlarm", "name": "监控告警"},
            {"value": "ConfManage", "name": "配置管理"},
            {"value": "DevTools", "name": "开发工具"},
            {"value": "EnterpriseIT", "name": "企业IT"},
            {"value": "OfficeApp", "name": "办公应用"},
            {"value": "Other", "name": "其它"},
            {"value": "Default", "name": "默认分类"},
        ],
        "flow_type_list": [
            {"value": "common", "name": "默认任务流程"},
            {"value": "common_func", "name": "职能化任务流程"},
        ],
        "notify_group": [
            {"value": "Maintainers", "text": "运维人员"},
            {"value": "ProductPm", "text": "产品人员"},
            {"value": "Developer", "text": "开发人员"},
            {"value": "Tester", "text": "测试人员"},
        ],
        "notify_type_list": [
            {"value": "weixin", "name": "微信"},
            {"value": "sms", "name": "短信"},
            {"value": "email", "name": "邮件"},
            {"value": "voice", "name": "语音"},
        ],
    }

    INTERNAL_VARIABLE = {
        "${_system.task_url}": {
            "key": "${_system.task_url}",
            "name": "任务URL",
            "index": "-9",
            "desc": "",
            "show_type": "hide",
            "source_type": "system",
            "source_tag": "",
            "source_info": {},
            "custom_type": "",
            "value": "",
            "hook": False,
            "validation": "",
        },
        "${_system.task_start_time}": {
            "key": "${_system.task_start_time}",
            "name": "任务开始时间",
            "index": -8,
            "desc": "",
            "show_type": "hide",
            "source_type": "system",
            "source_tag": "",
            "source_info": {},
            "custom_type": "",
            "value": "",
            "hook": False,
            "validation": "",
        },
        "${_system.language}": {
            "key": "${_system.language}",
            "name": "执行环境语言CODE",
            "index": -7,
            "desc": "中文对应 zh-hans，英文对应 en",
            "show_type": "hide",
            "source_type": "system",
            "source_tag": "",
            "source_info": {},
            "custom_type": "",
            "value": "",
            "hook": False,
            "validation": "",
        },
        "${_system.bk_biz_id}": {
            "key": "${_system.bk_biz_id}",
            "name": "任务所属的CMDB业务ID",
            "index": -6,
            "desc": "",
            "show_type": "hide",
            "source_type": "system",
            "source_tag": "",
            "source_info": {},
            "custom_type": "",
            "value": "",
            "hook": False,
            "validation": "",
        },
        "${_system.bk_biz_name}": {
            "key": "${_system.bk_biz_name}",
            "name": "任务所属的CMDB业务名称",
            "index": -5,
            "desc": "",
            "show_type": "hide",
            "source_type": "system",
            "source_tag": "",
            "source_info": {},
            "custom_type": "",
            "value": "",
            "hook": False,
            "validation": "",
        },
        "${_system.operator}": {
            "key": "${_system.operator}",
            "name": "任务的执行人（点击开始执行的人员）",
            "index": -4,
            "desc": "",
            "show_type": "hide",
            "source_type": "system",
            "source_tag": "",
            "source_info": {},
            "custom_type": "",
            "value": "",
            "hook": False,
            "validation": "",
        },
        "${_system.executor}": {
            "key": "${_system.executor}",
            "name": "任务的执行代理人",
            "index": -3,
            "desc": "",
            "show_type": "hide",
            "source_type": "system",
            "source_tag": "",
            "source_info": {},
            "custom_type": "",
            "value": "",
            "hook": False,
            "validation": "",
        },
        "${_system.task_id}": {
            "key": "${_system.task_id}",
            "index": -2,
            "name": "任务ID",
            "desc": "",
            "show_type": "hide",
            "source_type": "system",
            "source_tag": "",
            "source_info": {},
            "custom_type": "",
            "value": "",
            "hook": False,
            "validation": "",
        },
        "${_system.task_name}": {
            "key": "${_system.task_name}",
            "name": "任务名称",
            "index": -1,
            "desc": "",
            "show_type": "hide",
            "source_type": "system",
            "source_tag": "",
            "source_info": {},
            "custom_type": "",
            "value": "",
            "hook": False,
            "validation": "",
        },
    }

    def __init__(self, simple_flow: list):
        """
        初始化转换器

        :param simple_flow: 前端传入的简化流程列表
        """
        self.simple_flow = simple_flow
        self.nodes = {}
        self.links = []
        self.variables = []
        self.template_name = ""
        self.id_mapping = {}
        self._parse_input()

    def _parse_input(self):
        """解析输入数据，分类存储"""
        for item in self.simple_flow:
            item_type = item.get("type")
            if item_type == "Link":
                self.links.append(item)
            elif item_type == "Variable":
                self.variables.append(item)
            elif item_type == "name":
                self.template_name = item.get("value", "")
            else:
                node_id = item.get("id")
                if node_id:
                    new_id = self._generate_node_id()
                    self.id_mapping[node_id] = new_id
                    item["_original_id"] = node_id
                    item["id"] = new_id
                    self.nodes[new_id] = item

        self._validate_links()

    def _generate_node_id(self):
        """生成符合规范的节点 ID (格式: n + 31位hex，总长度32)"""
        return "n{}".format(uuid.uuid4().hex[:31])

    def _validate_links(self):
        """校验所有 Link 引用的节点是否存在"""
        missing_nodes = set()
        for link in self.links:
            source = link.get("source")
            target = link.get("target")
            if source and source not in self.id_mapping:
                missing_nodes.add(source)
            if target and target not in self.id_mapping:
                missing_nodes.add(target)

        if missing_nodes:
            raise KeyError("Link 引用了未定义的节点: {}".format(", ".join(sorted(missing_nodes))))

    def _generate_flow_id(self):
        """生成 flow ID (格式: l + 30位hex)"""
        return "l{}".format(uuid.uuid4().hex[:30])

    def _map_id(self, old_id):
        """将旧 ID 映射为新 ID"""
        return self.id_mapping.get(old_id, old_id)

    def _wrap_data_value(self, value):
        """
        将简单值包装为标准运维要求的 object 格式

        标准运维要求 component data 中的每个字段都必须是包含
        hook、need_render、value 的对象格式

        :param value: 原始值（可能是简单值或已经是 object 格式）
        :return: 标准格式的对象
        """
        if isinstance(value, dict) and "hook" in value and "value" in value:
            return value

        return {"hook": False, "need_render": True, "value": value}

    def _normalize_component_data(self, data):
        """
        标准化 component data，将所有字段值转换为标准格式

        :param data: 原始 data 字典
        :return: 标准化后的 data 字典
        """
        if not isinstance(data, dict):
            return {}

        normalized = {}
        for key, value in data.items():
            normalized[key] = self._wrap_data_value(value)

        return normalized

    def _parse_version_number(self, version_str):
        """
        解析版本号字符串，返回可比较的元组

        支持格式: "1.0", "v1.0", "1.0.0", "v1.0.0", "legacy" 等

        :param version_str: 版本号字符串
        :return: (主版本号, 次版本号, 修订号) 元组，用于比较
        """
        if not version_str or version_str == "legacy":
            return (0, 0, 0)

        version_str = version_str.lstrip("vV")

        match = re.match(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", version_str)
        if match:
            major = int(match.group(1)) if match.group(1) else 0
            minor = int(match.group(2)) if match.group(2) else 0
            patch = int(match.group(3)) if match.group(3) else 0
            return (major, minor, patch)

        return (0, 0, 0)

    def _get_latest_component_version(self, code):
        """
        从数据库获取指定 component code 的最新版本

        :param code: 组件 code
        :return: 最新版本号字符串，如果找不到返回 "legacy"
        """
        if not code:
            return "legacy"

        try:
            versions = ComponentModel.objects.filter(code=code, status=1).values_list("version", flat=True)

            if not versions:
                logger.warning("_get_latest_component_version: No component found for code={}".format(code))
                return "legacy"

            latest_version = None
            latest_tuple = (0, 0, 0)

            for version in versions:
                version_tuple = self._parse_version_number(version)
                if version_tuple > latest_tuple:
                    latest_tuple = version_tuple
                    latest_version = version

            logger.info(
                "_get_latest_component_version: code={}, versions={}, latest={}".format(
                    code, list(versions), latest_version
                )
            )

            return latest_version or "legacy"

        except Exception as e:
            logger.exception("_get_latest_component_version: Error getting version for code={}: {}".format(code, e))
            return "legacy"

    def convert(self) -> dict:
        """
        执行转换，返回 pipeline_tree

        :return: 标准运维 pipeline_tree 格式的字典
        """
        activities = {}
        gateways = {}
        flows = {}
        constants = {}

        start_event = None
        end_event = None

        node_incoming = {nid: [] for nid in self.nodes}
        node_outgoing = {nid: [] for nid in self.nodes}

        source_to_flows = {nid: [] for nid in self.nodes}

        for link in self.links:
            source = self._map_id(link["source"])
            target = self._map_id(link["target"])
            flow_id = self._generate_flow_id()

            flows[flow_id] = {"id": flow_id, "is_default": False, "source": source, "target": target}

            if source in node_outgoing:
                node_outgoing[source].append(flow_id)
            if target in node_incoming:
                node_incoming[target].append(flow_id)

            if source in source_to_flows:
                original_target = link["target"]
                source_to_flows[source].append((flow_id, target, original_target))

        for node_id, node in self.nodes.items():
            node_type = node["type"]

            if node_type == "StartEvent":
                start_event = self._build_start_event(node, node_outgoing.get(node_id, []))
            elif node_type == "EndEvent":
                end_event = self._build_end_event(node, node_incoming.get(node_id, []))
            elif node_type == "Activity":
                activities[node_id] = self._build_activity(
                    node, node_incoming.get(node_id, []), node_outgoing.get(node_id, [])
                )
            elif node_type in ("ParallelGateway", "ConditionalParallelGateway", "ExclusiveGateway", "ConvergeGateway"):
                gateways[node_id] = self._build_gateway(
                    node,
                    node_incoming.get(node_id, []),
                    node_outgoing.get(node_id, []),
                    source_to_flows.get(node_id, []),
                )

        for idx, var in enumerate(self.variables):
            key = var.get("key")
            if not key:
                raise KeyError('Variable 缺少必填字段 \'key\'，请确保格式为: {"type": "Variable", "key": "${变量名}", "name": "显示名"}')
            constants[key] = self._build_constant(var, idx)

        return {
            "name": self.template_name,
            "template_id": "",
            "projectBaseInfo": self.PROJECT_BASE_INFO,
            "notify_receivers": {
                "receiver_group": [],
                "more_receiver": "",
                "extra_info": {},
            },
            "notify_type": {
                "success": [],
                "fail": [],
            },
            "time_out": 20,
            "category": "Default",
            "description": "",
            "executor_proxy": "",
            "init_executor_proxy": "",
            "template_labels": [],
            "subprocess_info": {
                "subproc_has_update": False,
                "details": [],
            },
            "internalVariable": self.INTERNAL_VARIABLE,
            "default_flow_type": "common",
            "webhook_configs": {},
            "enable_webhook": False,
            "activities": activities,
            "gateways": gateways,
            "flows": flows,
            "start_event": start_event,
            "end_event": end_event,
            "constants": constants,
            "outputs": [],
            "line": self._build_line_positions(flows),
            "location": self._build_node_positions(),
        }

    def _build_activity(self, node, incoming, outgoing) -> dict:
        """
        构建 Activity 节点

        :param node: 原始节点数据
        :param incoming: 入边列表
        :param outgoing: 出边列表
        :return: Activity 节点字典
        """
        outgoing_value = outgoing[0] if len(outgoing) == 1 else outgoing

        raw_data = node.get("data", {})
        normalized_data = self._normalize_component_data(raw_data)

        code = node.get("code", "")
        version = self._get_latest_component_version(code)

        activity = {
            "id": node["id"],
            "name": node.get("name", ""),
            "type": "ServiceActivity",
            "incoming": incoming,
            "outgoing": outgoing_value,
            "stage_name": node.get("stage_name", node.get("name", "")),
            "component": {
                "code": code,
                "version": version,
                "data": normalized_data,
            },
        }
        activity.update(self.DEFAULT_ACTIVITY_CONFIG)
        return activity

    def _build_gateway(self, node, incoming, outgoing, outgoing_flows=None) -> dict:
        """
        构建网关节点

        :param node: 原始节点数据
        :param incoming: 入边列表
        :param outgoing: 出边列表
        :param outgoing_flows: 出边流信息列表 [(flow_id, target_new_id, target_original_id), ...]
        :return: 网关节点字典
        """
        node_type = node["type"]
        outgoing_flows = outgoing_flows or []

        if node_type == "ConvergeGateway":
            outgoing_value = outgoing[0] if outgoing else ""
        else:
            outgoing_value = outgoing

        gateway = {
            "id": node["id"],
            "name": node.get("name", ""),
            "type": node_type,
            "incoming": incoming,
            "outgoing": outgoing_value,
        }

        if node_type == "ExclusiveGateway":
            gateway["conditions"] = self._build_gateway_conditions(node.get("conditions", {}), outgoing_flows)

        if node_type in ("ParallelGateway", "ConditionalParallelGateway"):
            converge_id = node.get("converge_gateway_id", "")
            if converge_id:
                converge_id = self._map_id(converge_id)
            gateway["converge_gateway_id"] = converge_id

        return gateway

    def _build_gateway_conditions(self, raw_conditions, outgoing_flows) -> dict:
        """
        构建网关 conditions，将原始 conditions 转换为标准格式

        标准运维要求 conditions 的 key 必须是 outgoing flow_id，
        且每个 condition 需要包含 evaluate、name、tag 字段

        :param raw_conditions: 原始 conditions
        :param outgoing_flows: 出边流信息列表 [(flow_id, target_new_id, target_original_id), ...]
        :return: 标准格式的 conditions 字典
        """
        if not raw_conditions or not outgoing_flows:
            conditions = {}
            for idx, (flow_id, target_new_id, target_original_id) in enumerate(outgoing_flows):
                conditions[flow_id] = {
                    "evaluate": "True",
                    "name": "分支{}".format(idx + 1),
                    "tag": "branch_{}".format(flow_id),
                }
            return conditions

        target_to_flow = {}
        for flow_id, target_new_id, target_original_id in outgoing_flows:
            target_to_flow[target_original_id] = flow_id
            target_to_flow[target_new_id] = flow_id

        conditions = {}
        used_flows = set()

        if isinstance(raw_conditions, list):
            condition_items = []
            for cond in raw_conditions:
                if isinstance(cond, dict):
                    target_key = cond.get("target") or cond.get("target_id") or cond.get("id")
                    condition_items.append((target_key, cond))
        else:
            condition_items = list(raw_conditions.items())

        for cond_key, cond_value in condition_items:
            flow_id = target_to_flow.get(cond_key) if cond_key else None

            if not flow_id:
                for fid, _, _ in outgoing_flows:
                    if fid not in used_flows:
                        flow_id = fid
                        break

            if flow_id:
                used_flows.add(flow_id)
                expression = (
                    cond_value.get("evaluate") or cond_value.get("expression") or cond_value.get("expr") or "True"
                )
                conditions[flow_id] = {
                    "evaluate": expression,
                    "name": cond_value.get("name", ""),
                    "tag": "branch_{}".format(flow_id),
                }

        for flow_id, _, _ in outgoing_flows:
            if flow_id not in conditions:
                conditions[flow_id] = {"evaluate": "True", "name": "", "tag": "branch_{}".format(flow_id)}

        return conditions

    def _build_start_event(self, node, outgoing) -> dict:
        """
        构建开始事件

        :param node: 原始节点数据
        :param outgoing: 出边列表
        :return: 开始事件字典
        """
        return {
            "id": node["id"],
            "name": node.get("name", ""),
            "type": "EmptyStartEvent",
            "incoming": "",
            "outgoing": outgoing[0] if outgoing else "",
        }

    def _build_end_event(self, node, incoming) -> dict:
        """
        构建结束事件

        :param node: 原始节点数据
        :param incoming: 入边列表
        :return: 结束事件字典
        """
        return {
            "id": node["id"],
            "name": node.get("name", ""),
            "type": "EmptyEndEvent",
            "incoming": incoming,
            "outgoing": "",
        }

    def _build_constant(self, var, index) -> dict:
        """
        构建常量/变量

        :param var: 原始变量数据
        :param index: 变量索引
        :return: 常量字典
        """
        return {
            "key": var["key"],
            "name": var.get("name", ""),
            "value": var.get("value", ""),
            "desc": var.get("description", ""),
            "custom_type": var.get("custom_type", "input"),
            "source_type": var.get("source_type", "custom"),
            "source_tag": "",
            "source_info": {},
            "show_type": var.get("show_type", "show"),
            "validation": var.get("validation", ""),
            "index": index,
            "version": "legacy",
            "form_schema": {},
            "hook": False,
            "need_render": True,
        }

    def _build_line_positions(self, flows) -> list:
        """
        构建连线位置信息

        :param flows: flows 字典
        :return: 连线位置列表
        """
        return [{"id": fid, "source": {"id": f["source"]}, "target": {"id": f["target"]}} for fid, f in flows.items()]

    def _map_node_type_for_canvas(self, node_type) -> str:
        """
        将节点类型映射为前端画布识别的类型

        :param node_type: 原始节点类型
        :return: 画布节点类型
        """
        type_mapping = {
            "StartEvent": "startpoint",
            "EndEvent": "endpoint",
            "Activity": "tasknode",
            "ParallelGateway": "parallelgateway",
            "ConditionalParallelGateway": "parallelgateway",
            "ConvergeGateway": "convergegateway",
            "ExclusiveGateway": "branchgateway",
        }
        return type_mapping.get(node_type, node_type)

    def _build_node_positions(self) -> list:
        """
        构建节点位置信息（自动布局）

        :return: 节点位置列表
        """
        locations = []
        x, y = 80, 150
        x_step = 200
        y_step = 150
        max_x = 1000

        for node_id, node in self.nodes.items():
            canvas_type = self._map_node_type_for_canvas(node["type"])
            location = {
                "id": node_id,
                "type": canvas_type,
                "name": node.get("name", ""),
                "stage_name": node.get("stage_name", node.get("name", "")),
                "x": x,
                "y": y,
            }

            if canvas_type == "tasknode":
                location.update(
                    {
                        "group": "",
                        "icon": "",
                        "optional": True,
                        "error_ignorable": False,
                        "retryable": True,
                        "skippable": True,
                        "auto_retry": {"enable": False, "interval": 0, "times": 1},
                        "timeout_config": {"action": "forced_fail", "enable": False, "seconds": 10},
                    }
                )

            locations.append(location)
            x += x_step
            if x > max_x:
                x = 80
                y += y_step

        return locations
