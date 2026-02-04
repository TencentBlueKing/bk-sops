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
import copy
import enum
import logging
import random
import time
from contextlib import contextmanager
from functools import wraps
from typing import Optional

from django.conf import settings
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import Span as SDKSpan
from opentelemetry.sdk.trace import SpanLimits, TracerProvider
from opentelemetry.sdk.trace.export import SpanProcessor
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.trace import NonRecordingSpan, SpanContext, SpanKind, Status, StatusCode, TraceFlags

logger = logging.getLogger("root")


class CallFrom(enum.Enum):
    """调用来源"""

    WEB = "web"
    APIGW = "apigw"
    BACKEND = "backend"


class AttributeInjectionSpanProcessor(SpanProcessor):
    """Span处理器，用于在Span开始时设置属性"""

    def __init__(self, attributes):
        self.attributes = attributes

    def on_start(self, span: trace.Span, parent_context):
        if not isinstance(span, trace.Span):
            return

        for key, value in self.attributes.items():
            span.set_attribute(key, value)

    def on_end(self, span: trace.Span):
        # Implement custom logic if needed on span end
        pass

    def set_attributes(self, attributes):
        self.attributes = attributes


def propagate_attributes(attributes: dict):
    """把attributes设置到span上，并继承到后面所有span

    :param attributes: 默认属性
    """

    provider = trace.get_tracer_provider()

    if not provider or isinstance(provider, trace.ProxyTracerProvider):
        provider = TracerProvider()
        trace.set_tracer_provider(provider)

    # Add a span processor that sets attributes on every new span
    inject_attributes = False
    for sp in getattr(provider._active_span_processor, "_span_processors", []):
        if isinstance(sp, AttributeInjectionSpanProcessor):
            inject_attributes = True
            sp.set_attributes(attributes)
            break

    if not inject_attributes:
        provider.add_span_processor(AttributeInjectionSpanProcessor(attributes))


def append_attributes(attributes: dict):
    """追加属性到span上

    :param attributes: 需要追加的属性
    """
    current_span = trace.get_current_span()
    for key, value in attributes.items():
        current_span.set_attribute(f"{settings.APP_CODE}.{key}", value)


@contextmanager
def start_trace(span_name: str, propagate: bool = False, **attributes):
    """Start a trace

    :param span_name: 自定义Span名称
    :param propagate: 是否需要传播
    :param attributes: 需要跟span增加的属性, 默认为空
    :yield: 当前上下文的Span
    """
    tracer = trace.get_tracer(__name__)

    span_attributes = {f"{settings.APP_CODE}.{key}": value for key, value in attributes.items()}

    # 设置需要传播的属性
    if propagate:
        propagate_attributes(span_attributes)

    with tracer.start_as_current_span(span_name, kind=SpanKind.SERVER) as span:
        # 如果不进行传播，则在当前span手动配置需要添加的属性
        for attr_key, attr_value in span_attributes.items():
            span.set_attribute(attr_key, attr_value)

        yield span


def trace_view(propagate: bool = True, attr_keys=None, **default_attributes):
    """用来装饰view的trace装饰器

    :param propagate: 是否需要传播
    :param attr_keys: 需要从request和url中获取的属性
    :param default_attributes: 默认属性
    :return: view_func
    """
    attr_keys = attr_keys or []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            attributes = copy.deepcopy(default_attributes)

            for attr_key in attr_keys:
                # 需要的属性只要在kwargs, request.GET, request.query_params(drf), request.POST, request.data(drf)中就可以
                query_params = getattr(request, "GET", {}) or getattr(request, "query_params", {})
                query_data = getattr(request, "POST", {}) or getattr(request, "data", {})
                for scope in (kwargs, query_params, query_data):
                    if attr_key in scope:
                        attributes[attr_key] = scope[attr_key]
                        break

            with start_trace(view_func.__name__, propagate, **attributes):
                return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# ==================== Execution Span 相关功能 ====================


