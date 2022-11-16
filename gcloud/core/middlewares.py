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
import os
import uuid
import logging
import traceback

import pytz
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.db.models import ObjectDoesNotExist

from gcloud import err_code
from gcloud.core.models import Project
from gcloud.core.logging import local
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger("root")


class TimezoneMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if getattr(view_func, "login_exempt", False):
            return None

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
            message = _(f"数据不存在错误: 数据不存在错误, 错误内容 {exception} | process_exception")
            logger.error(message)
            return JsonResponse(
                {
                    "result": False,
                    "message": message,
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


class HttpResponseIndexRedirect(HttpResponseRedirect):
    def __init__(self, redirect_to, *args, **kwargs):
        super(HttpResponseIndexRedirect, self).__init__(redirect_to, *args, **kwargs)
        self["Location"] = os.path.join(settings.DEFAULT_REDIRECT_HOST, redirect_to.lstrip("/"))


class HttpRedirectMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not settings.NEED_HTTP_REDIRECT:
            return None

        absolute_uri = request.build_absolute_uri()
        if any([host in absolute_uri for host in settings.NOT_REDIRECT_HOSTS]):
            return None

        if not any([host in absolute_uri for host in settings.REDIRECT_HOSTS]):
            return None

        if settings.DEFAULT_REDIRECT_HOST and settings.DEFAULT_REDIRECT_HOST not in absolute_uri:
            return HttpResponseIndexRedirect(request.get_full_path())
