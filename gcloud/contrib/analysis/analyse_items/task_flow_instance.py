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

import re
import logging
import datetime

from gcloud.core.constant import AE
from gcloud.core.utils.common import timestamp_to_datetime
from gcloud.taskflow3.models import TaskFlowInstance

logger = logging.getLogger('root')

PIPELINE_REGEX = re.compile(r'^name|create_time|creator|create_time|executor|'
                            r'start_time|finish_time|is_started|is_finished')
TASK_GROUP_BY_METHODS = {
    # 按流程执行状态查询流程个数
    AE.state: TaskFlowInstance.objects.group_by_state,
    # 查询不同业务对应的流程数
    AE.project_id: TaskFlowInstance.objects.group_by_project_id,
    # 查询不同轻应用对应的流程数
    AE.appmaker_instance: TaskFlowInstance.objects.group_by_appmaker_instance,
    # 查询各标准插件被执行次数
    AE.atom_execute_times: TaskFlowInstance.objects.group_by_atom_execute_times,
    # 查询各标准插件失败次数
    AE.atom_execute_fail_times: TaskFlowInstance.objects.group_by_atom_execute_fail_times,
    # 查询各标准插件失败率
    AE.atom_fail_percent: TaskFlowInstance.objects.group_by_atom_fail_percent,
    # 查询各标准插件平均耗时（不计算子流程)
    AE.atom_avg_execute_time: TaskFlowInstance.objects.group_by_atom_avg_execute_time,
    # 被引用的任务实例列表
    AE.atom_instance: TaskFlowInstance.objects.group_by_atom_instance,
    # 各任务实例执行的标准插件节点个数、子流程节点个数、网关节点数
    AE.instance_node: TaskFlowInstance.objects.group_by_instance_node,
    #  按起始时间、业务（可选）、类型（可选）、图表类型（日视图，月视图），查询每一天或每一月的执行数量
    AE.instance_time: TaskFlowInstance.objects.group_by_instance_time,
}


def produce_filter(filters):
    """
    @summary: 按任务数据各维度统计条件规范化
    @param filters:
    @return:
    """
    orm_filters = {}
    for cond, value in list(filters.items()):
        # 如果conditions内容为空或为空字符，不可加入查询条件中
        if value in ['None', ''] or cond in ['component_code', 'order_by', 'type']:
            continue
        if PIPELINE_REGEX.match(cond):
            filter_cond = 'pipeline_instance__%s' % cond
            # 时间范围
            if cond == 'create_time':
                filter_cond = '%s__gte' % filter_cond
                orm_filters.update({filter_cond: timestamp_to_datetime(value)})
                continue
            # 结束时间由创建时间来决定
            if cond == 'finish_time':
                filter_cond = 'pipeline_instance__create_time__lt'
                orm_filters.update(
                    {filter_cond: timestamp_to_datetime(value) + datetime.timedelta(days=1)})
                continue
        else:
            filter_cond = cond
        orm_filters.update({filter_cond: value})

    return orm_filters


def dispatch(group_by, filters=None, page=None, limit=None):
    """
    @summary: 根据不同group_by指派任务
    @param group_by:
    @param filters:
    @param page:
    @param limit:
    @return:
    """
    if filters is None:
        filters = {}
    orm_filters = produce_filter(filters)
    try:
        taskflow = TaskFlowInstance.objects.filter(**orm_filters)
    except Exception as e:
        message = "query taskflow params conditions[{filters}] have invalid key or value: {error}".format(
            filters=filters,
            error=e)
        logger.error(message)
        return False, message

    # 查询不同类别、创建方式、流程类型对应的流程数
    if group_by in [AE.category, AE.create_method, AE.flow_type]:
        result, message, total, groups = TaskFlowInstance.objects.general_group_by(orm_filters, group_by)
        if not result:
            return False, message
    else:
        total, groups = TASK_GROUP_BY_METHODS[group_by](taskflow, filters, page, limit)

    data = {'total': total, 'groups': groups}
    return True, data
