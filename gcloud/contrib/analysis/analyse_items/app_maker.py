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
from gcloud.contrib.appmaker.models import AppMaker


def dispatch(group_by, filters=None):
    """
    @summary: 根据不同group_by指派任务
    :param group_by
    :param filters
    :return:
    """
    app_maker_manager = AppMaker.objects
    # 获取通用过滤后的queryset
    if filters is None:
        filters = {}
    result, appmaker, message = app_maker_manager.general_filter(filters)
    if not result:
        return False, message

    total = 0
    groups = []

    # 按起始时间、项目（可选）查询各类型轻应用个数和占比√(echarts)
    if group_by == AE.project_id:
        total, groups = app_maker_manager.group_by_project_id(appmaker, group_by)

    # 按起始时间、类型（可选）查询各业务下新增轻应用个数（排序）
    elif group_by == AE.category:
        total, groups = app_maker_manager.group_by_category(appmaker, group_by)
    data = {'total': total, 'groups': groups}
    return result, data
