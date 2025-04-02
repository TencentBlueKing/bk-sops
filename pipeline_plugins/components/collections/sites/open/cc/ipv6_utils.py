# -*- coding: utf-8 -*-
import logging
from collections import Counter

from gcloud.utils import cmdb
from gcloud.utils.cmdb import get_business_host_by_hosts_ids
from gcloud.utils.ip import extract_ip_from_ip_str, get_ipv6_and_cloud_id_from_ipv6_cloud_str
from pipeline_plugins.components.utils.sites.open.utils import compare_ip_list_and_return

logger = logging.getLogger("root")


# 以下是最基础的 compare_ip_list 逻辑


def compare_ip_list(host_list, ip_list, host_key="bk_host_innerip"):
    """
    对比查询结果与初始值的的值，本compare_ip_list 返回的是 bool, message 的格式
    @param host_list: 主机列表 [{"bk_host_innerip": "127.0.0.1", "bk_cloud_id":"2"}]
    @param ip_list: ["127.0.0.1"]
    @param host_key: 取ip的字段
    @return:
    """
    if len(host_list) > len(ip_list):
        # find repeat innerip host
        host_counter = Counter([host[host_key] for host in host_list])
        mutiple_innerip_hosts = [innerip for innerip, count in host_counter.items() if count > 1]
        return (
            False,
            "mutiple same innerip host found: {}".format(", ".join(mutiple_innerip_hosts)),
        )
    if len(host_list) < len(ip_list):
        return_innerip_set = {host[host_key] for host in host_list}
        absent_innerip = set(ip_list).difference(return_innerip_set)

        return False, "ip not found in business: {}".format(", ".join(absent_innerip))

    return True, ""


def compare_ip_with_cloud_list(host_list, ip_list):
    """
    对比带管控区域的管控区域是否有多了或者少了的情况,  返回的是 bool, message 的格式
    @param host_list: 主机列表 [{"bk_host_innerip": "127.0.0.1", "bk_cloud_id":"2"}]
    @param ip_list: ["2:127.0.0.1"]
    @param host_key: host_key: 取ip的字段 为了适配IPV4 OR IPV6
    @return:
    """
    if len(host_list) > len(ip_list):
        # find repeat innerip host
        return_innerip_set = {"{}:{}".format(host["bk_cloud_id"], host["bk_host_innerip"]) for host in host_list}
        mutiple_innerip_hosts = return_innerip_set.difference(set(ip_list))
        return (
            False,
            "mutiple same innerip host found: {}".format(", ".join(mutiple_innerip_hosts)),
        )
    if len(host_list) < len(ip_list):
        return_innerip_set = {"{}:{}".format(host["bk_cloud_id"], host["bk_host_innerip"]) for host in host_list}
        absent_innerip = set(ip_list).difference(return_innerip_set)

        return False, "ip not found in business: {}".format(", ".join(absent_innerip))

    return True, ""


def compare_ipv6_with_cloud_list(host_list, ip_list):
    """
    对比带管控区域的管控区域是否有多了或者少了的情况,  返回的是 bool, message 的格式
    @param host_list: 主机列表 [{"bk_host_innerip_ipv6": "0000:00000:0000:0000:0000", "bk_cloud_id":"2"}]
    @param ip_list: ["2:[0000:00000:0000:0000:0000]"]
    @return:
    """
    if len(host_list) > len(ip_list):
        # find repeat innerip host
        return_innerip_set = {"{}:[{}]".format(host["bk_cloud_id"], host["bk_host_innerip_v6"]) for host in host_list}
        mutiple_innerip_hosts = return_innerip_set.difference(set(ip_list))
        return (
            False,
            "mutiple same innerip host found: {}".format(", ".join(mutiple_innerip_hosts)),
        )
    if len(host_list) < len(ip_list):
        return_innerip_set = {"{}:[{}]".format(host["bk_cloud_id"], host["bk_host_innerip_v6"]) for host in host_list}
        absent_innerip = set(ip_list).difference(return_innerip_set)

        return False, "ip not found in business: {}".format(", ".join(absent_innerip))

    return True, ""


