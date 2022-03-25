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
import uuid
import socket
import logging
import traceback

import pytz
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.db.models import ObjectDoesNotExist
from django_prometheus.middleware import (
    Metrics,
    PrometheusAfterMiddleware,
    PrometheusBeforeMiddleware,
)
from django_prometheus.utils import Time, TimeSince

from gcloud import err_code
from gcloud.core.models import Project
from gcloud.core.logging import local

logger = logging.getLogger("root")


class TimezoneMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        project_id = view_kwargs.get("project_id")
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                logger.error("project[id={project_id}] does not exist".format(project_id=project_id))
                return None

            # set time_zone of business
            request.session["blueking_timezone"] = project.time_zone

        tzname = request.session.get("blueking_timezone")
        if tzname:
            try:
                timezone.activate(pytz.timezone(tzname))
            except Exception as e:
                logger.error(
                    "activate timezone[{blueking_timezone}] raise error[{error}]".format(
                        blueking_timezone=tzname, error=e
                    )
                )
        else:
            timezone.deactivate()


class ObjectDoesNotExistExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, ObjectDoesNotExist):
            logger.error("[ObjectDoesNotExistExceptionMiddleware] {} - {}".format(request.path, traceback.format_exc()))
            return JsonResponse(
                {
                    "result": False,
                    "message": "Object not found: %s" % exception,
                    "data": None,
                    "code": err_code.CONTENT_NOT_EXIST.code,
                }
            )


class TraceIDInjectMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.trace_id = request.META.get("HTTP_TRACEPARENT", uuid.uuid4().hex)
        local.trace_id = request.trace_id

    def process_response(self, request, response):
        delattr(local, "trace_id")
        if (
            isinstance(response, HttpResponse)
            and response.get("Content-Type") == "application/json"
            and hasattr(request, "trace_id")
        ):
            response.setdefault("Sops-Trace-Id", request.trace_id)
        return response


HOSTNAME = socket.gethostname()


class CustomMetics(Metrics):
    def register_metric(self, metric_cls, name, documentation, labelnames=(), **kwargs):
        return super().register_metric(metric_cls, name, documentation, labelnames=[*labelnames, "hostname"], **kwargs)


class AppMetricsBeforeMiddleware(PrometheusBeforeMiddleware):
    metrics_cls = CustomMetics

    def process_request(self, request):
        self.metrics.requests_total.labels(hostname=HOSTNAME).inc()
        request.prometheus_before_middleware_event = Time()

    def process_response(self, request, response):
        self.metrics.responses_total.labels(hostname=HOSTNAME).inc()
        if hasattr(request, "prometheus_before_middleware_event"):
            self.metrics.requests_latency_before.labels(hostname=HOSTNAME).observe(
                TimeSince(request.prometheus_before_middleware_event)
            )
        else:
            self.metrics.requests_unknown_latency_before.labels(hostname=HOSTNAME).inc()
        return response


class AppMetricsAfterMiddleware(PrometheusAfterMiddleware):
    metrics_cls = CustomMetics

    def label_metric(self, metric, request, response=None, **labels):
        labels.update({"hostname": HOSTNAME})
        return super().label_metric(metric, request, response=response, **labels)
