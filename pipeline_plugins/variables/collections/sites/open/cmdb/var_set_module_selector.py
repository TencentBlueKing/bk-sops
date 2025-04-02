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
from typing import List

from django.utils.translation import gettext_lazy as _
from pipeline.core.data.var import LazyVariable

from api.utils.request import batch_request
from gcloud.conf import settings
from gcloud.constants import Type
from gcloud.exceptions import ApiRequestError
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.variables.base import FieldExplain, SelfExplainVariable
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("root")


def cc_search_set_module_name_by_id(tenant_id, operator, bk_biz_id, bk_set_id, bk_module_ids):
    """
    通过集群ID和模块ID查询对应的名字
    :param tenant_id: 租户ID
    :param operator: 操作者
    :param bk_biz_id: 业务ID
    :param bk_set_id: 集群ID
    :param bk_module_id: 模块ID
    :return:
    """
    str_module_ids = [str(item) for item in bk_module_ids]
    set_module_info = {"set_id": bk_set_id, "module_id": bk_module_ids, "flat__module_id": ",".join(str_module_ids)}
    supplier_account = supplier_account_for_business(bk_biz_id)
    client = get_client_by_username(operator, stage=settings.BK_APIGW_STAGE_NAME)
    set_kwargs = {
        "bk_biz_id": bk_biz_id,
        "fields": ["bk_set_name"],
        "condition": {"bk_set_id": bk_set_id},
        "page": {"start": 0, "limit": 1},
    }
    set_result = client.api.search_set(
        set_kwargs,
        path_params={"bk_supplier_account": supplier_account, "bk_biz_id": bk_biz_id},
        headers={"X-Bk-Tenant-Id": tenant_id},
    )
    if set_result["result"] and set_result["data"]["info"]:
        set_module_info["set_name"] = set_result["data"]["info"][0]["bk_set_name"]
    else:
        err_msg = handle_api_error("CC", "search_set", set_kwargs, set_result)
        logger.error(err_msg)
        raise ApiRequestError(err_msg)

    module_kwargs = {"bk_biz_id": bk_biz_id, "bk_set_id": bk_set_id, "fields": ["bk_module_id", "bk_module_name"]}
    module_info = batch_request(
        client.api.search_module,
        module_kwargs,
        path_params={"bk_supplier_account": supplier_account, "bk_biz_id": bk_biz_id, "bk_set_id": bk_set_id},
        headers={"X-Bk-Tenant-Id": tenant_id},
    )
    bk_module_names = []
    for item in module_info:
        if item.get("bk_module_id") in bk_module_ids:
            bk_module_names.append(item.get("bk_module_name"))
    set_module_info["module_name"] = bk_module_names
    set_module_info["flat__module_name"] = ",".join(bk_module_names)

    return set_module_info


class SetModuleInfo(object):
    """
    设置集群和模块的信息
    """

    def __init__(self, data):
        self.set_name = data.get("set_name", "")
        self.set_id = data.get("set_id", 0)
        self.module_name = data.get("module_name", [])
        self.module_id = data.get("module_id", [])
        self.flat__module_id = data.get("flat__module_id", "")
        self.flat__module_name = data.get("flat__module_name", "")
        self._pipeline_var_str_value = "set: {}, modules: {}".format(self.set_name, ",".join(self.module_name))

    def __repr__(self):
        return self._pipeline_var_str_value


class VarSetModuleSelector(LazyVariable, SelfExplainVariable):
    code = "set_module_selector"
    name = _("集群模块选择器")
    type = "dynamic"
    tag = "var_set_module_selector.set_module_selector"
    form = "%svariables/cmdb/var_set_module_selector.js" % settings.STATIC_URL
    desc = _(
        "用于获取集群和模块的信息（名称或ID）\n"
        "引用${KEY}，返回类型为字符串，值的格式为set: {用英文逗号连接的集群名称}, modules: {用英文逗号连接的模块名称}\n"
        "引用${KEY.set_name}，返回类型为字符串，值为集群名称\n"
        "引用${KEY.set_id}，返回类型为数字，值为集群ID\n"
        "引用${KEY.module_name}，返回类型为列表，列表值为模块名称\n"
        "引用${KEY.flat__module_name}，返回类型为字符串，值为用英文逗号,连接的模块名称\n"
        "引用${KEY.module_id}，返回类型为列表，列表值为模块ID\n"
        "引用${KEY.flat__module_id}，返回类型为字符串，值为用英文逗号,连接的模块ID"
    )

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [
            FieldExplain(key="${KEY}", type=Type.STRING, description="选择了的集群模块的信息"),
            FieldExplain(key="${KEY.set_name}", type=Type.STRING, description="选择的集群名称"),
            FieldExplain(key="${KEY.set_id}", type=Type.INT, description="选择的集群ID"),
            FieldExplain(key="${KEY.module_name}", type=Type.LIST, description="选择的模块名列表"),
            FieldExplain(key="${KEY.flat__module_name}", type=Type.STRING, description="选择的模块名列表，以,连接"),
            FieldExplain(key="${KEY.module_id}", type=Type.LIST, description="选择的模块ID列表"),
            FieldExplain(key="${KEY.flat__module_id}", type=Type.STRING, description="选择的模块ID列表，以,连接"),
        ]

    def get_value(self):
        """
        获取该变量中对应属性值
        example:
            set_name: ${var.set_name}
            set_id: ${var.set_id}
            module_name: ${var.module_name}
            module_id: ${var.module_id}
            flat__module_name: ${var.flat__module_name}
            flat__module_id: ${var.flat__module_id}
        """
        if "executor" not in self.pipeline_data or "biz_cc_id" not in self.pipeline_data:
            raise Exception("ERROR: executor and biz_cc_id of pipeline is needed")
        tenant_id = self.pipeline_data.get("tenant_id", "")
        operator = self.pipeline_data.get("executor", "")
        bk_biz_id = int(self.pipeline_data.get("biz_cc_id", 0))
        bk_set_id = int(self.value.get("bk_set_id", 0))
        bk_module_ids = self.value.get("bk_module_id", [])

        set_module_info = cc_search_set_module_name_by_id(tenant_id, operator, bk_biz_id, bk_set_id, bk_module_ids)

        return SetModuleInfo(set_module_info)
