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
    SelectMethod,
    cc_format_tree_mode_id,
    cc_list_select_node_inst_id,
)
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username


__group_name__ = _("配置平台(CMDB)")
VERSION = "v1.0"
cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCCreateSetBySetTemplateService(Service):
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
                key="cc_select_set_parent_method",
                type="string",
                schema=StringItemSchema(
                    description=_("父实例填入方式，拓扑(topo)，层级文本(text)"), enum=["topo", "text"]
                ),
            ),
            self.InputItem(
                name=_("拓扑-父实例"),
                key="cc_set_parent_select_topo",
                type="array",
                schema=ArrayItemSchema(
                    description=_("父实例 ID 列表"), item_schema=IntItemSchema(description=_("实例 ID"))
                ),
            ),
            self.InputItem(
                name=_("文本路径-父实例"),
                key="cc_set_parent_select_text",
                type="string",
                schema=StringItemSchema(
                    description=_(
                        "父实例文本路径，请输入完整路径，从业务拓扑开始，如`业务A>网络B`，多个父实例用换行分隔"
                    )
                ),
            ),
            self.InputItem(
                name=_("集群名称"),
                key="cc_set_name",
                type="string",
                schema=StringItemSchema(description=_("集群名称")),
            ),
            self.InputItem(
                name=_("集群模板"),
                key="cc_set_template",
                type="string",
                schema=StringItemSchema(description=_("集群模板")),
            ),
        ]

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")

        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        supplier_account = supplier_account_for_business(biz_cc_id)
        cc_select_set_parent_method = data.get_one_of_inputs("cc_select_set_parent_method")

        if cc_select_set_parent_method == SelectMethod.TOPO.value:
            # topo类型直接通过cc_format_tree_mode_id解析父节点bz_inst_id
            cc_set_parent_select = cc_format_tree_mode_id(data.get_one_of_inputs("cc_set_parent_select_topo"))
        elif cc_select_set_parent_method == SelectMethod.TEXT.value:
            cc_set_parent_select_text = data.get_one_of_inputs("cc_set_parent_select_text")
            cc_list_select_node_inst_id_return = cc_list_select_node_inst_id(
                tenant_id, executor, biz_cc_id, supplier_account, BkObjType.LAST_CUSTOM, cc_set_parent_select_text
            )
            if not cc_list_select_node_inst_id_return["result"]:
                data.set_outputs("ex_data", cc_list_select_node_inst_id_return["message"])
                return False
            cc_set_parent_select = cc_list_select_node_inst_id_return["data"]
        else:
            data.set_outputs("ex_data", _("请选择填参方式"))
            return False

        cc_set_names = data.get_one_of_inputs("cc_set_name")
        cc_set_template = data.get_one_of_inputs("cc_set_template")

        result = {"fail": [], "success": []}

        for parent_id in cc_set_parent_select:
            cc_kwargs = {
                "bk_biz_id": biz_cc_id,
                "bk_supplier_account": supplier_account,
                "data": {"bk_parent_id": parent_id},
            }
            for cc_set_name in cc_set_names.split(","):
                try:
                    attr_data_list = data.get_one_of_inputs("cc_set_attr")
                except Exception:
                    attr_data_list = []

                cc_kwargs["data"].update(
                    {"bk_parent_id": parent_id, "bk_set_name": cc_set_name, "set_template_id": cc_set_template}
                )

                if attr_data_list:
                    for attr_data in attr_data_list:
                        cc_kwargs["data"].update({attr_data["attr_id"]: attr_data["attr_value"]})

                cc_result = client.api.create_set(
                    cc_kwargs,
                    path_params={"bk_biz_id": biz_cc_id},
                    headers={"X-Bk-Tenant-Id": tenant_id},
                )
                if not cc_result["result"]:
                    message = cc_handle_api_error("cc.create_set", cc_kwargs, cc_result)
                    self.logger.error(message)
                    result["fail"].append(message)
                else:
                    result["success"].append(cc_result["data"])
        if result["fail"]:
            data.set_outputs("ex_data", result["fail"])
            return False
        return True


class CCCreateSetBySetTemplateComponent(Component):
    name = _("根据模板创建集群")
    version = VERSION
    code = "cc_create_set_by_template"
    bound_service = CCCreateSetBySetTemplateService
    form = "{static_url}components/atoms/cc/create_set_by_template/v1_0.js".format(static_url=settings.STATIC_URL)
