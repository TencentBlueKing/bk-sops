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

from gcloud.conf import settings
from django.utils.translation import ugettext_lazy as _

from pipeline.core.data.var import LazyVariable


logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def cc_search_set_module_name_by_id(operator, bk_biz_id, bk_set_id, bk_module_id):
    """通过集群ID和模块ID查询对应的名字
    :param operator: 操作者
    :param bk_biz_id: 业务ID
    :param bk_set_id: 集群ID
    :param bk_module_id: 模块ID
    :return:
    """
    set_module_info = {"set_id": bk_set_id, "module_id": bk_module_id}
    client = get_client_by_user(operator)

    set_kwargs = {
        "bk_biz_id": bk_biz_id,
        "fields": ["bk_set_name"],
        "condition": {"bk_set_id": bk_set_id},
        "page": {"start": 0, "limit": 1},
    }
    set_result = client.cc.search_set(set_kwargs)
    if set_result["result"]:
        set_module_info["set"] = set_result["data"]["info"][0]["bk_set_name"]
    else:
        err_msg = "调用 cc.search_set 接口获取集群名字失败, kwargs={kwargs}, result={result}".format(
            kwargs=set_kwargs, result=set_result
        )
        logger.error(err_msg)
        set_module_info["set"] = ""

    module_kwargs = {
        "bk_biz_id": bk_biz_id,
        "bk_set_id": bk_set_id,
        "fields": ["bk_module_name"],
        "condition": {"bk_module_id": bk_module_id},
        "page": {"start": 0, "limit": 1},
    }
    module_result = client.cc.search_module(module_kwargs)
    if module_result["result"]:
        set_module_info["module"] = module_result["data"]["info"][0]["bk_module_name"]
    else:
        err_msg = "调用 cc.search_module 接口获取模块名字失败, kwargs={kwargs}, result={result}".format(
            kwargs=module_kwargs, result=module_result
        )
        logger.error(err_msg)
        set_module_info["module"] = ""

    return set_module_info


class SetModuleInfo(object):
    """设置集群和模块的信息
    """

    def __init__(self, data):
        setattr(self, "set", data.get("set", ""))
        setattr(self, "set_id", data.get("set_id", 0))
        setattr(self, "module", data.get("module", ""))
        setattr(self, "module_id", data.get("module_id", 0))


class VarSetModuleSelector(LazyVariable):
    code = "set_module_selector"
    name = _("集群模块选择器")
    type = "general"
    tag = "var_set_module_selector.set_module_selector"
    form = "%svariables/cmdb/var_set_module_selector.js" % settings.STATIC_URL

    def get_value(self):
        """ 获取该变量中对应属性值
        example:
            set: ${var.set}
            set_id: ${var.set_id}
            module: ${var.module}
            module_id: ${var.module_id}
        """
        operator = self.pipeline_data.get("executor", "")
        bk_biz_id = int(self.pipeline_data.get("biz_cc_id", 0))
        bk_set_id = int(self.value.get("bk_set_id", 0))
        bk_module_id = int(self.value.get("bk_module_id", 0))

        set_module_info = cc_search_set_module_name_by_id(operator, bk_biz_id, bk_set_id, bk_module_id)

        return SetModuleInfo(set_module_info)
