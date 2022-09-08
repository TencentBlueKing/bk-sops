# -*- coding: utf-8 -*-
import logging
from collections import Counter

from gcloud.utils import cmdb

logger = logging.getLogger("celery")


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


# 查询所有ip_v6的主机
def get_ip_v6_host_list(executor, bk_biz_id, supplier_account, ipv6_list):
    ip_v6_host_list = []
    if not ipv6_list:
        return {"result": True, "data": ip_v6_host_list}

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
            "[cc_get_host_by_innerip_with_ipv6] list_biz_hosts[ipv6] query failed, return empty list, "
            "ipv6_list = {}".format(ipv6_list)
        )
        return {
            "result": False,
            "message": "list_biz_hosts[ipv6] query failed, return empty list, ipv6_list = {}".format(ipv6_list),
        }
    result, message = compare_ip_list(host_list=ip_v6_host_list, ip_list=ipv6_list, host_key="bk_host_innerip_v6")
    if not result:
        logger.info(
            "[cc_get_host_by_innerip_with_ipv6] list_biz_hosts[ipv6] query failed, return empty list, "
            "message = {}".format(message)
        )
        return {"result": False, "message": message}
    return {"result": True, "data": ip_v6_host_list}


# 查询所有ip_v4带云区域带主机，并选出指定的ip，如果ip+cloud_id重复，则报错
def get_ip_v4_host_with_cloud_list(executor, bk_biz_id, supplier_account, ipv4_list_with_cloud_id):
    ip_v4_host_with_cloud_valid = []
    if not ipv4_list_with_cloud_id:
        return {"result": True, "data": ip_v4_host_with_cloud_valid}
    ip_list = [_ip.split(":")[1] for _ip in ipv4_list_with_cloud_id]
    ip_v4_host_with_cloud_list = cmdb.get_business_host(
        executor, bk_biz_id, supplier_account, ["bk_host_id", "bk_host_innerip", "bk_cloud_id"], ip_list
    )
    if not ip_v4_host_with_cloud_list:
        logger.info(
            "[cc_get_host_by_innerip_with_ipv6] list_biz_hosts[ipv4] query failed, return empty list, "
            "ipv6_list = {}".format(ipv4_list_with_cloud_id.values())
        )
        return {
            "result": False,
            "message": "list_biz_hosts[ipv4] query failed, return empty list, ipv4_list = {}".format(
                ipv4_list_with_cloud_id
            ),
        }

    check_result = check_ip_v6_cloud(ip_v4_host_with_cloud_list)
    if check_result:
        return {
            "result": False,
            "message": "list_biz_hosts[ipv4] query failed, "
            "the host with the same IP address and cloud area is displayed,"
            "repeated_list = {}".format(check_result),
        }

    for ip_info in ip_v4_host_with_cloud_list:
        # 清洗出来所有带云区域带ip

        plat_ip = "{}:{}".format(ip_info.get("bk_cloud_id", -1), ip_info.get("bk_host_innerip", ""))
        if plat_ip in ipv4_list_with_cloud_id:
            ip_v4_host_with_cloud_valid.append(ip_info)

    # 再比较查询结果和输入结果数量是否一致
    result, message = compare_ip_list(host_list=ip_v4_host_with_cloud_valid, ip_list=ip_list)
    if not result:
        logger.info(
            "[cc_get_host_by_innerip_with_ipv6] list_biz_hosts[ipv4] query failed, return empty list, "
            "message = {}".format(message)
        )
        return {"result": False, "message": message}

    return {"result": True, "data": ip_v4_host_with_cloud_valid}


# 查询所有ip_v4 不带云区域带主机，结果重复则返回False
def get_ip_v4_host_list(executor, bk_biz_id, supplier_account, ipv4_list):
    ip_v4_host_list = []
    if not ipv4_list:
        return {"result": True, "data": ip_v4_host_list}
    ip_v4_host_list = cmdb.get_business_host(
        executor, bk_biz_id, supplier_account, ["bk_host_id", "bk_host_innerip", "bk_cloud_id"], ipv4_list
    )
    if not ip_v4_host_list:
        logger.info(
            "[cc_get_host_by_innerip_with_ipv6] list_biz_hosts[ipv4] query failed, return empty list, "
            "ipv6_list = {}".format(ipv4_list)
        )
        return {
            "result": False,
            "message": "list_biz_hosts[ipv4] query failed, return empty list, ipv4_list = {}".format(ipv4_list),
        }

    result, message = compare_ip_list(host_list=ip_v4_host_list, ip_list=ipv4_list)
    if not result:
        logger.info(
            "[cc_get_host_by_innerip_with_ipv6] list_biz_hosts[ipv4] query failed, return empty list, "
            "message = {}".format(message)
        )
        return {"result": False, "message": message}

    return {"result": True, "data": ip_v4_host_list}
