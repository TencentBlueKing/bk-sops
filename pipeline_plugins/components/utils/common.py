# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging
import random
import re
import time
import typing
from copy import deepcopy

from django.utils.translation import ugettext_lazy as _

from api.utils.thread import ThreadPool

logger = logging.getLogger("root")

ip_re = r"(?<!\d)((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)(?!\d)"
ip_pattern = re.compile(ip_re)
plat_ip_reg = re.compile(r"\d+:((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)(?!\d)")


def loose_strip(data):
    """
    @summary: 尝试把 data 当做字符串处理两端空白字符
    @param data:
    @return:
    """
    if isinstance(data, str):
        return data.strip()
    try:
        return str(data).strip()
    except Exception:
        return data


def chunk_table_data(column_dict, break_line):
    """
    @summary: 表格参数值支持以break_line为分隔符分隔的多条数据，对一行数据，当有一列有多条数据时（包含换行符），其他列要么也有相等个数的
        数据（换行符个数相等），要么只有一条数据（不包含换行符，此时表示多条数据此列参数值都相同）
    @param column_dict: 表格单行数据，字典格式
    @param break_line: 分隔符
    @return:
    """
    count = 1
    chunk_data = []
    multiple_keys = []
    column = deepcopy(column_dict)
    for key, value in column.items():
        if not isinstance(value, str):
            # 如果列类型为int，则跳过处理
            if isinstance(value, int):
                continue
            else:
                return {"result": False, "message": _("数据[%s]格式错误，请改为字符串") % value, "data": []}
        value = value.strip()

        # 分隔符为空，则默认为”,“
        if not break_line:
            break_line = ","
        if break_line in value:
            multiple_keys.append(key)
            value = value.split(break_line)
            if len(value) != count and count != 1:
                message = _(f"非法请求: [单行自动扩展]中, [{value}] 按分隔符分割后的行数不一致, 请修复后重试 | chunk_table_data")
                logger.error(message)
                return {"result": False, "message": message, "data": []}
            count = len(value)
        column[key] = value

    if count == 1:
        return {"result": True, "data": [column], "message": ""}

    for i in range(count):
        item = deepcopy(column)
        for key in multiple_keys:
            item[key] = column[key][i]
        chunk_data.append(item)
    return {"result": True, "data": chunk_data, "message": ""}


def batch_execute_func(func, params_list: list, interval_enabled=False):
    """
    并发处理func
    :param func: 待处理函数
    :param params_list: 请求参数
    :param interval_enabled: 启用间隔
    :return: [{"result":结果，”params“: 参数}，{"result":结果，”params“: 参数}，....]
    """
    pool = ThreadPool()
    execute_future_list = []
    for params in params_list:
        execute_future_list.append({"result": pool.apply_async(func, kwds=params), "params": params})
        if interval_enabled:
            time.sleep(random.random())

    pool.close()
    pool.join()

    # 取值
    for future in execute_future_list:
        future["result"] = future["result"].get()

    return execute_future_list


def convert_num_to_str(export_data: list):
    """转换从excel导入值为number类型的数据为str"""
    for data in export_data:
        for key, value in data.items():
            if isinstance(value, int) or isinstance(value, float):
                data[key] = str(value)
    return export_data


def parse_passwd_value(passwd_value: typing.Union[str, typing.Dict[str, str]]) -> str:
    if isinstance(passwd_value, str):
        return passwd_value
    elif isinstance(passwd_value, dict):
        return parse_passwd_value(passwd_value.get("value", ""))
    else:
        # 仅有两种合法结构，如果都不满足直接返回空串
        return ""
