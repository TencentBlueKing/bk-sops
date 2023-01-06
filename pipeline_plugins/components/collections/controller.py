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

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component

__group_name__ = _("蓝鲸服务(BK)")

from pipeline_plugins.components.collections.sites.open.bk.timer.base import SleepTimerBaseService

LOGGER = logging.getLogger("celery")


class PauseService(Service):
    __need_schedule__ = True

    def execute(self, data, parent_data):
        return True

    def schedule(self, data, parent_data, callback_data=None):
        if callback_data is not None:
            data.outputs.callback_data = callback_data
            self.finish_schedule()
        return True

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("描述"), key="description", type="string", schema=StringItemSchema(description=_("描述")),
            )
        ]

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("API回调数据"),
                key="callback_data",
                type="object",
                schema=ObjectItemSchema(description=_("通过node_callback API接口回调并传入数据,支持dict数据"), property_schemas={},),
            ),
        ]


class PauseComponent(Component):
    name = _("人工确认(暂停)")
    code = "pause_node"
    bound_service = PauseService
    form = settings.STATIC_URL + "components/atoms/bk/pause.js"
    desc = _("该节点可以通过node_callback API接口进行回调并传入数据，callback_data参数为dict类型，回调数据会作为该节点的输出数据")


class SleepTimerService(SleepTimerBaseService):
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

    def is_force_check(self, data):
        return data.get_one_of_inputs("force_check", True)

    def get_timing(self, data):
        return data.get_one_of_inputs("bk_timing")


class SleepTimerComponent(Component):
    name = _("定时")
    code = "sleep_timer"
    bound_service = SleepTimerService
    form = settings.STATIC_URL + "components/atoms/bk/timer.js"
