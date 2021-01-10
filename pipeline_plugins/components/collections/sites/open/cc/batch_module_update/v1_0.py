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
from functools import partial

from django.utils.translation import ugettext_lazy as _
from gcloud.conf import settings

__group_name__ = _("配置平台(CMDB)")

from gcloud.utils.handlers import handle_api_error

from pipeline.component_framework.component import Component
from pipeline.core.flow.io import ArrayItemSchema, ObjectItemSchema, StringItemSchema
from pipeline.core.flow.activity import Service
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.cc.base import (
    cc_list_select_node_inst_id,
    BkObjType,
    get_module_set_id,
)
from pipeline_plugins.components.utils import chunk_table_data

VERSION = "1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


class CCBatchModuleUpdateService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("填参方式"), key="cc_tag_method", type="string", schema=StringItemSchema(description=_("填参方式")),
            ),
            self.InputItem(
                name=_("拓扑模块属性修改"),
                key="cc_module_update_data",
                type="array",
                schema=ArrayItemSchema(
                    description=_("拓扑模块属性修改"),
                    item_schema=ObjectItemSchema(description=_("拓扑模块属性修改对象"), property_schemas={}),
                ),
            ),
            self.InputItem(
                name=_("自动扩展分隔符"),
                key="cc_template_break_line",
                type="string",
                schema=StringItemSchema(description=_("批量修改模块属性参数")),
            ),
        ]

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        bk_biz_name = parent_data.inputs.bk_biz_name
        cc_module_update_data = data.get_one_of_inputs("cc_module_update_data")
        cc_template_break_line = data.get_one_of_inputs("cc_template_break_line")
        cc_tag_method = data.get_one_of_inputs("cc_tag_method")

        # 如果用户没有输入分隔符，则默认为 ','
        if not cc_template_break_line:
            cc_template_break_line = ","

        attr_list = []
        # 如果用户选择了单行扩展
        if cc_tag_method == "template":
            for cc_module_item in cc_module_update_data:
                chunk_result = chunk_table_data(cc_module_item, cc_template_break_line)
                if not chunk_result["result"]:
                    data.set_outputs("ex_data", chunk_result["message"])
                    return False
                attr_list.extend(chunk_result["data"])
        else:
            # 非单行扩展的情况无需处理
            attr_list = cc_module_update_data

        supplier_account = supplier_account_for_business(biz_cc_id)
        kwargs = {"bk_biz_id": biz_cc_id, "bk_supplier_account": supplier_account}
        tree_data = client.cc.search_biz_inst_topo(kwargs)
        if not tree_data["result"]:
            message = cc_handle_api_error("cc.search_biz_inst_topo", kwargs, tree_data)
            self.logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        success_update = []
        failed_update = []

        for update_item in attr_list:
            update_params = {key: value for key, value in update_item.items() if value}
            try:
                # 处理用户没有输出模块拓扑的情况
                # 拼接完整路径，biz>set>module
                cc_module_select_text = "{}>{}".format(bk_biz_name, update_params.pop("cc_module_select_text"))
            except Exception:
                failed_update.append(update_item)
                self.logger.error("module 属性更新失败,用户未输入模块拓扑的值 " "data={}".format(update_item))
                continue

            supplier_account = supplier_account_for_business(biz_cc_id)
            cc_list_select_node_inst_id_return = cc_list_select_node_inst_id(
                executor, biz_cc_id, supplier_account, BkObjType.MODULE, cc_module_select_text
            )
            if not cc_list_select_node_inst_id_return["result"]:
                failed_update.append(update_item)
                self.logger.error(
                    "module 属性更新失败, message={}, data={}".format(
                        update_item, cc_list_select_node_inst_id_return["message"]
                    )
                )
                continue
            bk_module_id = cc_list_select_node_inst_id_return["data"][0]
            bk_set_id = get_module_set_id(tree_data["data"], bk_module_id)

            kwargs = {
                "bk_biz_id": biz_cc_id,
                "bk_set_id": bk_set_id,
                "bk_module_id": bk_module_id,
                "data": update_params,
            }
            # 更新module属性
            update_result = client.cc.update_module(kwargs)
            if update_result["result"]:
                self.logger.info("module 属性更新成功, data={}".format(kwargs))
                success_update.append(update_item)
            else:
                self.logger.error("module 属性更新失败, data={}".format(kwargs))
                failed_update.append(update_item)

        data.set_outputs("module_update_success", success_update)
        data.set_outputs("module_update_failed", failed_update)
        # 如果没有更新失败的行
        if not failed_update:
            return True

        data.set_outputs("ex_data", "插件执行失败，原因:有更新失败的数据，data={}".format(failed_update))
        return False

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("更新成功的数据"),
                key="module_update_success",
                type="string",
                schema=StringItemSchema(description=_("更新成功的数据")),
            ),
            self.OutputItem(
                name="更新失败的数据",
                key="module_update_failed",
                type="string",
                schema=StringItemSchema(description=_("更新失败的数据")),
            ),
        ]


class CCBatchModuleUpdateComponent(Component):
    name = _("批量更新模块属性")
    version = VERSION
    code = "cc_batch_module_update"
    bound_service = CCBatchModuleUpdateService
    form = "{static_url}components/atoms/cc/batch_module_update/v1_0.js".format(static_url=settings.STATIC_URL)
