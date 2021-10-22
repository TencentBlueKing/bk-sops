# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
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

from gcloud.constants import TEMPLATE_NODE_NAME_MAX_LENGTH, AE

logger = logging.getLogger("root")


def standardize_name(name, max_length):
    """名称处理"""
    # 替换特殊字符
    name_str = re.compile(r"[<>$&\'\"]+").sub("", name)
    # 长度截取
    return name_str[:max_length]


def standardize_pipeline_node_name(pipeline_tree):
    for value in list(pipeline_tree.values()):
        if isinstance(value, dict):
            for info in list(value.values()):
                if isinstance(info, dict) and "name" in info:
                    info["name"] = standardize_name(info["name"], TEMPLATE_NODE_NAME_MAX_LENGTH)
            if "name" in value:
                value["name"] = standardize_name(value["name"], TEMPLATE_NODE_NAME_MAX_LENGTH)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and "name" in item:
                    item["name"] = standardize_name(item["name"], TEMPLATE_NODE_NAME_MAX_LENGTH)


def camel_case_to_underscore_naming(source):
    """
    将驼峰形式字符串转为下划线形式
    :param source:
    :return:
    """
    if not isinstance(source, six.string_types):
        return source
    result = ""
    for i, s in enumerate(source):
        if i == 0:
            result += s.lower()
        else:
            if s.isupper():
                if source[i - 1].islower():
                    result += "_" + s.lower()
                else:
                    result += s.lower()
            else:
                result += s
    return result


def check_and_rename_params(conditions, group_by, group_by_check=AE.group_list):
    """
    检验参数是否正确
    :param conditions:参数是一个dict
    :param group_by:分组凭据
    :param group_by_check:分组检查内容
    :return:
    """
    result_dict = {"success": False, "content": None, "conditions": conditions, "group_by": None}
    if not isinstance(conditions, dict):
        message = "params conditions[%s] are invalid dict data" % conditions
        logger.error(message)
        result_dict["content"] = message
        return result_dict
    # 检查传递分组是否有误
    if group_by not in group_by_check:
        message = "params group_by[%s] is invalid" % group_by
        logger.error(message)
        result_dict["content"] = message
        return result_dict

    result_dict["success"] = True
    result_dict["group_by"] = group_by
    result_dict["conditions"] = conditions
    return result_dict


def string_to_boolean(value):
    if isinstance(value, six.string_types) and value.lower() in ("false", "0"):
        value = False
    else:
        value = bool(value)

    return value


def django_celery_beat_cron_time_format_fit(cron_str):
    """
    django_celery_beat 2.1.0 cron格式变动兼容
    旧格式：10 0 * * * (m/h/d/dM/MY) Asia/Shanghai 或 */5 * * * * (m/h/d/dM/MY)
    新格式：0 7 1,4,6,8,10,12 10 * (m/h/dM/MY/d) Asia/Shanghai
    返回格式遵循旧格式
    """
    if not cron_str:
        return cron_str
    unit_order = ["m", "h", "d", "dM", "MY"]
    cron_list = cron_str.split(" ")
    # 下标0-4为对应时间值，5为时间单位，6为时区(可能不包含)
    cron_times, time_formats, time_zone = cron_list[:5], cron_list[5][1:-1].split("/"), cron_list[6:]
    cron_config = {time_format: cron_time for time_format, cron_time in zip(time_formats, cron_times)}
    result_cron_list = [cron_config[unit] for unit in unit_order] + ["({})".format("/".join(unit_order))] + time_zone
    return " ".join(result_cron_list).strip()
