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
from pipeline_plugins.components.collections.sites.open.cc.base import (
    BkObjType,
    cc_format_tree_mode_id,
    cc_parse_path_text,
    cc_list_match_node_inst_id,
    cc_batch_validated_business_level,
)

from pipeline_plugins.base.utils.inject import supplier_account_for_business

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")
VERSION = "v1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCEmptySetHostsService(Service):
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
                schema=ArrayItemSchema(
                    description=_("需要清空的集群 ID 列表"), item_schema=IntItemSchema(description=_("集群 ID"))
                ),
            ),
            self.InputItem(
                name=_("文本路径-集群"),
                key="cc_set_select_text",
                type="string",
                schema=StringItemSchema(description=_("集群文本路径")),
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

        # 选中集群bk_inst_id列表
        cc_set_select = []

        if cc_set_select_method == "topo":
            cc_set_select = cc_format_tree_mode_id(data.get_one_of_inputs("cc_set_select_topo"))
        elif cc_set_select_method == "text":
            # 文本路径解析
            cc_set_select_text = data.get_one_of_inputs("cc_set_select_text")
            path_list = cc_parse_path_text(cc_set_select_text)

            # 对输入的文本路径进行业务层级校验
            cc_batch_validated_business_level_return = cc_batch_validated_business_level(
                executor, supplier_account, BkObjType.SET, path_list
            )
            if not cc_batch_validated_business_level_return["result"]:
                data.set_outputs("ex_data", cc_batch_validated_business_level_return["message"])
                return False

            # 获取选中集群bk_inst_id列表
            cc_list_match_node_inst_id_return = cc_list_match_node_inst_id(
                executor, biz_cc_id, supplier_account, path_list
            )
            if not cc_list_match_node_inst_id_return["result"]:
                data.set_outputs("ex_data", cc_list_match_node_inst_id_return["message"])
                return False
            cc_set_select = cc_list_match_node_inst_id_return["data"]
        else:
            data.set_outputs("ex_data", _("请选择填参方式"))
        for set_id in cc_set_select:
            cc_kwargs = {
                "bk_biz_id": biz_cc_id,
                "bk_supplier_account": supplier_account,
                "bk_set_id": set_id,
            }
            cc_result = client.cc.transfer_sethost_to_idle_module(cc_kwargs)
            if not cc_result["result"]:
                message = cc_handle_api_error("cc.transfer_sethost_to_idle_module", cc_kwargs, cc_result)
                self.logger.error(message)
                data.set_outputs("ex_data", message)
                return False
        return True


class CCEmptySetHostsComponent(Component):
    name = _("清空集群中主机")
    code = "cc_empty_set_hosts"
    bound_service = CCEmptySetHostsService
    form = '{static_url}components/atoms/cc/empty_set_hosts/{ver}.js'.format(static_url=settings.STATIC_URL,
                                                                             ver=VERSION.replace('.', '_'))
    version = VERSION
