# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import pytz
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from common.mymako import render_mako_context

from gcloud import exceptions
from gcloud.core.utils import prepare_business


class GCloudPermissionMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        If a request path contains biz_cc_id parameter, check if current
        user has perm view_business or return http 403.
        """
        if getattr(view_func, 'login_exempt', False):
            return None
        biz_cc_id = view_kwargs.get('biz_cc_id')
        if biz_cc_id:
            try:
                business = prepare_business(request, cc_id=biz_cc_id)
            except exceptions.Unauthorized:
                # permission denied for target business (irregular request)
                return HttpResponse(status=401)
            except exceptions.Forbidden:
                # target business does not exist (irregular request)
                return HttpResponseForbidden()
            except exceptions.APIError as e:
                ctx = {
                    'system': e.system,
                    'api': e.api,
                    'message': e.message,
                }
                return render_mako_context(request, '503.html', ctx)

            # set time_zone of business
            if business.time_zone:
                request.session['blueking_timezone'] = business.time_zone

            if not request.user.has_perm('view_business', business):
                return HttpResponseForbidden()


class UnauthorizedMiddleware(object):

    def process_response(self, request, response):
        # 403: PaaS 平台用来控制应用白名单和 IP 白名单
        # 405: 用户无当前业务或者数据的查询/操作权限
        if response.status_code in (403,):
            response = HttpResponse(
                content=_(u"您没有权限进行此操作"),
                status=405
            )
        return response


class TimezoneMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        tzname = request.session.get('blueking_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
