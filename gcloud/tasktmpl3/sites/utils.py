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


def draw_pipeline_automatic(pipeline):
    line = []
    for flow_id, flow in pipeline['flows'].iteritems():
        line.append({
            "source": {
                "id": flow['source'],
                "arrow": "Right"
            },
            "id": flow_id,
            "target": {
                "id": flow['target'],
                "arrow": "Left"
            }
        })

    # TODO： 兼容多层嵌套和子流程
    acts = {}
    acts.update(pipeline['activities'])
    acts.update(pipeline['gateways'])
    acts.update({pipeline['end_event']['id']: pipeline['end_event']})

    flows = pipeline['flows']
    point_shift_y = 20
    gateway_shift_y = 18
    start_point_x = 60
    shift_x = 180
    shift_y = 140
    last_node = pipeline['start_event']
    last_node_x = 60
    last_node_y = 280
    current_flow = flows[last_node['outgoing']]

    location = [{
        'id': pipeline['start_event']['id'],
        'type': 'startpoint',
        'name': pipeline['start_event']['name'],
        'status': '',
        'x': start_point_x,
        'y': last_node_y + point_shift_y,
    }]

    while current_flow['target'] != pipeline['end_event']['id']:
        current_node = acts[current_flow['target']]
        if current_node['type'] == 'ServiceActivity':
            location.append({
                'id': current_node['id'],
                'type': 'tasknode',
                'name': current_node['name'],
                'stage_name': current_node.get('stage_name', ''),
                'status': '',
                'x': last_node_x + shift_x,
                'y': last_node_y,
            })
            last_node = current_node
            last_node_x = last_node_x + shift_x
            current_flow = flows[last_node['outgoing']]
        elif current_node['type'] == 'ParallelGateway':
            location.append({
                'id': current_node['id'],
                'type': 'parallelgateway',
                'name': current_node['name'],
                'status': '',
                'x': last_node_x + shift_x,
                'y': last_node_y + gateway_shift_y,
            })
            last_node_x = last_node_x + shift_x
            for index, flow_id in enumerate(current_node['outgoing']):
                parallel_flow = flows[flow_id]
                current_node = acts[parallel_flow['target']]
                location.append({
                    'id': current_node['id'],
                    'type': 'tasknode',
                    'name': current_node['name'],
                    'stage_name': current_node.get('stage_name', ''),
                    'status': '',
                    'x': last_node_x + shift_x,
                    # 第一个分支和网关对齐，剩余分支依次先下后上均匀分布两侧
                    'y': last_node_y + (-1) ** index * ((index + 1) / 2) * shift_y,
                })
            last_node = current_node
            last_node_x = last_node_x + shift_x
            current_flow = flows[last_node['outgoing']]
        elif current_node['type'] == 'ConvergeGateway':
            location.append({
                'id': current_node['id'],
                'type': 'convergegateway',
                'name': current_node['name'],
                'status': '',
                'x': last_node_x + shift_x,
                'y': last_node_y + gateway_shift_y,
            })
            last_node = current_node
            last_node_x = last_node_x + shift_x
            current_flow = flows[last_node['outgoing']]

    current_node = acts[current_flow['target']]
    location.append({
        'id': current_node['id'],
        'type': 'endpoint',
        'name': current_node['name'],
        'status': '',
        'x': last_node_x + shift_x,
        'y': last_node_y + point_shift_y,
    })

    pipeline.update({
        'location': location,
        'line': line,
    })
    return pipeline
