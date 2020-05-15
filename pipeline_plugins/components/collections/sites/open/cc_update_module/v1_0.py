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
from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, IntItemSchema
from pipeline.component_framework.component import Component
from pipeline_plugins.components.collections.sites.open.cc import (
    cc_format_tree_mode_id,
    cc_parse_path_text,
    cc_list_match_node_inst_id,
    cc_format_prop_data,
    get_module_set_id,
)

from pipeline_plugins.base.utils.inject import supplier_account_for_business

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")
VERSION = "v1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCUpdateModuleService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_(u"业务 ID"),
                key="biz_cc_id",
                type="string",
                schema=StringItemSchema(description=_(u"当前操作所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_(u"填参方式"),
                key="cc_module_select_method",
                type="string",
                schema=StringItemSchema(description=_(u"模块填入方式，拓扑(topo)，层级文本(text)"), enum=["topo", "text"]),
            ),
            self.InputItem(
                name=_(u"拓扑 -模块"),
                key="cc_module_select_topo",
                type="array",
                schema=ArrayItemSchema(
                    description=_(u"转移目标模块 ID 列表"), item_schema=IntItemSchema(description=_(u"模块 ID"))
                ),
            ),
            self.InputItem(
                name=_(u"文本路径 -模块"),
                key="cc_module_select_text",
                type="string",
                schema=StringItemSchema(description=_(u"模块文本路径")),
            ),
            self.InputItem(
                name=_(u"模块属性"),
                key="cc_module_property",
                type="string",
                schema=StringItemSchema(description=_(u"需要修改的模块属性")),
            ),
            self.InputItem(
                name=_(u"属性值"),
                key="cc_module_prop_value",
                type="string",
                schema=StringItemSchema(description=_(u"模块属性更新后的值")),
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

        if cc_module_select_method == "topo":
            cc_module_select = cc_format_tree_mode_id(data.get_one_of_inputs("cc_module_select_topo"))
        elif cc_module_select_method == "text":
            # 文本路径解析
            cc_module_select_text = data.get_one_of_inputs("cc_module_select_text")
            path_list = cc_parse_path_text(cc_module_select_text)

            # 获取主线模型业务拓扑
            mainline = client.cc.get_mainline_object_topo({"bk_supplier_account": supplier_account})
            # 主线模型中模块所处的深度（包含模块）= 主线模型的业务拓扑级数 - 主机（1）
            module_depth = len(mainline["data"]) - 1
            for path in path_list:
                if len(path) != module_depth:
                    data.set_outputs("ex_data", "输入文本路径[{}]与业务拓扑层级不匹配".format(">".join(path)))
                    return False
            # 获取模块bk_inst_id
            cc_list_match_node_inst_id_result = cc_list_match_node_inst_id(tree_data["data"], path_list)
            if not cc_list_match_node_inst_id_result["result"]:
                data.set_outputs("ex_data", cc_list_match_node_inst_id_result["message"])
                return False
            cc_module_select = cc_list_match_node_inst_id_result["data"]
        else:
            data.set_outputs("ex_data", u"请选择填参方式")

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
                data.set_outputs("ex_data", _(u"模块类型校验失败，请重试并填写正确的模块类型"))
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
    name = _(u"更新模块属性")
    code = "cc_update_module"
    bound_service = CCUpdateModuleService
    form = "{static_url}components/atoms/cc/{ver}/cc_update_module.js".format(
        static_url=settings.STATIC_URL, ver=VERSION
    )
    version = VERSION
