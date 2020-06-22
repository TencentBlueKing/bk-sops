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

import re
import logging

ip_pattern = re.compile(r"((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)")

logger = logging.getLogger("root")


def get_ip_by_regex(ip_str):
    """从给定文本中匹配 IP 并返回

    :param ip_str: 包含 IP 的文本
    :type ip_str: string
    :return: IP 字符串列表
    :rtype: list[string]
    """
    ret = []
    for match in ip_pattern.finditer(ip_str):
        ret.append(match.group())
    return ret


def format_sundry_ip(ip):
    """返回逗号分隔多 IP 的第一个 IP

    :param ip: IP 字符串
    :type ip:
    :return: 第一个 IP
    :rtype: string
    """

    if "," in ip:
        logger.info("HOST[%s] has multiple ip" % ip)
        return ip.split(",")[0]
    return ip