def create_execution_span(
    task_id: int,
    project_id: int,
    pipeline_instance_id: str,
) -> tuple:
    """
    创建 bksops.execution span 作为所有插件 span 的根 span

    :param task_id: 任务 ID
    :param project_id: 项目 ID
    :param pipeline_instance_id: Pipeline 实例 ID
    :return: (trace_id_hex, span_id_hex) 元组，如果创建失败则返回 (None, None)
    """
    if not settings.ENABLE_OTEL_TRACE:
        return None, None

    try:
        tracer = trace.get_tracer(__name__)
        platform_code = getattr(settings, "APP_CODE", "bk_sops")
        span_name = f"{platform_code}.execution"

        # 获取当前 span 作为父 span
        current_span = trace.get_current_span()
        parent_context = None
        if current_span and current_span.get_span_context().is_valid:
            parent_context = trace.set_span_in_context(current_span)

        # 创建 execution span
        start_time_ns = int(time.time() * 1e9)
        span = tracer.start_span(
            name=span_name,
            context=parent_context,
            start_time=start_time_ns,
            kind=SpanKind.INTERNAL,
        )

        # 设置属性
        span.set_attribute(f"{platform_code}.task_id", str(task_id))
        span.set_attribute(f"{platform_code}.project_id", str(project_id))
        span.set_attribute(f"{platform_code}.pipeline_instance_id", str(pipeline_instance_id))

        # 获取 span context
        span_context = span.get_span_context()
        trace_id_hex = format(span_context.trace_id, "032x")
        span_id_hex = format(span_context.span_id, "016x")

        # 立即结束 span（异步执行场景，span 只是作为父 span 使用）
        span.set_status(Status(StatusCode.OK))
        span.end()

        return trace_id_hex, span_id_hex

    except Exception as e:
        logger.debug(f"[plugin_span] Failed to create execution span: {e}")
        return None, None


# ==================== Plugin Span 相关功能 ====================

# Span 信息在 data.outputs 中的 key
PLUGIN_SPAN_START_TIME_KEY = "_plugin_span_start_time_ns"
PLUGIN_SPAN_NAME_KEY = "_plugin_span_name"
PLUGIN_SPAN_TRACE_ID_KEY = "_plugin_span_trace_id"
PLUGIN_SPAN_PARENT_SPAN_ID_KEY = "_plugin_span_parent_span_id"  # execution span 的 ID
PLUGIN_SPAN_ID_KEY = "_plugin_span_id"  # 预生成的 plugin span ID，用于作为 method span 的父 span
PLUGIN_SPAN_ATTRIBUTES_KEY = "_plugin_span_attributes"
PLUGIN_SPAN_ENDED_KEY = "_plugin_span_ended"
PLUGIN_SCHEDULE_COUNT_KEY = "_plugin_schedule_count"


def _generate_span_id() -> int:
    """
    生成一个 64 位的随机 span_id

    :return: span_id (整数)
    """
    return random.getrandbits(64)


