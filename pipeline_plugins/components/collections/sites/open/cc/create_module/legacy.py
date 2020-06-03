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

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, IntItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component

from pipeline_plugins.components.collections.sites.open.cc.base import (
    BkObjType,
    SelectMethod,
    ModuleCreateMethod,
    cc_format_tree_mode_id,
    cc_list_select_node_inst_id,
    cc_format_prop_data,
    cc_get_name_id_from_combine_value
)
from pipeline_plugins.base.utils.inject import supplier_account_for_business

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCCreateModuleService(Service):
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
                key="cc_set_select_method",
                type="string",
                schema=StringItemSchema(description=_("集群填入方式，拓扑(topo)，层级文本(text)"), enum=["topo", "text"]),
            ),
            self.InputItem(
                name=_("拓扑-集群列表"),
                key="cc_set_select_topo",
                type="array",
                schema=ArrayItemSchema(description=_("所属集群 ID 列表"), item_schema=IntItemSchema(description=_("集群 ID"))),
            ),
            self.InputItem(
                name=_("文本路径-集群"),
                key="cc_set_select_text",
                type="string",
                schema=StringItemSchema(description=_("集群文本路径，请输入完整路径，从业务拓扑开始，如`业务A>网络B>集群C`，多个目标集群用换行分隔")),
            ),
            self.InputItem(
                name=_("创建方式"),
                key="cc_create_method",
                type="string",
                schema=StringItemSchema(description=_("从模板创建(template)，层级文本(ca)"), enum=["topo", "text"]),
            ),
            self.InputItem(
                name=_("模块信息列表-直接创建（通过服务分类创建）"),
                key="cc_module_infos_category",
                type="array",
                schema=ArrayItemSchema(
                    description=_("模块信息对象列表"),
                    item_schema=ObjectItemSchema(description=_("模块信息描述对象"), property_schemas={}),
                ),
            ),
            self.InputItem(
                name=_("模块信息列表-按服务模板创建"),
                key="cc_module_infos_template",
                type="array",
                schema=ArrayItemSchema(
                    description=_("模块信息对象列表"),
                    item_schema=ObjectItemSchema(description=_("模块信息描述对象"), property_schemas={}),
                ),
            ),
        ]

    def outputs_format(self):
        return []

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))
        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        supplier_account = supplier_account_for_business(biz_cc_id)
        cc_set_select_method = data.get_one_of_inputs("cc_set_select_method")
        cc_create_method = data.get_one_of_inputs("cc_create_method")
        # 校验创建及填参方式，避免中途校验失败时已进行多余的逻辑判断
        if cc_set_select_method not in [SelectMethod.TOPO.value, SelectMethod.TEXT.value]:
            data.set_outputs("ex_data", _("请选择填参方式"))
            return False
        if cc_create_method not in [ModuleCreateMethod.CATEGORY.value, ModuleCreateMethod.TEMPLATE.value]:
            data.set_outputs("ex_data", _("请选择创建方式"))
            return False
        if cc_set_select_method == SelectMethod.TOPO.value:
            cc_set_select = cc_format_tree_mode_id(data.get_one_of_inputs("cc_set_select_topo"))
        else:   # text
            cc_set_select_text = data.get_one_of_inputs("cc_set_select_text")
            cc_list_select_node_inst_id_return = cc_list_select_node_inst_id(
                executor, biz_cc_id, supplier_account, BkObjType.SET, cc_set_select_text
            )
            if not cc_list_select_node_inst_id_return["result"]:
                data.set_outputs("ex_data", cc_list_select_node_inst_id_return["message"])
                return False
            cc_set_select = cc_list_select_node_inst_id_return["data"]

        if cc_create_method == ModuleCreateMethod.TEMPLATE.value:
            cc_module_infos_untreated = data.get_one_of_inputs("cc_module_infos_template")
        else:   # category
            cc_module_infos_untreated = data.get_one_of_inputs("cc_module_infos_category")
        cc_module_infos = []
        for cc_module_info_untreated in cc_module_infos_untreated:
            if cc_create_method == ModuleCreateMethod.TEMPLATE.value:
                service_template_name, service_template_id = cc_get_name_id_from_combine_value(
                    cc_module_info_untreated.pop("cc_service_template")
                )
                if service_template_id is None:
                    data.set_outputs("ex_data", _("请选择正确的服务模板"))
                    return False
                cc_module_info_untreated["service_template_id"] = service_template_id
                # 按模板创建时，模块名称与模板名称保持一致
                cc_module_info_untreated["bk_module_name"] = service_template_name
            else:   # category
                if len(cc_module_info_untreated["cc_service_category"]) != 2:
                    data.set_outputs("ex_data", _("请选择正确的服务类型"))
                    return False
                service_category_id = cc_module_info_untreated.pop("cc_service_category")[-1]
                cc_module_info_untreated["service_category_id"] = service_category_id

            # 过滤空值
            cc_module_info = {
                module_property: module_prop_value
                for module_property, module_prop_value in cc_module_info_untreated.items()
                if module_prop_value
            }

            if cc_create_method == ModuleCreateMethod.CATEGORY.value and "bk_module_name" not in cc_module_info:
                data.set_outputs("ex_data", _("模块名称不能为空"))
                return False
            # 校验模块类型
            if "bk_module_type" in cc_module_info:
                format_prop_data_return = cc_format_prop_data(
                    executor, "module", "bk_module_type", parent_data.get_one_of_inputs("language"), supplier_account
                )
                if not format_prop_data_return["result"]:
                    data.set_outputs("ex_data", format_prop_data_return["message"])
                    return False
                bk_module_type = format_prop_data_return["data"].get(cc_module_info["bk_module_type"])
                if not bk_module_type:
                    data.set_outputs("ex_data", _("模块类型校验失败，请重试并填写正确的模块类型"))
                    return False
                cc_module_info["bk_module_type"] = bk_module_type
            cc_module_infos.append(cc_module_info)
        for parent_id in cc_set_select:
            for cc_module_info in cc_module_infos:
                cc_kwargs = {
                    "bk_biz_id": biz_cc_id,
                    "bk_set_id": parent_id,
                    "data": {"bk_parent_id": parent_id},
                }
                cc_kwargs["data"].update(cc_module_info)
                cc_create_module_return = client.cc.create_module(cc_kwargs)
                if not cc_create_module_return["result"]:
                    message = cc_handle_api_error("cc.create_module", cc_kwargs, cc_create_module_return)
                    self.logger.error(message)
                    data.set_outputs("ex_data", message)
                    return False
        return True


class CCCreateModuleComponent(Component):
    """
    @version legacy:
        - 支持手动输入拓扑路径选择集群，并提供相应输入容错：冗余回车/换行
        - 支持按服务模板创建 & 直接创建
    """

    name = _("创建模块")
    code = "cc_create_module"
    bound_service = CCCreateModuleService
    form = "{static_url}components/atoms/cc/create_module/legacy.js".format(static_url=settings.STATIC_URL)
