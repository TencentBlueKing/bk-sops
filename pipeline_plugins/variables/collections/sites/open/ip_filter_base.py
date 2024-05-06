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
from abc import ABCMeta, abstractmethod

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from api.collections.nodeman import BKNodeManClient
from gcloud.conf import settings as gcloud_settings
from gcloud.constants import GseAgentStatus
from gcloud.core.models import Project
from gcloud.exceptions import ApiRequestError
from gcloud.utils import cmdb
from gcloud.utils.handlers import handle_api_error
from gcloud.utils.ip import IpRegexType, extract_ip_from_ip_str, get_ip_by_regex_type
from pipeline_plugins.base.utils.inject import supplier_account_for_business, supplier_id_for_project
from pipeline_plugins.cmdb_ip_picker.utils import format_agent_data, get_gse_agent_status_ipv6
from pipeline_plugins.components.collections.sites.open.cc.base import cc_get_host_by_innerip_with_ipv6

logger = logging.getLogger("root")
get_client_by_user = gcloud_settings.ESB_GET_CLIENT_BY_USER
get_nodeman_client_by_user = BKNodeManClient


class IpFilterBase(metaclass=ABCMeta):
    def __init__(self, origin_ip_list, data):
        self.origin_ip_list = origin_ip_list
        self.data = data

    @abstractmethod
    def get_match_ip(self):
        pass


class GseAgentStatusIpFilter(IpFilterBase):
    def match_ges_v2(self, gse_agent_status, username, bk_biz_id, bk_supplier_id, origin_ip_list):

        fields = ["bk_host_id", "bk_cloud_id", "bk_host_innerip", "bk_agent_id"]
        # 生成一个host列表
        origin_hosts = {
            "{}:{}".format(origin_host["bk_cloud_id"], origin_host["ip"]): origin_host for origin_host in origin_ip_list
        }

        ip_list = [host["ip"] for host in origin_ip_list]
        # 先去查出来所有host的gse_agent_id
        hosts = cmdb.get_business_host(username, bk_biz_id, bk_supplier_id, host_fields=fields, ip_list=ip_list)

        # 构造一个{bk_agent_id: bk_cloud_id:ip}的字典
        remote_hosts = {}

        for host in hosts:
            remote_host_value = "{}:{}".format(host["bk_cloud_id"], host["bk_host_innerip"])
            if remote_host_value in origin_hosts.keys():
                bk_agent_id = host.get("bk_agent_id")
                if not bk_agent_id:
                    # 没有agent_id 使用 云区域+ip 组成 agent_id
                    bk_agent_id = remote_host_value
                remote_hosts[bk_agent_id] = remote_host_value

        # 去查询agent状态
        agent_map = get_gse_agent_status_ipv6(bk_agent_id_list=list(remote_hosts.keys()))

        agent_online_ip_list = []  # 在线的ip的列表
        agent_offline_ip_list = []  # 不在线的ip的列表
        match_ip = []  # 过滤失败将不返回任何i
        for bk_agent_id, agent_code in agent_map.items():
            origin_host_key = remote_hosts.get(bk_agent_id)
            if not origin_host_key:
                continue
            origin_host = origin_hosts.get(origin_host_key)
            if not origin_host:
                continue

            if agent_code == GseAgentStatus.ONlINE.value:
                agent_online_ip_list.append(origin_host)
            if agent_code == GseAgentStatus.OFFLINE.value:
                agent_offline_ip_list.append(origin_host)

        if gse_agent_status == GseAgentStatus.ONlINE.value:
            match_ip = agent_online_ip_list
        if gse_agent_status == GseAgentStatus.OFFLINE.value:
            match_ip = agent_offline_ip_list

        return match_ip

    def match_gse_v1(self, gse_agent_status, username, bk_biz_id, bk_supplier_id, origin_ip_list):
        match_ip = origin_ip_list
        if gse_agent_status in [GseAgentStatus.ONlINE.value, GseAgentStatus.OFFLINE.value]:
            client = get_nodeman_client_by_user(username=username)
            agent_kwargs = {
                "all_scope": True,
                "host_list": [
                    {
                        "cloud_id": host["bk_cloud_id"],
                        "ip": host["ip"],
                        "meta": {"bk_biz_id": bk_biz_id, "scope_type": "biz", "scope_id": bk_biz_id},
                    }
                    for host in origin_ip_list
                    if host["ip"] != ""
                ],
            }
            agent_result = client.get_ipchooser_host_details(agent_kwargs)

            if not agent_result["result"]:
                message = handle_api_error(
                    _("节点管理(nodeman)"), "nodeman.get_ipchooser_host_details", agent_kwargs, agent_result
                )
                raise ApiRequestError(f"ERROR:{message}")
            agent_data = format_agent_data(agent_result["data"])
            agent_online_ip_list = []
            agent_offline_ip_list = []
            for plat_ip, info in agent_data.items():
                if info["bk_agent_alive"] == GseAgentStatus.ONlINE.value:
                    agent_online_ip_list.append({"bk_cloud_id": info["bk_cloud_id"], "ip": info["ip"]})
                if info["bk_agent_alive"] == GseAgentStatus.OFFLINE.value:
                    agent_offline_ip_list.append({"bk_cloud_id": info["bk_cloud_id"], "ip": info["ip"]})

            if gse_agent_status == GseAgentStatus.ONlINE.value:
                match_ip = agent_online_ip_list
            if gse_agent_status == GseAgentStatus.OFFLINE.value:
                match_ip = agent_offline_ip_list

        return match_ip

    def get_match_ip(self):

        origin_ip_list = self.origin_ip_list
        gse_agent_status = self.data.get("gse_agent_status", "")
        username = self.data["executor"]
        project_id = self.data["project_id"]
        project = Project.objects.get(id=project_id)
        bk_biz_id = project.bk_biz_id if project.from_cmdb else ""
        bk_supplier_id = supplier_id_for_project(project_id)
        if not origin_ip_list:
            return []

        if settings.ENABLE_GSE_V2:
            return self.match_ges_v2(gse_agent_status, username, bk_biz_id, bk_supplier_id, origin_ip_list)
        else:
            return self.match_gse_v1(gse_agent_status, username, bk_biz_id, bk_supplier_id, origin_ip_list)