def start_plugin_span(
    span_name: str,
    data,
    trace_id: Optional[str] = None,
    parent_span_id: Optional[str] = None,
    **attributes,
) -> int:
    """
    记录插件 Span 的开始信息，将相关信息保存到 data outputs 中，用于跨 schedule 调用追踪。
    实际的 Span 会在 end_plugin_span 时创建，以确保有正确的开始和结束时间。

    同时会预先生成 plugin span 的 span_id，用于作为 execute/schedule 方法 span 的父 span。

    :param span_name: Span 名称
    :param data: 插件数据对象
    :param trace_id: Trace ID (十六进制字符串)
    :param parent_span_id: Parent Span ID (十六进制字符串)，即 execution span 的 ID
    :param attributes: Span 属性
    :return: 开始时间（纳秒）
    """
    start_time_ns = int(time.time() * 1e9)

    # 将 span 信息保存到 data outputs 中，以便在 end_plugin_span 中使用
    data.set_outputs(PLUGIN_SPAN_START_TIME_KEY, start_time_ns)
    data.set_outputs(PLUGIN_SPAN_NAME_KEY, span_name)

    # 保存 trace context，用于在 end_plugin_span 时重建 parent 关系
    if trace_id:
        data.set_outputs(PLUGIN_SPAN_TRACE_ID_KEY, trace_id)
    if parent_span_id:
        data.set_outputs(PLUGIN_SPAN_PARENT_SPAN_ID_KEY, parent_span_id)

    # 预先生成 plugin span 的 span_id，用于作为 execute/schedule 方法的父 span
    # 这个 span_id 会在 end_plugin_span 时创建实际的 span 时使用
    plugin_span_id = _generate_span_id()
    plugin_span_id_hex = format(plugin_span_id, "016x")
    data.set_outputs(PLUGIN_SPAN_ID_KEY, plugin_span_id_hex)

    # 确保属性值可以序列化
    serializable_attributes = {k: str(v) if v is not None else "" for k, v in attributes.items()}
    data.set_outputs(PLUGIN_SPAN_ATTRIBUTES_KEY, serializable_attributes)

    return start_time_ns


def end_plugin_span(
    data,
    success: bool = True,
    error_message: Optional[str] = None,
    end_time_ns: Optional[int] = None,
):
    """
    结束插件 Span，创建完整的 Span 并立即结束。
    使用预先生成的 span_id 确保 execute/schedule 方法 span 正确地指向此 span 作为父 span。

    :param data: 插件数据对象
    :param success: 是否成功
    :param error_message: 错误信息
    :param end_time_ns: 结束时间（纳秒），如果不提供则使用当前时间
    """
    if not settings.ENABLE_OTEL_TRACE:
        return

    try:
        # 从 data.outputs 中获取保存的 span 信息
        start_time_ns = data.get_one_of_outputs(PLUGIN_SPAN_START_TIME_KEY)
        span_name = data.get_one_of_outputs(PLUGIN_SPAN_NAME_KEY)
        attributes = data.get_one_of_outputs(PLUGIN_SPAN_ATTRIBUTES_KEY) or {}
        trace_id_hex = data.get_one_of_outputs(PLUGIN_SPAN_TRACE_ID_KEY)
        parent_span_id_hex = data.get_one_of_outputs(PLUGIN_SPAN_PARENT_SPAN_ID_KEY)
        plugin_span_id_hex = data.get_one_of_outputs(PLUGIN_SPAN_ID_KEY)

        if not start_time_ns or not span_name:
            return

        if end_time_ns is None:
            end_time_ns = int(time.time() * 1e9)

        platform_code = getattr(settings, "APP_CODE", "bk_sops")

        # 使用预生成的 span_id 创建 span
        # 这确保 execute/schedule 方法 span 的父 span_id 指向正确的 span
        span = _create_span_with_custom_id(
            span_name=span_name,
            trace_id_hex=trace_id_hex,
            span_id_hex=plugin_span_id_hex,
            parent_span_id_hex=parent_span_id_hex,
            start_time_ns=start_time_ns,
            end_time_ns=end_time_ns,
        )

        if span is None:
            # 如果无法使用自定义 span_id 创建 span，回退到标准方式
            tracer = trace.get_tracer(__name__)
            parent_context = _build_parent_context(trace_id_hex, parent_span_id_hex)
            span = tracer.start_span(
                name=span_name,
                context=parent_context,
                start_time=start_time_ns,
                kind=SpanKind.CLIENT,
            )

            # 设置属性
            for key, value in attributes.items():
                span.set_attribute(f"{platform_code}.plugin.{key}", value)

            # 设置执行结果状态
            if success:
                span.set_status(Status(StatusCode.OK))
                span.set_attribute(f"{platform_code}.plugin.success", True)
            else:
                span.set_status(Status(StatusCode.ERROR, error_message or "Plugin execution failed"))
                span.set_attribute(f"{platform_code}.plugin.success", False)
                if error_message:
                    span.set_attribute(f"{platform_code}.plugin.error", str(error_message)[:1000])

            span.end(end_time=end_time_ns)
        else:
            # 使用自定义 span_id 创建成功，设置属性
            for key, value in attributes.items():
                span.set_attribute(f"{platform_code}.plugin.{key}", value)

            if success:
                span.set_status(Status(StatusCode.OK))
                span.set_attribute(f"{platform_code}.plugin.success", True)
            else:
                span.set_status(Status(StatusCode.ERROR, error_message or "Plugin execution failed"))
                span.set_attribute(f"{platform_code}.plugin.success", False)
                if error_message:
                    span.set_attribute(f"{platform_code}.plugin.error", str(error_message)[:1000])

            span.end(end_time=end_time_ns)

    except Exception as e:
        logger.debug(f"[plugin_span] Failed to end plugin span: {e}")


