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
import re
from collections import Counter

from cryptography.fernet import Fernet
from django.utils.translation import gettext_lazy as _

import env
from gcloud.conf import settings
from gcloud.core.models import EngineConfig
from gcloud.utils import cmdb
from gcloud.utils.ip import extract_ip_from_ip_str, get_ip_by_regex, get_ipv6_and_cloud_id_from_ipv6_cloud_str
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.variables.utils import find_module_with_relation

__all__ = [
    "cc_get_ips_info_by_str",
    "get_job_instance_url",
    "get_node_callback_url",
    "plat_ip_reg",
    "ip_pattern",
    "get_nodeman_job_url",
    "get_difference_ip_list",
    "get_biz_ip_from_frontend",
]

JOB_APP_CODE = "bk_job"

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
ip_re = r"(?<!\d)((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)(?!\d)"
plat_ip_reg = re.compile(r"(\d+:)((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)(?!\d)")
set_module_ip_reg = re.compile(r"[\u4e00-\u9fa5\w]+\|[\u4e00-\u9fa5\w]+\|" + ip_re)
ip_pattern = re.compile(ip_re)


def compare_ip_list_and_return(host_list, ip_list, host_key="bk_host_innerip", raise_exception=True):
    if len(host_list) > len(ip_list):
        # find repeat innerip host
        host_counter = Counter([host[host_key] for host in host_list])
        mutiple_innerip_hosts = [innerip for innerip, count in host_counter.items() if count > 1]
        if raise_exception:
            raise Exception("mutiple same innerip host found: {}".format(", ".join(mutiple_innerip_hosts)))
        return mutiple_innerip_hosts
    if len(host_list) < len(ip_list):
        return_innerip_set = {host[host_key] for host in host_list}
        absent_innerip = set(ip_list).difference(return_innerip_set)
        return absent_innerip
    return set()


def get_ipv6_info_list(tenant_id, username, biz_cc_id, supplier_account, ipv6_list):
    ipv6_info_list = cmdb.get_business_host_topo(
        tenant_id=tenant_id,
        username=username,
        bk_biz_id=biz_cc_id,
        supplier_account=supplier_account,
        host_fields=["bk_host_innerip_v6", "bk_host_id", "bk_cloud_id"],
        property_filters={
            "host_property_filter": {
                "condition": "AND",
                "rules": [{"field": "bk_host_innerip_v6", "operator": "in", "value": ipv6_list}],
            }
        },
    )
    if len(ipv6_list) != len(ipv6_info_list):
        return (
            False,
            compare_ip_list_and_return(
                [item["host"] for item in ipv6_info_list],
                ipv6_list,
                host_key="bk_host_innerip_v6",
                raise_exception=False,
            ),
        )

    ip_result = []
    for ip_info in ipv6_info_list:
        ip_result.append(
            {
                "InnerIP": ip_info["host"]["bk_host_innerip_v6"],
                "HostID": ip_info["host"]["bk_host_id"],
                "Source": ip_info["host"].get("bk_cloud_id", -1),
                "Sets": ip_info["set"],
                "Modules": ip_info["module"],
            }
        )

    return True, ip_result


def get_ipv4_info_list(tenant_id, username, biz_cc_id, supplier_account, ipv4_list):
    ip_result = []

    if not ipv4_list:
        return True, []

    ipv4_info_list = cmdb.get_business_host_topo(
        tenant_id=tenant_id,
        username=username,
        bk_biz_id=biz_cc_id,
        supplier_account=supplier_account,
        host_fields=["bk_host_innerip", "bk_host_id", "bk_cloud_id"],
        ip_list=ipv4_list,
    )

    if len(ipv4_list) != len(ipv4_info_list):
        return (
            False,
            compare_ip_list_and_return(
                [item["host"] for item in ipv4_info_list], ipv4_list, host_key="bk_host_innerip", raise_exception=False
            ),
        )

    for ip_info in ipv4_info_list:
        ip_result.append(
            {
                "InnerIP": ip_info["host"][
                    "bk_host_innerip"
                ],  # 即使多个host命中，也都是同一个主机id，这里以第一个合法host为标识
                "HostID": ip_info["host"]["bk_host_id"],
                "Source": ip_info["host"].get("bk_cloud_id", -1),
                "Sets": ip_info["set"],
                "Modules": ip_info["module"],
            }
        )

    return True, ip_result


