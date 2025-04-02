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
from typing import List

from django.conf import settings
from django.contrib.admin.utils import flatten
from django.utils.translation import gettext_lazy as _
from pipeline.core.data.var import LazyVariable

from gcloud.constants import Type
from gcloud.core.models import Project
from gcloud.utils.cmdb import get_business_host, get_business_host_by_hosts_ids
from gcloud.utils.ip import extract_ip_from_ip_str, get_ip_by_regex, get_plat_ip_by_regex
from pipeline_plugins.base.utils.adapter import cc_get_inner_ip_by_module_id
from pipeline_plugins.base.utils.inject import supplier_account_for_project
from pipeline_plugins.cmdb_ip_picker.utils import get_ip_picker_result
from pipeline_plugins.components.collections.sites.open.cc.base import cc_get_host_by_innerip_with_ipv6
from pipeline_plugins.components.utils import cc_get_ips_info_by_str
from pipeline_plugins.components.utils.common import ip_re
from pipeline_plugins.variables.base import FieldExplain, SelfExplainVariable
from pipeline_plugins.variables.collections.sites.open.ip_filter_base import (
    GseAgentStatusIpFilter,
    GseAgentStatusIpV6Filter,
)
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("root")


class VarIpPickerVariable(LazyVariable):
    code = "ip"
    name = _("IP选择器(已废弃)")
    type = "dynamic"
    tag = "var_ip_picker.ip_picker"
    form = "%svariables/cmdb/var_ip_picker.js" % settings.STATIC_URL
    desc = _("该变量已废弃，请替换为新版 IP 选择器")

    def get_value(self):
        if "executor" not in self.pipeline_data or "project_id" not in self.pipeline_data:
            raise Exception("ERROR: executor and project_id of pipeline is needed")
        var_ip_picker = self.value
        tenant_id = self.pipeline_data["tenant_id"]
        username = self.pipeline_data["executor"]
        project_id = self.pipeline_data["project_id"]
        project = Project.objects.get(id=project_id)
        bk_biz_id = project.bk_biz_id if project.from_cmdb else ""
        bk_supplier_account = supplier_account_for_project(project_id)

        produce_method = var_ip_picker["var_ip_method"]
        if produce_method == "custom":
            custom_value = var_ip_picker["var_ip_custom_value"]
            data = cc_get_ips_info_by_str(username, bk_biz_id, custom_value)
            ip_list = data["ip_result"]
            data = ",".join([ip["InnerIP"] for ip in ip_list])
        else:
            ip_pattern = re.compile(ip_re)
            module_id_list = var_ip_picker["var_ip_tree"]
            module_inst_id_list = []
            tree_ip_list = []
            for custom_id in module_id_list:
                try:
                    ip_or_module_id = custom_id.split("_")[-1]
                    if ip_pattern.match(ip_or_module_id):
                        # select certain ip
                        tree_ip_list.append(ip_or_module_id)
                    else:
                        # select whole module
                        module_inst_id_list.append(int(ip_or_module_id))
                except Exception:
                    logger.warning("ip_picker module ip transit failed: {origin}".format(origin=custom_id))

            # query cc to get module's ip list and filter tree_ip_list
            host_list = cc_get_inner_ip_by_module_id(
                tenant_id, username, bk_biz_id, module_inst_id_list, bk_supplier_account,
                ["host_id", "bk_host_innerip"]
            )
            cc_ip_list = cc_get_ips_info_by_str(username, bk_biz_id, ",".join(tree_ip_list))["ip_result"]
            select_ip = set()

            for host_info in host_list:
                select_ip.add(host_info["host"].get("bk_host_innerip", ""))

            for ip_info in cc_ip_list:
                select_ip.add(ip_info["InnerIP"])

            data = ",".join(list(set(select_ip)))

        return data


