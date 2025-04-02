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
from abc import ABCMeta, abstractmethod
from functools import partial

from django.utils import translation
from django.utils.translation import gettext_lazy as _
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.cc.base import CCPluginIPMixin
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("celery")

__group_name__ = _("配置平台(CMDB)")

cc_handle_api_error = partial(handle_api_error, __group_name__)


class HostLockTypeService(Service, metaclass=ABCMeta):
    @abstractmethod
    def host_lock_method(self):
        raise NotImplementedError()


class CCHostLockBaseService(HostLockTypeService, CCPluginIPMixin):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("主机 IP"),
                key="cc_host_ip",
                type="string",
                schema=StringItemSchema(description=_("主机 IP，多个用换行符分隔")),
            )
        ]

    def execute(self, data, parent_data):
        method = self.host_lock_method()
        executor = parent_data.get_one_of_inputs("executor")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        biz_cc_id = parent_data.get_one_of_inputs("biz_cc_id")

        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))
        cc_host_ip = data.get_one_of_inputs("cc_host_ip")
        supplier_account = supplier_account_for_business(biz_cc_id)
        host_list_result = self.get_host_list(tenant_id, executor, biz_cc_id, cc_host_ip, supplier_account)

        if not host_list_result["result"]:
            data.outputs.ex_data = _(
                "无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法, message={}".format(
                    host_list_result.get("message", "")
                )
            )
            return False

        host_list = [int(host_id) for host_id in host_list_result["data"]]
        cc_host_lock_kwargs = {"id_list": host_list}
        cc_host_lock_method = getattr(client.api, method)
        cc_host_lock_result = cc_host_lock_method(
            cc_host_lock_kwargs,
            headers={"X-Bk-Tenant-Id": tenant_id}
        )
        if cc_host_lock_result["result"]:
            return True

        message = handle_api_error(
            __group_name__, "cc.{method}".format(method=method), cc_host_lock_kwargs, cc_host_lock_result
        )
        data.set_outputs("ex_data", message)
        self.logger.error(message)
        return False

    def outputs_format(self):
        return []
