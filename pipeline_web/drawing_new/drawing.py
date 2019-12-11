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

from pipeline_web.drawing_new.constants import POSITION, CANVAS_WIDTH
from pipeline_web.drawing_new import (
    normalize,
    acyclic,
    position
)
from pipeline_web.drawing_new.rank import tight_tree
from pipeline_web.drawing_new.order import order
from pipeline_web.drawing_new.dummy import (
    replace_long_path_with_dummy,
    remove_dummy
)


def draw_pipeline(pipeline,
                  activity_size=POSITION['activity_size'],
                  event_size=POSITION['event_size'],
                  gateway_size=POSITION['gateway_size'],
                  start=POSITION['start'],
                  canvas_width=CANVAS_WIDTH):
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
    # 数据格式化
    normalize.normalize_run(pipeline)
    # 删除自环边
    self_edges = acyclic.remove_self_edges(pipeline)
    # 逆转反向边
    reversed_flows = acyclic.acyclic_run(pipeline)
    # 使用紧凑树算法分配rank
    ranks = tight_tree.tight_tree_ranker(pipeline)
    # 使用虚拟节点替换长度大于 MIN_LEN 的边
    real_flows_chain = replace_long_path_with_dummy(pipeline, ranks)
    # 使用中位数法分配层级内节点顺序，使交叉最小
    orders = order.ordering(pipeline, ranks)
    # 还原自环边
    acyclic.insert_self_edges(pipeline, self_edges)
    # 根据 orders 分配位置，注意 real_flows_chain 中可能包含 reversed_flows 的 flow_id，即被反向过的边恰好是长边
    # 所以需要使用 reversed_flows 覆盖 real_flows_chain
    more_flows = {}
    more_flows.update(real_flows_chain)
    more_flows.update(reversed_flows)
    locations, lines = position.position(pipeline=pipeline,
                                         orders=orders,
                                         activity_size=activity_size,
                                         event_size=event_size,
                                         gateway_size=gateway_size,
                                         start=start,
                                         canvas_width=canvas_width,
                                         more_flows=more_flows)
    # 删除虚拟节点并恢复长边
    remove_dummy(pipeline, real_flows_chain, dummy_nodes_included=[locations], dummy_flows_included=[lines])
    # 恢复反向边
    acyclic.acyclic_undo(pipeline, reversed_flows)
    # 数据格式还原
    normalize.normalize_undo(pipeline)
    # 添加画布信息
    pipeline.update({
        'location': list(locations.values()),
        'line': list(lines.values())
    })