class VarCmdbIpSelector(LazyVariable, SelfExplainVariable):
    code = "ip_selector"
    name = _("IP选择器")
    type = "dynamic"
    tag = "var_cmdb_ip_selector.ip_selector"
    form = "%svariables/cmdb/var_cmdb_ip_selector.js" % settings.STATIC_URL
    desc = _(
        "输出格式为选中 IP 以 ',' 分隔的字符串\n"
        "筛选条件和排除条件为 AND 关系\n"
        "- 筛选：会从IP列表中筛选出符合条件的IP\n"
        "- 排除：会从IP列表中去除符合条件的IP\n"
        "变量值是否带管控区域\n"
        "- 是，返回格式为{BK-Net_id}:{ip},{BK-Net_id}:{ip}\n"
        "- 否，返回格式为{ip},{ip}"
    )

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [FieldExplain(key="${KEY}", type=Type.STRING, description="选择的IP列表，以,分隔")]

    def get_value(self):
        if "executor" not in self.pipeline_data or "project_id" not in self.pipeline_data:
            raise Exception("ERROR: executor and project_id of pipeline is needed")
        tenant_id = self.pipeline_data["tenant_id"]
        username = self.pipeline_data["executor"]
        project_id = self.pipeline_data["project_id"]
        project = Project.objects.get(id=project_id)
        bk_biz_id = project.bk_biz_id if project.from_cmdb else ""
        bk_supplier_account = supplier_account_for_project(project_id)

        ip_selector = self.value
        ip_result = get_ip_picker_result(tenant_id, username, bk_biz_id, bk_supplier_account, ip_selector)
        if not ip_result["result"]:
            logger.error(f"[ip_selector get_value] error: {ip_result}")
            raise Exception(f'ERROR: {ip_result["message"]}, ip_selector_key: {self.original_value.key}')
        separator = self.value.get("separator", ",")

        # get for old value compatible
        if self.value.get("with_cloud_id", False):
            hosts = []
            for host in ip_result["data"]:
                p_address = ipaddress.ip_address(host["bk_host_innerip"])
                # 如果是ipv6地址，则不携带管控区域
                if settings.ENABLE_IPV6 and p_address.version == 6:
                    hosts.append(f'{host["bk_cloud_id"]}:[{host["bk_host_innerip"]}]')
                else:
                    hosts.append("{}:{}".format(host["bk_cloud_id"], host["bk_host_innerip"]))

            ip = separator.join(hosts)
        else:
            ip = separator.join([host["bk_host_innerip"] for host in ip_result["data"]])
        return ip


class SetDetailData(object):
    def __init__(self, data, separator=","):
        self._value = data
        self.set_count = len(self._value)
        item_values = {}
        modules = []
        total_ip_set = set()
        # verbose_ip_list 和 ip_module_list 元素一一对应
        verbose_ip_list = []
        verbose_ip_module_list = []
        for item in data:
            set_name = item["bk_set_name"]
            for key, val in item.items():
                if key == "__module":
                    module_ips = flatten([mod["value"] for mod in val])
                    total_ip_set.update(module_ips)
                    verbose_ip_list += module_ips
                    verbose_ip_module_list += flatten(
                        [["{}>{}".format(set_name, mod["key"])] * len(mod["value"]) for mod in val]
                    )
                    item_module = {mod["key"]: separator.join(mod["value"]) for mod in val}
                    modules.append(item_module)
                else:
                    item_values.setdefault(key, []).append(val)
        for attr, attr_val in item_values.items():
            setattr(self, attr, attr_val)
            flat_val = separator.join(map(str, attr_val))
            setattr(self, "flat__{}".format(attr), flat_val)
        setattr(self, "_module", modules)
        setattr(self, "flat__ip_list", separator.join(list(total_ip_set)))
        setattr(self, "flat__verbose_ip_list", separator.join(verbose_ip_list))
        setattr(self, "flat__verbose_ip_module_list", separator.join(verbose_ip_module_list))
        self._pipeline_var_str_value = "Allocate {} sets with names: {}".format(
            self.set_count, separator.join(item_values["bk_set_name"])
        )

    def __repr__(self):
        return self._pipeline_var_str_value


