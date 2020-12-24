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
from functools import partial

from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.components.utils.sites.open.utils import cc_get_ips_info_by_str

logger = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")
VERSION = "v1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCHostCustomPropertyChangeService(Service):
    class FileCode(object):
        host_rule = "1"
        set_rule = "2"
        module_rule = "3"
        ip_type_rule = "4"
        auto_var_rule = "5"
        custom_string = "6"

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("IP"), key="cc_ip_list", type="string", schema=StringItemSchema(description=_("多个用换行分隔")),
            ),
            self.InputItem(
                name=_("自定义属性"),
                key="cc_custom_property",
                type="string",
                schema=StringItemSchema(description=_("请选择主机自定义属性")),
            ),
            self.InputItem(
                name=_("规则定义(主机属性)"),
                description="cc_hostname_rule",
                type="array",
                schema=ArrayItemSchema(
                    description=_("没有数据"),
                    item_schema=ObjectItemSchema(
                        description=_("规则定义(主机属性)"),
                        property_schemas={
                            "field_rule_code": StringItemSchema(description=_("字段组件")),
                            "field_content": StringItemSchema(description=_("具体内容")),
                            "field_order": StringItemSchema(description=_("次序")),
                        },
                    ),
                ),
            ),
            self.InputItem(
                name=_("规则定义(自定义属性)"),
                description="cc_hostname_rule",
                type="array",
                schema=ArrayItemSchema(
                    description=_("没有数据"),
                    item_schema=ObjectItemSchema(
                        description=_("规则定义(自定义属性)"),
                        property_schemas={
                            "field_rule_code": StringItemSchema(description=_("字段组件")),
                            "field_content": StringItemSchema(description=_("具体内容")),
                            "field_order": StringItemSchema(description=_("次序")),
                        },
                    ),
                ),
            ),
        ]

    def execute(self, data, parent_data):
        operator = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(operator)
        biz_cc_id = parent_data.get_one_of_inputs("biz_cc_id")

        sa_ip_list = data.get_one_of_inputs("cc_ip_list")
        custom_property = data.get_one_of_inputs("cc_custom_property")
        host_rule = data.get_one_of_inputs("cc_hostname_rule")
        custom_rule = data.get_one_of_inputs("cc_custom_rule")

        hostname_rule = []
        if host_rule:
            hostname_rule.extend(host_rule)
        if custom_rule:
            hostname_rule.extend(custom_rule)
        if not hostname_rule:
            data.set_outputs("ex_data", _("请选择至少一种规则"))
            return False

        hostname_rule = sorted(hostname_rule, key=lambda e: str(e.__getitem__("field_order")))

        ip_list = cc_get_ips_info_by_str(username=operator, biz_cc_id=biz_cc_id, ip_str=sa_ip_list, use_cache=False)
        if not ip_list["result"] or not ip_list["ip_count"]:
            data.outputs.ex_data = _("无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法")
            return False
        if ip_list["invalid_ip"]:
            data.outputs.ex_data = _("无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法")
            data.outputs.invalid_ip = ",".join(ip_list["invalid_ip"])
            return False

        # 规则中包含的自增变量个数
        inc_num = 0
        host_rule_list = []
        set_rule_list = []
        module_rule_list = []
        for rule in hostname_rule:
            if rule["field_rule_code"] == self.FileCode.host_rule and rule["field_content"] not in host_rule_list:
                host_rule_list.append(rule["field_content"])
            if rule["field_rule_code"] == self.FileCode.set_rule and rule["field_content"] not in set_rule_list:
                set_rule_list.append(rule["field_content"])
            if rule["field_rule_code"] == self.FileCode.module_rule and rule["field_content"] not in module_rule_list:
                module_rule_list.append(rule["field_content"])
            if rule["field_rule_code"] == self.FileCode.auto_var_rule:
                inc_num += 1

        # 如果集群规则不为空，拉取集群属性信息
        set_property = {}
        if set_rule_list:
            # 获取所有的集群id和模型id
            set_id_list = []
            for host_data in ip_list["ip_result"]:
                id_list = [_set["bk_set_id"] for _set in host_data["Sets"]]
                set_id_list.extend(id_list)
            set_rule_list.append("bk_set_id")
            # 查询集群的属性值
            set_kwargs = {"bk_biz_id": biz_cc_id, "bk_ids": list(set(set_id_list)), "fields": set_rule_list}
            set_result = client.cc.find_set_batch(set_kwargs)
            if not set_result.get("result"):
                error_message = handle_api_error("蓝鲸配置平台(CC)", "cc.find_set_batch", set_kwargs, set_result)
                data.set_outputs("ex_data", error_message)
                self.logger.error(error_message)
                return False

            for set_data in set_result["data"]:
                set_property[set_data["bk_set_id"]] = set_data

        # 如果模块规则不为空，拉取模块属性信息
        module_property = {}
        if module_rule_list:
            module_id_list = []
            for host_data in ip_list["ip_result"]:
                id_list = [_module["bk_module_id"] for _module in host_data["Modules"]]
                module_id_list.extend(id_list)
            module_rule_list.append("bk_module_id")
            # 查询模块的属性值
            module_kwargs = {"bk_biz_id": biz_cc_id, "bk_ids": list(set(module_id_list)), "fields": module_rule_list}
            module_result = client.cc.find_module_batch(module_kwargs)
            if not module_result.get("result"):
                error_message = handle_api_error("蓝鲸配置平台(CC)", "cc.find_module_batch", module_kwargs, module_result)
                data.set_outputs("ex_data", error_message)
                self.logger.error(error_message)
                return False

            for module_data in module_result["data"]:
                module_property[module_data["bk_module_id"]] = module_data

        # 数据组装，将规则连接起来，并和ip对应
        host_list = []
        # 自增变量
        inc = [-1] * inc_num
        for host in ip_list["ip_result"]:
            custom_property_value = ""
            inc_num_temp = 0
            # 主机属性
            host_kwargs = {"bk_host_id": host["HostID"]}
            host_result = client.cc.get_host_base_info(**host_kwargs)
            if not host_result.get("result"):
                error_message = handle_api_error("蓝鲸配置平台(CC)", "cc.get_host_base_info", host_kwargs, host_result)
                data.set_outputs("ex_data", error_message)
                self.logger.error(error_message)
                return False
            host_content = {}
            for host_prop in host_result["data"]:
                if host_prop["bk_property_id"] in host_rule_list:
                    host_content[host_prop["bk_property_id"]] = host_prop["bk_property_value"]

            for rule in hostname_rule:
                if rule["field_rule_code"] == self.FileCode.host_rule and host_content[rule["field_content"]]:
                    custom_property_value += host_content[rule["field_content"]]
                if rule["field_rule_code"] == self.FileCode.set_rule:
                    # 集群属性
                    set_content_list = [set_property[_set["bk_set_id"]] for _set in host["Sets"]]
                    for set_content in set_content_list:
                        if set_content.get(rule["field_content"]):
                            custom_property_value += set_content[rule["field_content"]]
                if rule["field_rule_code"] == self.FileCode.module_rule:
                    # 模块属性
                    module_content_list = [module_property[_module["bk_module_id"]] for _module in host["Modules"]]
                    for module_content in module_content_list:
                        if module_content.get(rule["field_content"]):
                            custom_property_value += module_content[rule["field_content"]]
                if rule["field_rule_code"] == self.FileCode.ip_type_rule:
                    custom_property_value += host["InnerIP"].replace(".", rule["field_content"])
                # 第一个自增变量
                if rule["field_rule_code"] == self.FileCode.auto_var_rule:
                    if inc[inc_num_temp] == -1:
                        inc[inc_num_temp] = int(rule["field_content"])
                    else:
                        inc[inc_num_temp] += 1
                    custom_property_value += str(inc[inc_num_temp])
                    inc_num_temp += 1
                # 自定义字符串
                if rule["field_rule_code"] == self.FileCode.custom_string:
                    custom_property_value += rule["field_content"]
            host_list.append({"bk_host_id": host["HostID"], "properties": {custom_property: custom_property_value}})

        kwargs = {"update": host_list}
        result = client.cc.batch_update_host(kwargs)
        if not result["result"]:
            message = cc_handle_api_error("cc.batch_update_host", kwargs, result)
            self.logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        return True

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("不合法的IP"), key="invalid_ip", type="string", schema=StringItemSchema(description=_("不合法的IP"))
            ),
        ]


class CCHostCustomPropertyChangeComponent(Component):
    name = _("按规则修改主机自定义属性")
    code = "cc_host_custom_property_change"
    bound_service = CCHostCustomPropertyChangeService
    form = "{static_url}components/atoms/cc/host_custom_property_change/{ver}.js".format(
        static_url=settings.STATIC_URL, ver=VERSION.replace(".", "_")
    )
    version = VERSION
    desc = _(
        "1.规则示例：\n"
        "  IP: 192.168.0.1\n"
        "  自定义属性：主要维护人\n"
        "  规则定义(主机属性)：\n"
        "     主机属性      | 主要维护人 | 1 \n"
        "     set属性      | 集群名    | 3 \n"
        "  规则定义(自定义属性)：\n"
        "     自定义字符(串) | hello    | 2 \n"
        "     ip(.需替换成) | *        | 4 \n"
        "  修改成功后的期望值为：\n"
        "     主要维护人 = 主要维护人【admin】 + 自定义字符(串)【hello】 + 集群名【set_name】 + ip(.需替换成)【192*168*0*1】\n"
        "     即： 主要维护人 = adminhelloset_name192*168*0*1 \n"
        "2.次序是用来给规则排序的"
    )
