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

import os

from django.conf import settings

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace.sampling import _KNOWN_SAMPLERS
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from blueapps.opentelemetry.instrumentor import BKAppInstrumentor


def setup_trace_config():
    if settings.ENVIRONMENT == "dev":
        # local environment, use jaeger as trace service
        # docker run -p 16686:16686 -p 6831:6831/udp jaegertracing/all-in-one
        trace.set_tracer_provider(
            TracerProvider(
                resource=Resource.create({SERVICE_NAME: os.getenv("BKAPP_OTEL_SERVICE_NAME") or settings.APP_CODE})
            )
        )
        jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831, udp_split_oversized_batches=True)
        trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))
    else:
        # stage and prod environment, use bk_log as trace service
        trace.set_tracer_provider(
            tracer_provider=TracerProvider(
                resource=Resource.create(
                    {
                        "service.name": os.getenv("BKAPP_OTEL_SERVICE_NAME") or settings.APP_CODE,
                        "bk_data_id": int(os.getenv("BKAPP_OTEL_BK_DATA_ID")),
                    },
                ),
                sampler=_KNOWN_SAMPLERS[os.getenv("BKAPP_OTEL_SAMPLER", "parentbased_always_off")],
            )
        )
        otlp_exporter = OTLPSpanExporter(endpoint=os.getenv("BKAPP_OTEL_GRPC_HOST"))
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)


def setup_by_settings():
    if getattr(settings, "ENABLE_OTEL_TRACE", False):
        setup_trace_config()
        BKAppInstrumentor().instrument()
