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
import re
from collections import defaultdict

from pipeline.exceptions import PipelineException

logger = logging.getLogger("root")


def validate_pipeline_tree_constants(constants):
    """
    校验流水线常量定义，禁止自引用和循环引用
    Args:
        constants: 待校验的参数字典，格式为 {参数名: 参数值或参数字典}
    Returns:
        校验通过的参数字典
    Raises:
        PipelineException: 当检测到自引用或循环引用时抛出
    """
    validation_errors = []

    graph = defaultdict(set)
    constant_values = {}

    # 首先构建参数值映射表
    for key, const in constants.items():
        value = const.get("value") if isinstance(const, dict) else const
        constant_values[key] = str(value) if value is not None else ""

    # 构建依赖关系图
    for key, value in constant_values.items():
        if not value:
            continue

        # 检查当前参数值中引用的所有参数
        referenced_keys = set()
        for other_key in constant_values:
            if re.search(re.escape(other_key), value):
                referenced_keys.add(other_key)

        # 分离出自引用和其他引用
        if key in referenced_keys:
            validation_errors.append(key)
            referenced_keys.remove(key)

        # 记录非自引用的依赖关系
        if referenced_keys:
            graph[key] = referenced_keys

    # 如果发现自引用立即报错
    if validation_errors:
        error_message = "常量 {} 的值不能引用自身作为值".format(", ".join(validation_errors))
        logger.error(error_message)
        raise PipelineException(error_message)

    visited = set()
    recursion_stack = []

    def has_cycle(node):
        """深度优先搜索检测环路"""
        visited.add(node)
        recursion_stack.append(node)

        # 遍历当前节点的所有依赖项
        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in recursion_stack:
                return True

        recursion_stack.remove(node)
        return False

    # 对每个未访问的节点进行检查
    for node in graph:
        if node not in visited and has_cycle(node):
            # 记录环路涉及到的节点
            error_message = "检测到常量{}存在循环引用".format(", ".join(recursion_stack))
            logger.error(error_message)
            raise PipelineException(error_message)

    return constants
