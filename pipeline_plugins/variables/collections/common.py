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

from gcloud.core.models import StaffGroupSet
from gcloud.utils.cmdb import get_notify_receivers, get_client_by_user
from pipeline.core.data.var import SpliceVariable, LazyVariable, RegisterVariableMeta
from pipeline.core.flow.io import StringItemSchema, IntItemSchema
from pipeline_plugins.base.utils.inject import supplier_account_for_business

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


class Date(CommonPlainVariable):
    code = "date"
    name = _("日期")
    type = "general"
    tag = "date.date"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("日期变量"))


class Time(LazyVariable):
    code = "time"
    name = _("时间")
    type = "general"
    tag = "time.time"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("时间变量"))

    def get_value(self):
        """
        由于用户需要，这里的时间格式由“小时:分钟:秒”处理成“小时:分钟”
        """
        return self.value[:-3]


class StaffGroupSelector(LazyVariable):
    code = "staff_group_selector"
    name = _("人员分组选择器")
    type = "general"
    tag = "staff_group_multi_selector.staff_group_selector"
    form = "%svariables/staff_group_multi_selector.js" % settings.STATIC_URL

    def get_value(self):
        operator = self.pipeline_data.get("executor", "")
        bk_biz_id = int(self.pipeline_data.get("biz_cc_id", 0))
        supplier_account = supplier_account_for_business(bk_biz_id)
        client = get_client_by_user(operator)

        # 自定义项目分组和cc 人员分组
        staff_group_id_list = [group_id for group_id in self.value if str(group_id).isdigit()]
        cc_staff_group = list(set(self.value).difference(set(staff_group_id_list)))

        # 获取项目的自定义人员分组人员
        staff_names_list = StaffGroupSet.objects.filter(id__in=staff_group_id_list, is_deleted=False).values_list(
            "members", flat=True
        )

        staff_names_str = ",".join(staff_names_list)
        staff_names_list_clear = list(set(staff_names_str.split(",")))
        staff_names = ",".join(staff_names_list_clear)

        # 拼接cc分组人员和自定义分组人员
        res = get_notify_receivers(client, bk_biz_id, supplier_account, cc_staff_group, staff_names)

        if res["result"]:
            return res["data"]
        else:
            logger.error("get cc({}) staff_group failed".format(bk_biz_id))
            return staff_names