class VarCmdbSetAllocation(LazyVariable, SelfExplainVariable):
    code = "set_allocation"
    name = _("集群资源筛选")
    type = "general"
    tag = "var_cmdb_resource_allocation.set_allocation"
    form = "%svariables/cmdb/var_cmdb_resource_allocation.js" % settings.STATIC_URL
    desc = _(
        "此变量用于按照资源筛选方案配置的新集群信息（此变量不会在 CMDB 创建新集群）\n"
        "引用${KEY}，返回的是创建集群成功的信息Allocate {set_number} sets with names: {set_names}\n"
        "引用${KEY._module}，返回的是集群下的模块信息列表，元素类型为字典，键为模块名，值为模块下的主机列\n"
        "引用${KEY.{集群属性编码}}，返回的是本次操作创建的所有集群的指定属性值的列表\n"
        "如：\n"
        "获取集群的名称列表: ${KEY.bk_set_name}\n"
        "获取集群环境类型: ${KEY.bk_set_env}\n"
        "引用${KEY.flat__{集群属性编码}}，返回的是本次操作创建的所有集群的指定属性值，用 ',' 连接\n"
        "如：\n"
        "获取集群的名称值: ${KEY.flat__bk_set_name}\n"
        "获取集群环境类型值: ${KEY.flat__bk_set_env}\n"
        "引用${KEY.flat__ip_list}，返回的是本次操作创建的所有集群下的主机（去重后），用 ',' 连接\n"
        "引用${KEY.flat__verbose_ip_list}，返回的是本次操作创建的所有集群下的主机（未去重），用 ',' 连接\n"
        "引用${KEY.flat__verbose_ip_module_list}，返回的是本次操作创建的所有模块名称，格式为set_name>module_name，用 ',' 连接"
    )

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:

        fields = [
            FieldExplain(key="${KEY}", type=Type.OBJECT, description="集群资源筛选结果对象"),
            FieldExplain(key="${KEY.set_count}", type=Type.INT, description="新增集群数量"),
            FieldExplain(
                key="${KEY._module}",
                type=Type.LIST,
                description="集群下的模块信息列表，元素类型为字典，键为模块名，值为模块下的主机列",
            ),
            FieldExplain(
                key="${KEY.flat__ip_list}",
                type=Type.STRING,
                description="本次操作创建的所有集群下的主机（去重后），用 ',' 连接",
            ),
            FieldExplain(
                key="${KEY.flat__verbose_ip_list}",
                type=Type.STRING,
                description="返回的是本次操作创建的所有集群下的主机（未去重），用 ',' 连接",
            ),
            FieldExplain(
                key="${KEY.flat__verbose_ip_module_list}",
                type=Type.STRING,
                description="本次操作创建的所有模块名称，格式为set_name>module_name，用 ',' 连接",
            ),
        ]

        client = get_client_by_username(settings.SYSTEM_USE_API_ACCOUNT, stage=settings.BK_APIGW_STAGE_NAME)
        tenant_id = kwargs["tenant_id"]
        params = {"bk_obj_id": "set"}
        if "bk_biz_id" in kwargs:
            params["bk_biz_id"] = kwargs["bk_biz_id"]
        resp = client.api.search_object_attribute(
            params,
            headers={"X-Bk-Tenant-Id": tenant_id},
        )
        resp_data = []

        if not resp["result"]:
            logger.error("[_self_explain] %s search_object_attribute err: %s" % (cls.tag, resp["message"]))
        else:
            resp_data = resp["data"]

        for item in resp_data:
            if not item["editable"]:
                continue
            fields.append(
                FieldExplain(
                    key="${KEY.%s}" % item["bk_property_id"],
                    type=Type.LIST,
                    description="集群属性(%s)列表" % item["bk_property_name"],
                )
            )
            fields.append(
                FieldExplain(
                    key="${KEY.flat__%s}" % item["bk_property_id"],
                    type=Type.STRING,
                    description="集群属性(%s)列表，以,分隔" % item["bk_property_name"],
                )
            )

        return fields

    def get_value(self):
        """
        @summary: 返回 SetDetailData 对象
        @note: 引用集群资源变量某一列某一行的属性，如 ${value.bk_set_name[0]} -> "集群1"
        @note: 引用集群资源变量某一列的全部属性，多行用换行符 `\n` 分隔，如 ${value.flat__bk_set_name} -> "集群1\n集群2"
        @note: 引用集群资源变量的模块分配的 IP ${value._module[0]["gamesvr"]} -> "127.0.0.1,127.0.0.2"
        @return:
        """
        separator = self.value.get("separator", ",")
        return SetDetailData(self.value["data"], separator)


