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

from pipeline.engine import states as pipeline_states
from pipeline.engine.utils import calculate_elapsed_time
from bamboo_engine import states as bamboo_engine_states

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
        elif pipeline_states.SUSPENDED in child_status or "NODE_SUSPENDED" in child_status:
            status_tree["state"] = "NODE_SUSPENDED"
        # 子流程 BLOCKED 状态表示子节点失败
        elif not child_status:
            status_tree["state"] = pipeline_states.FAILED


def format_bamboo_engine_status(status_tree):
    """
    @summary: 转换通过 bamboo engine api 获取的任务状态格式
    @return:
    """
    _format_status_time(status_tree)
    child_status = set()
    for identifier_code, child_tree in list(status_tree["children"].items()):
        format_bamboo_engine_status(child_tree)
        child_status.add(child_tree["state"])

    if status_tree["state"] == bamboo_engine_states.RUNNING:
        if bamboo_engine_states.FAILED in child_status:
            status_tree["state"] = bamboo_engine_states.FAILED
        elif bamboo_engine_states.SUSPENDED in child_status or "NODE_SUSPENDED" in child_status:
            status_tree["state"] = "NODE_SUSPENDED"


def add_node_name_to_status_tree(pipeline_tree, status_tree_children):
    for node_id, status in status_tree_children.items():
        status["name"] = pipeline_tree.get("activities", {}).get(node_id, {}).get("name", "")
        children = status.get("children", {})
        add_node_name_to_status_tree(pipeline_tree["activities"].get(node_id, {}).get("pipeline", {}), children)
