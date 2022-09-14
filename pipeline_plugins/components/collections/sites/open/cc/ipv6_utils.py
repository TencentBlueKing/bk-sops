# -*- coding: utf-8 -*-
import logging
from collections import Counter

from gcloud.utils import cmdb
from gcloud.utils.ip import extract_ip_from_ip_str

logger = logging.getLogger("root")


def compare_ip_list(host_list, ip_list, host_key="bk_host_innerip"):
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


def compare_ip_with_cloud_list(host_list, ip_list, host_key="bk_host_innerip"):
    if len(host_list) > len(ip_list):
        # find repeat innerip host
        return_innerip_set = {"{}:{}".format(host["bk_cloud_id"], host[host_key]) for host in host_list}
        mutiple_innerip_hosts = return_innerip_set.difference(set(ip_list))
        return (
            False,
            "mutiple same innerip host found: {}".format(", ".join(mutiple_innerip_hosts)),
        )
    if len(host_list) < len(ip_list):
        return_innerip_set = {host[host_key] for host in host_list}
        absent_innerip = set(ip_list).difference(return_innerip_set)

        return False, "ip not found in business: {}".format(", ".join(absent_innerip))

    return True, ""


def check_ip_v6_cloud(ip_v4_host_with_cloud_list):
    """
    检查cc查询结果中，是否有云区域+ip重复的主机
    @param ip_v4_host_with_cloud_list:
    @return:
    """
    repeated_hosts = []
    data = []
    for host in ip_v4_host_with_cloud_list:
        bk_cloud_id = host["bk_cloud_id"]
        bk_host_innerip = host["bk_host_innerip"]
        plat_ip = "{}:{}".format(bk_cloud_id, bk_host_innerip)
        # 已有的ip
        if plat_ip not in data:
            data.append(plat_ip)
        else:
            repeated_hosts.append(plat_ip)

        return repeated_hosts


def get_ip_v6_hosts(executor, bk_biz_id, supplier_account, ipv6_list, is_biz_set=False):
    ip_v6_host_list = []
    if not ipv6_list:
        return ip_v6_host_list

    if is_biz_set:
        # 去查询ip_v6 相关的主机信息
        ip_v6_host_list = cmdb.get_business_set_host_ipv6(
            executor,
            supplier_account,
            ["bk_host_id", "bk_host_innerip_v6", "bk_cloud_id"],
            ipv6_list,
        )
    else:
        # 去查询ip_v6 相关的主机信息
        ip_v6_host_list = cmdb.get_business_host_ipv6(
            executor,
            bk_biz_id,
            supplier_account,
            ["bk_host_id", "bk_host_innerip_v6", "bk_cloud_id"],
            ipv6_list,
        )
    if not ip_v6_host_list:
        logger.info(
            "[get_ip_v6_hosts] list_biz_hosts[ipv6] query failed, return empty list, "
            "ipv6_list = {}".format(ipv6_list)
        )
        return []

    return ip_v6_host_list


def get_ip_v4_host_with_cloud(executor, bk_biz_id, supplier_account, ipv4_list_with_cloud_id, is_biz_set=False):
    ip_v4_host_with_cloud_valid = []
    if not ipv4_list_with_cloud_id:
        return ip_v4_host_with_cloud_valid
    ip_list = [_ip.split(":")[1] for _ip in ipv4_list_with_cloud_id]

    if is_biz_set:
        ip_v4_host_with_cloud_list = cmdb.get_business_set_host(
            executor, supplier_account, ["bk_host_id", "bk_host_innerip", "bk_cloud_id"], ip_list
        )
    else:
        ip_v4_host_with_cloud_list = cmdb.get_business_host(
            executor, bk_biz_id, supplier_account, ["bk_host_id", "bk_host_innerip", "bk_cloud_id"], ip_list
        )

    if not ip_v4_host_with_cloud_list:
        logger.info(
            "[get_ip_v4_host_with_cloud] list_biz_hosts[ipv4] query failed, return empty list, "
            "ipv6_list = {}".format(ipv4_list_with_cloud_id)
        )
        return []

    check_result = check_ip_v6_cloud(ip_v4_host_with_cloud_list)
    if check_result:
        raise Exception(
            "list_biz_hosts[ipv4] query failed, "
            "the host with the same IP address and cloud area is displayed,"
            "repeated_list = {}".format(check_result)
        )

    for ip_info in ip_v4_host_with_cloud_list:
        # 清洗出来所有带云区域带ip
        plat_ip = "{}:{}".format(ip_info.get("bk_cloud_id", -1), ip_info.get("bk_host_innerip", ""))
        if plat_ip in ipv4_list_with_cloud_id:
            ip_v4_host_with_cloud_valid.append(ip_info)

    return ip_v4_host_with_cloud_valid


def get_ip_v4_hosts(executor, bk_biz_id, supplier_account, ipv4_list, is_biz_set=False):
    ip_v4_host_list = []
    if not ipv4_list:
        return ip_v4_host_list

    if is_biz_set:
        ip_v4_host_list = cmdb.get_business_set_host(
            executor,
            supplier_account,
            ["bk_host_id", "bk_host_innerip", "bk_cloud_id"],
            ipv4_list,
        )
    else:
        ip_v4_host_list = cmdb.get_business_host(
            executor, bk_biz_id, supplier_account, ["bk_host_id", "bk_host_innerip", "bk_cloud_id"], ipv4_list
        )

    if not ip_v4_host_list:
        logger.info(
            "[get_ip_v4_hosts] list_biz_hosts[ipv4] query failed, return empty list, "
            "ipv6_list = {}".format(ipv4_list)
        )
        return []
    return ip_v4_host_list