def check_ip_cloud(ip_host_with_cloud_list, bk_host_innerip_key="bk_host_innerip"):
    """
    检查cc查询结果中，是否有管控区域+ip重复的主机
    @param ipv4_host_with_cloud_list: [{"host_id":1,"bk_host_innerip": "127.0.0.1", "bk_cloud_id":"2"},
                                        {"host_id":2,"bk_host_innerip": "127.0.0.1", "bk_cloud_id":"2"}]
    @return: ["2:127.0.0.1"]
    """
    repeated_hosts = []
    data = set()
    for host in ip_host_with_cloud_list:
        bk_cloud_id = host["bk_cloud_id"]
        bk_host_innerip = host[bk_host_innerip_key]
        plat_ip = "{}:{}".format(bk_cloud_id, bk_host_innerip)
        # 已有的ip
        if plat_ip not in data:
            data.add(plat_ip)
        else:
            repeated_hosts.append(plat_ip)

    return repeated_hosts


# IP查询相关函数, 最基础的查询，根据ipv4 或者 ipv6 查询，只包含最基础的查询和校验逻辑


def get_ipv6_hosts(tenant_id, executor, bk_biz_id, supplier_account, ipv6_list, is_biz_set=False):
    """
    根据ip地址查询ipv6的主机信息，当 is_biz_set 为 True的时候，调用全业务查询接口查询
    @param tenant_id: 租户 ID
    @param executor: 执行人
    @param bk_biz_id: 业务id, 当is_biz_set时，bk_biz_id 可为 None
    @param supplier_account: 服务商
    @param ipv6_list: ipv6 ip列表。["xxxx:xxxx:xxxx:xxxx"]
    @param is_biz_set: 是否全业务查询
    @return:
    [
        {
            "bk_cloud_id": 0,
            "bk_host_id": 1,
            "bk_host_innerip_v6": "0:::1",
            "bk_mac": "",
            "bk_os_type": null
        }
        ...
    ]
    """
    ipv6_host_list = []
    if not ipv6_list:
        return ipv6_host_list

    if is_biz_set:
        # 全业务去查询ip_v6 相关的主机信息
        ipv6_host_list = cmdb.get_business_set_host_ipv6(
            tenant_id,
            executor,
            supplier_account,
            ["bk_host_id", "bk_host_innerip_v6", "bk_cloud_id", "bk_agent_id", "bk_host_innerip"],
            ipv6_list,
        )
    else:
        # 去查询ip_v6 相关的主机信息
        ipv6_host_list = cmdb.get_business_host_ipv6(
            tenant_id,
            executor,
            bk_biz_id,
            supplier_account,
            ["bk_host_id", "bk_host_innerip_v6", "bk_cloud_id", "bk_agent_id", "bk_host_innerip"],
            ipv6_list,
        )

    # 如果没接口报错，则打印日志，返回空，下层有compare逻辑去保证在插件执行当过程中一定会报错
    if not ipv6_host_list:
        logger.error(
            "[get_ip_v6_hosts] list_biz_hosts[ipv6] query failed, return empty list, "
            "ipv6_list = {}".format(ipv6_list)
        )
        return []

    return ipv6_host_list


