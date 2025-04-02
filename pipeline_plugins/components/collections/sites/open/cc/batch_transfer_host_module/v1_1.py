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
from pipeline.core.flow.io import ArrayItemSchema, BooleanItemSchema, ObjectItemSchema

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from gcloud.utils.ip import get_ip_by_regex
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.cc.base import (
    BkObjType,
    cc_get_host_id_by_innerip,
    cc_list_select_node_inst_id,
)
from pipeline_plugins.components.utils import convert_num_to_str
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("celery")

__group_name__ = _("配置平台(CMDB)")
VERSION = "1.1"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCBatchTransferHostModule(Service):
    def inputs_format(self):
        return [
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

    def get_cc_module_select(self, tenant_id, executor, biz_cc_id, supplier_account, parent_data, cc_module_path_list):
        cc_module_select = []
        for cc_module_path in cc_module_path_list:
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
                return False, [], cc_list_select_node_inst_id_return["message"]
            cc_module_select.extend(cc_list_select_node_inst_id_return["data"])
        return True, cc_module_select, ""

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        supplier_account = supplier_account_for_business(biz_cc_id)
        cc_host_transfer_detail = data.get_one_of_inputs("cc_host_transfer_detail")
        is_append = data.get_one_of_inputs("is_append", default=True)
        cc_host_transfer_detail = convert_num_to_str(cc_host_transfer_detail)

        attr_list = cc_host_transfer_detail
        success_update = []
        failed_update = []
        for attr in attr_list:
            cc_host_ip_list = get_ip_by_regex(attr["cc_transfer_host_ip"])
            cc_module_path_list = attr["cc_transfer_host_target_module"].split(",")

            # 获取主机id列表
            host_result = cc_get_host_id_by_innerip(tenant_id, executor, biz_cc_id, cc_host_ip_list, supplier_account)
            if not host_result["result"]:
                message = _(
                    f"主机转移模块失败: [配置平台]里未找到待转移的主机, 请检查配置. 主机属性:{attr}, 错误信息: {host_result['message']}"
                )
                self.logger.info(message)
                failed_update.append(message)
                continue

            # 获取所有的module_id
            result, cc_module_select, message = self.get_cc_module_select(
                tenant_id, executor, biz_cc_id, supplier_account, parent_data, cc_module_path_list
            )

            if not result:
                message = _(
                    f"主机转移模块失败: [配置平台]未找到目标模块, 请检查配置. 主机属性: {attr}, 错误信息: {message}"
                )
                self.logger.info(message)
                failed_update.append(message)
                continue

            cc_kwargs = {
                "bk_biz_id": biz_cc_id,
                "bk_supplier_account": supplier_account,
                "bk_host_id": [int(host_id) for host_id in host_result["data"]],
                "bk_module_id": [int(module_id) for module_id in set(cc_module_select)],
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
    @version log（v1.1）:支持 单行扩展输入配置方式
    """

    name = _("批量更新主机所属业务模块")
    code = "cc_batch_transfer_host_module"
    bound_service = CCBatchTransferHostModule
    form = "{static_url}components/atoms/cc/batch_transfer_host_module/v{ver}.js".format(
        static_url=settings.STATIC_URL, ver=VERSION.replace(".", "_")
    )
    version = VERSION
    desc = _(
        "支持cc接口ip->模块多对多转移能力，可以在单行输入多个ip和多个模块,使用英文符号(,)分割,执行成功后,这些ip会被转移到对应的模块中,如果ip或模块填写有误,整行将不会执行转移操作\n"
        "注意：如果需要移动主机到待回收/故障机/空闲机，请使用插件如下插件:\n"
        "转移主机至待回收模块, 转移主机至故障机模块, 转移主机至空闲机模块"
    )
