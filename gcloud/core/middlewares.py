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
import ujson as json

import pytz
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.db.models import ObjectDoesNotExist

from gcloud.core.models import Project

logger = logging.getLogger("root")


class GCloudPermissionMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        If a request path contains project_id parameter, check whether project exist
        """
        if getattr(view_func, 'login_exempt', False):
            return None
        project_id = view_kwargs.get('project_id')
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return HttpResponseBadRequest(content='project does not exist.')

            # set time_zone of business
            request.session['blueking_timezone'] = project.time_zone

    def _get_biz_cc_id_in_rest_request(self, request):
        biz_cc_id = None
        try:
            body = json.loads(request.body)
            biz_cc_id = int(body.get('business').split('/')[-2])
        except Exception:
            pass
        return biz_cc_id


class UnauthorizedMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def process_response(self, request, response):
        # 403: PaaS 平台用来控制应用白名单和 IP 白名单
        # 405: 用户无当前业务或者数据的查询/操作权限
        if response.status_code in (403,):
            response = HttpResponse(
                content=_(u"您没有权限进行此操作"),
                status=405
            )
        return response


class TimezoneMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def process_view(self, request, view_func, view_args, view_kwargs):
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
