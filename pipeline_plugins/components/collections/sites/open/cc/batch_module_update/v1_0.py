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
from functools import partial

from django.utils.translation import gettext_lazy as _

from gcloud.conf import settings

__group_name__ = _("配置平台(CMDB)")

from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import ArrayItemSchema, ObjectItemSchema, StringItemSchema

from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.cc.base import (
    BkObjType,
    cc_list_select_node_inst_id,
    get_module_set_id,
)
from pipeline_plugins.components.utils import chunk_table_data, convert_num_to_str
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

VERSION = "1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCBatchModuleUpdateService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("填参方式"),
                key="cc_tag_method",
                type="string",
                schema=StringItemSchema(description=_("填参方式")),
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
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        bk_biz_name = parent_data.inputs.bk_biz_name
        cc_module_update_data = data.get_one_of_inputs("cc_module_update_data")
        cc_template_break_line = data.get_one_of_inputs("cc_template_break_line") or ","
        cc_tag_method = data.get_one_of_inputs("cc_tag_method")

        cc_module_update_data = convert_num_to_str(cc_module_update_data)

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
        tree_data = client.api.search_biz_inst_topo(
            kwargs,
            path_params={"bk_biz_id": biz_cc_id},
            headers={"X-Bk-Tenant-Id": tenant_id},
        )
        if not tree_data["result"]:
            message = cc_handle_api_error("cc.search_biz_inst_topo", kwargs, tree_data)
            self.logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        success_update = []
        failed_update = []

        search_attr_kwargs = {"bk_obj_id": "module", "bk_supplier_account": supplier_account}
        attr_result = client.api.search_object_attribute(
            search_attr_kwargs,
            headers={"X-Bk-Tenant-Id": tenant_id},
        )
        if not attr_result["result"]:
            message = handle_api_error("cc", "cc.search_object_attribute", search_attr_kwargs, attr_result)
            self.logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        attr_type_mapping = {}
        for item in attr_result["data"]:
            attr_type_transformer = None
            if item["bk_property_type"] == "bool":
                attr_type_transformer = bool
            elif item["bk_property_type"] == "int":
                attr_type_transformer = int
            if attr_type_transformer:
                attr_type_mapping[item["bk_property_id"]] = attr_type_transformer

        for update_item in attr_list:
            # 过滤,去除用户没有填的字段
            update_params = {key: value for key, value in update_item.items() if value}
            # 对字段类型进行转换
            transform_success = True
            for attr, value in update_params.items():
                if attr in attr_type_mapping:
                    try:
                        update_params[attr] = attr_type_mapping[attr](value)
                    except Exception as e:
                        transform_success = False
                        message = _(
                            f"模块属性更新失败: 插件配置的属性不合法, 请修复后重试. item: {update_item}, "
                            f"转换属性: {attr}为{attr_type_mapping[attr]}类型时出错, 错误内容: {e}"
                        )
                        self.logger.error(message)
                        failed_update.append(message)
                        break
            if not transform_success:
                continue

            try:
                # 处理用户没有输出模块拓扑的情况
                # 拼接完整路径，biz>set>module
                cc_module_select_text = "{}>{}".format(bk_biz_name, update_params.pop("cc_module_select_text"))
            except Exception as e:
                message = _(f"模块属性更新失败: 没有提供待更新的模块, 请检查配置. item: {update_item}, message: {e}")
                failed_update.append(message)
                self.logger.error(message)
                continue

            supplier_account = supplier_account_for_business(biz_cc_id)
            cc_list_select_node_inst_id_return = cc_list_select_node_inst_id(
                tenant_id, executor, biz_cc_id, supplier_account, BkObjType.MODULE, cc_module_select_text
            )
            if not cc_list_select_node_inst_id_return["result"]:

                message = _(
                    f"模块属性更新失败: 主机属性: {update_item}, message: {cc_list_select_node_inst_id_return['message']}"
                )
                failed_update.append(message)
                self.logger.error(message)
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
            update_result = client.api.update_module(
                kwargs,
                params={"bk_biz_id": biz_cc_id, "bk_set_id": bk_set_id, "bk_module_id": bk_module_id},
                headers={"X-Bk-Tenant-Id": tenant_id},
            )
            if update_result["result"]:
                self.logger.info("module 属性更新成功, item={}, data={}".format(update_item, kwargs))
                success_update.append(update_item)
            else:
                message = _(
                    f"模块属性更新失败: 主机属性: {update_item}, 更新属性: {kwargs}, 错误消息: {update_result['message']}"
                )
                self.logger.error(message)
                failed_update.append(message)

        data.set_outputs("module_update_success", success_update)
        data.set_outputs("module_update_failed", failed_update)
        # 如果没有更新失败的行
        if not failed_update:
            return True
        data.set_outputs("ex_data", failed_update)
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
                name=_("更新失败的数据"),
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
    desc = _(
        "1. 填参方式支持手动填写和结合模板生成（单行自动扩展）\n"
        "2. 使用单行自动扩展模式时，每一行支持填写多个已自定义分隔符或是英文逗号分隔的数据，"
        '插件后台会自动将其扩展成多行，如 "1,2,3,4" 会被扩展成四行：1 2 3 4\n'
        "3. 结合模板生成（单行自动扩展）当有一列有多条数据时，其他列要么也有相等个数的数据，要么只有一条数据"
    )
