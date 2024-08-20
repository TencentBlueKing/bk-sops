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
import ipaddress
import logging
import re
from enum import Enum
from typing import List

ip_pattern = re.compile(r"(?<!\d)((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)(?!\d)")
plat_ip_reg = re.compile(r"\d+:((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)(?!\d)")
# https://codverter.com/blog/articles/tech/20190105-extract-ipv4-ipv6-ip-addresses-using-regex.html
ipv6_pattern = re.compile(
    r"((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:)))"  # noqa
)  # noqa
plat_ipv6_reg = re.compile(
    r"\d+:\[((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:)))\]"  # noqa
)  # noqa

number_pattern = re.compile(r"\d+")

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


def get_ip_or_cloudid_ip_by_regex(ip_list: List[str]) -> dict:
    """从给定文本中匹配couldID:IP 或纯IP 并返回

    :param ip_list: couldID:IP 或纯IP 的文本
    :type ip_list: list
    :return: couldID:ip_list
    :rtype: dict
    """
    ret = {}
    for ip in ip_list:
        if plat_ip_reg.match(ip) and ":" in ip:
            cloudIP = ip.split(":")
            if int(cloudIP[0]) not in ret:
                ret[int(cloudIP[0])] = [cloudIP[1]]
            else:
                ret[int[cloudIP[0]]].append(cloudIP[1])
        else:
            if None not in ret:
                ret[None] = [ip]
            else:
                ret[None].append(ip)
    return ret


def extend_ipv6(ip_list):
    """
    将ipv6扩展为完整ipv6地址列表
    @param ip_list: ["::0001"]
    @return: ["0000:0000:0000:0000:0000:0000:0000:0001"]
    """
    ip_v6_list = []
    for ip_v6 in ip_list:
        p_address = ipaddress.ip_address(ip_v6)
        if p_address.version == 6:
            ip_v6_list.append(p_address.exploded)

    return ip_v6_list


def get_ipv6_and_cloud_id_from_ipv6_cloud_str(ipv6_cloud_str):
    """ "
    从ipv6+管控区域的格式中提取出来ipv6和管控区域地址
    ipv6_cloud_str: 0:[0000:0000:0000:0000:0000:0000]
    """
    cloud_id = ipv6_cloud_str.split(":")[0]
    ip_v6_address, _ = get_ip_by_regex_type(IpRegexType.IPV6.value, ipv6_cloud_str)
    return cloud_id, ip_v6_address[0]


def extend_ipv6_with_cloud_id(ip_list):
    # @ip_list = ["0:[xxx:xxx:xxx:xxx]"]
    ip_list_result = []
    for item in ip_list:
        # item: "0:[0000:0000:0000:0000:0000:0000:0000:0000]"
        cloud_id, ip_v6_address = get_ipv6_and_cloud_id_from_ipv6_cloud_str(item)
        ip_list_result.append("{}:[{}]".format(cloud_id, ip_v6_address))
    return ip_list_result


class IpRegexType(Enum):
    IPV4 = "IPV4"
    IPV6 = "IPV6"
    IPV6_WITH_CLOUD_ID = "IPV6_WITH_CLOUD_ID"
    IPV4_WITH_CLOUD_ID = "IPV4_WITH_CLOUD_ID"
    HOST_ID = "HOST_ID"


def get_ip_by_regex_type(regex_type, ip_str):
    """
    根据传入的正则类型，匹配指定的数据，并返回去除匹配结果的子串
    :param regex: ipv4, ipv6, number
    :param ip_str:
    :return:
    """
    regex_map = {
        IpRegexType.IPV4.value: ip_pattern,
        IpRegexType.IPV4_WITH_CLOUD_ID.value: plat_ip_reg,
        IpRegexType.IPV6.value: ipv6_pattern,
        IpRegexType.HOST_ID.value: number_pattern,
        IpRegexType.IPV6_WITH_CLOUD_ID.value: plat_ipv6_reg,
    }

    if regex_type not in regex_map.keys():
        raise Exception("暂不支持的正则类型")

    logger.info(
        "[get_ip_by_regex_type] start match ip by regex type, regex_type={}, ip_str={}".format(regex_type, ip_str)
    )
    regex = regex_map[regex_type]
    ip_list = []
    for match in regex.finditer(ip_str):
        ip_list.append(match.group())
    new_ip_str = regex.sub("", ip_str)
    logger.info(
        "[get_ip_by_regex_type] match ip by regex type end, regex_type={}, new_ip_str={}".format(regex_type, new_ip_str)
    )

    # 对于IPV6的主机, 需要将压缩格式的ipv6扩展为全格式
    if regex_type == IpRegexType.IPV6.value:
        ip_list = extend_ipv6(ip_list)

    if regex_type == IpRegexType.IPV6_WITH_CLOUD_ID.value:
        ip_list = extend_ipv6_with_cloud_id(ip_list)

    if regex_type == IpRegexType.HOST_ID.value:
        ip_list = [int(host_id) for host_id in ip_list]

    return list(set(ip_list)), new_ip_str


def extract_ip_from_ip_str(ip_str):
    ipv6_list_with_cloud_id, ip_str_without_ipv6_with_cloud_id = get_ip_by_regex_type(
        IpRegexType.IPV6_WITH_CLOUD_ID.value, ip_str
    )

    ipv6_list, ip_str_without_ipv6 = get_ip_by_regex_type(IpRegexType.IPV6.value, ip_str_without_ipv6_with_cloud_id)

    ipv4_list_with_cloud_id, ip_str_without_ipv4_with_cloud_id = get_ip_by_regex_type(
        IpRegexType.IPV4_WITH_CLOUD_ID.value, ip_str_without_ipv6
    )
    # 在ipv6下，管控区域+ip 将不再唯一
    ipv4_list, ip_str_without_ipv4 = get_ip_by_regex_type(IpRegexType.IPV4.value, ip_str_without_ipv4_with_cloud_id)

    host_id_list, _ = get_ip_by_regex_type(IpRegexType.HOST_ID.value, ip_str_without_ipv4)

    return ipv6_list, ipv4_list, host_id_list, ipv4_list_with_cloud_id, ipv6_list_with_cloud_id


def get_plat_ip_by_regex(ip_str):
    """
    从给定文本匹配【管控区域ID:IP】并返回,【IP】格式管控区域默认为0
    @param ip_str:
    @return: [
        {
            "bk_cloud_id":0,
            "ip":"x.x.x.x"
        },
        {
            "bk_cloud_id":0,
            "ip":"x.x.x.x"
        },
    ]
    """

    ip_list = []
    for match in plat_ip_reg.finditer(ip_str):
        plat_ip = match.group()
        ip_str = ip_str.replace(plat_ip, "")
        info = plat_ip.split(":")
        ip_list.append({"bk_cloud_id": int(info[0]), "ip": info[1]})

    for match in ip_pattern.finditer(ip_str):
        ip = match.group()
        ip_list.append({"bk_cloud_id": 0, "ip": ip})

    return ip_list


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
