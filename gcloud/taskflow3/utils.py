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
import typing
from collections import defaultdict
from typing import Any, Dict, List, Optional

from django.apps import apps
from django.utils.translation import ugettext_lazy as _
from pipeline.core import constants as pipeline_constants
from pipeline.engine import states as pipeline_states
from pipeline.engine.utils import calculate_elapsed_time

from gcloud.constants import TaskExtraStatus
from gcloud.utils.dates import format_datetime

logger = logging.getLogger("root")


def _format_status_time(status_tree):
    status_tree.setdefault("children", {})
    status_tree.pop("created_time", "")
    started_time = status_tree.pop("started_time", None)
    archived_time = status_tree.pop("archived_time", None)

    if "elapsed_time" not in status_tree:
        status_tree["elapsed_time"] = calculate_elapsed_time(started_time, archived_time)

    status_tree["start_time"] = format_datetime(started_time) if started_time else None
    status_tree["finish_time"] = format_datetime(archived_time) if archived_time else None


def format_pipeline_status(status_tree):
    """
    @summary: 转换通过 pipeline api 获取的任务状态格式
    @return:
    """
    _format_status_time(status_tree)
    child_status = set()
    # engine v1 v2 响应保持一致
    if ("error_ignorable" in status_tree) and ("error_ignored" not in status_tree):
        status_tree["error_ignored"] = status_tree["error_ignorable"]

    for identifier_code, child_tree in list(status_tree["children"].items()):
        format_pipeline_status(child_tree)
        child_status.add(child_tree["state"])

    if status_tree["state"] == pipeline_states.BLOCKED:
        if pipeline_states.RUNNING in child_status:
            status_tree["state"] = pipeline_states.RUNNING
        elif pipeline_states.FAILED in child_status:
            status_tree["state"] = pipeline_states.FAILED
        elif pipeline_states.SUSPENDED in child_status or TaskExtraStatus.NODE_SUSPENDED.value in child_status:
            status_tree["state"] = TaskExtraStatus.NODE_SUSPENDED.value
        # 子流程 BLOCKED 状态表示子节点失败
        elif not child_status:
            status_tree["state"] = pipeline_states.FAILED


def find_nodes_from_pipeline_tree(
    pipeline_tree: typing.Dict[str, typing.Any], codes: typing.Iterable[str]
) -> typing.Dict[str, typing.List[typing.Dict[str, typing.Any]]]:
    """
    在 pipeline tree 查找指定的 Component codes
    :param pipeline_tree:
    :param codes:
    :return:
    """
    # 转 set 去重，提高 in 查找效率
    codes: typing.Set[str] = set(codes)
    node_infos_gby_code: typing.Dict[str, typing.List[typing.Dict[str, typing.Any]]] = defaultdict(list)
    if not codes:
        raise ValueError("Empty codes")
    for act_id, act in pipeline_tree[pipeline_constants.PE.activities].items():
        if act["type"] == pipeline_constants.PE.SubProcess:
            # 非独立子流程继续递归查找
            child_node_infos_gby_code: typing.Dict[
                str, typing.List[typing.Dict[str, typing.Any]]
            ] = find_nodes_from_pipeline_tree(act[pipeline_constants.PE.pipeline], codes)
            # 子树查找结果同父流程合并
            for code in codes:
                node_infos_gby_code[code].extend(child_node_infos_gby_code.get(code) or [])
        elif act["type"] == pipeline_constants.PE.ServiceActivity:
            code_or_none: typing.Optional[str] = act.get(pipeline_constants.PE.component, {}).get(
                pipeline_constants.PE.code
            )
            if code_or_none and code_or_none in codes:
                # 使用 Dict 结构，便于后续扩展更多需要的字段
                node_infos_gby_code[code_or_none].append({"act_id": act_id})
    return node_infos_gby_code


def add_node_name_to_status_tree(pipeline_tree, status_tree_children):
    for node_id, status in status_tree_children.items():
        status["name"] = pipeline_tree.get("activities", {}).get(node_id, {}).get("name", "")
        children = status.get("children", {})
        add_node_name_to_status_tree(pipeline_tree.get("activities", {}).get(node_id, {}).get("pipeline", {}), children)


def extract_nodes_by_statuses(status_tree: Dict, statuses: Optional[List[str]] = None) -> List[str]:
    """
    在状态树中获取指定状态的节点 ID 列表
    :param status_tree:
    :param statuses: 为空取任意状态
    :return:
    """
    nodes: List[str] = []
    for node_id, status in status_tree["children"].items():
        if not statuses or status["state"] in statuses:
            nodes.append(node_id)
            nodes += extract_nodes_by_statuses(status, statuses)
    return nodes


def get_failed_nodes_info(root_pipeline_id, failed_node_ids):
    info = {failed_node_id: {} for failed_node_id in failed_node_ids}

    for node_id, auto_retry_info in fetch_node_id__auto_retry_info_map(root_pipeline_id, failed_node_ids).items():
        info[node_id].update(auto_retry_info)

    return info


def fetch_node_id__auto_retry_info_map(root_pipeline_id, node_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """获取指定节点ID列表的自动重试配置信息"""
    node_id__auto_retry_info_map: Dict[str, Dict[str, Any]] = {}
    AutoRetryNodeStrategy = apps.get_model("taskflow3", "AutoRetryNodeStrategy")
    strategy_info = AutoRetryNodeStrategy.objects.filter(
        root_pipeline_id=root_pipeline_id, node_id__in=node_ids
    ).values("node_id", "retry_times", "max_retry_times")

    for strategy in strategy_info:
        node_id__auto_retry_info_map[strategy["node_id"]] = {
            "node_id": strategy["node_id"],
            "auto_retry_times": strategy["retry_times"],
            "max_auto_retry_times": strategy["max_retry_times"],
        }
    return node_id__auto_retry_info_map


def parse_node_timeout_configs(pipeline_tree: dict) -> list:
    configs = []
    for act_id, act in pipeline_tree[pipeline_constants.PE.activities].items():
        if act["type"] == pipeline_constants.PE.SubProcess:
            result = parse_node_timeout_configs(act[pipeline_constants.PE.pipeline])
            if not result["result"]:
                return result
            configs.extend(result["data"])
        elif act["type"] == pipeline_constants.PE.ServiceActivity:
            timeout_config = act.get("timeout_config", {})
            enable = timeout_config.get("enable")
            if not enable:
                continue
            timeout_seconds = timeout_config.get("seconds")
            action = timeout_config.get("action")
            if not timeout_seconds or not isinstance(timeout_seconds, int):
                message = _(
                    f"节点执行失败: 节点[ID: {act_id}]配置了非法的超时时间: {timeout_seconds}, 请修改配置后重试 | parse_node_timeout_configs"
                )
                logger.error(message)
                # 对于不符合格式要求的情况，则不设置对应超时时间
                continue
            configs.append({"action": action, "node_id": act_id, "timeout": timeout_seconds})
    return {"result": True, "data": configs, "message": ""}
