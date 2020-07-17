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
import re
import logging

from django.conf import settings
from django.utils import translation, timezone
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.core.flow.io import StringItemSchema
from pipeline.component_framework.component import Component

from gcloud.core.models import Project

__group_name__ = _("蓝鲸服务(BK)")

LOGGER = logging.getLogger("celery")


class PauseService(Service):
    __need_schedule__ = True

    def execute(self, data, parent_data):
        return True

    def schedule(self, data, parent_data, callback_data=None):
        return True

    def outputs_format(self):
        return []


class PauseComponent(Component):
    name = _("暂停")
    code = "pause_node"
    bound_service = PauseService
    form = settings.STATIC_URL + "components/atoms/bk/pause.js"


class SleepTimerService(Service):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(0)
    #  匹配年月日 时分秒 正则 yyyy-MM-dd HH:mm:ss
    date_regex = re.compile(
        r"%s %s"
        % (
            r"^(((\d{3}[1-9]|\d{2}[1-9]\d{1}|\d{1}[1-9]\d{2}|[1-9]\d{3}))|"
            r"(29/02/((\d{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))))-"
            r"((0[13578]|1[02])-((0[1-9]|[12]\d|3[01]))|"
            r"((0[469]|11)-(0[1-9]|[12]\d|30))|(02)-(0[1-9]|[1]\d|2[0-8]))",
            r"((0|[1])\d|2[0-3]):(0|[1-5])\d:(0|[1-5])\d$",
        )
    )

    seconds_regex = re.compile(r"^\d{1,8}$")

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("定时时间"),
                key="bk_timing",
                type="string",
                schema=StringItemSchema(description=_("定时时间，格式为秒(s) 或 (%%Y-%%m-%%d %%H:%%M:%%S)")),
            ),
            self.InputItem(
                name=_("是否强制晚于当前时间"),
                key="force_check",
                type="bool",
                schema=StringItemSchema(description=_("用户输入日期格式时是否强制要求时间晚于当前时间，只对日期格式定时输入有效")),
            ),
        ]

    def outputs_format(self):
        return []

    def execute(self, data, parent_data):
        if parent_data.get_one_of_inputs("language"):
            translation.activate(parent_data.get_one_of_inputs("language"))

        timing = data.get_one_of_inputs("bk_timing")
        force_check = data.get_one_of_inputs("force_check", True)
        # 项目时区获取
        project = Project.objects.get(id=parent_data.inputs.project_id)

        project_tz = timezone.pytz.timezone(project.time_zone)
        data.outputs.business_tz = project_tz

        now = datetime.datetime.now(tz=project_tz)
        if self.date_regex.match(timing):
            eta = project_tz.localize(datetime.datetime.strptime(timing, "%Y-%m-%d %H:%M:%S"))
            if force_check and now > eta:
                message = _("定时时间需晚于当前时间")
                data.set_outputs("ex_data", message)
                return False
        elif self.seconds_regex.match(timing):
            #  如果写成+号 可以输入无限长，或考虑前端修改
            eta = now + datetime.timedelta(seconds=int(timing))
        else:
            message = _("输入参数%s不符合【秒(s) 或 时间(%%Y-%%m-%%d %%H:%%M:%%S)】格式") % timing
            data.set_outputs("ex_data", message)
            return False

        data.outputs.timing_time = eta

        return True

    def schedule(self, data, parent_data, callback_data=None):
        timing_time = data.outputs.timing_time
        business_tz = data.outputs.business_tz

        now = datetime.datetime.now(tz=business_tz)
        t_delta = timing_time - now
        if t_delta.total_seconds() < 1:
            self.finish_schedule()

        # 这里减去 0.5s 的目的是尽可能的减去 execute 执行带来的误差
        self.interval.interval = t_delta.total_seconds() - 0.5

        return True


class SleepTimerComponent(Component):
    name = _("定时")
    code = "sleep_timer"
    bound_service = SleepTimerService
    form = settings.STATIC_URL + "components/atoms/bk/timer.js"
