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
import json
import logging
import re
from copy import deepcopy

from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger("root")

ip_re = r"((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)"
ip_pattern = re.compile(ip_re)


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


def chunk_table_data(column, break_line):
    """
    @summary: 表格参数值支持以break_line为分隔符分隔的多条数据，对一行数据,当有一列有多条数据时（包含换行符）,其他列要么也有相等个数的
        数据 （换行符个数相等），要么只有一条数据（不包含换行符，此时表示多条数据此列参数值都相同）
    @param column:  表格单行数据，字典格式
    @param break_line: 分隔符
    @return:
    """
    count = 1
    chunk_data = []
    multiple_keys = []
    for key, value in column.items():
        # 如果字符串里是list,dict等数据类型可以序列化成功成功，说明这一列是单个数据，不需要扩展，跳过此次循环
        # 例如：‘123’ ‘[1,2,3]’ '{"k1":1}'
        try:
            json.loads(value)
            continue
        # 触发异常说明传入的类型是int类型，，说明这一列是单个数据，不需要扩展，跳过此次循环
        # 例如： 123
        except TypeError:
            continue
        # 普通字符串触发json.JSONDecodeError
        # 例如：'1,2,3'  '[1,2],[2,3]'  '{"k1":1},{"k2":2}'
        except json.JSONDecodeError:
            pass
        value = value.strip()
        if break_line in value:
            multiple_keys.append(key)
            value = value.split(break_line)
            if len(value) != count and count != 1:
                return {"result": False, "message": _("单行数据[%s]的各列换行符个数不一致，请改为一致或者去掉换行符") % value, "data": []}
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
