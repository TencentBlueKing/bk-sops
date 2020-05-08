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

import calendar
import datetime
import logging
import time
import pytz
import math

from django.utils import timezone

logger = logging.getLogger("root")


def timestamp_to_datetime(timestamp):
    """
    时间戳转为datetime类型
    :param timestamp:
    :return:
    """
    try:
        # 前端是传过来的是毫秒需要进行转换为秒
        timestamp = timestamp / 1000
        # 时间戳转为 datetime
        return timezone.datetime.fromtimestamp(timestamp, tz=pytz.utc)
    except ValueError:
        logger.error("illegal parameter format :%s" % time)
        return None


def format_datetime(dt):
    """
    时间转换为字符串格式（附带时区）
    :param dt: type:datetime.datetime
    :return:
    """
    # translate to time in local timezone
    if not dt:
        return ''
    if timezone.is_aware(dt):
        dt = timezone.localtime(dt)
    return dt.strftime("%Y-%m-%d %H:%M:%S %z")


def time_now_str():
    return timezone.localtime(timezone.now()).strftime('%Y%m%d%H%M%S')


def gen_day_dates(start_time, days):
    """
        获取两个日期之间的所有日期
        :param start_time: 开始时间:
        :param days: 相差日期:
        :return:
        """
    day = datetime.timedelta(days=1)
    for index in range(days):
        yield start_time + day * index


def get_month_dates(start_time, end_time):
    """
    获取两个日期之间的所有月份
    :param start_time: 开始时间:
    :param end_time: 结束时间
    :return:
    """
    out_dates = []
    # 需要额外是最后一天的情况，需要增加一天
    _, last_day = calendar.monthrange(start_time.year, start_time.month)
    if last_day == start_time.day:
        start_time += datetime.timedelta(days=1)
    while start_time <= end_time:
        date_str = start_time.strftime('%Y-%m')
        if date_str not in out_dates:
            out_dates.append(date_str)
        start_time = add_months(start_time, 1)
    return out_dates


def add_months(dt, months):
    """
    添加N个月份
    :param dt: 开始时间:
    :param months: 增加的月份
    :return:
    """
    month = dt.month - 1 + months
    year = dt.year + math.floor(month / 12)
    month = month % 12 + 1
    return dt.replace(year=year, month=month)
