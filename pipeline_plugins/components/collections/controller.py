# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
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

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from pipeline.conf import settings
from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.component_framework.component import Component

from gcloud.core.models import Business

__group_name__ = _(u"蓝鲸服务(BK)")

LOGGER = logging.getLogger('celery')


class PauseService(Service):
    __need_schedule__ = True

    def execute(self, data, parent_data):
        return True

    def schedule(self, data, parent_data, callback_data=None):
        return True

    def outputs_format(self):
        return []


class PauseComponent(Component):
    name = _(u'暂停')
    code = 'pause_node'
    bound_service = PauseService
    form = settings.STATIC_URL + 'components/atoms/bk/pause.js'


class SleepTimerService(Service):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(0)
    #  匹配年月日 时分秒 正则 yyyy-MM-dd HH:mm:ss
    date_regex = re.compile(r"%s %s" %
                            (r'^(((\d{3}[1-9]|\d{2}[1-9]\d{1}|\d{1}[1-9]\d{2}|[1-9]\d{3}))|'
                             r'(29/02/((\d{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))))-'
                             r'((0[13578]|1[02])-((0[1-9]|[12]\d|3[01]))|'
                             r'((0[469]|11)-(0[1-9]|[12]\d|30))|(02)-(0[1-9]|[1]\d|2[0-8]))',
                             r'((0|[1])\d|2[0-3]):(0|[1-5])\d:(0|[1-5])\d$'))

    seconds_regex = re.compile(r'^\d{1,8}$')

    def execute(self, data, parent_data):
        if parent_data.get_one_of_inputs('language'):
            translation.activate(parent_data.get_one_of_inputs('language'))

        timing = str(data.inputs.bk_timing)

        # 业务时区获取
        business = Business.objects.get(cc_id=parent_data.inputs.biz_cc_id)

        business_tz = timezone.pytz.timezone(business.time_zone)
        data.outputs.business_tz = business_tz

        if self.date_regex.match(timing):
            eta = business_tz.localize(datetime.datetime.strptime(timing, "%Y-%m-%d %H:%M:%S"))
        elif self.seconds_regex.match(timing):
            #  如果写成+号 可以输入无限长，或考虑前端修改
            eta = datetime.datetime.now(tz=business_tz) + datetime.timedelta(
                seconds=int(timing))
        else:
            message = _(u"输入参数%s不符合【秒(s) 或 时间(%%Y-%%m-%%d %%H:%%M:%%S)】格式") % timing
            data.set_outputs('ex_data', message)
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

    def outputs_format(self):
        return []


class SleepTimerComponent(Component):
    name = _(u'定时')
    code = 'sleep_timer'
    bound_service = SleepTimerService
    form = settings.STATIC_URL + 'components/atoms/bk/timer.js'