def get_ip_v6_host_list(executor, bk_biz_id, supplier_account, ipv6_list, is_biz_set=False):
    # 查询所有ip_v6的主机
    ip_v6_host_list = get_ip_v6_hosts(executor, bk_biz_id, supplier_account, ipv6_list, is_biz_set)
    result, message = compare_ip_list(host_list=ip_v6_host_list, ip_list=ipv6_list, host_key="bk_host_innerip_v6")
    if not result:
        logger.info(
            "[cc_get_host_by_innerip_with_ipv6] list_biz_hosts[ipv6] query failed, return empty list, "
            "message = {}".format(message)
        )
        return {"result": False, "message": message}
    return {"result": True, "data": ip_v6_host_list}


def get_ip_v4_host_with_cloud_list(executor, bk_biz_id, supplier_account, ipv4_list_with_cloud_id, is_biz_set=False):
    """
    # 查询所有ip_v4带云区域带主机，并选出指定的ip，如果ip+cloud_id重复，则报错
    @param executor:
    @param bk_biz_id:
    @param supplier_account:
    @param ipv4_list_with_cloud_id:
    @param is_biz_set:
    @return:
    """
    ip_v4_host_with_cloud_valid = get_ip_v4_host_with_cloud(
        executor, bk_biz_id, supplier_account, ipv4_list_with_cloud_id, is_biz_set
    )
    ip_list = [_ip.split(":")[1] for _ip in ipv4_list_with_cloud_id]
    # 再比较查询结果和输入结果数量是否一致
    result, message = compare_ip_with_cloud_list(host_list=ip_v4_host_with_cloud_valid, ip_list=ip_list)
    if not result:
        logger.info(
            "[cc_get_host_by_innerip_with_ipv6] list_biz_hosts[ipv4] query failed, return empty list, "
            "message = {}".format(message)
        )
        return {"result": False, "message": message}

    return {"result": True, "data": ip_v4_host_with_cloud_valid}


# 查询所有ip_v4 不带云区域带主机，结果重复则返回False
def get_ip_v4_host_list(executor, bk_biz_id, supplier_account, ipv4_list, is_biz_set=False):
    ip_v4_host_list = get_ip_v4_hosts(executor, bk_biz_id, supplier_account, ipv4_list, is_biz_set)
    result, message = compare_ip_list(host_list=ip_v4_host_list, ip_list=ipv4_list)
    if not result:
        logger.info(
            "[cc_get_host_by_innerip_with_ipv6] list_biz_hosts[ipv4] query failed, return empty list, "
            "message = {}".format(message)
        )
        return {"result": False, "message": message}

    return {"result": True, "data": ip_v4_host_list}


def compare_ip_list_and_return(host_list, ip_list, host_key="bk_host_innerip"):
    if len(host_list) > len(ip_list):
        # find repeat innerip host
        host_counter = Counter([host[host_key] for host in host_list])
        mutiple_innerip_hosts = [innerip for innerip, count in host_counter.items() if count > 1]
        raise Exception("mutiple same innerip host found: {}".format(", ".join(mutiple_innerip_hosts)))
    if len(host_list) < len(ip_list):
        return_innerip_set = {host[host_key] for host in host_list}
        absent_innerip = set(ip_list).difference(return_innerip_set)
        return absent_innerip
    return []


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


def cc_get_host_by_innerip_with_ipv6_across_business(executor, bk_biz_id, ip_str, supplier_account, is_biz_set=False):
    ipv6_list, ipv4_list, host_id_list, ipv4_list_with_cloud_id = extract_ip_from_ip_str(ip_str)

    ip_v6_host_list = get_ip_v6_hosts(executor, bk_biz_id, supplier_account, ipv6_list, is_biz_set)

    # 说明查出来还少了一些，将没查到的收集起来:
    ip_v6_absent_innerip = compare_ip_list_and_return(
        host_list=ip_v6_host_list, ip_list=ipv6_list, host_key="bk_host_innerip_v6"
    )

    ip_v4_host_list = get_ip_v4_hosts(executor, bk_biz_id, supplier_account, ipv4_list, is_biz_set)

    ip_v4_absent_innerip = compare_ip_list_and_return(host_list=ip_v4_host_list, ip_list=ipv4_list)

    # 提取ipv4的列表, 确定有哪些没查出来的
    ip_list = [_ip.split(":")[1] for _ip in ipv4_list_with_cloud_id]
    ip_v4_host_with_cloud_valid = get_ip_v4_host_with_cloud(
        executor, bk_biz_id, supplier_account, ipv4_list_with_cloud_id, is_biz_set
    )
    # 再比较查询结果和输入结果数量是否一致
    ip_v4_with_cloud_absent_innerip = compare_ip_list_and_return_with_cloud(
        host_list=ip_v4_host_with_cloud_valid, ip_list=ip_list
    )

    # host_id 不作查询
    host_list = [{"bk_host_id": host_id} for host_id in host_id_list]
    # 本业务查到的host集合
    host_list = ip_v6_host_list + ip_v4_host_list + ip_v4_host_with_cloud_valid + host_list

    return host_list, list(ip_v4_absent_innerip), list(ip_v4_with_cloud_absent_innerip), list(ip_v6_absent_innerip)
