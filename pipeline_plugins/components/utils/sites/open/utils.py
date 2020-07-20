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
import os
import logging

from urllib.parse import urlencode
from cryptography.fernet import Fernet

from pipeline_plugins.base.utils.inject import supplier_account_for_business

from gcloud.utils import cmdb
from gcloud.utils.ip import get_ip_by_regex
from gcloud.conf import settings

__all__ = ["cc_get_ips_info_by_str", "get_job_instance_url", "get_node_callback_url", "plat_ip_reg"]

JOB_APP_CODE = "bk_job"

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
ip_re = r"((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)"
plat_ip_reg = re.compile(r"\d+:" + ip_re)
set_module_ip_reg = re.compile(r"[\u4e00-\u9fa5\w]+\|[\u4e00-\u9fa5\w]+\|" + ip_re)
ip_pattern = re.compile(ip_re)


def cc_get_ips_info_by_str(username, biz_cc_id, ip_str, use_cache=True):
    """
    @summary: 从ip_str中匹配出IP信息
    @param username
    @param biz_cc_id
    @param ip_str
    @param use_cache
    @note: 需要兼容的ip_str格式有
        1： IP，纯IP格式
        2： 集群名称|模块名称|IP，集群名称|模块名称|IP  这种格式可以唯一定位到一
            个IP（如果业务把相同IP放到同一模块，还是有问题）
        3： 云区域ID:IP，云区域ID:IP  这种格式可以唯一定位到一个IP，主要是兼容Job组件
            传参需要和获取Job作业模板步骤参数
    @return: {'result': True or False, 'data': [{'InnerIP': ,'HostID': ,
        'Source': , 'SetID': , 'SetName': , 'ModuleID': , 'ModuleName': },{}]}
    """

    ip_input_list = get_ip_by_regex(ip_str)

    supplier_account = supplier_account_for_business(biz_cc_id)

    ip_list = cmdb.get_business_host_topo(
        username, biz_cc_id, supplier_account, ["bk_host_innerip", "bk_host_id", "bk_cloud_id"]
    )
    ip_result = []

    # 如果是格式2，可以返回IP的集群、模块、平台信息
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
                            }
                        )

    # 如果是格式3，返回IP的平台信息
    elif plat_ip_reg.match(ip_str):
        plat_ip = []
        for match in plat_ip_reg.finditer(ip_str):
            plat_ip.append(match.group())

        for ip_info in ip_list:
            if (
                "%s:%s" % (ip_info["host"].get("bk_cloud_id", -1), ip_info["host"].get("bk_host_innerip", ""),)
                in plat_ip
            ):
                ip_result.append(
                    {
                        "InnerIP": ip_info["host"].get("bk_host_innerip", ""),
                        "HostID": ip_info["host"]["bk_host_id"],
                        "Source": ip_info["host"].get("bk_cloud_id", -1),
                    }
                )

    # 格式1
    else:
        ip = []
        for match in ip_pattern.finditer(ip_str):
            ip.append(match.group())

        host_id_list = []
        for ip_info in ip_list:
            if ip_info["host"].get("bk_host_innerip", "") in ip and ip_info["host"]["bk_host_id"] not in host_id_list:
                ip_result.append(
                    {
                        "InnerIP": ip_info["host"].get("bk_host_innerip", ""),
                        "HostID": ip_info["host"]["bk_host_id"],
                        "Source": ip_info["host"].get("bk_cloud_id", -1),
                    }
                )
                host_id_list.append(ip_info["host"]["bk_host_id"])

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

    if settings.BK_JOB_VERSION == "V2":
        url_format = "%s?taskInstanceList&appId=%s#taskInstanceId=%s"

        if settings.OPEN_VER == "community":
            return url_format % (settings.BK_JOB_HOST, biz_cc_id, job_instance_id,)

        else:
            query = {
                "app": JOB_APP_CODE,
                "url": url_format % (settings.BK_JOB_HOST, biz_cc_id, job_instance_id,),
            }
            return "%s/console/?%s" % (settings.BK_PAAS_HOST, urlencode(query))
    else:
        url_format = "{}/api_execute/{}"

        return url_format.format(settings.BK_JOB_HOST, job_instance_id)


def get_node_callback_url(node_id):
    f = Fernet(settings.CALLBACK_KEY)
    return "%staskflow/api/nodes/callback/%s/" % (
        os.getenv("BKAPP_INNER_CALLBACK_HOST", settings.APP_HOST),
        f.encrypt(bytes(node_id, encoding="utf8")).decode(),
    )
