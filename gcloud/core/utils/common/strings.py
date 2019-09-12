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

from django.utils import six

from gcloud.core.constant import TEMPLATE_NODE_NAME_MAX_LENGTH

logger = logging.getLogger("root")


def name_handler(name, max_length):
    """名称处理"""
    # 替换特殊字符
    name_str = re.compile(r'[<>.,;~!@#^&*￥\'\"]+').sub('', name)
    # 长度截取
    return name_str[:max_length]


def pipeline_node_name_handle(pipeline_tree):
    for value in pipeline_tree.values():
        if isinstance(value, dict):
            for info in value.values():
                if isinstance(info, dict) and 'name' in info:
                    info['name'] = name_handler(info['name'], TEMPLATE_NODE_NAME_MAX_LENGTH)
            if 'name' in value:
                value['name'] = name_handler(value['name'], TEMPLATE_NODE_NAME_MAX_LENGTH)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and 'name' in item:
                    item['name'] = name_handler(item['name'], TEMPLATE_NODE_NAME_MAX_LENGTH)


def camel_case_to_underscore_naming(source):
    """
    将驼峰形式字符串转为下划线形式
    :param source:
    :return:
    """
    if not isinstance(source, six.string_types):
        return source
    result = ''
    for i, s in enumerate(source):
        if i == 0:
            result += s.lower()
        else:
            if s.isupper():
                if source[i - 1].islower():
                    result += '_' + s.lower()
                else:
                    result += s.lower()
            else:
                result += s
    return result
