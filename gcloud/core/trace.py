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
from contextlib import contextmanager
from functools import wraps

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SpanProcessor
from opentelemetry.trace import SpanKind


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


def propagate_attributes(attributes: dict):
    """把attributes设置到span上，并继承到后面所有span

    :param attributes: 默认属性
    """

    provider = trace.get_tracer_provider()

    if not provider or isinstance(provider, trace.ProxyTracerProvider):
        provider = TracerProvider()
        trace.set_tracer_provider(provider)

    # Add a span processor that sets attributes on every new span
    provider.add_span_processor(AttributeInjectionSpanProcessor(attributes))


def append_attributes(attributes: dict):
    """追加属性到span上

    :param attributes: 需要追加的属性
    """
    current_span = trace.get_current_span()
    for key, value in attributes.items():
        current_span.set_attribute(f"bk_sops.{key}", value)


@contextmanager
def start_trace(span_name: str, propagate: bool = False, **attributes):
    """Start a trace

    :param span_name: 自定义Span名称
    :param propagate: 是否需要传播
    :param attributes: 需要跟span增加的属性, 默认为空
    :yield: 当前上下文的Span
    """
    tracer = trace.get_tracer(__name__)

    span_attributes = {f"bk_sops.{key}": value for key, value in attributes.items()}

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
                # 需要的属性只要在kwargs, request.GET, request.POST中就可以
                for scope in (kwargs, request.GET, request.POST):
                    if attr_key in scope:
                        attributes[attr_key] = kwargs[attr_key]
                        break

            with start_trace(view_func.__name__, propagate, **attributes):
                return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