def get_ipv4_hosts_with_cloud(tenant_id, executor, bk_biz_id, supplier_account, ipv4_list_with_cloud_id,
                              is_biz_set=False):
    """
    根据ipv4带管控区域的列表查询主机，这个和get_ipv4_hosts地方在于，会将查出来的机器把ip和目标管控区域匹配的拿出来，抛弃不匹配的，再去校验匹配而来的主机
    @param tenant_id: 租户 ID
    @param executor: 执行人
    @param bk_biz_id: 业务id， 当is_biz_set=True可以不传
    @param supplier_account:服务商
    @param ipv4_list_with_cloud_id: ["1:127.0.0.1", "2:127.0.0.1"]
    @param is_biz_set: 是否全业务查询
    @return: [
        {
            "bk_cloud_id": 1,
            "bk_host_id": 1,
            "bk_host_innerip": "127.0.0.1",
            "bk_mac": "",
            "bk_os_type": null
        }
        {
            "bk_cloud_id": 2,
            "bk_host_id": 2,
            "bk_host_innerip": "127.0.0.1",
            "bk_mac": "",
            "bk_os_type": null
        }
        ...
    ]
    """

    ipv4_host_with_cloud_valid = []
    if not ipv4_list_with_cloud_id:
        return ipv4_host_with_cloud_valid

    # 先把所有的ip拿出来去查询所有符合的主机
    ip_list = [_ip.split(":")[1] for _ip in ipv4_list_with_cloud_id]

    if is_biz_set:
        ipv4_host_with_cloud_list = cmdb.get_business_set_host(
            tenant_id, executor, supplier_account,
            ["bk_host_id", "bk_host_innerip", "bk_cloud_id", "bk_agent_id"], ip_list
        )
    else:
        ipv4_host_with_cloud_list = cmdb.get_business_host(
            tenant_id,
            executor,
            bk_biz_id,
            supplier_account,
            ["bk_host_id", "bk_host_innerip_v6", "bk_cloud_id", "bk_agent_id", "bk_host_innerip"],
            ip_list,
        )

    # 如果接口报错or其他的导致返回个空，则return []， 上层的compare逻辑会保证插件执行失败
    if not ipv4_host_with_cloud_list:
        logger.info(
            "[get_ip_v4_host_with_cloud] list_biz_hosts[ipv4] query failed, return empty list, "
            "ipv6_list = {}".format(ipv4_list_with_cloud_id)
        )
        return []

    # 在ipv6语境下需要确认查出来的这一批主机，有没有ip和管控区域一样，但是host_id不一样的，有的话要直接抛异常
    exist_repeated_host = check_ip_cloud(ipv4_host_with_cloud_list)
    if exist_repeated_host:
        raise Exception(
            "list_biz_hosts[ipv4] query failed, "
            "the host with the same IP address and BK-Net is displayed,"
            "repeated_list = {}".format(exist_repeated_host)
        )
    # 查出来的数据需要根据最初始的管控区域:ip 列表清洗出来用户想要的那一部分主机
    for ip_info in ipv4_host_with_cloud_list:
        # 清洗出来所有带管控区域带ip
        plat_ip = "{}:{}".format(ip_info.get("bk_cloud_id", -1), ip_info.get("bk_host_innerip", ""))
        if plat_ip in ipv4_list_with_cloud_id:
            ipv4_host_with_cloud_valid.append(ip_info)

    return ipv4_host_with_cloud_valid


