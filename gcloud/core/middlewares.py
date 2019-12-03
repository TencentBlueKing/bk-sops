# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import traceback

import pytz
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.db.models import ObjectDoesNotExist

from gcloud.core.models import Project

logger = logging.getLogger("root")


class TimezoneMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        project_id = view_kwargs.get('project_id')
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return HttpResponseBadRequest(content='project does not exist.')

            # set time_zone of business
            request.session['blueking_timezone'] = project.time_zone

        tzname = request.session.get('blueking_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()


class ObjectDoesNotExistExceptionMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        if isinstance(exception, ObjectDoesNotExist):
            logger.error(traceback.format_exc())
            return JsonResponse({
                'result': False,
                'message': 'Object not found: %s' % exception.message
            })
