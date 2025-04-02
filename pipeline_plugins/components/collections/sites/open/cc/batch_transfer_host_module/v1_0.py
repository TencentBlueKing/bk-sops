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

from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import ArrayItemSchema, BooleanItemSchema, ObjectItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.cc.base import (
    BkObjType,
    CCPluginIPMixin,
    cc_list_select_node_inst_id,
)
from pipeline_plugins.components.utils import chunk_table_data, convert_num_to_str
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("celery")

__group_name__ = _("配置平台(CMDB)")
VERSION = "1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCBatchTransferHostModule(Service, CCPluginIPMixin):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("填参方式"),
                key="cc_transfer_select_method_method",
                type="string",
                schema=StringItemSchema(description=_("填参方式")),
            ),
            self.InputItem(
                name=_("更新主机所属业务模块详情"),
                key="cc_host_transfer_detail",
                type="array",
                schema=ArrayItemSchema(
                    description=_("更新主机所属业务模块详情"),
                    item_schema=ObjectItemSchema(description=_("业务模块属性修改对象"), property_schemas={}),
                ),
            ),
            self.InputItem(
                name=_("自动扩展分隔符"),
                key="cc_transfer_host_template_break_line",
                type="string",
                schema=StringItemSchema(description=_("在自动填参时使用的扩展分割符")),
            ),
            self.InputItem(
                name=_("更新方式"),
                key="is_append",
                type="boolean",
                schema=BooleanItemSchema(description=_("更新方式")),
            ),
        ]

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("更新成功的主机"),
                key="set_update_success",
                type="object",
                schema=ObjectItemSchema(description=_("更新成功的主机"), property_schemas={}),
            ),
            self.OutputItem(
                name=_("更新失败的主机"),
                key="set_update_failed",
                type="object",
                schema=ObjectItemSchema(description=_("更新失败的主机"), property_schemas={}),
            ),
        ]

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        supplier_account = supplier_account_for_business(biz_cc_id)

        cc_module_select_method = data.get_one_of_inputs("cc_module_select_method")
        cc_host_transfer_detail = data.get_one_of_inputs("cc_host_transfer_detail")
        cc_transfer_host_template_break_line = data.get_one_of_inputs("cc_transfer_host_template_break_line") or ","
        is_append = data.get_one_of_inputs("is_append", default=True)
        cc_host_transfer_detail = convert_num_to_str(cc_host_transfer_detail)

        attr_list = []
        # 对 单行扩展 填参方式
        if cc_module_select_method == "auto":
            for cc_srv_busi_item in cc_host_transfer_detail:
                chunk_result = chunk_table_data(cc_srv_busi_item, cc_transfer_host_template_break_line)
                if not chunk_result["result"]:
                    data.set_outputs("ex_data", chunk_result["message"])
                    return False
                attr_list.extend(chunk_result["data"])
        else:
            # 非单行扩展的情况无需处理
            attr_list = cc_host_transfer_detail
        success_update = []
        failed_update = []
        for attr in attr_list:
            cc_module_path = attr["cc_transfer_host_target_module"]
            # 获取主机id列表
            host_result = self.get_host_list(executor, biz_cc_id, attr["cc_transfer_host_ip"], supplier_account)
            if not host_result["result"]:
                message = _(
                    f"主机转移模块失败: [配置平台]里未找到待转移的主机, 请检查配置. 主机属性:{attr}, 错误信息: {host_result['message']}"
                )
                self.logger.info(message)
                failed_update.append(message)
                continue
            # 获取 bk module id
            cc_list_select_node_inst_id_return = cc_list_select_node_inst_id(
                tenant_id,
                executor,
                biz_cc_id,
                supplier_account,
                BkObjType.MODULE,
                cc_module_path,
                parent_data.get_one_of_inputs("bk_biz_name"),
            )
            if not cc_list_select_node_inst_id_return["result"]:
                message = _(
                    "无法获取bk module id，"
                    "主机属性={}, message={}".format(attr, cc_list_select_node_inst_id_return["message"])
                )
                self.logger.info(message)
                failed_update.append(message)
                continue
            cc_module_select = cc_list_select_node_inst_id_return["data"]

            cc_kwargs = {
                "bk_biz_id": biz_cc_id,
                "bk_supplier_account": supplier_account,
                "bk_host_id": [int(host_id) for host_id in host_result["data"]],
                "bk_module_id": [int(module_id) for module_id in cc_module_select],
                "is_increment": is_append,
            }
            update_result = client.api.transfer_host_module(
                cc_kwargs,
                headers={"X-Bk-Tenant-Id": tenant_id},
            )

            if update_result["result"]:
                self.logger.info("主机所属业务模块更新成功, data={}".format(cc_kwargs))
                success_update.append(attr)
            else:
                message = _(
                    f"主机所属业务模块更新失败: 主机属性={attr}, kwargs: {cc_kwargs}, 错误信息: {update_result['message']}"
                )
                self.logger.info(message)
                failed_update.append(message)

        data.set_outputs("transfer_host_module_success", success_update)
        data.set_outputs("transfer_host_module_failed", failed_update)
        # 如果没有更新失败的行
        if not failed_update:
            return True
        data.set_outputs("ex_data", failed_update)
        return False


class CCBatchTransferHostModuleComponent(Component):
    """
    @version log（v1.0）:支持 单行扩展输入配置方式
    """

    name = _("批量更新主机所属业务模块")
    code = "cc_batch_transfer_host_module"
    bound_service = CCBatchTransferHostModule
    form = "{static_url}components/atoms/cc/batch_transfer_host_module/v{ver}.js".format(
        static_url=settings.STATIC_URL, ver=VERSION.replace(".", "_")
    )
    version = VERSION
    desc = _(
        "1. 填参方式支持手动填写和结合模板生成（单行自动扩展）\n"
        '2. 使用单行自动扩展模式时，每一行支持填写多个已自定义分隔符或是英文逗号分隔的数据，插件后台会自动将其扩展成多行，如 "1,2,3,4" 会被扩展成四行：1 2 3 4 \n'
        "3. 结合模板生成（单行自动扩展）当有一列有多条数据时，其他列要么也有相等个数的数据，要么只有一条数据 \n"
        "注意：如果需要移动主机到待回收/故障机/空闲机，请使用插件如下插件:\n"
        "转移主机至待回收模块, 转移主机至故障机模块, 转移主机至空闲机模块"
    )