def get_ipv6_hosts_with_cloud(tenant_id, executor, bk_biz_id, supplier_account, ipv6_list_with_cloud_id,
                              is_biz_set=False):
    """
    根据ipv6带管控区域的列表查询主机，这个和get_ipv6_hosts地方在于，会将查出来的机器把ip和目标管控区域匹配的拿出来，抛弃不匹配的，再去校验匹配而来的主机
    @param tenant_id: 租户 ID
    @param executor: 执行人
    @param bk_biz_id: 业务id， 当is_biz_set=True可以不传
    @param supplier_account:服务商
    @param ipv6_list_with_cloud_id: ["1:[1111:1111:1111:1111:1111:1111]"]
    @param is_biz_set: 是否全业务查询
    @return: [
        {
            "bk_cloud_id": 1,
            "bk_host_id": 1,
            "bk_host_innerip_innerip": "1111:1111:1111:1111:1111:1111",
            "bk_mac": "",
            "bk_os_type": null
        }
        ...
    ]
    """

    ipv6_host_with_cloud_valid = []
    if not ipv6_list_with_cloud_id:
        return ipv6_host_with_cloud_valid

    # 先把所有的ip拿出来去查询符合条件的主机
    ipv6_list = []
    for item in ipv6_list_with_cloud_id:
        _, ip = get_ipv6_and_cloud_id_from_ipv6_cloud_str(item)
        ipv6_list.append(ip)

    # 如果是跨业务的情况
    if is_biz_set:
        # 全业务去查询ip_v6 相关的主机信息
        ipv6_host_with_cloud_list = cmdb.get_business_set_host_ipv6(
            tenant_id,
            executor,
            supplier_account,
            ["bk_host_id", "bk_host_innerip_v6", "bk_cloud_id", "bk_agent_id", "bk_host_innerip"],
            ipv6_list,
        )
    else:
        # 去查询ip_v6 相关的主机信息
        ipv6_host_with_cloud_list = cmdb.get_business_host_ipv6(
            tenant_id,
            executor,
            bk_biz_id,
            supplier_account,
            ["bk_host_id", "bk_host_innerip_v6", "bk_cloud_id", "bk_agent_id", "bk_host_innerip"],
            ipv6_list,
        )

    # 如果接口报错or其他的导致返回个空，则return []， 上层的compare逻辑会保证插件执行失败
    if not ipv6_host_with_cloud_list:
        logger.info(
            "[get_ipv6_hosts_with_cloud] list_biz_hosts[ipv6] query failed, return empty list, "
            "ipv6_list = {}".format(ipv6_host_with_cloud_list)
        )
        return []

    # 在ipv6语境下需要确认查出来的这一批主机，有没有ip和管控区域一样，但是host_id不一样的，有的话要直接抛异常
    exist_repeated_host = check_ip_cloud(ipv6_host_with_cloud_list, bk_host_innerip_key="bk_host_innerip_v6")
    if exist_repeated_host:
        raise Exception(
            "[get_ipv6_hosts_with_cloud] is failed "
            "the host with the same IP address and BK-Net is displayed,"
            "repeated_list = {}".format(exist_repeated_host)
        )

    # 查出来的数据需要根据最初始的管控区域:ip 列表清洗出来用户想要的那一部分主机
    for ip_info in ipv6_host_with_cloud_list:
        plat_ip = "{}:[{}]".format(ip_info.get("bk_cloud_id", -1), ip_info.get("bk_host_innerip_v6", ""))
        if plat_ip in ipv6_list_with_cloud_id:
            ipv6_host_with_cloud_valid.append(ip_info)

    return ipv6_host_with_cloud_valid


def get_ipv4_hosts(tenant_id, executor, bk_biz_id, supplier_account, ipv4_list, is_biz_set=False):
    """
    根据ipv4的ip列表去cc查询ip信息
    @param tenant_id: 租户 ID
    @param executor: 执行人
    @param bk_biz_id: 业务id，is_biz_set=true时可以不填
    @param supplier_account: 服务商
    @param ipv4_list:ipv4列表 ["127.0.0.1"]
    @param is_biz_set: 是否全业务查询
    @return: [{
            "bk_cloud_id": 1,
            "bk_host_id": 1,
            "bk_host_innerip": "127.0.0.1",
            "bk_mac": "",
            "bk_os_type": null
        }]
    """
    ipv4_host_list = []
    if not ipv4_list:
        return ipv4_host_list

    if is_biz_set:
        # 全业务查询ipv4主机
        ipv4_host_list = cmdb.get_business_set_host(
            tenant_id,
            executor,
            supplier_account,
            ["bk_host_id", "bk_host_innerip_v6", "bk_cloud_id", "bk_agent_id", "bk_host_innerip"],
            ipv4_list,
        )
    else:
        # 在本业务下查询ipv4主机
        ipv4_host_list = cmdb.get_business_host(
            tenant_id,
            executor,
            bk_biz_id,
            supplier_account,
            ["bk_host_id", "bk_host_innerip_v6", "bk_cloud_id", "bk_agent_id", "bk_host_innerip"],
            ipv4_list,
        )

    # 如果接口报错or其他的导致返回个空，则return []， 上层的compare逻辑会保证插件执行失败
    if not ipv4_host_list:
        logger.error(
            "[get_ip_v4_hosts] list_biz_hosts[ipv4] query failed, return empty list, "
            "ipv6_list = {}".format(ipv4_list)
        )
        return []
    return ipv4_host_list


