# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from gcloud.conf import settings
from django.utils.translation import ugettext_lazy as _

from api.utils.request import batch_request
from gcloud.exceptions import ApiRequestError
from pipeline.core.data.var import LazyVariable

from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def cc_search_set_module_name_by_id(operator, bk_biz_id, bk_set_id, bk_module_ids):
    """
    通过集群ID和模块ID查询对应的名字
    :param operator: 操作者
    :param bk_biz_id: 业务ID
    :param bk_set_id: 集群ID
    :param bk_module_id: 模块ID
    :return:
    """
    str_module_ids = [str(item) for item in bk_module_ids]
    set_module_info = {"set_id": bk_set_id, "module_id": bk_module_ids, "flat__module_id": ",".join(str_module_ids)}
    client = get_client_by_user(operator)

    set_kwargs = {
        "bk_biz_id": bk_biz_id,
        "fields": ["bk_set_name"],
        "condition": {"bk_set_id": bk_set_id},
        "page": {"start": 0, "limit": 1},
    }
    set_result = client.cc.search_set(set_kwargs)
    if set_result["result"] and set_result["data"]["info"]:
        set_module_info["set_name"] = set_result["data"]["info"][0]["bk_set_name"]
    else:
        err_msg = handle_api_error("CC", "search_set", set_kwargs, set_result)
        logger.error(err_msg)
        raise ApiRequestError(err_msg)

    module_kwargs = {"bk_biz_id": bk_biz_id, "bk_set_id": bk_set_id, "fields": ["bk_module_id", "bk_module_name"]}
    module_info = batch_request(client.cc.search_module, module_kwargs)
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


class VarSetModuleSelector(LazyVariable):
    code = "set_module_selector"
    name = _("集群模块选择器")
    type = "dynamic"
    tag = "var_set_module_selector.set_module_selector"
    form = "%svariables/cmdb/var_set_module_selector.js" % settings.STATIC_URL
    desc = """
    用于获取集群和模块的信息（名称或ID）
    引用${KEY}，返回类型为字符串，值的格式为set: {用英文逗号连接的集群名称}, modules: {用英文逗号连接的模块名称}
    引用${KEY.set_name}，返回类型为列表，列表值为集群名称
    引用${KEY.set_id}，返回类型为列表，列表值为集群ID
    引用${KEY.module_name}，返回类型为列表，列表值为模块名称
    引用${KEY.flat__module_name}，返回类型为字符串，值为用英文逗号,连接的模块名称
    引用${KEY.module_id}，返回类型为列表，列表值为模块ID
    引用${KEY.flat__module_id}，返回类型为字符串，值为用英文逗号,连接的模块ID
    """

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
            return "ERROR: executor and biz_cc_id of pipeline is needed"
        operator = self.pipeline_data.get("executor", "")
        bk_biz_id = int(self.pipeline_data.get("biz_cc_id", 0))
        bk_set_id = int(self.value.get("bk_set_id", 0))
        bk_module_ids = self.value.get("bk_module_id", [])

        set_module_info = cc_search_set_module_name_by_id(operator, bk_biz_id, bk_set_id, bk_module_ids)

        return SetModuleInfo(set_module_info)