def _build_parent_context(trace_id_hex: Optional[str], parent_span_id_hex: Optional[str]):
    """
    根据保存的 trace_id 和 parent_span_id 重建 parent context

    :param trace_id_hex: Trace ID (十六进制字符串)
    :param parent_span_id_hex: Parent Span ID (十六进制字符串)
    :return: Parent context 或 None
    """
    if not trace_id_hex or not parent_span_id_hex:
        return None

    try:
        # 将十六进制字符串转换为整数
        trace_id_int = int(trace_id_hex, 16)
        parent_span_id_int = int(parent_span_id_hex, 16)

        # 创建 SpanContext
        parent_span_context = SpanContext(
            trace_id=trace_id_int,
            span_id=parent_span_id_int,
            is_remote=True,
            trace_flags=TraceFlags(0x01),  # SAMPLED
        )

        if not parent_span_context.is_valid:
            return None

        parent_span = NonRecordingSpan(parent_span_context)
        parent_context = trace.set_span_in_context(parent_span)
        return parent_context

    except (ValueError, TypeError) as e:
        logger.debug(f"[plugin_span] Failed to parse trace context: {e}")
        return None


def _create_span_with_custom_id(
    span_name: str,
    trace_id_hex: Optional[str],
    span_id_hex: Optional[str],
    parent_span_id_hex: Optional[str],
    start_time_ns: int,
    end_time_ns: int,
):
    """
    使用自定义的 span_id 创建 span。这是为了确保 execute/schedule 方法 span
    能够正确地指向 plugin span 作为父 span。

    :param span_name: Span 名称
    :param trace_id_hex: Trace ID (十六进制字符串)
    :param span_id_hex: 预生成的 Span ID (十六进制字符串)
    :param parent_span_id_hex: Parent Span ID (十六进制字符串)
    :param start_time_ns: 开始时间（纳秒）
    :param end_time_ns: 结束时间（纳秒）
    :return: Span 对象或 None
    """
    if not trace_id_hex or not span_id_hex:
        return None

    try:
        # 将十六进制字符串转换为整数
        trace_id_int = int(trace_id_hex, 16)
        span_id_int = int(span_id_hex, 16)
        parent_span_id_int = int(parent_span_id_hex, 16) if parent_span_id_hex else 0

        # 创建自定义 SpanContext
        span_context = SpanContext(
            trace_id=trace_id_int,
            span_id=span_id_int,
            is_remote=False,
            trace_flags=TraceFlags(0x01),  # SAMPLED
        )

        if not span_context.is_valid:
            return None

        # 创建 parent SpanContext
        parent_span_context = None
        if parent_span_id_int:
            parent_span_context = SpanContext(
                trace_id=trace_id_int,
                span_id=parent_span_id_int,
                is_remote=True,
                trace_flags=TraceFlags(0x01),
            )

        # 获取 TracerProvider 和相关资源
        provider = trace.get_tracer_provider()

        # 尝试获取 span processor
        span_processor = None
        resource = Resource.create({})
        if hasattr(provider, "_active_span_processor"):
            span_processor = provider._active_span_processor
        if hasattr(provider, "resource"):
            resource = provider.resource

        # 创建 InstrumentationScope
        instrumentation_scope = InstrumentationScope(
            name=__name__,
            version="",
        )

        # 创建 SDK Span
        span = SDKSpan(
            name=span_name,
            context=span_context,
            parent=parent_span_context,
            resource=resource,
            attributes=None,
            events=None,
            links=None,
            kind=SpanKind.CLIENT,
            span_processor=span_processor,
            limits=SpanLimits(),
            instrumentation_scope=instrumentation_scope,
            record_exception=True,
            set_status_on_exception=True,
            start_time=start_time_ns,
        )

        return span

    except Exception as e:
        logger.debug(f"[plugin_span] Failed to create span with custom id: {e}")
        return None