class GseAgentStatusIpV6Filter:
    def __init__(self, ip_str, data):
        self.ip_str = ip_str
        self.data = data

    def get_match_ip(self):
        username = self.data["executor"]
        project_id = self.data["project_id"]
        project = Project.objects.get(id=project_id)
        bk_biz_id = project.bk_biz_id if project.from_cmdb else ""
        supplier_account = supplier_account_for_business(bk_biz_id)

        ipv6_list, ipv4_list, _, ipv4_list_with_cloud_id, ipv6_list_with_cloud_id = extract_ip_from_ip_str(self.ip_str)

        user_input_ip_set = set(ipv6_list + ipv4_list + ipv4_list_with_cloud_id + ipv6_list_with_cloud_id)

        # 先去cmdb查询倒所有用户输入的主机
        hosts_result = cc_get_host_by_innerip_with_ipv6(
            username, bk_biz_id, self.ip_str, supplier_account, host_id_detail=True
        )

        if not hosts_result["result"]:
            raise ApiRequestError(hosts_result.get("message"))

        hosts = hosts_result.get("data", [])

        # 查询这批主机的所有的gse状态
        bk_agent_id_list = []
        for host in hosts:
            bk_agent_id = host.get("bk_agent_id")
            # 如果bk_agent_id = 空
            if not bk_agent_id:
                if not host["bk_host_innerip"]:
                    # 如果既没有如果bk_agent_id，又没有ipv4地址，说明这个主机是台没有安装agent的ipv6主机，忽略，不再查询agent状态
                    continue
                bk_agent_id = "{}:{}".format(host["bk_cloud_id"], host["bk_host_innerip"])
            bk_agent_id_list.append(bk_agent_id)

        try:
            agent_id_status_map = get_gse_agent_status_ipv6(bk_agent_id_list)
        except Exception as e:
            raise ApiRequestError(f"ERROR:{e}")

        match_host = []
        agent_online_ip_list = []
        agent_offline_ip_list = []
        for host in hosts:
            match_result = self.get_ip_type_matched(host, user_input_ip_set)
            bk_agent_id = host.get("bk_agent_id")
            # 如果bk_agent_id = 空
            if not bk_agent_id:
                if not host["bk_host_innerip"]:
                    # 如果既没有如果bk_agent_id，又没有ipv4地址，说明这个主机石台没有安装agent的ipv6主机, 直接算作不在线的主机
                    agent_offline_ip_list.append(match_result)
                    continue
                bk_agent_id = "{}:{}".format(host["bk_cloud_id"], host["bk_host_innerip"])
            # 如果用户输入的是ipv6, 应该优先采用ipv6的地址
            if agent_id_status_map.get(bk_agent_id, 0) == 1:
                agent_online_ip_list.append(match_result)
            # agent 状态为 0 或者 未知 则认为 该主机 不在线
            if agent_id_status_map.get(bk_agent_id, 0) in [0, -1]:
                agent_offline_ip_list.append(match_result)
        gse_agent_status = self.data.get("gse_agent_status", "")
        if gse_agent_status == GseAgentStatus.ONlINE.value:
            match_host = agent_online_ip_list
        if gse_agent_status == GseAgentStatus.OFFLINE.value:
            match_host = agent_offline_ip_list

        return match_host

    def get_ip_type_matched(self, host, user_input_ip_set):
        # 取交集, 并返回结论是ipv4命中还是ipv6命中

        host_ip_set = {
            host.get("bk_host_innerip"),
            "{}:{}".format(host["bk_cloud_id"], host["bk_host_innerip"]),
            host.get("bk_host_innerip_v6"),
            "{}:[{}]".format(host["bk_cloud_id"], host["bk_host_innerip_v6"]),
        }

        result = host_ip_set & user_input_ip_set
        host_ip = host.get("bk_host_innerip") or host.get("bk_host_innerip_v6")
        if len(result) != 1:
            # 如果命中多个，则默认取ipv4
            return {"bk_cloud_id": host["bk_cloud_id"], "ip": host_ip}
        ip_str = list(result)[0]

        ip_type_map = {
            IpRegexType.IPV6_WITH_CLOUD_ID.value: "IPV6",
            IpRegexType.IPV6.value: "IPV6",
            IpRegexType.IPV4.value: "IPV4",
            IpRegexType.IPV4_WITH_CLOUD_ID.value: "IPV4",
        }

        ip_type_final = "IPV4"

        for regex_type, ip_type in ip_type_map.items():
            ip_list, _ = get_ip_by_regex_type(regex_type, ip_str)
            if ip_list:
                ip_type_final = ip_type
                break

        if ip_type_final == "IPV4":
            return {"bk_cloud_id": host["bk_cloud_id"], "ip": host_ip}
        else:
            # 命中了ipv6的说明这台主机一定有ipv6地址
            return {"bk_cloud_id": host["bk_cloud_id"], "ip": host.get("bk_host_innerip_v6")}
