# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from pipeline.core.constants import PE

CANVAS_WIDTH = 1300
START_X = 60
START_Y = 100
EVENT_OR_GATEWAY_SHIFT_Y = 15
SHIFT_X = 180
SHIFT_Y = 120

PIPELINE_ELEMENT_TO_WEB = {
    PE.ServiceActivity: 'tasknode',
    PE.EmptyStartEvent: 'startpoint',
    PE.EmptyEndEvent: 'endpoint',
    PE.ExclusiveGateway: 'branchgateway',
    PE.ParallelGateway: 'parallelgateway',
    PE.ConvergeGateway: 'convergegateway'
}


def draw_branch_group(start_x, start_y, start_gateway, pipeline, all_nodes):
    """
    @summary: 绘制一个以分支/并行网关开始、以配对汇聚网关结束的多分支流程
    @return:
    """
    flows = pipeline['flows']
    location = [{
        'id': start_gateway[PE.id],
        'type': PIPELINE_ELEMENT_TO_WEB[start_gateway[PE.type]],
        'name': start_gateway[PE.name],
        'status': '',
        'x': start_x,
        'y': start_y + EVENT_OR_GATEWAY_SHIFT_Y,
    }]
    next_y = start_y
    line = []
    branch_next_x = []
    next_node = None
    for flow_index, flow_id in enumerate(start_gateway[PE.outgoing]):
        current_flow = flows[flow_id]
        next_node = all_nodes[current_flow[PE.target]]
        next_x = start_x + SHIFT_X
        # 第一个分支，和分支/并行网关横向排列
        if flow_index == 0:
            line.append({
                'id': current_flow[PE.id],
                'source': {
                    'id': current_flow[PE.source],
                    'arrow': 'Right'
                },
                'target': {
                    'id': current_flow[PE.target],
                    'arrow': 'Left'
                }
            })
        # 剩余分支，在分支/并行网关右下方排列
        else:
            line.append({
                'id': current_flow[PE.id],
                PE.source: {
                    'id': current_flow[PE.source],
                    'arrow': 'Bottom'
                },
                PE.target: {
                    'id': current_flow[PE.target],
                    'arrow': 'Left'
                }
            })

        # 当前分支绘制，直到遇到 start_gateway 匹配的汇聚网关
        while next_node[PE.type] != PE.ConvergeGateway:
            if next_node[PE.type] in [PE.ServiceActivity, PE.SubProcess]:
                # 把 next_node 加入 location，把 next_flow 加入line，然后把 next_node 设置为下一个节点
                location.append({
                    'id': next_node[PE.id],
                    'type': PIPELINE_ELEMENT_TO_WEB[next_node[PE.type]],
                    'name': next_node[PE.name],
                    'stage_name': next_node[PE.stage_name],
                    'status': '',
                    'x': next_x,
                    'y': next_y,
                })
                current_flow = flows[next_node[PE.outgoing]]
                line.append({
                    'id': current_flow[PE.id],
                    'source': {
                        'arrow': 'Right',
                        'id': current_flow[PE.source]
                    },
                    'target': {
                        'arrow': 'Left',
                        'id': current_flow[PE.target]
                    }
                })
                next_x += SHIFT_X
                next_node = all_nodes[current_flow[PE.target]]
            elif next_node[PE.type] in [PE.ParallelGateway, PE.ExclusiveGateway]:
                # 把并行/分支网关和配对的汇聚网关之间的节点加入 location（包含网关）、line（包含汇聚网关下一个节点）
                # 然后把 next_node 设置为汇聚网关下一个节点
                branch_location, branch_line, next_node, next_x, next_y = draw_branch_group(
                    next_x, next_y, next_node, pipeline, all_nodes)
                location += branch_location
                line += branch_line

        # 非首个分支，和网关的顺序流连线改为 Bottom
        if flow_index != 0:
            line[-1]['target']['arrow'] = 'Bottom'

        next_y += SHIFT_Y
        branch_next_x.append(next_x)

    # 最后加入汇聚网关节点和汇聚网关出度顺序流
    next_x = max(branch_next_x)
    location.append({
        'id': next_node[PE.id],
        'type': PIPELINE_ELEMENT_TO_WEB[next_node[PE.type]],
        'name': next_node[PE.name],
        'status': '',
        'x': next_x,
        'y': start_y + EVENT_OR_GATEWAY_SHIFT_Y,
    })
    current_flow = flows[next_node[PE.outgoing]]
    line.append({
        'id': current_flow[PE.id],
        'source': {
            'arrow': 'Right',
            'id': current_flow[PE.source]
        },
        'target': {
            'arrow': 'Left',
            'id': current_flow[PE.target]
        }
    })
    next_node = all_nodes[current_flow[PE.target]]
    next_x += SHIFT_X

    branch_max_y = next_y - SHIFT_Y
    return location, line, next_node, next_x, branch_max_y