def get_hosts_by_hosts_ids(tenant_id, executor, bk_biz_id, supplier_account, host_id_list):
    if not host_id_list:
        return {"result": True, "data": []}

    host_list = get_business_host_by_hosts_ids(
        tenant_id,
        executor,
        bk_biz_id,
        supplier_account,
        ["bk_host_id", "bk_host_innerip_v6", "bk_cloud_id", "bk_agent_id", "bk_host_innerip"],
        host_id_list,
    )
    # 如果接口报错or其他的导致返回个空，则return []， 上层的compare逻辑会保证插件执行失败
    if not host_list:
        logger.info(
            "[get_hosts_by_hosts_ids] list_biz_hosts[host_id] query failed, return empty list, "
            "ipv6_list = {}".format(host_id_list)
        )
        return {"result": False, "message": "list_biz_hosts[host_id] query failed, return empty list"}

    result, message = compare_ip_list(host_list, host_id_list, "bk_host_id")
    if not result:
        logger.info("[get_hosts_by_hosts_ids] list_biz_hosts[bk_host_id] query failed, " "message = {}".format(message))
        return {"result": False, "message": message}
    return {"result": True, "data": host_list}


# 第二层的查询，相较于上一层查询，带了一些返回值的封装以及额外的校验逻辑


def get_ipv6_host_list(tenant_id, executor, bk_biz_id, supplier_account, ipv6_list, is_biz_set=False):
    """
    查询ipv
    @param tenant_id: 租户 ID
    @param executor:  执行人
    @param bk_biz_id: 业务id
    @param supplier_account : 服务商
    @param ipv6_list: ipv6 列表
    @param is_biz_set: 是否跨业务
    @return: {
        "result": True,
        "data": [{
            "bk_cloud_id": 0,
            "bk_host_id": 1,
            "bk_host_innerip_v6": "0:::1",
            "bk_mac": "",
            "bk_os_type": null
        }]
    }
    """
    ipv6_host_list = get_ipv6_hosts(tenant_id, executor, bk_biz_id, supplier_account, ipv6_list, is_biz_set)
    result, message = compare_ip_list(host_list=ipv6_host_list, ip_list=ipv6_list, host_key="bk_host_innerip_v6")
    if not result:
        logger.info(
            "[cc_get_host_by_innerip_with_ipv6] list_biz_hosts[ipv6] query failed, " "message = {}".format(message)
        )
        return {"result": False, "message": message}
    return {"result": True, "data": ipv6_host_list}


def get_ipv4_host_with_cloud_list(tenant_id, executor, bk_biz_id, supplier_account, ipv4_list_with_cloud_id,
                                  is_biz_set=False):
    """
    # 查询所有ip_v4带管控区域带主机，并选出指定的ip，如果ip+cloud_id重复，则报错
    @param tenant_id: 租户 ID
    @param executor: 执行人
    @param bk_biz_id: 业务id
    @param supplier_account:
    @param ipv4_list_with_cloud_id: ["0:127.0.0.1"]
    @param is_biz_set:
    @return:  {
        "result": True,
        "data": [{
            "bk_cloud_id": 0,
            "bk_host_id": 1,
            "bk_host_innerip_v6": "0:::1",
            "bk_mac": "",
            "bk_os_type": null
        }]
    """
    ipv4_host_with_cloud_valid = get_ipv4_hosts_with_cloud(
        tenant_id, executor, bk_biz_id, supplier_account, ipv4_list_with_cloud_id, is_biz_set
    )
    # 再比较查询结果和输入结果数量是否一致
    result, message = compare_ip_with_cloud_list(host_list=ipv4_host_with_cloud_valid, ip_list=ipv4_list_with_cloud_id)
    if not result:
        logger.info(
            "[cc_get_host_by_innerip_with_ipv6] list_biz_hosts[ipv4] query failed, return empty list, "
            "message = {}".format(message)
        )
        return {"result": False, "message": message}

    return {"result": True, "data": ipv4_host_with_cloud_valid}