class VarCmdbAttributeQuery(LazyVariable, SelfExplainVariable):
    code = "attribute_query"
    name = _("主机属性查询器")
    type = "dynamic"
    tag = "var_cmdb_attr_query.attr_query"
    form = "%svariables/cmdb/var_cmdb_attribute_query.js" % settings.STATIC_URL
    desc = _(
        "输出字典，键为主机IP，值为主机所有的属性值字典（键为属性，值为属性值）\n"
        '例如，通过 ${hosts["1.1.1.1"]["bk_host_id"]} 获取主机在 CMDB 中的唯一 ID\n'
        "输入请保证每台主机都有唯一的 IP，否则可能会出现数据覆盖的情况\n"
        "更多可使用的主机属性请在 CMDB 主机模型页面查阅"
    )

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [
            FieldExplain(key="${KEY}", type=Type.DICT, description="主机属性查询结果"),
        ]

    @staticmethod
    def _handle_value_with_ipv4(tenant_id, username, bk_biz_id, bk_supplier_account, host_fields, ip_str):
        """根据 ip 字符串获取对应主机属性信息"""
        ip_list = get_ip_by_regex(ip_str)
        if not ip_list:
            return []

        hosts_list = get_business_host(
            tenant_id,
            username,
            bk_biz_id,
            bk_supplier_account,
            host_fields,
            ip_list,
        )
        return hosts_list

    @staticmethod
    def _handle_value_with_ipv4_and_ipv6(tenant_id, username, bk_biz_id, bk_supplier_account, host_fields, ip_str):
        """根据 ip 字符串获取对应主机属性信息"""
        # 兼容多种字符串模式，转换成 host_id 列表后统一获取
        result = cc_get_host_by_innerip_with_ipv6(tenant_id, username, bk_biz_id, ip_str, bk_supplier_account)
        if not result["result"]:
            message = f"获取主机列表失败: {result} | cc_get_host_by_innerip_with_ipv6"
            logger.error(message)
            raise Exception(message)
        host_ids = [host["bk_host_id"] for host in result["data"]]
        if not host_ids:
            return []
        return get_business_host_by_hosts_ids(tenant_id, username, bk_biz_id, bk_supplier_account, host_fields,
                                              host_ids)

    def get_value(self):
        """
        @summary: 返回 dict 对象，将每个可从CMDB查询到的输入IP作为键，将从CMDB查询到的主机属性封装成字典作为值
        @note: 引用127.0.0.1的所有属性，如 ${value["127.0.0.1"]} -> {"bk_host_id": 999, "import_from": 3, ...}
        @note: 引用127.0.0.1的bk_host_id属性，如 ${value["127.0.0.1"]["bk_host_id"]} -> 999
        @return:
        """
        if "executor" not in self.pipeline_data or "project_id" not in self.pipeline_data:
            raise Exception("ERROR: executor and project_id of pipeline is needed")
        HOST_FIELDS = [
            "bk_cpu",
            "bk_isp_name",
            "bk_os_name",
            "bk_province_name",
            "bk_host_id",
            "import_from",
            "bk_os_version",
            "bk_disk",
            "operator",
            "bk_mem",
            "bk_host_name",
            "bk_host_innerip",
            "bk_comment",
            "bk_os_bit",
            "bk_outer_mac",
            "bk_asset_id",
            "bk_service_term",
            "bk_sla",
            "bk_cpu_mhz",
            "bk_host_outerip",
            "bk_state_name",
            "bk_os_type",
            "bk_mac",
            "bk_bak_operator",
            "bk_supplier_account",
            "bk_sn",
            "bk_cpu_module",
        ]
        username = self.pipeline_data["executor"]
        tenant_id = self.pipeline_data["tenant_id"]
        project_id = self.pipeline_data["project_id"]
        project = Project.objects.get(id=project_id)
        bk_biz_id = project.bk_biz_id if project.from_cmdb else ""
        bk_supplier_account = supplier_account_for_project(project_id)

        if settings.ENABLE_IPV6:
            hosts_list = self._handle_value_with_ipv4_and_ipv6(
                tenant_id, username, bk_biz_id, bk_supplier_account, HOST_FIELDS + ["bk_host_innerip_v6"], self.value
            )
            ipv6_list, *_ = extract_ip_from_ip_str(self.value)
        else:
            hosts_list = self._handle_value_with_ipv4(
                tenant_id, username, bk_biz_id, bk_supplier_account, HOST_FIELDS, self.value)
            ipv6_list = []
        hosts = {}
        for host in hosts_list:
            ip = host["bk_host_innerip_v6"] if host.get("bk_host_innerip_v6") in ipv6_list else host["bk_host_innerip"]
            # bk_cloud_id as a dict is not needed
            if "bk_cloud_id" in host:
                host.pop("bk_cloud_id")
            hosts[ip] = host
        return hosts


