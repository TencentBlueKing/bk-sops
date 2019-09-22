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
from gcloud.core.constant import AE
from gcloud.taskflow3.models import TaskFlowInstance


def dispatch(group_by, filters=None, page=None, limit=None):
    """
    @summary: 根据不同group_by指派任务
    :param group_by:
    :param filters:
    :param page:
    :param limit:
    :return:
    """
    task_flow_instance_manager = TaskFlowInstance.objects
    # 获取通用过滤后的queryset
    if filters is None:
        filters = {}
    result, message, taskflow, prefix_filters = task_flow_instance_manager.general_filter(filters)
    if not result:
        return False, message

    total = 0
    groups = []

    # 按流程执行状态查询流程个数
    if group_by == AE.state:
        total, groups = task_flow_instance_manager.group_by_state(taskflow)

    # 查询不同业务对应的流程数
    elif group_by == AE.business__cc_id:
        total, groups = task_flow_instance_manager.group_by_biz_cc_id(taskflow, group_by)

    # 查询不同轻应用对应的流程数
    elif group_by == AE.appmaker_instance:
        total, groups = task_flow_instance_manager.group_by_appmaker_instance(taskflow, filters, page, limit)

    # 查询各标准插件被执行次数
    elif group_by == AE.atom_execute_times:
        total, groups = task_flow_instance_manager.group_by_atom_execute_times(taskflow)

    # 查询各标准插件失败次数
    elif group_by == AE.atom_execute_fail_times:
        total, groups = task_flow_instance_manager.group_by_atom_execute_fail_times(taskflow)

    # 查询各标准插件失败率
    elif group_by == AE.atom_fail_percent:
        total, groups = task_flow_instance_manager.group_by_atom_fail_percent(taskflow)

    # 查询各标准插件平均耗时（不计算子流程）
    elif group_by == AE.atom_avg_execute_time:
        total, groups = task_flow_instance_manager.group_by_atom_avg_execute_time(taskflow)

    # 被引用的任务实例列表
    elif group_by == AE.atom_instance:
        total, groups = task_flow_instance_manager.group_by_atom_instance(taskflow, filters, page, limit)

    # 各任务实例执行的标准插件节点个数、子流程节点个数、网关节点数
    elif group_by == AE.instance_node:
        total, groups = task_flow_instance_manager.group_by_instance_node(taskflow, filters, page, limit)

    # 各任务执行耗时
    elif group_by == AE.instance_details:
        total, groups = task_flow_instance_manager.group_by_instance_details(filters, prefix_filters, page, limit)

    #  按起始时间、业务（可选）、类型（可选）、图表类型（日视图，月视图），查询每一天或每一月的执行数量
    elif group_by == AE.instance_time:
        total, groups = task_flow_instance_manager.group_by_instance_time(taskflow, filters)

    # 查询不同类别、创建方式、流程类型对应的流程数
    elif group_by in [AE.category, AE.create_method, AE.flow_type]:
        result, message, total, groups = task_flow_instance_manager.general_group_by(prefix_filters, group_by)
        if not result:
            return False, message

    data = {'total': total, 'groups': groups}
    return True, data
