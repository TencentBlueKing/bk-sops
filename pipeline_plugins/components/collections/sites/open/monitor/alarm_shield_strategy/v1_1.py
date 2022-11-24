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
import datetime
import time

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from api.collections.monitor import BKMonitorClient
from gcloud.conf import settings

from pipeline.core.flow.io import StringItemSchema
from pipeline.component_framework.component import Component

from pipeline_plugins.components.collections.sites.open.monitor.base import MonitorBaseService

__group_name__ = _("监控平台(Monitor)")


class MonitorAlarmShieldStrategyService(MonitorBaseService):
    def get_end_time_by_duration(self, shield_start_time, shield_duration):
        dt = datetime.datetime.strptime(shield_start_time, "%Y-%m-%d %H:%M:%S")
        shield_end_time = (dt + datetime.timedelta(minutes=shield_duration)).strftime("%Y-%m-%d %H:%M:%S")
        return shield_end_time

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("策略 ID"),
                key="bk_alarm_shield_strategy",
                type="string",
                schema=StringItemSchema(description=_("需要执行屏蔽的策略 ID")),
            ),
            self.InputItem(
                name=_("IP"), key="bk_alarm_shield_IP", type="string", schema=StringItemSchema(description=_("IP"))
            ),
            self.InputItem(
                name=_("时间选择"),
                key="bk_alarm_time_type",
                type="string",
                schema=StringItemSchema(description=_("开始屏蔽的时间")),
            ),
            self.InputItem(
                name=_("屏蔽开始时间"),
                key="bk_alarm_shield_begin_time",
                type="string",
                schema=StringItemSchema(description=_("开始屏蔽的时间")),
            ),
            self.InputItem(
                name=_("屏蔽结束时间"),
                key="bk_alarm_end_time",
                type="string",
                schema=StringItemSchema(description=_("结束屏蔽的时间")),
            ),
            self.InputItem(
                name=_("屏蔽持续时间"),
                key="bk_alarm_shield_duration",
                type="string",
                schema=StringItemSchema(description=_("屏蔽持续的时间")),
            ),
        ]

    def execute(self, data, parent_data):
        if parent_data.get_one_of_inputs("language"):
            translation.activate(parent_data.get_one_of_inputs("language"))

        bk_biz_id = parent_data.get_one_of_inputs("biz_cc_id")
        executor = parent_data.get_one_of_inputs("executor")
        client = BKMonitorClient(username=executor)
        strategy = data.get_one_of_inputs("bk_alarm_shield_strategy")
        begin_time = data.get_one_of_inputs("bk_alarm_shield_begin_time")
        end_time = data.get_one_of_inputs("bk_alarm_shield_end_time")
        scope_value = data.get_one_of_inputs("bk_alarm_shield_IP")
        time_type = int(data.get_one_of_inputs("bk_alarm_time_type"))
        shield_duration = data.get_one_of_inputs("bk_alarm_shield_duration")

        # 从当前时间开始，仅输入持续时间
        if time_type == 1:
            begin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            end_time = self.get_end_time_by_duration(begin_time, int(shield_duration))
        # 输入开始时间和持续时间
        elif time_type == 2:
            end_time = self.get_end_time_by_duration(begin_time, int(shield_duration))

        request_body = self.get_request_body(bk_biz_id, begin_time, end_time, "strategy", strategy, executor)

        if scope_value:
            target = self.get_ip_dimension(scope_value, bk_biz_id, executor)
            request_body["dimension_config"].update(target)

        result_flag = self.send_request(request_body, data, client)

        return result_flag

    def get_dimension_config(self, shied_type, shied_value, bk_biz_id, client):
        return {"id": shied_value}

    def get_ip_dimension(self, scope_value, bk_biz_id, username):
        ip_dimension = super(MonitorAlarmShieldStrategyService, self).get_ip_dimension_config(
            scope_value, bk_biz_id, username
        )
        return ip_dimension

    def get_request_body(self, bk_biz_id, begin_time, end_time, shied_type, shied_value, username):
        dimension_config = self.get_dimension_config(shied_type, shied_value, bk_biz_id, username)
        request_body = self.build_request_body(
            begin_time=begin_time,
            bk_biz_id=bk_biz_id,
            shied_type=shied_type,
            dimension_config=dimension_config,
            end_time=end_time,
        )
        return request_body


class MonitorAlarmShieldStrategyComponent(Component):
    name = _("蓝鲸监控告警屏蔽(按策略)")
    code = "monitor_alarm_shield_strategy"
    bound_service = MonitorAlarmShieldStrategyService
    form = "{static_url}components/atoms/monitor/alarm_shield_strategy/v1_1.js".format(static_url=settings.STATIC_URL)
    version = "1.1"
