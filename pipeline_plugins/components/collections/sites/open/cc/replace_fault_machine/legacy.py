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
from functools import partial

from django.utils import translation
from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import ArrayItemSchema, BooleanItemSchema, ObjectItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.cc.base import CCPluginIPMixin
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("celery")

__group_name__ = _("配置平台(CMDB)")

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCReplaceFaultMachineService(Service, CCPluginIPMixin):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务 ID"),
                key="biz_cc_id",
                type="string",
                schema=StringItemSchema(description=_("当前操作所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_("主机替换信息"),
                key="cc_host_replace_detail",
                type="object",
                schema=ArrayItemSchema(
                    description=_("主机替换信息"),
                    item_schema=ObjectItemSchema(
                        description=_("替换机与被替换机信息"),
                        property_schemas={
                            "cc_fault_ip": StringItemSchema(description=_("故障机 内网IP")),
                            "cc_new_ip": StringItemSchema(description=_("替换机 内网IP")),
                        },
                    ),
                ),
            ),
            self.InputItem(
                name=_("复制故障机属性"),
                key="copy_attributes",
                type="bool",
                schema=BooleanItemSchema(description=_("复制故障机属性")),
            ),
        ]

    def outputs_format(self):
        return []

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")

        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        supplier_account = supplier_account_for_business(biz_cc_id)
        cc_hosts = data.get_one_of_inputs("cc_host_replace_detail")
        copy_attrs = data.get_one_of_inputs("copy_attributes", True)

        # 查询主机可编辑属性
        search_attr_kwargs = {"bk_obj_id": "host", "bk_supplier_account": supplier_account}
        search_attr_result = client.api.search_object_attribute(
            search_attr_kwargs,
            headers={"X-Bk-Tenant-Id": tenant_id},
        )
        if not search_attr_result["result"]:
            message = cc_handle_api_error("cc.search_object_attribute", search_attr_kwargs, search_attr_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

        editable_attrs = []
        for item in search_attr_result["data"]:
            if item["editable"]:
                editable_attrs.append(item["bk_property_id"])

        host_attrs = editable_attrs

        # 只有复制故障机属性时才用到
        batch_update_kwargs = {"bk_obj_id": "host", "bk_supplier_account": supplier_account, "update": []}
        fault_replace_id_map = {}
        fault_host_map = {}
        for host in cc_hosts:
            fault_ip = host["cc_fault_ip"]
            new_ip = host["cc_new_ip"]

            fault_host_list = self.get_host_topo(tenant_id, executor, biz_cc_id, supplier_account, host_attrs, fault_ip)
            new_host_list = self.get_host_topo(tenant_id, executor, biz_cc_id, supplier_account, host_attrs, new_ip)

            # 如果不存在，或者查询到的值大于1
            if not fault_host_list or len(fault_host_list) != 1:
                # 查询旧的主机出错
                data.outputs.ex_data = data.outputs.ex_data = (
                    _("无法查询到 %s 机器信息，请确认该机器是否在当前业务下") % fault_ip
                )
                return False

            if not new_host_list or len(new_host_list) != 1:
                data.outputs.ex_data = data.outputs.ex_data = (
                    _("无法查询到 %s 机器信息，请确认该机器是否在当前业务下") % fault_ip
                )
                return False

            fault_host = fault_host_list[0]
            new_host = new_host_list[0]
            if copy_attrs:
                update_item = {"properties": {}, "bk_host_id": new_host["host"]["bk_host_id"]}
                for attr in [attr for attr in editable_attrs if attr in fault_host["host"]]:
                    update_item["properties"][attr] = fault_host["host"][attr]
                batch_update_kwargs["update"].append(update_item)

            fault_replace_id_map[fault_host["host"]["bk_host_id"]] = new_host
            fault_host_map[fault_host["host"]["bk_host_id"]] = fault_host

        # 更新替换机信息
        if copy_attrs:
            update_result = client.api.batch_update_host(
                batch_update_kwargs,
                headers={"X-Bk-Tenant-Id": tenant_id},
            )
            if not update_result["result"]:
                message = cc_handle_api_error("cc.batch_update_host", batch_update_kwargs, update_result)
                self.logger.error(message)
                data.outputs.ex_data = message
                return False

        # 将主机上交至故障机模块
        fault_transfer_kwargs = {
            "bk_supplier_account": supplier_account,
            "bk_biz_id": biz_cc_id,
            "bk_host_id": list(fault_replace_id_map.keys()),
        }
        fault_transfer_result = client.api.transfer_host_to_faultmodule(
            fault_transfer_kwargs,
            headers={"X-Bk-Tenant-Id": tenant_id},
        )
        if not fault_transfer_result["result"]:
            message = cc_handle_api_error(
                "cc.transfer_host_to_faultmodule", fault_transfer_kwargs, fault_transfer_result
            )
            self.logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        # 转移主机模块
        transfer_kwargs_list = []
        for fault_replace_id, new_host in fault_replace_id_map.items():
            fault_host = fault_host_map[fault_replace_id]
            transfer_kwargs_list.append(
                {
                    "bk_biz_id": biz_cc_id,
                    "bk_supplier_account": supplier_account,
                    "bk_host_id": [new_host["host"]["bk_host_id"]],
                    "bk_module_id": [module_info["bk_module_id"] for module_info in fault_host["module"]],
                    "is_increment": True,
                }
            )

        success = []
        for kwargs in transfer_kwargs_list:
            transfer_result = client.api.transfer_host_module(
                kwargs,
                headers={"X-Bk-Tenant-Id": tenant_id},
            )
            if not transfer_result["result"]:
                message = cc_handle_api_error("cc.transfer_host_module", kwargs, transfer_result)
                self.logger.error(message)
                data.outputs.ex_data = "{msg}\n{success}".format(
                    msg=message, success=_("成功替换的机器: %s") % ",".join(success)
                )
                return False
            success.append(kwargs["bk_host_id"][0])


class CCReplaceFaultMachineComponent(Component):
    name = _("故障机替换")
    code = "cc_replace_fault_machine"
    bound_service = CCReplaceFaultMachineService
    form = "%scomponents/atoms/cc/cc_replace_fault_machine.js" % settings.STATIC_URL
    desc = _("如果配置平台中模块启动了属性自动应用策略，则 复制故障机属性 选项无法复制对应属性")