def get_ipv6_host_list_with_cloud_list(tenant_id, executor, bk_biz_id, supplier_account, ipv6_list_with_cloud,
                                       is_biz_set=False):
    """
    # 查询所有ip_v6带管控区域带主机，并选出指定的ip，如果ip+cloud_id重复，则报错
    @param tenant_id: 租户 ID
    @param executor: 执行人
    @param bk_biz_id: 业务id
    @param supplier_account:
    @param ipv4_list_with_cloud_id: ["0:[0000:0000:0000:0000:0000:0000]"]
    @param is_biz_set: False
    @return:  {
        "result": True,
        "data": [{
            "bk_cloud_id": 0,
            "bk_host_id": 1,
            "bk_host_innerip_v6": "0:::1",
            "bk_mac": "",
            "bk_os_type": null
        }]
    """
    ipv6_host_with_cloud_valid = get_ipv6_hosts_with_cloud(
        tenant_id, executor, bk_biz_id, supplier_account, ipv6_list_with_cloud, is_biz_set
    )

    result, message = compare_ipv6_with_cloud_list(host_list=ipv6_host_with_cloud_valid, ip_list=ipv6_list_with_cloud)
    if not result:
        logger.info(
            "[get_ipv6_host_list_with_cloud_list] list_biz_hosts[ipv6] query failed" "message = {}".format(message)
        )
        return {"result": False, "message": message}

    return {"result": True, "data": ipv6_host_with_cloud_valid}


def get_ipv4_host_list(tenant_id, executor, bk_biz_id, supplier_account, ipv4_list, is_biz_set=False):
    """
    # 查询所有ip_v4的主机
    @param tenant_id: 租户 ID
    @param executor:
    @param bk_biz_id:
    @param supplier_account:
    @param ipv4_list:
    @param is_biz_set:
    @return:
    """
    ipv4_host_list = get_ipv4_hosts(tenant_id, executor, bk_biz_id, supplier_account, ipv4_list, is_biz_set)
    result, message = compare_ip_list(host_list=ipv4_host_list, ip_list=ipv4_list)
    if not result:
        logger.info(
            "[cc_get_host_by_innerip_with_ipv6] list_biz_hosts[ipv4] query failed, return empty list, "
            "message = {}".format(message)
        )
        return {"result": False, "message": message}

    return {"result": True, "data": ipv4_host_list}


# 以下的代码用在job跨业务的场景中, 该场景需要先将本业务的ip查出来，并返回本业务没有查到的ip，去全业务查，隐藏在compare_ip_list_and_return逻辑中，
# 当查询到的主机多于实际的主机时，说明查到了重复的主机，则报错，少于时说明有没有查询到的主机，则返回没有查询到的主机列表


def compare_ip_list_and_return_with_cloud(host_list, ip_list, host_key="bk_host_innerip"):
    if len(host_list) > len(ip_list):
        # find repeat innerip host
        return_innerip_set = {"{}:{}".format(host["bk_cloud_id"], host[host_key]) for host in host_list}
        mutiple_innerip_hosts = return_innerip_set.difference(set(ip_list))
        raise Exception("mutiple same innerip host found: {}".format(", ".join(mutiple_innerip_hosts)))
    if len(host_list) < len(ip_list):
        return_innerip_set = {"{}:{}".format(host["bk_cloud_id"], host[host_key]) for host in host_list}
        absent_innerip = set(ip_list).difference(return_innerip_set)
        return absent_innerip
    return set()


def compare_ipv6_list_and_return_with_cloud(host_list, ip_list):
    if len(host_list) > len(ip_list):
        # find repeat innerip host
        return_innerip_set = {"{}:[{}]".format(host["bk_cloud_id"], host["bk_host_innerip_v6"]) for host in host_list}
        mutiple_innerip_hosts = return_innerip_set.difference(set(ip_list))
        raise Exception("mutiple same innerip host found: {}".format(", ".join(mutiple_innerip_hosts)))
    if len(host_list) < len(ip_list):
        return_innerip_set = {"{}:[{}]".format(host["bk_cloud_id"], host["bk_host_innerip_v6"]) for host in host_list}
        absent_innerip = set(ip_list).difference(return_innerip_set)
        return absent_innerip
    return set()


