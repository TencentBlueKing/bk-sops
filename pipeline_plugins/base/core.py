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
import re

from django.conf import settings
from pipeline.core.flow.activity import Service

from gcloud.core.trace import (
    PLUGIN_SCHEDULE_COUNT_KEY,
    PLUGIN_SPAN_ENDED_KEY,
    PLUGIN_SPAN_ID_KEY,
    end_plugin_span,
    plugin_method_span,
    start_plugin_span,
)

logger = logging.getLogger("root")


def _camel_to_snake(name):
    """
    将驼峰命名转换为下划线命名
    例如: JobExecuteTaskService -> job_execute_task

    :param name: 驼峰命名的字符串
    :return: 下划线命名的字符串
    """
    # 移除末尾的 "Service"
    name = re.sub(r"Service$", "", name)
    # 在大写字母前插入下划线（除了第一个字符）
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", name)
    # 转换为小写
    return name.lower()


class BasePluginService(Service):
    """
    插件基类，提供统一的 Span 追踪功能
    所有插件应该继承此类而不是直接继承 Service
    """

    # 是否启用插件 Span 追踪，子类可以覆盖
    enable_plugin_span = True

    def _get_trace_context(self, data, parent_data):
        """
        获取 trace context，包括从 parent_data 中获取的 trace_id 和 parent_span_id，
        以及从 data.outputs 中获取的 plugin_span_id

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        :return: 包含 trace_id、parent_span_id 和 plugin_span_id 的字典
        """
        return {
            "trace_id": parent_data.get_one_of_inputs("_trace_id"),
            "parent_span_id": parent_data.get_one_of_inputs("_parent_span_id"),
            "plugin_span_id": data.get_one_of_outputs(PLUGIN_SPAN_ID_KEY),
        }

    def _get_span_name(self):
        """
        获取 Span 名称，子类可以覆盖此方法来自定义名称

        :return: Span 名称
        """
        # 将类名从驼峰命名转换为下划线命名
        # 例如: JobExecuteTaskService -> job_execute_task
        plugin_name = _camel_to_snake(self.__class__.__name__)
        platform_code = getattr(settings, "APP_CODE", "bk_sops")
        return f"{platform_code}.plugin.{plugin_name}"

    def _get_span_attributes(self, data, parent_data):
        """
        获取 Span 属性，子类可以覆盖此方法来添加自定义属性

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        :return: 属性字典
        """
        attributes = {
            "project_id": parent_data.get_one_of_inputs("project_id"),
            "bk_biz_id": parent_data.get_one_of_inputs("bk_biz_id"),
            "task_id": parent_data.get_one_of_inputs("task_id"),
            "operator": parent_data.get_one_of_inputs("operator"),
            "executor": parent_data.get_one_of_inputs("executor"),
            "node_id": self.id,
            "plugin_type": "builtin",  # 内置插件
        }

        return attributes

    def _get_method_span_attributes(self, data, parent_data):
        """
        获取方法级别 Span 属性

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        :return: 属性字典
        """
        attributes = self._get_span_attributes(data, parent_data)
        # 添加插件名称，将类名从驼峰命名转换为下划线命名
        plugin_name = _camel_to_snake(self.__class__.__name__)
        attributes["plugin_name"] = plugin_name
        return attributes

    def _get_error_message(self, data):
        """
        获取错误信息

        :param data: 插件数据对象
        :return: 错误信息字符串
        """
        ex_data = data.get_one_of_outputs("ex_data")
        if ex_data:
            return str(ex_data)
        return "Plugin execution failed"

    def _start_plugin_span(self, data, parent_data):
        """
        启动插件执行 Span

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        """
        if not self.enable_plugin_span or not settings.ENABLE_OTEL_TRACE:
            return

        span_name = self._get_span_name()
        attributes = self._get_span_attributes(data, parent_data)

        trace_id = parent_data.get_one_of_inputs("_trace_id")
        parent_span_id = parent_data.get_one_of_inputs("_parent_span_id")

        start_plugin_span(
            span_name=span_name,
            data=data,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            **attributes,
        )
        data.set_outputs(PLUGIN_SPAN_ENDED_KEY, False)

    def _end_plugin_span(self, data, success, error_message=None):
        """
        结束插件执行 Span（确保只调用一次）

        :param data: 插件数据对象
        :param success: 是否成功
        :param error_message: 错误信息
        """
        if not self.enable_plugin_span or not settings.ENABLE_OTEL_TRACE:
            return

        if data.get_one_of_outputs(PLUGIN_SPAN_ENDED_KEY, False):
            return  # 幂等保护

        end_plugin_span(data, success=success, error_message=error_message)
        data.set_outputs(PLUGIN_SPAN_ENDED_KEY, True)

    def execute(self, data, parent_data):
        """
        执行插件，包装原有逻辑并添加 Span 追踪

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        :return: 执行结果
        """
        self._start_plugin_span(data, parent_data)

        trace_context = self._get_trace_context(data, parent_data)
        method_attrs = self._get_method_span_attributes(data, parent_data)

        if self.enable_plugin_span and settings.ENABLE_OTEL_TRACE:
            with plugin_method_span(
                method_name="execute",
                trace_id=trace_context.get("trace_id"),
                parent_span_id=trace_context.get("parent_span_id"),
                plugin_span_id=trace_context.get("plugin_span_id"),
                **method_attrs,
            ) as span_result:
                result = self.plugin_execute(data, parent_data)
                if not result:
                    span_result.set_error(self._get_error_message(data))
        else:
            result = self.plugin_execute(data, parent_data)

        if not result:
            self._end_plugin_span(data, success=False, error_message=self._get_error_message(data))
        elif not getattr(self, "__need_schedule__", False):
            # 如果不需要 schedule，说明是同步插件，直接结束 span
            self._end_plugin_span(data, success=True)

        return result

    def schedule(self, data, parent_data, callback_data=None):
        """
        调度插件，包装原有逻辑并添加 Span 追踪

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        :param callback_data: 回调数据
        :return: 调度结果
        """
        trace_context = self._get_trace_context(data, parent_data)
        method_attrs = self._get_method_span_attributes(data, parent_data)

        if self.enable_plugin_span and settings.ENABLE_OTEL_TRACE:
            schedule_count = data.get_one_of_outputs(PLUGIN_SCHEDULE_COUNT_KEY, 0) + 1
            data.set_outputs(PLUGIN_SCHEDULE_COUNT_KEY, schedule_count)
            method_attrs["schedule_count"] = schedule_count

            with plugin_method_span(
                method_name="schedule",
                trace_id=trace_context.get("trace_id"),
                parent_span_id=trace_context.get("parent_span_id"),
                plugin_span_id=trace_context.get("plugin_span_id"),
                **method_attrs,
            ) as span_result:
                result = self.plugin_schedule(data, parent_data, callback_data)
                if not result:
                    span_result.set_error(self._get_error_message(data))
        else:
            result = self.plugin_schedule(data, parent_data, callback_data)

        if not result:
            self._end_plugin_span(data, success=False, error_message=self._get_error_message(data))
        else:
            # 尝试调用 is_schedule_finished() 方法（如果存在）
            # 如果不存在，则检查 __need_schedule__ 属性
            try:
                if hasattr(self, "is_schedule_finished") and callable(getattr(self, "is_schedule_finished")):
                    if self.is_schedule_finished():
                        self._end_plugin_span(data, success=True)
                elif not getattr(self, "__need_schedule__", False):
                    # 如果不再需要 schedule，说明已完成
                    self._end_plugin_span(data, success=True)
            except Exception:
                # 如果判断失败，不结束 span，让下次 schedule 调用时再判断
                pass

        return result

    def plugin_execute(self, data, parent_data):
        """
        插件执行逻辑，子类应该覆盖此方法而不是 execute

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        :return: 执行结果
        """
        # 默认实现，子类应该覆盖
        return True

    def plugin_schedule(self, data, parent_data, callback_data=None):
        """
        插件调度逻辑，子类应该覆盖此方法而不是 schedule

        注意：对于需要调度的插件（__need_schedule__ = True），在调度完成时
        必须调用 self.finish_schedule() 来标记调度结束。否则 BasePluginService
        无法感知调度已完成，会导致插件级别的父 Span 无法正确结束和导出。

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        :param callback_data: 回调数据
        :return: 调度结果
        """
        # 默认实现，子类应该覆盖
        return True
