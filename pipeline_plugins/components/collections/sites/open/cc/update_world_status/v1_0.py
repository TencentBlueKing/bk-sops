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
from gcloud.utils.cmdb import batch_request
from gcloud.utils.handlers import handle_api_error
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema
from pipeline_plugins.base.utils.inject import supplier_account_for_business

logger = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")
VERSION = "v1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCUpdateWorldStatusService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("填参方式"),
                key="cc_set_select_method",
                type="string",
                schema=StringItemSchema(description=_("集群填入方式，Set名称(name)，大区ID(id)"), enum=["name", "id"]),
            ),
            self.InputItem(name=_("大区范围"), key="set_list", type="string",),
        ]

    def outputs_format(self):
        return []

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        bk_biz_id = parent_data.get_one_of_inputs("bk_biz_id")
        supplier_account = supplier_account_for_business(bk_biz_id)
        set_list = data.get_one_of_inputs("set_list")
        cc_set_select = set_list.split(",")
        set_select_method = data.get_one_of_inputs("set_select_method")
        set_status = data.get_one_of_inputs("set_status")

        bk_set_ids = []
        if set_select_method == "name":
            for set_name in cc_set_select:
                cc_search_set_kwargs = {
                    "bk_biz_id": int(bk_biz_id),
                    "fields": ["bk_set_id", "bk_set_name"],
                    "condition": {"bk_set_name": set_name},
                    # "page": {"start": 0, "limit": 100, "sort": "bk_set_name"},
                }
                cc_search_set_result = batch_request(client.cc.search_set, cc_search_set_kwargs)
                if not cc_search_set_result:
                    self.logger.error("batch_request client.cc.search_set error")
                    data.set_outputs("ex_data", "batch_request client.cc.search_set error")
                    return False
                for bk_set in cc_search_set_result:
                    if bk_set["bk_set_name"] == set_name:
                        bk_set_ids.append(bk_set["bk_set_id"])
        else:
            bk_set_ids = cc_set_select
        for set_id in bk_set_ids:
            cc_kwargs = {
                "bk_biz_id": bk_biz_id,
                "bk_supplier_account": supplier_account,
                "bk_set_id": set_id,
                "data": {"bk_service_status": set_status},
            }
            cc_result = client.cc.update_set(cc_kwargs)
            if not cc_result["result"]:
                message = cc_handle_api_error("cc.update_set", cc_kwargs, cc_result)
                self.logger.error(message)
                data.set_outputs("ex_data", message)
                return False
        return True


class CCUpdateWorldStatusComponent(Component):
    """
    @version log（v1.0）:支持手动输入拓扑路径选择集群，并提供相应输入容错： 冗余回车/换行
    """

    name = _("服务状态修改")
    code = "cc_update_world_status"
    bound_service = CCUpdateWorldStatusService
    form = "{static_url}components/atoms/cc/update_world_status/{ver}.js".format(
        static_url=settings.STATIC_URL, ver=VERSION.replace(".", "_")
    )
    version = VERSION