def get_ipv4_info_list_with_cloud_id(tenant_id, username, biz_cc_id, supplier_account, ipv4_list_with_cloud_id):
    ip_list = [_ip.split(":")[1] for _ip in ipv4_list_with_cloud_id]

    if not ip_list:
        return True, []

    ipv4_info_list = cmdb.get_business_host_topo(
        tenant_id=tenant_id,
        username=username,
        bk_biz_id=biz_cc_id,
        supplier_account=supplier_account,
        host_fields=["bk_host_innerip", "bk_host_id", "bk_cloud_id"],
        ip_list=ip_list,
    )

    ipv4_info_with_cloud_valid = []
    for ip_info in ipv4_info_list:
        # 清洗出来所有带管控区域带ip
        plat_ip = "{}:{}".format(ip_info["host"].get("bk_cloud_id", -1), ip_info["host"].get("bk_host_innerip", ""))
        if plat_ip in ipv4_list_with_cloud_id:
            ipv4_info_with_cloud_valid.append(ip_info)

    # 再比较查询结果和输入结果数量是否一致
    compare_data = compare_ip_list_and_return(
        [item["host"] for item in ipv4_info_with_cloud_valid], ip_list, "bk_host_innerip", raise_exception=False
    )
    if compare_data:
        return False, compare_data
    ip_result = []
    for item in ipv4_info_with_cloud_valid:
        ip_result.append(
            {
                "InnerIP": item["host"][
                    "bk_host_innerip"
                ],  # 即使多个host命中，也都是同一个主机id，这里以第一个合法host为标识
                "HostID": item["host"]["bk_host_id"],
                "Source": item["host"].get("bk_cloud_id", -1),
                "Sets": item["set"],
                "Modules": item["module"],
            }
        )

    return True, ip_result


def get_ipv6_info_list_with_cloud_id(tenant_id, username, biz_cc_id, supplier_account, ipv6_list_with_cloud_id):
    if not ipv6_list_with_cloud_id:
        return True, []

    # 先把所有的ip拿出来去查询符合条件的主机
    ipv6_list = []
    for item in ipv6_list_with_cloud_id:
        _, ip = get_ipv6_and_cloud_id_from_ipv6_cloud_str(item)
        ipv6_list.append(ip)

    ipv6_info_list = cmdb.get_business_host_topo(
        tenant_id=tenant_id,
        username=username,
        bk_biz_id=biz_cc_id,
        supplier_account=supplier_account,
        host_fields=["bk_host_innerip_v6", "bk_host_id", "bk_cloud_id"],
        property_filters={
            "host_property_filter": {
                "condition": "AND",
                "rules": [{"field": "bk_host_innerip_v6", "operator": "in", "value": ipv6_list}],
            }
        },
    )

    ipv6_info_with_cloud_valid = []
    for ip_info in ipv6_info_list:
        # 清洗出来所有带管控区域带ip
        plat_ip = "{}:[{}]".format(
            ip_info["host"].get("bk_cloud_id", -1), ip_info["host"].get("bk_host_innerip_v6", "")
        )
        if plat_ip in ipv6_list_with_cloud_id:
            ipv6_info_with_cloud_valid.append(ip_info)

    compare_data = compare_ip_list_and_return(
        [item["host"] for item in ipv6_info_with_cloud_valid],
        ipv6_list,
        host_key="bk_host_innerip_v6",
        raise_exception=False,
    )

    if compare_data:
        return False, compare_data

    ip_result = []
    for item in ipv6_info_with_cloud_valid:
        ip_result.append(
            {
                "InnerIP": item["host"][
                    "bk_host_innerip_v6"
                ],  # 即使多个host命中，也都是同一个主机id，这里以第一个合法host为标识
                "HostID": item["host"]["bk_host_id"],
                "Source": item["host"].get("bk_cloud_id", -1),
                "Sets": item["set"],
                "Modules": item["module"],
            }
        )

    return True, ip_result


