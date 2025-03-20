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

from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema

from api.utils.request import batch_request
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("celery")

__group_name__ = _("配置平台(CMDB)")
VERSION = "1.1"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCUpdateSetServiceStatusService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("传参形式"),
                key="set_select_method",
                type="string",
                schema=StringItemSchema(
                    description=_("集群填入方式，Set名称(name)，Set ID(id)，自定义（根据集群属性过滤）"),
                    enum=["name", "id", "custom"],
                ),
            ),
            self.InputItem(
                name=_("集群属性ID"),
                key="set_attr_id",
                type="string",
                schema=StringItemSchema(description=_("集群范围中填写的值会在此处填写的属性 ID 的值上进行过滤")),
            ),
            self.InputItem(
                name=_("集群范围"),
                key="set_list",
                type="string",
                schema=StringItemSchema(description=_("集群范围，多个集群使用英文','分割")),
            ),
            self.InputItem(
                name=_("服务状态"),
                key="set_status",
                type="string",
                schema=StringItemSchema(description=_("实时拉取的服务状态")),
            ),
        ]

    def outputs_format(self):
        return []

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")

        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        bk_biz_id = parent_data.get_one_of_inputs("bk_biz_id")
        supplier_account = supplier_account_for_business(bk_biz_id)
        set_list = data.get_one_of_inputs("set_list")
        cc_set_select = set_list.split(",")
        set_select_method = data.get_one_of_inputs("set_select_method")
        set_status = data.get_one_of_inputs("set_status")
        set_attr_id = data.get_one_of_inputs("set_attr_id") or "bk_set_name"

        bk_set_ids = []
        if set_select_method in ("name", "custom"):
            for set_name in cc_set_select:
                cc_search_set_kwargs = {
                    "bk_biz_id": int(bk_biz_id),
                    "fields": ["bk_set_id", set_attr_id],
                    "condition": {set_attr_id: set_name},
                }
                cc_search_set_result = batch_request(
                    client.api.search_set,
                    cc_search_set_kwargs,
                    path_params={"bk_supplier_account": supplier_account, "bk_biz_id": bk_biz_id},
                    headers={"X-Bk-Tenant-Id": tenant_id},
                )
                if not cc_search_set_result:
                    self.logger.error("batch_request client.cc.search_set error")
                    data.set_outputs("ex_data", "batch_request client.cc.search_set error")
                    return False
                for bk_set in cc_search_set_result:
                    if bk_set[set_attr_id] == set_name:
                        bk_set_ids.append(bk_set["bk_set_id"])
        elif set_select_method == "id":
            bk_set_ids = cc_set_select

        for set_id in bk_set_ids:
            cc_kwargs = {
                "bk_biz_id": bk_biz_id,
                "bk_supplier_account": supplier_account,
                "bk_set_id": set_id,
                "data": {"bk_service_status": set_status},
            }
            cc_result = client.api.update_set(
                cc_kwargs,
                path_params={"bk_biz_id": bk_biz_id, "bk_set_id": set_id},
                headers={"X-Bk-Tenant-Id": tenant_id},
            )
            if not cc_result["result"]:
                message = cc_handle_api_error("cc.update_set", cc_kwargs, cc_result)
                self.logger.error(message)
                data.set_outputs("ex_data", message)
                return False
        return True


class CCUpdateSetServiceStatusComponent(Component):
    """
    @version log （v1.1）:修改服务状态
    """

    name = _("修改集群服务状态")
    code = "cc_update_set_service_status"
    bound_service = CCUpdateSetServiceStatusService
    form = "{static_url}components/atoms/cc/update_set_service_status/v{ver}.js".format(
        static_url=settings.STATIC_URL, ver=VERSION.replace(".", "_")
    )
    version = VERSION
