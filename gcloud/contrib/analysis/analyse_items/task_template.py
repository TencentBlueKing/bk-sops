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
from gcloud.tasktmpl3.models import TaskTemplate

logger = logging.getLogger('root')

TEMPLATE_REGEX = re.compile(r'^name|creator_name|editor_name|'
                            r'create_time|edit_time|edit_finish_time|finish_time')
TEMPLATE_GROUP_BY_METHODS = {
    # 按流程模板执行状态查询流程个数
    AE.state: TaskTemplate.objects.group_by_state,
    # 查询不同业务的模板个数
    AE.project_id: TaskTemplate.objects.group_by_project_id,
    # 查询不同原子引用的模板个数
    AE.atom_cite: TaskTemplate.objects.group_by_atom_cite,
    # 按起始时间、业务（可选）、类型（可选）、标准插件查询被引用的流程模板列表(dataTable)
    AE.atom_template: TaskTemplate.objects.group_by_atom_template,
    # 需要获得符合的查询的对应 template_id 列表
    AE.atom_execute: TaskTemplate.objects.group_by_atom_execute,
    # 按起始时间、业务（可选）、类型（可选）查询各流程模板标准插件节点个数、子流程节点个数、网关节点数
    AE.template_node: TaskTemplate.objects.group_by_template_node
}


def produce_filter(filters):
    """
    @summary: 按流程数据各维度统计条件规范化
    @param filters:
    @return:
    """
    orm_filters = {}
    for cond, value in list(filters.items()):
        # component_code不加入查询条件中
        if value in ['None', ''] or cond in ['component_code', 'order_by', 'type']:
            continue
        if TEMPLATE_REGEX.match(cond):
            filter_cond = 'pipeline_template__%s' % cond
            # 时间范围
            if cond == 'create_time':
                filter_cond = '%s__gte' % filter_cond
                orm_filters.update({filter_cond: timestamp_to_datetime(value)})
                continue
            elif cond == 'finish_time':
                filter_cond = 'pipeline_template__create_time__lt'
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
    :param group_by:
    :param filters:
    :param page:
    :param limit:
    :return:
    """
    if filters is None:
        filters = {}
    orm_filters = produce_filter(filters)
    try:
        tasktmpl = TaskTemplate.objects.filter(**orm_filters)
    except Exception as e:
        message = "query template params conditions[{filters}] have invalid key or value: {error}".format(
            filters=filters,
            error=e)
        logger.error(message)
        return False, message

    # 不同类别、创建方法、流程类型对应的任务数
    if group_by in [AE.category, AE.create_method, AE.flow_type]:
        result, message, total, groups = TaskTemplate.objects.general_group_by(orm_filters, group_by)
        if not result:
            return False, message
    else:
        total, groups = TEMPLATE_GROUP_BY_METHODS[group_by](tasktmpl, filters, page, limit)

    data = {'total': total, 'groups': groups}
    return True, data