class VarCmdbIpFilter(LazyVariable, SelfExplainVariable):
    code = "ip_filter"
    name = _("IP过滤器")
    type = "dynamic"
    tag = "var_cmdb_ip_filter.ip_filter"
    form = "%svariables/cmdb/var_cmdb_ip_filter.js" % settings.STATIC_URL
    desc = _("引用${KEY}，返回符合过滤条件的IP, IP格式为下面表单指定的格式")

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        fields = [
            FieldExplain(key="${KEY}", type=Type.STRING, description="返回符合过滤条件的【管控区域:IP】"),
        ]
        return fields

    def get_value(self):
        if "executor" not in self.pipeline_data or "project_id" not in self.pipeline_data:
            raise Exception("ERROR: executor and project_id of pipeline is needed")

        tenant_id = self.pipeline_data["tenant_id"]
        origin_ips = self.value.get("origin_ips", "")
        ip_cloud = self.value.get("ip_cloud", True)
        ip_separator = self.value.get("ip_separator", ",")

        origin_ip_list = get_plat_ip_by_regex(origin_ips)
        filter_data = {**self.value, **self.pipeline_data}
        if settings.ENABLE_IPV6:
            gse_agent_status_ipv6_filter = GseAgentStatusIpV6Filter(tenant_id, origin_ips, filter_data)
            match_result_ip = gse_agent_status_ipv6_filter.get_match_ip()
            if not ip_cloud:
                return ip_separator.join(["{}".format(host["ip"]) for host in match_result_ip])
            result = []
            for host in match_result_ip:
                p_address = ipaddress.ip_address(host["ip"])
                if p_address.version == 6:
                    # 针对于ipv6 需要保持ipv6+管控区域的格式
                    result.append("{}:[{}]".format(host["bk_cloud_id"], host["ip"]))
                else:
                    result.append("{}:{}".format(host["bk_cloud_id"], host["ip"]))
            return ip_separator.join(result)
        else:
            # 进行gse agent状态过滤
            gse_agent_status_filter = GseAgentStatusIpFilter(tenant_id, origin_ip_list, filter_data)
            match_result_ip = gse_agent_status_filter.get_match_ip()
            if not ip_cloud:
                return ip_separator.join(["{}".format(host["ip"]) for host in match_result_ip])

            return ip_separator.join(["{}:{}".format(host["bk_cloud_id"], host["ip"]) for host in match_result_ip])
