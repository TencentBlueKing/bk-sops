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
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.io import StringItemSchema

from api.collections.monitor import BKMonitorClient
from gcloud.conf import settings
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.monitor.alarm_shield.base import MonitorAlarmShieldServiceBase
from pipeline_plugins.components.utils.sites.open.choose_time_tools import choose_time

__group_name__ = _("监控平台(Monitor)")


class MonitorAlarmShieldService(MonitorAlarmShieldServiceBase):
    def inputs_format(self):
        return super().inputs_format() + [
            self.InputItem(
                name=_("屏蔽原因"),
                key="bk_alarm_shield_reason",
                type="string",
                schema=StringItemSchema(description=_("屏蔽原因")),
            ),
        ]

    def plugin_execute(self, data, parent_data):
        bk_biz_id = parent_data.get_one_of_inputs("biz_cc_id")
        executor = parent_data.get_one_of_inputs("executor")
        client = BKMonitorClient(username=executor)
        combine = data.get_one_of_inputs("bk_alarm_shield_info")
        scope_type = combine.get("bk_alarm_shield_scope")
        scope_value = self.get_scope_value(bk_biz_id, scope_type, combine)
        target = data.get_one_of_inputs("bk_alarm_shield_target")
        shield_reason = data.get_one_of_inputs("bk_alarm_shield_reason")
        begin_time = data.get_one_of_inputs("bk_alarm_shield_begin_time")
        end_time = data.get_one_of_inputs("bk_alarm_shield_end_time")
        time_type = int(data.get_one_of_inputs("bk_alarm_time_type"))
        shield_duration = data.get_one_of_inputs("bk_alarm_shield_duration")
        try:
            begin_time, end_time = choose_time(time_type, begin_time, end_time, shield_duration)
        except ValueError:
            return False

        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        supplier_account = supplier_account_for_business(bk_biz_id)

        request_body = self.get_request_body(
            bk_biz_id, begin_time, end_time, scope_type, scope_value, executor, supplier_account
        )
        if shield_reason:
            request_body["description"] = shield_reason
        if "all" not in target:
            request_body["dimension_config"].update({"metric_id": target})

        result_flag = self.send_request(request_body, data, client)

        return result_flag

    def get_scope_value(self, bk_biz_id, scope_type, combine):
        scope = {"IP": "bk_alarm_shield_IP", "node": "bk_alarm_shield_node"}
        if scope_type == "business":
            scope_value = bk_biz_id
        else:
            scope_value = combine.get(scope[scope_type])

        return scope_value


class MonitorAlarmShieldComponent(Component):
    name = _("蓝鲸监控告警屏蔽(按范围)")
    code = "monitor_alarm_shield"
    bound_service = MonitorAlarmShieldService
    form = "{static_url}components/atoms/monitor/alarm_shield/v2_0.js".format(static_url=settings.STATIC_URL)
    version = "2.0"
    desc = _("注意： 1.屏蔽方案选择自定义监控时，屏蔽范围CC大区和集群必须选择all, 2.当按业务屏蔽时，使用当前项目选择的业务值")