def get_host_info_list(tenant_id, username, biz_cc_id, supplier_account, host_id_list):
    ip_result = []
    host_info_list = cmdb.get_business_host_topo(
        tenant_id=tenant_id,
        username=username,
        bk_biz_id=biz_cc_id,
        supplier_account=supplier_account,
        host_fields=["bk_host_innerip_v6", "bk_host_innerip", "bk_host_id", "bk_cloud_id"],
        property_filters={
            "host_property_filter": {
                "condition": "AND",
                "rules": [
                    {"field": "bk_host_id", "operator": "in", "value": [int(host_id) for host_id in host_id_list]}
                ],
            }
        },
    )
    if len(host_id_list) != len(host_info_list):
        return (
            False,
            compare_ip_list_and_return(
                [item["host"] for item in host_info_list], host_id_list, host_key="bk_host_id", raise_exception=False
            ),
        )

    # 默认使用bk_host_innerip地址
    for ip_info in host_info_list:
        bk_host_innerip = ip_info["host"]["bk_host_innerip"]
        if not bk_host_innerip:
            bk_host_innerip = ip_info["host"]["bk_host_innerip_v6"]

        ip_result.append(
            {
                "InnerIP": bk_host_innerip,  # 即使多个host命中，也都是同一个主机id，这里以第一个合法host为标识
                "HostID": ip_info["host"]["bk_host_id"],
                "Source": ip_info["host"].get("bk_cloud_id", -1),
                "Sets": ip_info["set"],
                "Modules": ip_info["module"],
            }
        )

    return True, ip_result


def cc_get_ips_info_by_str_ipv6(tenant_id, username, biz_cc_id, ip_str, use_cache=True):
    ipv6_list, ipv4_list, host_id_list, ipv4_list_with_cloud_id, ipv6_list_with_cloud_id = extract_ip_from_ip_str(
        ip_str
    )

    supplier_account = supplier_account_for_business(biz_cc_id)

    ipv6_result, ipv6_data = get_ipv6_info_list(tenant_id, username, biz_cc_id, supplier_account, ipv6_list)
    if not ipv6_result:
        return {"result": False, "ip_result": [], "ip_count": 0, "invalid_ip": ipv6_data}

    # ipv6带管控区域
    ipv6_list_with_cloud_id_result, ipv6_list_with_cloud_id_data = get_ipv6_info_list_with_cloud_id(
        tenant_id, username, biz_cc_id, supplier_account, ipv6_list_with_cloud_id
    )
    if not ipv6_list_with_cloud_id_result:
        return {"result": False, "ip_result": [], "ip_count": 0, "invalid_ip": ipv6_list_with_cloud_id_data}

    ipv4_result, ipv4_data = get_ipv4_info_list(tenant_id, username, biz_cc_id, supplier_account, ipv4_list)
    if not ipv4_result:
        return {"result": False, "ip_result": [], "ip_count": 0, "invalid_ip": ipv4_data}

    host_result, host_data = get_host_info_list(tenant_id, username, biz_cc_id, supplier_account, host_id_list)
    if not host_result:
        return {"result": False, "ip_result": [], "ip_count": 0, "invalid_ip": host_data}

    ipv4_with_cloud_id_result, ipv4_info_with_cloud_id_data = get_ipv4_info_list_with_cloud_id(
        tenant_id, username, biz_cc_id, supplier_account, ipv4_list_with_cloud_id
    )
    if not ipv4_with_cloud_id_result:
        return {"result": False, "ip_result": [], "ip_count": 0, "invalid_ip": ipv4_with_cloud_id_result}

    ip_result = ipv6_data + ipv4_data + host_data + ipv4_info_with_cloud_id_data + ipv6_list_with_cloud_id_data

    return {
        "result": True,
        "ip_result": ip_result,
        "ip_count": len(ip_result),
        "invalid_ip": [],
    }