def draw_pipeline_automatic(pipeline, start_x=START_X, start_y=START_Y, canvas_width=CANVAS_WIDTH):
    """
    @summary：将后台 pipeline tree 转换成带前端 location、line 画布信息的数据
    @param pipeline: 后台流程树
    @param start_x: 开始节点绝对定位X轴坐标
    @param start_y: 开始节点绝对定位轴坐标
    @param canvas_width: 画布最大宽度
    @return:
    """
    if canvas_width == 0:
        canvas_width = CANVAS_WIDTH

    all_nodes = {}
    all_nodes.update(pipeline['activities'])
    all_nodes.update(pipeline['gateways'])
    all_nodes.update({pipeline['start_event']['id']: pipeline['start_event']})
    all_nodes.update({pipeline['end_event']['id']: pipeline['end_event']})

    flows = pipeline['flows']
    start_node = pipeline['start_event']
    current_flow = flows[start_node['outgoing']]
    next_node = all_nodes[current_flow[PE.target]]
    next_x = start_x + SHIFT_X
    next_y = start_y

    location = [{
        'id': start_node[PE.id],
        'type': 'startpoint',
        'name': start_node[PE.name],
        'status': '',
        'x': start_x,
        'y': start_y + EVENT_OR_GATEWAY_SHIFT_Y,
    }]
    line = [{
        'id': current_flow[PE.id],
        'source': {
            'arrow': 'Right',
            'id': start_node[PE.id]
        },
        'target': {
            'arrow': 'Left',
            'id': next_node[PE.id]
        }
    }]

    branch_max_height = [next_y]
    while next_node[PE.type] != PE.EmptyEndEvent:
        # 宽度超出画布，换行处理
        if next_x > canvas_width - SHIFT_X:
            next_x = start_x
            next_y = max(branch_max_height) + SHIFT_Y
            # 换行的 line 设置最优折线比例，也就是下折线高度为 0.5 * SHIFT_Y
            line[-1]['midpoint'] = 1 - SHIFT_Y * 0.5 / (next_y - branch_max_height[0])
            branch_max_height = [next_y]
        # 重置为当前行第一个节点的 y 轴
        else:
            next_y = branch_max_height[0]
        if next_node[PE.type] in [PE.ServiceActivity, PE.SubProcess]:
            # 把 next_node 加入 location，把 next_flow 加入line，然后把 next_node 设置为下一个节点
            location.append({
                'id': next_node[PE.id],
                'type': PIPELINE_ELEMENT_TO_WEB[next_node[PE.type]],
                'name': next_node[PE.name],
                'stage_name': next_node[PE.stage_name],
                'status': '',
                'x': next_x,
                'y': next_y,
            })
            current_flow = flows[next_node[PE.outgoing]]
            line.append({
                'id': current_flow[PE.id],
                'source': {
                    'arrow': 'Right',
                    'id': current_flow[PE.source]
                },
                'target': {
                    'arrow': 'Left',
                    'id': current_flow[PE.target]
                }
            })
            next_x += SHIFT_X
            next_node = all_nodes[current_flow[PE.target]]
        elif next_node[PE.type] in [PE.ParallelGateway, PE.ExclusiveGateway]:
            # 把并行/分支网关和配对的汇聚网关之间的节点加入 location（包含网关）、line（包含汇聚网关下一个节点）
            # 然后把 next_node 设置为汇聚网关下一个节点
            branch_location, branch_line, next_node, next_x, next_y = draw_branch_group(
                next_x, next_y, next_node, pipeline, all_nodes)
            location += branch_location
            line += branch_line
            branch_max_height.append(next_y)

    # 最后加入结束节点
    location.append({
        'id': next_node[PE.id],
        'type': PIPELINE_ELEMENT_TO_WEB[next_node[PE.type]],
        'name': next_node[PE.name],
        'status': '',
        'x': next_x,
        'y': branch_max_height[0] + EVENT_OR_GATEWAY_SHIFT_Y,
    })

    pipeline.update({
        'location': location,
        'line': line,
    })
