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

import copy

from pipeline.core.constants import PE

CANVAS_WIDTH = 1300
POSITION = {
    'activity_size': (150, 42),
    'event_size': (42, 42),
    'gateway_size': (32, 32),
    'start': (60, 100)
}

PIPELINE_ELEMENT_TO_WEB = {
    PE.ServiceActivity: 'tasknode',
    PE.SubProcess: 'subflow',
    PE.EmptyStartEvent: 'startpoint',
    PE.EmptyEndEvent: 'endpoint',
    PE.ExclusiveGateway: 'branchgateway',
    PE.ParallelGateway: 'parallelgateway',
    PE.ConvergeGateway: 'convergegateway'
}


def draw_branch_group(start_x, start_y, start_gateway, shift_x, shift_y, gateway_shift_y, pipeline, all_nodes):
    """
    @summary: 绘制一个以分支/并行网关开始、以配对汇聚网关结束的多分支流程
    @param start_x: 起始网关绝对定位X轴坐标
    @param start_y: 起始网关绝对定位轴坐标
    @param start_gateway: 起始网关数据
    @param shift_x: 节点之间的平均X轴距离
    @param shift_y: 节点之间的平均Y轴距离
    @param gateway_shift_y: 网关节点相对任务节点的轴偏移
    @return:
    """
    old_locations = {location[PE.id]: location for location in pipeline.get('location', [])}
    flows = pipeline['flows']
    if start_gateway[PE.id] in old_locations:
        location_start = copy.deepcopy(old_locations[start_gateway[PE.id]])
        location_start.update({
            'x': start_x,
            'y': start_y + gateway_shift_y,
        })
        location = [location_start]
    else:
        location = [{
            'id': start_gateway[PE.id],
            'type': PIPELINE_ELEMENT_TO_WEB[start_gateway[PE.type]],
            'name': start_gateway[PE.name],
            'status': '',
            'x': start_x,
            'y': start_y + gateway_shift_y,
        }]
    next_y = start_y
    line = []
    branch_next_x = []
    next_node = None
    for flow_index, flow_id in enumerate(start_gateway[PE.outgoing]):
        current_flow = flows[flow_id]
        next_node = all_nodes[current_flow[PE.target]]
        next_x = start_x + shift_x
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
            if next_node[PE.type] in PE.TaskNodes:
                # 把 next_node 加入 location，把 next_flow 加入line，然后把 next_node 设置为下一个节点
                if next_node[PE.id] in old_locations:
                    location_next = copy.deepcopy(old_locations[next_node[PE.id]])
                    location_next.update({
                        'x': next_x,
                        'y': next_y,
                    })
                    location.append(location_next)
                else:
                    location.append({
                        'id': next_node[PE.id],
                        'type': PIPELINE_ELEMENT_TO_WEB[next_node[PE.type]],
                        'name': next_node[PE.name],
                        'stage_name': next_node.get(PE.stage_name),
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
                next_x += shift_x
                next_node = all_nodes[current_flow[PE.target]]
            elif next_node[PE.type] in PE.BranchGateways:
                # 把并行/分支网关和配对的汇聚网关之间的节点加入 location（包含网关）、line（包含汇聚网关下一个节点）
                # 然后把 next_node 设置为汇聚网关下一个节点
                branch_location, branch_line, next_node, next_x, next_y = draw_branch_group(
                    next_x, next_y, next_node, shift_x, shift_y, gateway_shift_y, pipeline, all_nodes)
                location += branch_location
                line += branch_line

        # 非首个分支，和网关的顺序流连线改为 Bottom
        if flow_index != 0:
            line[-1]['target']['arrow'] = 'Bottom'

        next_y += shift_y
        branch_next_x.append(next_x)

    # 最后加入汇聚网关节点和汇聚网关出度顺序流
    next_x = max(branch_next_x)
    if next_node[PE.id] in old_locations:
        location_next = copy.deepcopy(old_locations[next_node[PE.id]])
        location_next.update({
            'x': next_x,
            'y': start_y + gateway_shift_y,
        })
        location.append(location_next)
    else:
        location.append({
            'id': next_node[PE.id],
            'type': PIPELINE_ELEMENT_TO_WEB[next_node[PE.type]],
            'name': next_node[PE.name],
            'status': '',
            'x': next_x,
            'y': start_y + gateway_shift_y,
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
    next_x += shift_x

    branch_max_y = next_y - shift_y
    return location, line, next_node, next_x, branch_max_y


def draw_pipeline(pipeline, activity_size=POSITION['activity_size'], event_size=POSITION['event_size'],
                  gateway_size=POSITION['gateway_size'], start=POSITION['start'], canvas_width=CANVAS_WIDTH):
    """
    @summary：将后台 pipeline tree 转换成带前端 location、line 画布信息的数据
    @param pipeline: 后台流程树
    @param activity_size: 任务节点长宽，如 (150, 42)
    @param event_size: 事件节点长宽，如 (40, 40)
    @param gateway_size: 网关节点长宽，如 (36, 36)
    @param start: 开始节点绝对定位X、Y轴坐标
    @param canvas_width: 画布最大宽度
    @return:
    """
    all_nodes = {}
    all_nodes.update(pipeline['activities'])
    all_nodes.update(pipeline['gateways'])
    all_nodes.update({pipeline['start_event']['id']: pipeline['start_event']})
    all_nodes.update({pipeline['end_event']['id']: pipeline['end_event']})
    start_x, start_y = start

    # 节点之间的平均距离
    shift_x = max(activity_size[0], event_size[0], gateway_size[0]) * 1.2
    shift_y = max(activity_size[1], event_size[1], gateway_size[1]) * 2
    # 开始/结束事件节点纵坐标偏差
    event_shift_y = (activity_size[1] - event_size[1]) * 0.5
    gateway_shift_y = (activity_size[1] - gateway_size[1]) * 0.5

    flows = pipeline['flows']
    start_node = pipeline['start_event']
    current_flow = flows[start_node['outgoing']]
    next_node = all_nodes[current_flow[PE.target]]
    next_x = start_x + shift_x
    next_y = start_y

    old_locations = {location[PE.id]: location for location in pipeline.get('location', [])}
    if start_node[PE.id] in old_locations:
        location_start = copy.deepcopy(old_locations[start_node[PE.id]])
        location_start.update({
            'x': start_x,
            'y': start_y + event_shift_y,
        })
        location = [location_start]
    else:
        location = [{
            'id': start_node[PE.id],
            'type': 'startpoint',
            'name': start_node[PE.name],
            'status': '',
            'x': start_x,
            'y': start_y + event_shift_y,
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
        if next_x > canvas_width - shift_x:
            next_x = start_x
            next_y = max(branch_max_height) + shift_y
            # 换行的 line 设置最优折线比例，也就是下折线高度为 0.5 * shift_y
            line[-1]['midpoint'] = 1 - shift_y * 0.5 / (next_y - branch_max_height[0])
            branch_max_height = [next_y]
        # 重置为当前行第一个节点的 y 轴
        else:
            next_y = branch_max_height[0]
        if next_node[PE.type] in PE.TaskNodes:
            # 把 next_node 加入 location，把 next_flow 加入line，然后把 next_node 设置为下一个节点
            if next_node[PE.id] in old_locations:
                location_next = copy.deepcopy(old_locations[next_node[PE.id]])
                location_next.update({
                    'x': next_x,
                    'y': next_y,
                })
                location.append(location_next)
            else:
                location.append({
                    'id': next_node[PE.id],
                    'type': PIPELINE_ELEMENT_TO_WEB[next_node[PE.type]],
                    'name': next_node[PE.name],
                    'stage_name': next_node.get(PE.stage_name),
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
            next_x += shift_x
            next_node = all_nodes[current_flow[PE.target]]
        elif next_node[PE.type] in PE.BranchGateways:
            # 把并行/分支网关和配对的汇聚网关之间的节点加入 location（包含网关）、line（包含汇聚网关下一个节点）
            # 然后把 next_node 设置为汇聚网关下一个节点
            branch_location, branch_line, next_node, next_x, next_y = draw_branch_group(
                next_x, next_y, next_node, shift_x, shift_y, gateway_shift_y, pipeline, all_nodes)
            location += branch_location
            line += branch_line
            branch_max_height.append(next_y)

    # 最后加入结束节点
    if next_node[PE.id] in old_locations:
        location_next = copy.deepcopy(old_locations[next_node[PE.id]])
        location_next.update({
            'x': next_x,
            'y': branch_max_height[0] + event_shift_y,
        })
        location.append(location_next)
    else:
        location.append({
            'id': next_node[PE.id],
            'type': PIPELINE_ELEMENT_TO_WEB[next_node[PE.type]],
            'name': next_node[PE.name],
            'status': '',
            'x': next_x,
            'y': branch_max_height[0] + event_shift_y,
        })

    pipeline.update({
        'location': location,
        'line': line,
    })
