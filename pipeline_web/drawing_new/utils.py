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

from pipeline_web.constants import PWE


def format_pipeline_node_types(pipeline):
    node_types = {pipeline[PWE.start_event][PWE.id]: PWE.start_event, pipeline[PWE.end_event][PWE.id]: PWE.end_event}
    for act_id in pipeline[PWE.activities].keys():
        node_types[act_id] = PWE.activities
    for gw_id in pipeline[PWE.gateways].keys():
        node_types[gw_id] = PWE.gateways
    return node_types


def add_flow_id_to_node_io(node, flow_id, io_type):
    if isinstance(node[io_type], list):
        node[io_type].append(flow_id)
    elif node[io_type]:
        node[io_type] = [node[io_type], flow_id]
    else:
        node[io_type] = flow_id


def delete_flow_id_from_node_io(node, flow_id, io_type):
    if node[io_type] == flow_id:
        node[io_type] = ""
    elif isinstance(node[io_type], list):
        if len(node[io_type]) == 1 and node[io_type][0] == flow_id:
            node[io_type] = (
                ""
                if node[PWE.type] not in [PWE.ExclusiveGateway, PWE.ParallelGateway, PWE.ConditionalParallelGateway]
                else []
            )
        else:
            node[io_type].pop(node[io_type].index(flow_id))

            # recover to original format
            if (
                len(node[io_type]) == 1
                and io_type == PWE.outgoing
                and node[PWE.type] in [PWE.EmptyStartEvent, PWE.ServiceActivity, PWE.ConvergeGateway]
            ):
                node[io_type] = node[io_type][0]
