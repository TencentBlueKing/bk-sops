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
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.io import StringItemSchema
from pipeline.component_framework.component import Component

from gcloud.conf import settings

from pipeline_plugins.components.collections.sites.open.bk.timer.base import SleepTimerBaseService

__group_name__ = _("蓝鲸服务(BK)")


class SleepTimerService(SleepTimerBaseService):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("定时模式"), key="timing_mode", type="string", schema=StringItemSchema(description=_("定时模式"))
            ),
            self.InputItem(
                name=_("等待时间"), key="timing_seconds", type="string", schema=StringItemSchema(description=_("等待时间"))
            ),
            self.InputItem(
                name=_("时间日期"),
                key="timing_specific_time",
                type="string",
                schema=StringItemSchema(description=_("时间日期")),
            ),
        ]

    def outputs_format(self):
        return []

    def get_timing(self, data):
        timing_settings = data.get_one_of_inputs("timing_settings")
        timing = (
            timing_settings.get("timing_seconds")
            if timing_settings["timing_mode"] == "seconds"
            else timing_settings["timing_specific_time"]
        )
        return timing


class SleepTimerComponent(Component):
    name = _("定时")
    code = "sleep_timer"
    bound_service = SleepTimerService
    form = f"{settings.STATIC_URL}components/atoms/bk/timer/v1_0.js"
    version = "1.0"
