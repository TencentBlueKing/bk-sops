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
from gcloud.tasktmpl3.models import TaskTemplate


def dispatch(group_by, filters=None, page=None, limit=None):
    """
    @summary: 根据不同group_by指派任务
    :param group_by:
    :param filters:
    :param page:
    :param limit:
    :return:
    """
    taskTemplateManager = TaskTemplate.objects
    # 获取通用过滤后的queryset
    if filters is None:
        filters = {}
    result, message, tasktmpl, prefix_filters = taskTemplateManager.general_filter(filters)
    if not result:
        return False, message

    total = 0
    groups = []

    # 按流程模板执行状态查询流程个数
    if group_by == AE.state:
        total, groups = taskTemplateManager.group_by_state(tasktmpl)

    # 查询不同业务的模板个数
    elif group_by == AE.business__cc_id:
        total, groups = taskTemplateManager.group_by_biz_cc_id(tasktmpl, group_by)

    # 查询不同原子引用的模板个数
    elif group_by == AE.atom_cite:
        total, groups = taskTemplateManager.group_by_atom_cite(tasktmpl)

    # 按起始时间、业务（可选）、类型（可选）、标准插件查询被引用的流程模板列表(dataTable)
    elif group_by == AE.atom_template:
        total, groups = taskTemplateManager.group_by_atom_template(tasktmpl, filters, page, limit)

    # 需要获得符合的查询的对应 template_id 列表
    elif group_by == AE.atom_execute:
        total, groups = taskTemplateManager.group_by_atom_execute(tasktmpl, filters, page, limit)

    # 按起始时间、业务（可选）、类型（可选）查询各流程模板标准插件节点个数、子流程节点个数、网关节点数
    elif group_by == AE.template_node:
        total, groups = taskTemplateManager.group_by_template_node(tasktmpl, filters, page, limit)

    # 不同类别、创建方法、流程类型对应的任务数
    elif group_by in [AE.category, AE.create_method, AE.flow_type]:
        result, message, total, groups = taskTemplateManager.general_group_by(prefix_filters, group_by)
        if not result:
            return False, message

    data = {'total': total, 'groups': groups}
    return result, data
