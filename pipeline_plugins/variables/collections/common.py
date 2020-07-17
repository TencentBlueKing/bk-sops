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
import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from pipeline.core.data.var import SpliceVariable, LazyVariable, RegisterVariableMeta
from pipeline.core.flow.io import StringItemSchema, IntItemSchema

logger = logging.getLogger("root")


class CommonPlainVariable(SpliceVariable, metaclass=RegisterVariableMeta):
    pass


class Input(CommonPlainVariable):
    code = "input"
    name = _("输入框")
    type = "general"
    tag = "input.input"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("输入框变量"))


class Textarea(CommonPlainVariable):
    code = "textarea"
    name = _("文本框")
    type = "general"
    tag = "textarea.textarea"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("文本框变量"))


class Datetime(CommonPlainVariable):
    code = "datetime"
    name = _("日期时间")
    type = "general"
    tag = "datetime.datetime"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("日期时间变量"))


class Int(CommonPlainVariable):
    code = "int"
    name = _("整数")
    type = "general"
    tag = "int.int"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = IntItemSchema(description=_("整数变量"))


class Password(LazyVariable):
    code = "password"
    name = _("密码")
    type = "general"
    tag = "password.password"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("密码变量"))

    def get_value(self):
        return self.value


class Select(LazyVariable):
    code = "select"
    name = _("下拉框")
    type = "meta"
    tag = "select.select"
    meta_tag = "select.select_meta"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("下拉框变量"))

    def get_value(self):
        # multiple select
        if isinstance(self.value, list):
            return ",".join([str(v) for v in self.value])
        # single select
        else:
            return self.value


class CurrentTime(LazyVariable):
    code = "current_time"
    name = _("系统当前时间")
    type = "general"
    tag = "current_time.current_time"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("系统当前时间变量"))

    def get_value(self):
        time_units = self.value.get("time_unit") or ["year", "month", "day", "hour", "minute", "second"]
        time_zone = self.value.get("time_zone", "Asia/Shanghai")
        now = datetime.datetime.now(timezone.pytz.timezone(time_zone))
        current_time = now.strftime(self._generate_time_format(time_units))
        return current_time

    @staticmethod
    def _generate_time_format(needed_units):
        """
        根据用户选择的时间格式生成对应的转换格式字符串
        """
        time_units = [
            ("year", "%Y", ""),
            ("month", "%m", "-"),
            ("day", "%d", "-"),
            ("hour", "%H", ""),
            ("minute", "%M", ":"),
            ("second", "%S", ":"),
        ]
        final_format = ""
        # needed_units 形如['year', 'month', 'day', 'hour', 'minute', 'second']
        for time_unit in time_units:
            unit, time_format, separator = time_unit[0], time_unit[1], time_unit[2]
            if unit == "hour":
                final_format += " "
            if unit in needed_units:
                if len(final_format) > 0 and final_format[-1] != " ":
                    final_format += separator
                final_format += time_format
        return final_format.strip()
