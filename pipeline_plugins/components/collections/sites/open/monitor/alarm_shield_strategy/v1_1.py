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
import datetime
import time
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from gcloud.conf.default_settings import ESB_GET_OLD_CLIENT_BY_USER as get_client_by_user
from gcloud.conf import settings
from gcloud.utils import cmdb
from gcloud.core.models import Business
from gcloud.utils.handlers import handle_api_error

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema
from pipeline.component_framework.component import Component

__group_name__ = _("监控平台(Monitor)")

monitor_handle_api_error = partial(handle_api_error, __group_name__)


class MonitorAlarmShieldStrategyService(Service):
    def get_end_time_by_duration(self, shield_start_time, shield_duration):
        dt = datetime.datetime.strptime(shield_start_time, "%Y-%m-%d %H:%M:%S")
        shield_end_time = (dt + datetime.timedelta(minutes=shield_duration)).strftime("%Y-%m-%d %H:%M:%S")
        return shield_end_time

    def inputs_format(self):
        return (
            [
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
            ],
        )

    def execute(self, data, parent_data):
        if parent_data.get_one_of_inputs("language"):
            translation.activate(parent_data.get_one_of_inputs("language"))

        bk_biz_id = parent_data.get_one_of_inputs("biz_cc_id")
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        strategy = data.get_one_of_inputs("bk_alarm_shield_strategy")
        begin_time = data.get_one_of_inputs("bk_alarm_shield_strategy_begin_time")
        end_time = data.get_one_of_inputs("bk_alarm_shield_strategy_end_time")
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
        ip_list = scope_value.split(",")
        hosts = cmdb.get_business_host(
            username=username,
            bk_biz_id=bk_biz_id,
            supplier_account=Business.objects.supplier_account_for_business(bk_biz_id),
            host_fields=["bk_host_id", "bk_cloud_id", "bk_host_innerip"],
            ip_list=ip_list,
        )
        if not hosts:
            raise Exception("cmdb.get_business_host return empty")

        target = []
        for host in hosts:
            target.append({"ip": host["bk_host_innerip"], "bk_cloud_id": host["bk_cloud_id"]})

        return {"scope_type": "ip", "target": target}

    def get_request_body(self, bk_biz_id, begin_time, end_time, shied_type, shied_value, username):
        category_map = {"business": "scope", "IP": "scope", "node": "scope", "strategy": "strategy"}
        dimension_config = self.get_dimension_config(shied_type, shied_value, bk_biz_id, username)
        request_body = {
            "begin_time": begin_time,
            "bk_biz_id": bk_biz_id,
            "category": category_map[shied_type],
            "cycle_config": {"begin_time": "", "end_time": "", "day_list": [], "week_list": [], "type": 1},
            "description": "shield by bk_sops",
            "dimension_config": dimension_config,
            "end_time": end_time,
            "notice_config": {},
            "shield_notice": False,
            "source": settings.APP_ID,
        }
        return request_body

    def send_request(self, request_body, data, client):
        response = client.monitor.create_shield(request_body)
        if not response["result"]:
            message = monitor_handle_api_error("monitor.create_shield", request_body, response)
            self.logger.error(message)
            shield_id = ""
            ret_flag = False
        else:
            shield_id = response["data"]["id"]
            ret_flag = True
            message = response["message"]
        data.set_outputs("shield_id", shield_id)
        data.set_outputs("message", message)
        return ret_flag

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("屏蔽Id"), key="shield_id", type="string", schema=StringItemSchema(description=_("创建的告警屏蔽 ID"))
            ),
            self.OutputItem(
                name=_("详情"), key="message", type="string", schema=StringItemSchema(description=_("创建的告警屏蔽详情"))
            ),
        ]


class MonitorAlarmShieldStrategyComponent(Component):
    name = _("蓝鲸监控告警屏蔽(按策略)")
    code = "monitor_alarm_shield_strategy"
    bound_service = MonitorAlarmShieldStrategyService
    form = "{static_url}components/atoms/monitor/alarm_shield_strategy/v1_1.js".format(static_url=settings.STATIC_URL)
    version = "1.1"
