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

    def clean(self):
        # clean labels
        nodes_attr = {}
        all_nodes = get_all_nodes(self.pipeline_tree)
        for node_id, node in all_nodes.items():
            attr = node.pop(PWE.labels, None)
            if attr:
                nodes_attr.setdefault(node_id, {}).update({PWE.labels: attr})
        return nodes_attr

    def to_web(self, nodes_attr):
        all_nodes = get_all_nodes(self.pipeline_tree)
        for node_id, node in all_nodes.items():
            node.update(nodes_attr.get(node_id, {}))