def cc_get_ips_info_by_str(tenant_id, username, biz_cc_id, ip_str, use_cache=True):
    """
    @summary: 从ip_str中匹配出IP信息
    @param tenant_id: 租户 ID
    @param username
    @param biz_cc_id
    @param ip_str
    @param use_cache(deprecated)
    @note: 需要兼容的ip_str格式有
        1： IP，纯IP格式
        2： 集群名称|模块名称|IP，集群名称|模块名称|IP  这种格式可以唯一定位到一
            个IP（如果业务把相同IP放到同一模块，还是有问题）
        3： 管控区域ID:IP，管控区域ID:IP  这种格式可以唯一定位到一个IP，主要是兼容Job组件
            传参需要和获取Job作业模板步骤参数
    @return: {'result': True or False, 'data': [{'InnerIP': ,'HostID': ,
        'Source': , 'SetID': , 'SetName': , 'ModuleID': , 'ModuleName': , 'Sets': , 'Module': },{}]}
    """

    ip_input_list = get_ip_by_regex(ip_str)

    supplier_account = supplier_account_for_business(biz_cc_id)
    ip_list = cmdb.get_business_host_topo(
        tenant_id=tenant_id,
        username=username,
        bk_biz_id=biz_cc_id,
        supplier_account=supplier_account,
        host_fields=["bk_host_innerip", "bk_host_id", "bk_cloud_id"],
        ip_list=ip_input_list,
    )
    ip_result = []

    # 如果是格式2 集群名称|模块名称|IP，暂时不支持这种格式bk_host_innerip有多个值的情况
    if set_module_ip_reg.match(ip_str):
        set_module_ip_list = []
        for match in set_module_ip_reg.finditer(ip_str):
            set_module_ip_list.append(match.group())

        for ip_info in ip_list:
            match = False
            for parent_set in ip_info["set"]:
                if match:
                    break

                for parent_module in ip_info["module"]:
                    if match:
                        break

                    topo_ip = "{set}|{module}|{ip}".format(
                        set=parent_set["bk_set_name"],
                        module=parent_module["bk_module_name"],
                        ip=ip_info["host"].get("bk_host_innerip", ""),
                    )

                    if topo_ip in set_module_ip_list:
                        match = True
                        ip_result.append(
                            {
                                "InnerIP": ip_info["host"].get("bk_host_innerip", ""),
                                "HostID": ip_info["host"]["bk_host_id"],
                                "Source": ip_info["host"].get("bk_cloud_id", -1),
                                "SetID": parent_set["bk_set_id"],
                                "SetName": parent_set["bk_set_name"],
                                "ModuleID": parent_module["bk_module_id"],
                                "ModuleName": parent_module["bk_module_name"],
                                "Sets": ip_info["set"],
                                "Modules": ip_info["module"],
                            }
                        )

    # 格式3 管控区域ID:IP
    elif plat_ip_reg.match(ip_str):
        plat_ip = []
        for match in plat_ip_reg.finditer(ip_str):
            plat_ip.append(match.group())

        for ip_info in ip_list:
            valid_hosts = [
                x
                for x in ip_info["host"].get("bk_host_innerip", "").split(",")
                if x and f'{ip_info["host"].get("bk_cloud_id", -1)}:{x}' in plat_ip
            ]
            if valid_hosts:
                ip_result.append(
                    {
                        "InnerIP": valid_hosts[0],  # 即使多个host命中，也都是同一个主机id，这里以第一个合法host为标识
                        "HostID": ip_info["host"]["bk_host_id"],
                        "Source": ip_info["host"].get("bk_cloud_id", -1),
                        "Sets": ip_info["set"],
                        "Modules": ip_info["module"],
                    }
                )

    # 格式1 纯IP格式
    else:
        ip = []
        for match in ip_pattern.finditer(ip_str):
            ip.append(match.group())

        proccessed = set()
        for ip_info in ip_list:
            valid_hosts = [x for x in ip_info["host"].get("bk_host_innerip", "").split(",") if x and x in ip]
            if valid_hosts and ip_info["host"]["bk_host_id"] not in proccessed:
                ip_result.append(
                    {
                        "InnerIP": valid_hosts[0],  # 即使多个host命中，也都是同一个主机id，这里以第一个合法host为标识
                        "HostID": ip_info["host"]["bk_host_id"],
                        "Source": ip_info["host"].get("bk_cloud_id", -1),
                        "Sets": ip_info["set"],
                        "Modules": ip_info["module"],
                    }
                )
                proccessed.add(ip_info["host"]["bk_host_id"])

    valid_ip = [ip_info["InnerIP"] for ip_info in ip_result]
    invalid_ip = list(set(ip_input_list) - set(valid_ip))
    result = {
        "result": True,
        "ip_result": ip_result,
        "ip_count": len(ip_result),
        "invalid_ip": invalid_ip,
    }
    return result