@contextmanager
def plugin_method_span(
    method_name: str,
    trace_id: Optional[str] = None,
    parent_span_id: Optional[str] = None,
    plugin_span_id: Optional[str] = None,
    **attributes,
):
    """
    追踪 plugin_execute 和 plugin_schedule 方法的 Span 上下文管理器

    :param method_name: 方法名称 (execute 或 schedule)
    :param trace_id: Trace ID (十六进制字符串)
    :param parent_span_id: Parent Span ID (来自 parent_data，即 execution span 的 ID，作为备选)
    :param plugin_span_id: Plugin Span ID (预生成的 plugin span ID，作为首选父 span)
    :param attributes: Span 属性
    :yield: SpanResult 对象，用于设置执行结果
    """
    if not settings.ENABLE_OTEL_TRACE:
        yield None
        return

    start_time_ns = int(time.time() * 1e9)

    plugin_name = attributes.get("plugin_name", "unknown")

    # 构建 span 名称
    platform_code = getattr(settings, "APP_CODE", "bk_sops")
    span_name = f"{platform_code}.plugin.{plugin_name}.{method_name}"

    # 用于存储执行结果的容器
    class SpanResult:
        def __init__(self):
            self.success = True
            self.error_message = None

        def set_error(self, message: str):
            self.success = False
            self.error_message = message

    result = SpanResult()

    try:
        yield result
    finally:
        try:
            end_time_ns = int(time.time() * 1e9)
            tracer = trace.get_tracer(__name__)

            # 优先使用 plugin_span_id 作为父 span，如果没有则使用 execution span
            # 这样 execute/schedule 方法 span 会正确地显示为 plugin span 的子 span
            actual_parent_span_id = plugin_span_id if plugin_span_id else parent_span_id
            parent_context = _build_parent_context(trace_id, actual_parent_span_id)

            # 创建 span
            span = tracer.start_span(
                name=span_name,
                context=parent_context,
                start_time=start_time_ns,
                kind=SpanKind.INTERNAL,
            )

            # 设置属性
            span.set_attribute(f"{platform_code}.plugin.method", method_name)
            for key, value in attributes.items():
                if value is not None:
                    span.set_attribute(f"{platform_code}.plugin.{key}", str(value))

            # 设置执行结果状态
            if result.success:
                span.set_status(Status(StatusCode.OK))
                span.set_attribute(f"{platform_code}.plugin.success", True)
            else:
                span.set_status(Status(StatusCode.ERROR, result.error_message or f"{method_name} failed"))
                span.set_attribute(f"{platform_code}.plugin.success", False)
                if result.error_message:
                    span.set_attribute(f"{platform_code}.plugin.error", str(result.error_message)[:1000])

            # 结束 span
            span.end(end_time=end_time_ns)
        except Exception as e:
            logger.debug(f"[plugin_span] Failed to create method span: {e}")
