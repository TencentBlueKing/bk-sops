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
from functools import partial

from django.utils import translation
from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import IntItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from packages.bkapi.bk_monitor.shortcuts import get_client_by_username

__group_name__ = _("监控平台(Monitor)")

monitor_handle_api_error = partial(handle_api_error, __group_name__)


class MonitorAlarmShieldDisableService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("屏蔽 ID"),
                key="bk_alarm_shield_id_input",
                type="string",
                schema=StringItemSchema(description=_("当前操作的屏蔽 ID")),
            )
        ]

    def execute(self, data, parent_data):
        if parent_data.get_one_of_inputs("language"):
            translation.activate(parent_data.get_one_of_inputs("language"))

        executor = parent_data.get_one_of_inputs("executor")
        shield_id = data.get_one_of_inputs("bk_alarm_shield_id_input")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        client = get_client_by_username(username=executor, stage=settings.BK_APIGW_STAGE_NAME)
        request_body = {"id": shield_id}
        response = client.api.disable_shield(request_body, headers={"X-Bk-Tenant-Id": tenant_id})
        if not response["result"]:
            message = monitor_handle_api_error("monitor.disable_shield", request_body, response)
            self.logger.error(message)
            result = message
            ret_flag = False
        else:
            result = response["data"]
            ret_flag = True

        data.set_outputs("data", {"result": result})
        data.set_outputs("status_code", response["code"])
        return ret_flag

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("响应内容"),
                key="data",
                type="string",
                schema=StringItemSchema(description=_("解除告警屏蔽的响应内容")),
            ),
            self.OutputItem(
                name=_("状态码"),
                key="status_code",
                type="int",
                schema=IntItemSchema(description=_("解除告警屏蔽的响应状态码")),
            ),
        ]


class MonitorAlarmShieldDisableComponent(Component):
    name = _("解除告警屏蔽")
    code = "monitor_alarm_shield_disable"
    desc = _("提示: 屏蔽id请从告警屏蔽或蓝鲸监控获取")
    bound_service = MonitorAlarmShieldDisableService
    version = "1.0"
    form = "{static_url}components/atoms/monitor/alarm_shield_disable/v1_0.js".format(static_url=settings.STATIC_URL)
