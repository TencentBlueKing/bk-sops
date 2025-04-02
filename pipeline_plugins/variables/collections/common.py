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
import json
import logging
from typing import List

import pytz
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from pipeline.core.data.var import LazyVariable, RegisterVariableMeta, SpliceVariable
from pipeline.core.flow.io import IntItemSchema, StringItemSchema

from gcloud.constants import Type
from gcloud.core.models import StaffGroupSet
from gcloud.exceptions import ApiRequestError
from gcloud.utils.cmdb import get_notify_receivers
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.variables.base import FieldExplain, SelfExplainVariable

logger = logging.getLogger("root")


class CommonPlainVariable(SpliceVariable, metaclass=RegisterVariableMeta):
    pass


class Input(CommonPlainVariable, SelfExplainVariable):
    code = "input"
    name = _("输入框")
    type = "general"
    tag = "input.input"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("输入框变量"))

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [FieldExplain(key="${KEY}", type=Type.STRING, description="用户输入的值")]


class Textarea(CommonPlainVariable, SelfExplainVariable):
    code = "textarea"
    name = _("文本框")
    type = "general"
    tag = "textarea.textarea"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("文本框变量"))

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [FieldExplain(key="${KEY}", type=Type.STRING, description="用户输入的值")]


class Datetime(CommonPlainVariable, SelfExplainVariable):
    code = "datetime"
    name = _("日期时间")
    type = "general"
    tag = "datetime.datetime"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("日期时间变量"))
    desc = _("输出格式: 2000-04-19 14:45:16")

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [
            FieldExplain(key="${KEY}", type=Type.STRING, description="用户选择的时间，输出格式: 2000-04-19 14:45:16")
        ]


class Int(CommonPlainVariable, SelfExplainVariable):
    code = "int"
    name = _("整数")
    type = "general"
    tag = "int.int"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = IntItemSchema(description=_("整数变量"))

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [FieldExplain(key="${KEY}", type=Type.INT, description="用户输入的数值")]


class Password(LazyVariable, SelfExplainVariable):
    code = "password"
    name = _("密码")
    type = "general"
    tag = "password.password"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("密码变量"))
    desc = _("请注意，并非所有插件字段都支持密码变量的使用，请结合具体插件进行使用")

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [FieldExplain(key="${KEY}", type=Type.STRING, description=_("用户输入的密码加密后的值"))]

    def get_value(self):
        return self.value


class Select(LazyVariable, SelfExplainVariable):
    code = "select"
    name = _("下拉框")
    type = "meta"
    tag = "select.select"
    meta_tag = "select.select_meta"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("下拉框变量"))
    desc = _(
        "单选模式下输出选中的 value，多选模式下输出选中 value 以 ',' 拼接的字符串\n该变量默认不支持输入任意值，仅在子流程节点配置填参时支持输入任意值"
    )

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [
            FieldExplain(
                key="${KEY}", type=Type.STRING, description="选中的 value，多选模式下输出选中 value 以 ',' 拼接的字符串"
            )
        ]

    def get_value(self):
        # multiple select
        if isinstance(self.value, list):
            return ",".join([str(v) for v in self.value])
        # single select
        else:
            return self.value


class TextValueSelect(LazyVariable, SelfExplainVariable):
    code = "text_value_select"
    name = _("文本值下拉框")
    type = "meta"
    tag = "select.select"
    meta_tag = "select.select_meta"
    form = "%svariables/%s.js" % (settings.STATIC_URL, "select")
    schema = StringItemSchema(description=_("文本值下拉框变量"))
    desc = _(
        '单选模式下 ${KEY["value"]} 输出选中的 value，\n'
        '${KEY["text"]} 输出选中的 text。\n'
        '多选模式下 ${KEY["value"]} 输出选中的 value 以 ","拼接的字符串，\n'
        '${KEY["text"]} 输出选中的 text 以 "," 拼接的字符串。\n'
        '对于未选择的 text 和 value，通过 ${KEY["text_not_selected"]} 和 ${KEY["value_not_selected"]} 输出对应拼接字符串。\n'
        "注意：请确保不同选项的value值不相同。"
    )

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [
            FieldExplain(
                key="${KEY}", type=Type.DICT, description="用户选择的选项的text与value以及未选中的text与value"
            ),
            FieldExplain(key='${KEY["value"]}', type=Type.STRING, description="用户选中选项的value，多个以,分隔"),
            FieldExplain(key='${KEY["text"]}', type=Type.STRING, description="用户选中选项的text，多个以,分隔"),
            FieldExplain(
                key='${KEY["value_not_selected"]}', type=Type.STRING, description="用户未选中选项的value，多个以,分隔"
            ),
            FieldExplain(
                key='${KEY["text_not_selected"]}', type=Type.STRING, description="用户未选中选项的text，多个以,分隔"
            ),
        ]

    def get_value(self):

        meta_values = json.loads(self.value["meta_data"])
        info_values = TextValueSelect.process_info_value(self.value["info_value"])
        text_values = [
            meta["text"] for value in info_values for meta in meta_values if meta["value"] == value and meta["text"]
        ]
        text_not_selected_values = [meta["text"] for meta in meta_values if meta["value"] not in info_values]
        info_not_selected_values = [meta["value"] for meta in meta_values if meta["value"] not in info_values]

        return {
            "value": ",".join(info_values),
            "text": ",".join(text_values),
            "text_not_selected": ",".join(text_not_selected_values),
            "value_not_selected": ",".join(info_not_selected_values),
        }

    @classmethod
    def process_info_value(cls, info_value):
        if isinstance(info_value, str):
            return [info_value]

        # 在 子流程 变量传递的过程中，会出现info_value = {"value": 1, "text": "xx", "text_not_selected": "xx"}的情况，
        # 所以需要特殊处理一下
        if isinstance(info_value, dict):
            if set(info_value.keys()) == {"value", "text", "text_not_selected", "value_not_selected"}:
                return [info_value["value"]]

        return info_value

    @classmethod
    def process_meta_value(self, meta_data, info_value):
        if meta_data["value"]["datasource"] == "1":
            # 远程数据源模式下需要记录拉取的数据而不是 URL
            meta_value = meta_data["value"]["remote_data"]
        else:
            meta_value = meta_data["value"]["items_text"]
        return {"meta_data": meta_value, "info_value": info_value}