def cc_get_host_by_innerip_with_ipv6_across_business(tenant_id, executor, bk_biz_id, ip_str, supplier_account,
                                                     is_biz_set=False):
    """
    查询主机，并返回在本业务查询到的主机和在本业务下查不到的主机
    @param tenant_id: 租户 ID
    @param executor: 执行人
    @param bk_biz_id: 业务id
    @param ip_str: ip文本字符串
    @param supplier_account: 服务商
    @param is_biz_set: 是否跨业务查询
    @return:
    """
    ipv6_list, ipv4_list, host_id_list, ipv4_list_with_cloud_id, ipv6_list_with_cloud_id = extract_ip_from_ip_str(
        ip_str
    )

    # 查询ipv6带管控区域的主机
    ipv6_host_with_cloud_valid = get_ipv6_hosts_with_cloud(
        tenant_id, executor, bk_biz_id, supplier_account, ipv6_list_with_cloud_id, is_biz_set
    )

    ipv6_with_cloud_absent_innerip = compare_ipv6_list_and_return_with_cloud(
        host_list=ipv6_host_with_cloud_valid, ip_list=ipv6_list_with_cloud_id
    )

    # 查询ipv6的主机
    ipv6_host_list = get_ipv6_hosts(tenant_id, executor, bk_biz_id, supplier_account, ipv6_list, is_biz_set)

    # 说明查出来还少了一些，将没查到的收集起来:
    ipv6_absent_innerip = compare_ip_list_and_return(
        host_list=ipv6_host_list, ip_list=ipv6_list, host_key="bk_host_innerip_v6"
    )

    # 查询ipv4的主机
    ipv4_host_list = get_ipv4_hosts(tenant_id, executor, bk_biz_id, supplier_account, ipv4_list, is_biz_set)

    ipv4_absent_innerip = compare_ip_list_and_return(host_list=ipv4_host_list, ip_list=ipv4_list)

    # 提取ipv4带管控区域的列表, 确定有哪些没查出来的
    ipv4_host_with_cloud_valid = get_ipv4_hosts_with_cloud(
        tenant_id, executor, bk_biz_id, supplier_account, ipv4_list_with_cloud_id, is_biz_set
    )
    # 再比较查询结果和输入结果数量是否一致
    ipv4_with_cloud_absent_innerip = compare_ip_list_and_return_with_cloud(
        host_list=ipv4_host_with_cloud_valid, ip_list=ipv4_list_with_cloud_id
    )
    # host_id 不作查询
    host_list = [{"bk_host_id": host_id} for host_id in host_id_list]
    # 本业务查到的host集合
    host_list = ipv6_host_list + ipv4_host_list + ipv4_host_with_cloud_valid + host_list + ipv6_host_with_cloud_valid
    # 返回依次表示 本业务查到的ip列表，没查到的ipv4列表，没查到的ipv4带管控区域列表，没查到的ipv6列表
    return (
        host_list,
        list(ipv4_absent_innerip),
        list(ipv4_with_cloud_absent_innerip),
        list(ipv6_absent_innerip),
        list(ipv6_with_cloud_absent_innerip),
    )


def format_host_with_ipv6(host, with_cloud=False):
    """如果host ipv4字段存在，优先返回ipv4，否则返回ipv6"""
    if host.get("bk_host_innerip"):
        return f'{host["bk_cloud_id"]}:{host["bk_host_innerip"]}' if with_cloud else f'{host["bk_host_innerip"]}'
    if host.get("bk_host_innerip_v6"):
        return f'{host["bk_cloud_id"]}:[{host["bk_host_innerip_v6"]}]' if with_cloud else host["bk_host_innerip_v6"]
    raise ValueError("bk_host_innerip and bk_host_innerip_v6 can not both be empty")
