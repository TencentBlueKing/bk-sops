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
from abc import abstractmethod

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, IntItemSchema
from pipeline_plugins.components.utils import cc_get_ips_info_by_str
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")

cc_handle_api_error = partial(handle_api_error, __group_name__)


class HostLockTypeService(Service):
    @abstractmethod
    def host_lock_method(self):
        raise NotImplementedError()


class AddHostLockMixin(HostLockTypeService):
    def host_lock_method(self):
        return "add_host_lock"


class DeleteHostLockMixin(HostLockTypeService):
    def host_lock_method(self):
        return "delete_host_lock"


class CCHostLockBaseService(HostLockTypeService):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("主机 IP"),
                key="cc_host_ip",
                type="string",
                schema=StringItemSchema(description=_("主机 IP，多个用英文逗号 `,` 分隔")),
            ),
            self.InputItem(
                name=_("云区域ID"), key="cc_bk_cloud_id", type="int", schema=IntItemSchema(description=_("云区域ID，默认为0")),
            ),
        ]

    def execute(self, data, parent_data):
        method = self.host_lock_method()
        executor = parent_data.get_one_of_inputs("executor")
        biz_cc_id = parent_data.get_one_of_inputs("biz_cc_id")

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))
        cc_host_ip = data.get_one_of_inputs("cc_host_ip")
        id_info = cc_get_ips_info_by_str(executor, biz_cc_id, cc_host_ip)
        id_list = id_info["ip_result"] if id_info["result"] else []
        cc_host_lock_kwargs = {"id_list": id_list}
        cc_host_lock_method = getattr(client.cc, method)
        cc_host_lock_result = cc_host_lock_method(cc_host_lock_kwargs)
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
