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
    SelectMethod,
    cc_format_prop_data,
    cc_format_tree_mode_id,
    cc_list_select_node_inst_id,
    get_module_set_id,
)

logger = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")
VERSION = "v1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCUpdateModuleService(Service):
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
                    description=_(
                        "模块文本路径，请输入完整路径，从业务拓扑开始，如`业务A>集群B>模块C`，多个目标模块用换行分隔"
                    )
                ),
            ),
            self.InputItem(
                name=_("模块属性"),
                key="cc_module_property",
                type="string",
                schema=StringItemSchema(description=_("需要修改的模块属性")),
            ),
            self.InputItem(
                name=_("属性值"),
                key="cc_module_prop_value",
                type="string",
                schema=StringItemSchema(description=_("模块属性更新后的值")),
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
        cc_module_select_method = data.get_one_of_inputs("cc_module_select_method")
        supplier_account = supplier_account_for_business(biz_cc_id)
        kwargs = {"bk_biz_id": biz_cc_id, "bk_supplier_account": supplier_account}
        tree_data = client.cc.search_biz_inst_topo(kwargs)
        if not tree_data["result"]:
            message = cc_handle_api_error("cc.search_biz_inst_topo", kwargs, tree_data)
            self.logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        if cc_module_select_method == SelectMethod.TOPO.value:
            module_list = data.get_one_of_inputs("cc_module_select_topo")
            # 过滤掉set的情况
            module_list = list(filter(lambda x: x.startswith("module"), module_list))
            cc_module_select = cc_format_tree_mode_id(module_list)
        elif cc_module_select_method == SelectMethod.TEXT.value:
            cc_module_select_text = data.get_one_of_inputs("cc_module_select_text")
            cc_list_select_node_inst_id_return = cc_list_select_node_inst_id(
                executor, biz_cc_id, supplier_account, BkObjType.MODULE, cc_module_select_text
            )
            if not cc_list_select_node_inst_id_return["result"]:
                data.set_outputs("ex_data", cc_list_select_node_inst_id_return["message"])
                return False
            cc_module_select = cc_list_select_node_inst_id_return["data"]
        else:
            data.set_outputs("ex_data", _("请选择模块填参方式"))
            return False

        cc_module_property = data.get_one_of_inputs("cc_module_property")
        if cc_module_property == "bk_module_type":
            bk_module_type = cc_format_prop_data(
                executor, "module", "bk_module_type", parent_data.get_one_of_inputs("language"), supplier_account
            )
            if not bk_module_type["result"]:
                data.set_outputs("ex_data", bk_module_type["message"])
                return False

            cc_module_prop_value = bk_module_type["data"].get(data.get_one_of_inputs("cc_module_prop_value"))
            if not cc_module_prop_value:
                data.set_outputs("ex_data", _("模块类型校验失败，请重试并填写正确的模块类型"))
                return False
        else:
            cc_module_prop_value = data.get_one_of_inputs("cc_module_prop_value")

        for module_id in cc_module_select:
            cc_kwargs = {
                "bk_biz_id": biz_cc_id,
                "bk_supplier_account": supplier_account,
                "bk_set_id": get_module_set_id(tree_data["data"], module_id),
                "bk_module_id": module_id,
                "data": {cc_module_property: cc_module_prop_value},
            }
            cc_result = client.cc.update_module(cc_kwargs)
            if not cc_result["result"]:
                message = cc_handle_api_error("cc.update_module", cc_kwargs, cc_result)
                self.logger.error(message)
                data.set_outputs("ex_data", message)
                return False
        return True


class CCUpdateModuleComponent(Component):
    """
    @version log（v1.0）:支持手动输入拓扑路径选择模块，并提供相应输入容错： 冗余回车/换行
    """

    name = _("更新模块属性")
    code = "cc_update_module"
    bound_service = CCUpdateModuleService
    form = "{static_url}components/atoms/cc/update_module/{ver}.js".format(
        static_url=settings.STATIC_URL, ver=VERSION.replace(".", "_")
    )
    version = VERSION
