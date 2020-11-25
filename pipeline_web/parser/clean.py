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

from pipeline_web.constants import PWE
from pipeline_web.parser.format import get_all_nodes


class PipelineWebTreeCleaner(object):
    """
    @summary: pipeline tree 数据清洗
    """
    def __init__(self, pipeline_tree):
        self.origin_data = copy.deepcopy(pipeline_tree)
        self.pipeline_tree = pipeline_tree

    def clean(self, pipeline_tree=None, with_subprocess=False):
        """
        @summary: 清理 pipeline_tree 的节点部分上层属性，独立存储
        @param pipeline_tree:
        @param with_subprocess: 是否递归清理子流程中
        @return:
        """
        nodes_attr = {}
        if pipeline_tree is None:
            pipeline_tree = self.pipeline_tree
        all_nodes = get_all_nodes(pipeline_tree)
        for node_id, node in all_nodes.items():
            attr = node.pop(PWE.labels, None)
            if attr:
                nodes_attr.setdefault(node_id, {}).update({PWE.labels: attr})
            if with_subprocess and node[PWE.type] == PWE.SubProcess:
                sub_pipeline_tree = node[PWE.pipeline]
                nodes_attr.setdefault(PWE.subprocess_detail, {})
                nodes_attr[PWE.subprocess_detail].update({
                    node_id: self.clean(pipeline_tree=sub_pipeline_tree, with_subprocess=with_subprocess)
                })
        return nodes_attr

    @classmethod
    def replace_id(cls, nodes_attr, nodes_id_maps, with_subprocess=False):
        """
        @summary: 节点属性集合按照节点ID映射，返回新ID的节点属性结合
        @param nodes_attr:
        @param nodes_id_maps:
        @param with_subprocess: 是否递归处理子流程中
        @return:
        """
        new_nodes_attr = {}
        activities_id_maps = nodes_id_maps[PWE.activities]
        subprocess_detail = nodes_attr.pop(PWE.subprocess_detail, {})
        for node_id, attr in nodes_attr.items():
            new_node_id = activities_id_maps[node_id]
            new_nodes_attr.update({new_node_id: attr})

        if with_subprocess:
            for node_id, sub_nodes_attr in subprocess_detail.items():
                new_node_id = activities_id_maps[node_id]
                sub_nodes_id_maps = nodes_id_maps[PWE.subprocess_detail][new_node_id]
                new_nodes_attr.setdefault(PWE.subprocess_detail, {}).update({
                    new_node_id: cls.replace_id(sub_nodes_attr, sub_nodes_id_maps)
                })
        return new_nodes_attr

    def to_web(self, nodes_attr, pipeline_tree=None, with_subprocess=False):
        """
        @summary: 将独立存储的节点属性还原到任务树中
        @param nodes_attr: 有两种格式，一种是平铺的（适合所有流程节点全局ID唯一，例如任务实例），另一种是子流程属性集合包含在
            subprocess_detail 中（适合所有流程节点全局ID不唯一，例如展开子流程树的流程模板）
        @param pipeline_tree:
        @param with_subprocess: 是否递归处理子流程中
        @return:
        """
        if pipeline_tree is None:
            pipeline_tree = self.pipeline_tree
        all_nodes = get_all_nodes(pipeline_tree, with_subprocess)
        for node_id, node in all_nodes.items():
            node.update(nodes_attr.get(node_id, {}))

        if with_subprocess:
            subprocess_detail = nodes_attr.pop(PWE.subprocess_detail, {})
            for node_id, sub_nodes_attr in subprocess_detail.items():
                sub_pipeline_tree = pipeline_tree[PWE.activities][node_id][PWE.pipeline]
                self.to_web(sub_nodes_attr, pipeline_tree=sub_pipeline_tree, with_subprocess=with_subprocess)