class FormatSupportCurrentTime(LazyVariable, SelfExplainVariable):
    code = "format_support_current_time"
    name = _("系统当前时间(支持格式自定义)")
    type = "dynamic"
    tag = "format_support_current_time.format_support_current_time"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("系统当前时间变量(支持格式自定义)"))

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [FieldExplain(key="${KEY}", type=Type.STRING, description="自定义格式的系统当前时间")]

    def get_value(self):
        time_format = self.value.get("time_format", "%Y-%m-%d %H:%M:%S").strip()
        time_zone = self.value.get("time_zone", "Asia/Shanghai")
        now = datetime.datetime.now(pytz.timezone(time_zone))
        current_time = now.strftime(time_format)
        return current_time


class CurrentTime(LazyVariable, SelfExplainVariable):
    code = "current_time"
    name = _("系统当前时间")
    type = "dynamic"
    tag = "current_time.current_time"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("系统当前时间变量"))

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [FieldExplain(key="${KEY}", type=Type.STRING, description="自定义格式的系统当前时间")]

    def get_value(self):
        time_units = self.value.get("time_unit") or ["year", "month", "day", "hour", "minute", "second"]
        time_zone = self.value.get("time_zone", "Asia/Shanghai")
        now = datetime.datetime.now(pytz.timezone(time_zone))
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


class Date(CommonPlainVariable, SelfExplainVariable):
    code = "date"
    name = _("日期")
    type = "general"
    tag = "date.date"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("日期变量"))
    desc = _("输出格式: 2000-04-19")

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [FieldExplain(key="${KEY}", type=Type.STRING, description=_("用户选择的日期，格式为2000-04-19"))]


class Time(LazyVariable, SelfExplainVariable):
    code = "time"
    name = _("时间")
    type = "general"
    tag = "time.time"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_("时间变量"))
    desc = _("输出格式: 14:45")

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [FieldExplain(key="${KEY}", type=Type.STRING, description="用户选择的日期，格式为14:45")]

    def get_value(self):
        """
        由于用户需要，这里的时间格式由“小时:分钟:秒”处理成“小时:分钟”
        """
        return self.value[:-3]


class FormatSupportDateTime(LazyVariable, SelfExplainVariable):
    code = "format_support_datetime"
    name = _("日期时间（支持格式自定义）")
    type = "general"
    tag = "format_support_datetime.format_support_datetime"
    form = "%svariables/%s.js" % (settings.STATIC_URL, code)
    desc = _("默认输出格式: 2020-10-10 14:45:00, 可自行配置显示格式")

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [FieldExplain(key="${KEY}", type=Type.STRING, description=_("用户选择的自定义格式的日期时间"))]

    def get_value(self):
        time_format = self.value.get("datetime_format", "%Y-%m-%d %H:%M:%S").strip()
        time = datetime.datetime.strptime(self.value.get("datetime"), "%Y-%m-%d %H:%M:%S")
        return time.strftime(time_format)


class StaffGroupSelector(LazyVariable, SelfExplainVariable):
    code = "staff_group_selector"
    name = _("人员分组选择器")
    type = "dynamic"
    tag = "staff_group_multi_selector.staff_group_selector"
    form = "%svariables/staff_group_multi_selector.js" % settings.STATIC_URL
    desc = _(
        "可选cc业务固定的四个人员分组(运维人员、产品人员、开发人员、测试人员)和标准运维【项目管理】中配置的人员分组\n"
        "输出格式为选中人员用户名以 ',' 拼接的字符串"
    )

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [FieldExplain(key="${KEY}", type=Type.STRING, description="人员列表，以,分隔")]

    def get_value(self):
        if "executor" not in self.pipeline_data or "biz_cc_id" not in self.pipeline_data:
            raise Exception("ERROR: executor and biz_cc_id of pipeline is needed")
        tenant_id = self.pipeline_data["tenant_id"]
        operator = self.pipeline_data["executor"]
        bk_biz_id = int(self.pipeline_data["biz_cc_id"])
        supplier_account = supplier_account_for_business(bk_biz_id)

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
        res = get_notify_receivers(tenant_id, operator, bk_biz_id, supplier_account, cc_staff_group, staff_names)

        if not res["result"]:
            message = f'get cc({bk_biz_id}) staff_group failed: {res["message"]}'
            logger.error(message)
            raise ApiRequestError(message)

        return res["data"]
