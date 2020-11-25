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
from pipeline.core.flow.io import StringItemSchema
from pipeline.component_framework.component import Component

from pipeline_plugins.components.collections.sites.open.cc.base import cc_get_host_id_by_innerip

from gcloud.conf import settings
from gcloud.utils.ip import get_ip_by_regex
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CmdbTransferFaultHostService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务 ID"),
                key="biz_cc_id",
                type="string",
                schema=StringItemSchema(description=_("当前操作所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_("主机 IP"),
                key="cc_host_ip",
                type="string",
                schema=StringItemSchema(description=_("转移到故障机的主机内网 IP，多个用英文逗号 `,` 分隔")),
            ),
        ]

    def outputs_format(self):
        return []

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        supplier_account = parent_data.get_one_of_inputs("biz_supplier_account")

        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        # 查询主机id
        ip_list = get_ip_by_regex(data.get_one_of_inputs("cc_host_ip"))
        host_result = cc_get_host_id_by_innerip(executor, biz_cc_id, ip_list, supplier_account)
        if not host_result["result"]:
            data.set_outputs("ex_data", host_result["message"])
            return False

        transfer_params = {"bk_biz_id": biz_cc_id, "bk_host_id": [int(host_id) for host_id in host_result["data"]]}
        transfer_result = client.cc.transfer_host_to_faultmodule(transfer_params)
        if transfer_result["result"]:
            return True
        else:
            message = cc_handle_api_error("cc.transfer_host_to_fault_module", transfer_params, transfer_result)
            self.logger.error(message)
            data.set_outputs("ex_data", message)
            return False


class CmdbTransferFaultHostComponent(Component):
    name = _("转移主机至故障机模块")
    code = "cmdb_transfer_fault_host"
    bound_service = CmdbTransferFaultHostService
    form = "%scomponents/atoms/cc/cmdb_transfer_fault_host.js" % settings.STATIC_URL
