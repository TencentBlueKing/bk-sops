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
from pipeline.core.flow.io import ArrayItemSchema, IntItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.cc.base import (
    BkObjType,
    CCPluginIPMixin,
    SelectMethod,
    cc_format_tree_mode_id,
    cc_list_select_node_inst_id,
)
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("celery")

__group_name__ = _("配置平台(CMDB)")
VERSION = "v1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCTransferHostModuleService(Service, CCPluginIPMixin):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务 ID"),
                key="biz_cc_id",
                type="string",
                schema=StringItemSchema(description=_("当前操作所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_("填参方式"),
                key="cc_module_select_method",
                type="string",
                schema=StringItemSchema(
                    description=_("模块填入方式，拓扑(topo)，层级文本(text)"), enum=["topo", "text"]
                ),
            ),
            self.InputItem(
                name=_("主机内网 IP"),
                key="cc_host_ip",
                type="string",
                schema=StringItemSchema(description=_("待转移的主机内网 IP，多个用英文逗号 `,` 分隔")),
            ),
            self.InputItem(
                name=_("拓扑-模块"),
                key="cc_module_select_topo",
                type="array",
                schema=ArrayItemSchema(
                    description=_("转移目标模块 ID 列表"), item_schema=IntItemSchema(description=_("模块 ID"))
                ),
            ),
            self.InputItem(
                name=_("文本路径-模块"),
                key="cc_module_select_text",
                type="string",
                schema=StringItemSchema(
                    description=_("请输入完整路径，从业务拓扑开始，如`业务A>集群B>模块C`，多个目标模块用换行分隔")
                ),
            ),
            self.InputItem(
                name=_("转移方式"),
                key="cc_is_increment",
                type="string",
                schema=StringItemSchema(description=_("主机转移方式，覆盖(false)或追加(true)"), enum=["false", "true"]),
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

        # 查询主机id
        ip_str = data.get_one_of_inputs("cc_host_ip")
        # 获取主机id列表
        host_result = self.get_ip_info_list(tenant_id, executor, biz_cc_id, ip_str, supplier_account)
        if not host_result["result"]:
            data.set_outputs("ex_data", host_result["message"])
            return False

        cc_is_increment = data.get_one_of_inputs("cc_is_increment")
        cc_module_select_method = data.get_one_of_inputs("cc_module_select_method")
        if cc_module_select_method == SelectMethod.TOPO.value:
            cc_module_select = data.get_one_of_inputs("cc_module_select_topo") or []
            filtered_modules = [module for module in cc_module_select if module.startswith("module")]
            cc_module_select = cc_format_tree_mode_id(filtered_modules)
        elif cc_module_select_method == SelectMethod.TEXT.value:
            cc_module_select_text = data.get_one_of_inputs("cc_module_select_text")
            cc_list_select_node_inst_id_return = cc_list_select_node_inst_id(
                tenant_id, executor, biz_cc_id, supplier_account, BkObjType.MODULE, cc_module_select_text
            )
            if not cc_list_select_node_inst_id_return["result"]:
                data.set_outputs("ex_data", cc_list_select_node_inst_id_return["message"])
                return False
            cc_module_select = cc_list_select_node_inst_id_return["data"]
        else:
            data.set_outputs("ex_data", _("请选择填参方式"))
            return False

        cc_kwargs = {
            "bk_biz_id": biz_cc_id,
            "bk_supplier_account": supplier_account,
            "bk_host_id": [int(host["HostID"]) for host in host_result["ip_result"]],
            "bk_module_id": cc_module_select,
            "is_increment": True if cc_is_increment == "true" else False,
        }
        cc_result = client.api.transfer_host_module(
            cc_kwargs,
            headers={"X-Bk-Tenant-Id": tenant_id},
        )
        if cc_result["result"]:
            return True
        else:
            message = cc_handle_api_error("cc.transfer_host_module", cc_kwargs, cc_result)
            self.logger.error(message)
            data.set_outputs("ex_data", message)
            return False


class CCTransferHostModuleComponent(Component):
    """
    @version log（v1.0）:支持手动输入拓扑路径选择模块，并提供相应输入容错： 冗余回车/换行
    """

    name = _("转移主机模块")
    code = "cc_transfer_host_module"
    bound_service = CCTransferHostModuleService
    form = "{static_url}components/atoms/cc/transfer_host_module/{ver}.js".format(
        static_url=settings.STATIC_URL, ver=VERSION.replace(".", "_")
    )
    version = VERSION
    desc = _(
        "注意：如果需要移动主机到空闲机池，请使用插件如下插件:\n"
        "转移主机至待回收模块, 转移主机至故障机模块, 转移主机至空闲机模块\n"
        "转移方式为【追加】且主机源模块为A（非空闲模块）目标模块为B（非空闲模块）时，主机最终会属于A+B，其它情况下主机均仅属于B"
    )
