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
from gcloud.contrib.appmaker.models import AppMaker

logger = logging.getLogger('root')

APPMAKER_REGEX = re.compile(r'^category|create_time|creator_name|editor_name|'
                            r'template_schema_id|finish_time|task_template_id|task_template_name')


def produce_filter(filters):
    """
    @summary: 按轻应用数据各维度统计条件规范化
    @param filters:
    @return:
    """
    orm_filters = {}
    for cond, value in list(filters.items()):
        if value in ['None', ''] or cond == 'type':
            continue
        if cond == 'create_time':
            filter_cond = '%s__gte' % cond
            orm_filters.update({filter_cond: timestamp_to_datetime(value)})
            continue
        elif cond == 'finish_time':
            filter_cond = 'create_time__lt'
            orm_filters.update({filter_cond: timestamp_to_datetime(value) + datetime.timedelta(days=1)})
            continue
        if APPMAKER_REGEX.match(cond):
            filter_cond = 'task_template__%s' % cond
        else:
            filter_cond = cond
        orm_filters.update({filter_cond: value})
    return orm_filters


def dispatch(group_by, filters=None):
    """
    @summary: 根据不同group_by指派任务
    @param group_by
    @param filters
    @return:
    """
    if filters is None:
        filters = {}
    orm_filters = produce_filter(filters)
    try:
        appmaker = AppMaker.objects.filter(**orm_filters)
    except Exception as e:
        message = "query appmaker params conditions[{filters}] have invalid key or value: {error}".format(
            filters=filters,
            error=e)
        logger.error(message)
        return False, message

    total = 0
    groups = []
    # 按起始时间、项目（可选）查询各类型轻应用个数和占比
    if group_by == AE.project_id:
        total, groups = AppMaker.objects.group_by_project_id(appmaker, group_by)
    # 按起始时间、类型（可选）查询各业务下新增轻应用个数（排序）
    elif group_by == AE.category:
        total, groups = AppMaker.objects.group_by_category(appmaker, group_by)
    data = {'total': total, 'groups': groups}
    return True, data
