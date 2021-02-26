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

from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.components.utils import chunk_table_data

from pipeline_plugins.components.collections.sites.open.cc.base import (
    BkObjType,
    cc_get_host_id_by_innerip,
    cc_list_select_node_inst_id,
)


logger = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")
VERSION = "1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCBatchTransferHostModule(Service):
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
        client = get_client_by_user(executor)
        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        supplier_account = supplier_account_for_business(biz_cc_id)

        cc_module_select_method = data.get_one_of_inputs("cc_module_select_method")
        cc_host_transfer_detail = data.get_one_of_inputs("cc_host_transfer_detail")
        cc_transfer_host_template_break_line = data.get_one_of_inputs("cc_transfer_host_template_break_line") or ","

        attr_list = []
        # 对 单行扩展 填参方式
        if cc_module_select_method == "template":
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
            cc_host_ip_list = [attr["cc_transfer_host_ip"]]
            cc_module_path = attr["cc_transfer_host_target_module"]

            # 获取主机id列表
            host_result = cc_get_host_id_by_innerip(executor, biz_cc_id, cc_host_ip_list, supplier_account)
            if not host_result["result"]:
                data.set_outputs("ex_data", host_result["message"])
                failed_update.append(attr)
                continue
            # 获取 bk module id
            cc_list_select_node_inst_id_return = cc_list_select_node_inst_id(
                executor, biz_cc_id, supplier_account, BkObjType.MODULE, cc_module_path
            )
            if not cc_list_select_node_inst_id_return["result"]:
                data.set_outputs("ex_data", cc_list_select_node_inst_id_return["message"])
                failed_update.append(attr)
                continue
            cc_module_select = cc_list_select_node_inst_id_return["data"]

            cc_kwargs = {
                "bk_biz_id": biz_cc_id,
                "bk_supplier_account": supplier_account,
                "bk_host_id": [int(host_id) for host_id in host_result["data"]],
                "bk_module_id": [int(module_id) for module_id in cc_module_select],
                "is_increment": True,
            }
            update_result = client.cc.transfer_host_module(cc_kwargs)

            if update_result["result"]:
                self.logger.info("主机所属业务模块更新成功, data={}".format(cc_kwargs))
                success_update.append(attr)
            else:
                self.logger.info("主机所属业务模块更新失败, data={}".format(cc_kwargs))
                failed_update.append(attr)

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
