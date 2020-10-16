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

from django.utils.translation import ugettext_lazy as _

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema

logger = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")
VERSION = "v1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCSetDeleteByNameService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("Set名称"),
                key="cc_set_name",
                type="string",
                schema=StringItemSchema(description=_("多个set请以英文【,】分隔")),
            )
        ]

    def outputs_format(self):
        return []

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        bk_biz_id = parent_data.get_one_of_inputs("bk_biz_id")
        set_names = data.get_one_of_inputs("cc_set_name")
        client = get_client_by_user(executor)

        if "，" in set_names:
            self.logger.info("set_names invalid: Please use English ','")
            data.set_outputs("ex_data", _("存在中文逗号"))
            return False

        # query id by name
        bk_set_ids = []
        for set_name in set_names.split(","):
            cc_search_set_kwargs = {
                "bk_biz_id": int(bk_biz_id),
                "fields": ["bk_set_id"],
                "condition": {"bk_set_name": set_name},
                "page": {"start": 0, "limit": 100, "sort": "bk_set_name"},
            }
            cc_search_set_result = client.cc.search_set(cc_search_set_kwargs)
            for bk_set in cc_search_set_result["data"]["info"]:
                bk_set_ids.append(bk_set["bk_set_id"])
        if not bk_set_ids:
            self.logger.info("Do not search any sets by these names")
            data.set_outputs("ex_data", "未找到任何主机")
            return True
        # delete sets
        cc_batch_delete_set_kwargs = {"bk_biz_id": int(bk_biz_id), "delete": {"inst_ids": bk_set_ids}}
        cc_batch_delete_set_result = client.cc.batch_delete_set(cc_batch_delete_set_kwargs)
        if not cc_batch_delete_set_result["result"]:
            message = cc_handle_api_error("cc.batch_delete_set", cc_batch_delete_set_kwargs, cc_batch_delete_set_result)
            self.logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        return True


class CCSetDeleteByNameComponent(Component):
    """
    @version log（v1.0）: 表格参数值支持以英文`,` 分隔的多条数据
    """

    name = _("根据名称删除集群")
    code = "cc_set_delete_by_name"
    bound_service = CCSetDeleteByNameService
    form = "{}components/atoms/cc/cc_set_delete_by_name/v1_0.js".format(settings.STATIC_URL)
    version = VERSION
