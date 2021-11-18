# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json

from typing import Collection

from django.conf import settings

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation import dbapi
from opentelemetry.trace import Span, Status, StatusCode
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


def requests_callback(span: Span, response):
    """
    处理蓝鲸标准协议响应
    """
    try:
        json_result = response.json()
    except Exception:  # pylint: disable=broad-except
        return
    if not isinstance(json_result, dict):
        return
    result = json_result.get("result")
    if result is None:
        return
    span.set_attribute("result_code", json_result.get("code", 0))
    span.set_attribute("blueking_esb_request_id", json_result.get("request_id", ""))
    span.set_attribute("result_message", json_result.get("message", ""))
    span.set_attribute("result_errors", str(json_result.get("errors", "")))
    if result:
        span.set_status(Status(StatusCode.OK))
        return
    span.set_status(Status(StatusCode.ERROR))


def django_response_hook(span, request, response):
    """
    处理蓝鲸标准协议 Django 响应
    """
    if hasattr(response, "data"):
        result = response.data
    else:
        try:
            result = json.loads(response.content)
        except Exception:  # pylint: disable=broad-except
            return
    if not isinstance(result, dict):
        return
    span.set_attribute("result_code", result.get("code", 0))
    span.set_attribute("result_message", result.get("message", ""))
    span.set_attribute("result_errors", result.get("errors", ""))
    result = result.get("result", True)
    if result:
        span.set_status(Status(StatusCode.OK))
        return
    span.set_status(Status(StatusCode.ERROR))


class BKAppInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return []

    def _instrument(self, **kwargs):
        LoggingInstrumentor().instrument()
        RequestsInstrumentor().instrument(span_callback=requests_callback)
        DjangoInstrumentor().instrument(response_hook=django_response_hook)
        CeleryInstrumentor().instrument()
        RedisInstrumentor().instrument()

        for instrumentor in getattr(settings, "BK_APP_OTEL_ADDTIONAL_INSTRUMENTORS", []):
            instrumentor.instrument()

        if getattr(settings, "BK_APP_OTEL_INSTRUMENT_DB_API", False):
            import MySQLdb  # noqa

            dbapi.wrap_connect(
                __name__,
                MySQLdb,
                "connect",
                "mysql",
                {"database": "db", "port": "port", "host": "host", "user": "user",},
            )

    def _uninstrument(self, **kwargs):
        for instrumentor in self.instrumentors:
            instrumentor.uninstrument()