def get_job_instance_url(biz_cc_id, job_instance_id):
    url_format = "{}/api_execute/{}"
    return url_format.format(settings.BK_JOB_HOST, job_instance_id)


def get_node_callback_url(root_pipeline_id, node_id, node_version=""):
    engine_ver = EngineConfig.ENGINE_VER_V1 if not node_version else EngineConfig.ENGINE_VER_V2
    f = Fernet(settings.CALLBACK_KEY)
    callback_entry = (
        env.BKAPP_INNER_CALLBACK_ENTRY or env.BKAPP_INNER_CALLBACK_HOST + "taskflow/api/v4/nodes/callback/%s/"
    )
    return (
        callback_entry
        % f.encrypt(
            bytes("{}:{}:{}:{}".format(root_pipeline_id, engine_ver, node_id, node_version), encoding="utf8")
        ).decode()
    )


def get_module_id_list_by_name(tenant_id, bk_biz_id, username, set_list, service_template_list):
    """
    @summary 根据集群、服务模板名称筛选出符合条件的模块id
    @param tenant_id: 租户 ID
    @param username: 执行用户名
    @param bk_biz_id: 业务id
    @param set_list: 集群list
    @param service_template_list: 服务模板list
    @return:
    """
    set_ids = [set_item["bk_set_id"] for set_item in set_list]
    service_template_ids = [service_template_item["id"] for service_template_item in service_template_list]
    # 调用find_module_with_relation接口根据set id list, service_template_id_list查询模块id
    module_id_list = find_module_with_relation(
        tenant_id, bk_biz_id, username, set_ids, service_template_ids, ["bk_module_id"])
    return module_id_list


def get_nodeman_job_url(instance_id, bk_host_id):
    return "{}/#/task-history/{}/log/host|instance|host|{}".format(settings.BK_NODEMAN_HOST, instance_id, bk_host_id)


def get_difference_ip_list(original_ip_list, ip_list):
    """
    @summary IP存在性校验
    @param original_ip_list: 手动填写的IP列表
    @param ip_list: 查询到的IP列表
    @return:
    """
    difference_ip_list = set(original_ip_list).difference(set(ip_list))
    return difference_ip_list


def get_biz_ip_from_frontend(
        tenant_id, ip_str, executor, biz_cc_id, data, logger_handle, is_across=False, ip_is_exist=False,
        ignore_ex_data=False
):
    """
    从前端表单中获取有效IP
    """
    # ip 字符串为空时不做处理
    if ip_str is None or not ip_str.strip():
        return True, []

    # 跨业务，不校验IP归属
    if is_across:
        plat_ip = [match.group() for match in plat_ip_reg.finditer(ip_str)]
        ip_list = [{"ip": _ip.split(":")[1], "bk_cloud_id": _ip.split(":")[0]} for _ip in plat_ip]
        err_msg = _("允许跨业务时IP格式需满足：【管控区域ID:IP】。失败 IP： {}")
    else:
        var_ip = cc_get_ips_info_by_str(
            tenant_id=tenant_id, username=executor, biz_cc_id=biz_cc_id, ip_str=ip_str, use_cache=False)
        ip_list = [{"ip": _ip["InnerIP"], "bk_cloud_id": _ip["Source"]} for _ip in var_ip["ip_result"]]
        err_msg = _("无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法。查询失败 IP： {}")

    # 校验Ip是否存在, 格式是否符合要求
    input_ip_set = get_ip_by_regex(ip_str)
    logger_handle.info("The valid IP list is:{}, User input IP list is:{}".format(ip_list, input_ip_set))
    difference_ip_list = list(get_difference_ip_list(input_ip_set, [ip_item["ip"] for ip_item in ip_list]))

    if len(ip_list) != len(set(input_ip_set)):
        difference_ip_list.sort()
        if not ignore_ex_data:
            data.outputs.ex_data = err_msg.format(",".join(difference_ip_list))
        return False, ip_list
    if not ip_list:
        if not ignore_ex_data:
            data.outputs.ex_data = _("IP 为空，请确认是否输入IP,请检查IP格式是否正确：{}".format(ip_str))
        return False, ip_list
    return True, ip_list


