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

import logging
import re

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from pipeline.core.data.var import LazyVariable

from pipeline_plugins.cmdb_ip_picker.utils import get_ip_picker_result
from pipeline_plugins.base.utils.inject import supplier_account_for_project
from pipeline_plugins.base.utils.adapter import cc_get_inner_ip_by_module_id
from pipeline_plugins.components.utils import cc_get_ips_info_by_str

from pipeline_plugins.components.utils.common import ip_re

from gcloud.core.models import Project
from gcloud.utils.cmdb import get_business_host
from gcloud.utils.ip import get_ip_by_regex

logger = logging.getLogger("root")


class VarIpPickerVariable(LazyVariable):
    code = "ip"
    name = _("IP选择器(即将下线，请用新版)")
    type = "general"
    tag = "var_ip_picker.ip_picker"
    form = "%svariables/cmdb/var_ip_picker.js" % settings.STATIC_URL

    def get_value(self):
        var_ip_picker = self.value
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
            host_list = cc_get_inner_ip_by_module_id(username, bk_biz_id, module_inst_id_list, bk_supplier_account)
            cc_ip_list = cc_get_ips_info_by_str(username, bk_biz_id, ",".join(tree_ip_list))["ip_result"]
            select_ip = set()

            for host_info in host_list:
                select_ip.add(host_info["host"].get("bk_host_innerip", ""))

            for ip_info in cc_ip_list:
                select_ip.add(ip_info["InnerIP"])

            data = ",".join(list(set(select_ip)))

        return data


class VarCmdbIpSelector(LazyVariable):
    code = "ip_selector"
    name = _("IP选择器")
    type = "general"
    tag = "var_cmdb_ip_selector.ip_selector"
    form = "%svariables/cmdb/var_cmdb_ip_selector.js" % settings.STATIC_URL

    def get_value(self):
        username = self.pipeline_data["executor"]
        project_id = self.pipeline_data["project_id"]
        project = Project.objects.get(id=project_id)
        bk_biz_id = project.bk_biz_id if project.from_cmdb else ""
        bk_supplier_account = supplier_account_for_project(project_id)

        ip_selector = self.value
        ip_result = get_ip_picker_result(username, bk_biz_id, bk_supplier_account, ip_selector)

        # get for old value compatible
        if self.value.get("with_cloud_id", False):
            ip = ",".join(["{}:{}".format(host["bk_cloud_id"], host["bk_host_innerip"]) for host in ip_result["data"]])
        else:
            ip = ",".join([host["bk_host_innerip"] for host in ip_result["data"]])
        return ip


class SetDetailData(object):
    def __init__(self, data):
        self._value = data
        item_values = {}
        modules = []
        for item in data:
            for key, val in item.items():
                if key == "__module":
                    item_module = {mod["key"]: ",".join(mod["value"]) for mod in val}
                    modules.append(item_module)
                else:
                    item_values.setdefault(key, []).append(val)
        for attr, attr_val in item_values.items():
            setattr(self, attr, attr_val)
            flat_val = "\n".join(map(str, attr_val))
            setattr(self, "flat__{}".format(attr), flat_val)
        setattr(self, "_module", modules)


class VarCmdbSetAllocation(LazyVariable):
    code = "set_allocation"
    name = _("集群资源筛选")
    type = "general"
    tag = "var_cmdb_resource_allocation.set_allocation"
    form = "%svariables/cmdb/var_cmdb_resource_allocation.js" % settings.STATIC_URL

    def get_value(self):
        """
        @summary: 返回 SetDetailData 对象
        @note: 引用集群资源变量某一列某一行的属性，如 ${value.bk_set_name[0]} -> "集群1"
        @note: 引用集群资源变量某一列的全部属性，多行用换行符 `\n` 分隔，如 ${value.flat__bk_set_name} -> "集群1\n集群2"
        @note: 引用集群资源变量的模块分配的 IP ${value._module[0]["gamesvr"]} -> "127.0.0.1,127.0.0.2"
        @return:
        """
        return SetDetailData(self.value["data"])


class VarCmdbAttributeQuery(LazyVariable):
    code = "attribute_query"
    name = _("主机属性查询器")
    type = "general"
    tag = "var_cmdb_attr_query.attr_query"
    form = "%svariables/cmdb/var_cmdb_attribute_query.js" % settings.STATIC_URL

    def get_value(self):
        """
        @summary: 返回 dict 对象，将每个可从CMDB查询到的输入IP作为键，将从CMDB查询到的主机属性封装成字典作为值
        @note: 引用127.0.0.1的所有属性，如 ${value["127.0.0.1"]} -> {"bk_host_id": 999, "import_from": 3, ...}
        @note: 引用127.0.0.1的bk_host_id属性，如 ${value["127.0.0.1"]["bk_host_id"]} -> 999
        @return:
        """
        username = self.pipeline_data["executor"]
        project_id = self.pipeline_data["project_id"]
        project = Project.objects.get(id=project_id)
        bk_biz_id = project.bk_biz_id if project.from_cmdb else ""
        bk_supplier_account = supplier_account_for_project(project_id)
        ip_list = get_ip_by_regex(self.value)
        if not ip_list:
            return {}

        hosts_list = get_business_host(
            username,
            bk_biz_id,
            bk_supplier_account,
            [
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
            ],
            ip_list,
        )

        hosts = {}
        for host in hosts_list:
            ip = host["bk_host_innerip"]
            # bk_cloud_id as a dict is not needed
            if "bk_cloud_id" in host:
                host.pop("bk_cloud_id")
            hosts[ip] = host
        return hosts
