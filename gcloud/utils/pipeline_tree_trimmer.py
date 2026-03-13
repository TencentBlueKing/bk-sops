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

pipeline_tree MCP 响应裁剪模块

对 pipeline_tree 执行结构化裁剪：移除前端渲染、画布布局、冗余元数据等字段，
保留 Skill 所需的全部语义信息。

裁剪规则：
- Activities: 白名单保留核心字段，SubProcess 递归裁剪
- Component.data: hook 解包 + 空值移除 + 黑名单过滤
- Gateways: 白名单保留
- Flows: 仅保留 source/target/is_default
- Events: 仅保留 id/type/name
- Constants: 白名单保留 + 空值过滤
- 顶层 line/location: 移除
"""

_ACTIVITY_KEEP = {
    "id",
    "type",
    "name",
    "component",
    "pipeline",
    "stage_name",
    "retryable",
    "skippable",
    "error_ignorable",
    "auto_retry",
    "source_info",
}
_SUBPROCESS_EXTRA = {"template_id", "template_source", "version", "hooked_constants"}

_GATEWAY_KEEP = {"id", "type", "name", "conditions", "default_condition", "converge_gateway_id"}

_CONSTANT_KEEP = {"key", "name", "desc", "source_type", "custom_type", "value", "source_tag", "source_info"}

_DATA_FIELD_BLACKLIST = {
    "button_refresh",
    "button_refresh_2",
    "button_refresh_3",
    "ip_is_exist",
    "is_tagged_ip",
    "need_log_outputs_even_fail",
    "job_rolling_config",
    "\u00a9",
}


def trim_pipeline_tree(pipeline_tree):
    if not isinstance(pipeline_tree, dict):
        return pipeline_tree
    return _trim_tree(pipeline_tree)


def _trim_tree(tree):
    result = {}
    for key, val in tree.items():
        if key in ("line", "location"):
            continue
        if key == "activities" and isinstance(val, dict):
            result[key] = _trim_activities(val)
        elif key == "gateways" and isinstance(val, dict):
            result[key] = _trim_gateways(val)
        elif key == "flows" and isinstance(val, dict):
            result[key] = _trim_flows(val)
        elif key in ("start_event", "end_event") and isinstance(val, dict):
            result[key] = _trim_event(val)
        elif key == "constants" and isinstance(val, dict):
            result[key] = _trim_constants(val)
        else:
            result[key] = val
    return result


def _trim_activities(activities):
    trimmed = {}
    for act_id, act in activities.items():
        is_subprocess = act.get("type") == "SubProcess"
        keep = _ACTIVITY_KEEP | _SUBPROCESS_EXTRA if is_subprocess else _ACTIVITY_KEEP
        node = {}
        for field, val in act.items():
            if field not in keep:
                continue
            if field == "pipeline" and isinstance(val, dict):
                val = _trim_tree(val)
            elif field == "component" and isinstance(val, dict):
                val = _trim_component(val)
            node[field] = val
        trimmed[act_id] = node
    return trimmed


def _trim_component(component):
    result = {"code": component.get("code", "")}
    if "version" in component:
        result["version"] = component["version"]
    if "data" in component and isinstance(component["data"], dict):
        result["data"] = _trim_component_data(component["data"])
    return result


def _trim_component_data(data):
    result = {}
    for field_name, field_val in data.items():
        if field_name in _DATA_FIELD_BLACKLIST:
            continue
        val = _unwrap_hook(field_val)
        if _is_empty(val):
            continue
        result[field_name] = val
    return result


def _unwrap_hook(val):
    if isinstance(val, dict) and "value" in val and "hook" in val:
        return val["value"]
    return val


def _is_empty(val):
    return val == "" or val == [] or val == {} or val is None


def _trim_gateways(gateways):
    return {gw_id: {k: v for k, v in gw.items() if k in _GATEWAY_KEEP} for gw_id, gw in gateways.items()}


def _trim_flows(flows):
    trimmed = {}
    for fl_id, fl in flows.items():
        if "source" not in fl or "target" not in fl:
            continue
        entry = {"source": fl["source"], "target": fl["target"]}
        if fl.get("is_default"):
            entry["is_default"] = True
        trimmed[fl_id] = entry
    return trimmed


def _trim_event(event):
    return {
        "id": event.get("id", ""),
        "type": event.get("type", ""),
        "name": event.get("name", ""),
    }


def _trim_constants(constants):
    trimmed = {}
    for key, const in constants.items():
        if isinstance(const, dict):
            entry = {}
            for field, val in const.items():
                if field not in _CONSTANT_KEEP:
                    continue
                if field == "value":
                    val = _unwrap_hook(val)
                if _is_empty(val):
                    continue
                entry[field] = val
            trimmed[key] = entry
        else:
            trimmed[key] = const
    return trimmed