def get_repeat_ip(ip_list):
    repeat_ip_detail = {}
    for ip_info in ip_list:
        repeat_ip_detail.setdefault(ip_info["ip"], []).append(ip_info["bk_cloud_id"])

    return ",".join(
        [
            "ip: {} 管控区域{}".format(repeat_ip, value)
            for repeat_ip, value in repeat_ip_detail.items()
            if len(value) > 0
        ]
    )


def get_biz_ip_from_frontend_hybrid(tenant_id, executor, ip_str, biz_cc_id, data, ignore_ex_data=False):
    """
    处理前端ip,管控区域:ip 混合输入的情况，最终提取出来的格式为:
    [
        {
            "bk_cloud_id": 0,
            "ip": 127.0.0.1
        }
    ]
    """
    logger.info(
        "[get_biz_ip_from_frontend_hybrid] -> start get ip from frontend, ip_str={}, biz_cc_id={}".format(
            ip_str, biz_cc_id
        )
    )
    # 先提取所有带管控区域的ip
    plat_ip = [match.group().split(":") for match in plat_ip_reg.finditer(ip_str)]
    plat_ip_list = [{"ip": _ip, "bk_cloud_id": int(_cloud)} for _cloud, _ip in plat_ip]
    logger.info(
        "[get_biz_ip_from_frontend_hybrid] -> get_plat_ip_list, ip_str={}, plat_ip_list={}".format(ip_str, plat_ip_list)
    )
    # 替换掉所有的ip地址为空:
    ip_str = plat_ip_reg.sub("", ip_str)

    # 再提取所有非跨业务的ip,多一次匹配，但是如果without_plat_ip_list 为空，可以少一次查询
    without_plat_ip_list = [match.group() for match in ip_pattern.finditer(ip_str)]
    logger.info(
        "[get_biz_ip_from_frontend_hybrid] -> get_without_plat_ip_list, ip_str={}, plat_ip_list={}".format(
            ip_str, without_plat_ip_list
        )
    )
    # 对于用户没有输入管控区域的ip,则去当前业务下查询管控区域
    if not without_plat_ip_list:
        return True, plat_ip_list

    var_ip = cc_get_ips_info_by_str(
        tenant_id=tenant_id, username=executor, biz_cc_id=biz_cc_id, ip_str=",".join(without_plat_ip_list),
        use_cache=False
    )
    ip_list = [{"ip": _ip["InnerIP"], "bk_cloud_id": _ip["Source"]} for _ip in var_ip["ip_result"]]

    err_msg = _("无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法。查询失败 IP： {}")

    difference_ip_list = list(get_difference_ip_list(without_plat_ip_list, [ip_item["ip"] for ip_item in ip_list]))

    if difference_ip_list:
        difference_ip_list.sort()
        if not ignore_ex_data:
            data.outputs.ex_data = err_msg.format(",".join(difference_ip_list))
        return False, []

    if len(ip_list) != len(set(without_plat_ip_list)):
        # 这种情况应该是存在一个ip下有多个管控区域的情况
        if not ignore_ex_data:
            repeat_err_msg = get_repeat_ip(ip_list)
            data.outputs.ex_data = "IP在多个管控区域下重复，建议输入管控区域:ip确定目标主机，详情: {}".format(
                repeat_err_msg
            )
        return False, []
    if not ip_list:
        if not ignore_ex_data:
            data.outputs.ex_data = _("IP 为空，请确认是否输入IP,请检查IP格式是否正确：{}".format(ip_str))
        return False, []

    ip_list.extend(plat_ip_list)
    return True, ip_list
