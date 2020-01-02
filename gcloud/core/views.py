# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import datetime
import logging

import ujson as json
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)
from django.utils.translation import check_for_language
from django.shortcuts import render

from blueapps.account.middlewares import LoginRequiredMiddleware

from gcloud import exceptions
from gcloud.conf import settings
from gcloud.core.models import UserBusiness
from gcloud.core.api_adapter import is_user_functor, is_user_auditor
from gcloud.core.utils import prepare_user_business

logger = logging.getLogger("root")


def page_not_found(request):
    user = LoginRequiredMiddleware.authenticate(request)
    # 未登录重定向到首页，跳到登录页面
    if not user:
        return HttpResponseRedirect(settings.SITE_URL)
    request.user = user
    return render(request, 'core/base_vue.html', {})


def home(request):
    username = request.user.username
    if is_user_functor(request):
        return HttpResponseRedirect(settings.SITE_URL + 'function/home/')
    if is_user_auditor(request):
        return HttpResponseRedirect(settings.SITE_URL + 'audit/home/')
    try:
        biz_list = prepare_user_business(request)
    except exceptions.Unauthorized:
        return HttpResponseRedirect(settings.SITE_URL + 'error/401/')
    except exceptions.Forbidden:
        return HttpResponseRedirect(settings.SITE_URL + 'error/403/')
    except exceptions.APIError as e:
        ctx = {
            'system': e.system,
            'api': e.api,
            'message': e.message,
        }
        logger.error(json.dumps(ctx))
        return HttpResponse(status=503, content=json.dumps(ctx))
    if biz_list:
        try:
            obj = UserBusiness.objects.get(user=username)
            biz_cc_id = obj.default_buss
            biz_cc_id_list = [item.cc_id for item in biz_list]
            if biz_cc_id not in set(biz_cc_id_list):
                biz_cc_id = biz_cc_id_list[0]
                obj.default_buss = biz_cc_id
                obj.save()
        except UserBusiness.DoesNotExist:
            biz_cc_id = biz_list[0].cc_id
            UserBusiness.objects.create(user=username, default_buss=biz_cc_id)
        return HttpResponseRedirect(settings.SITE_URL + 'business/home/' + str(biz_cc_id) + '/')
    else:
        return HttpResponseRedirect(settings.SITE_URL + 'error/406/')


def biz_home(request, biz_cc_id):
    """
    @note: only use to authentication
    @param request:
    @param biz_cc_id:
    @return:
    """
    ctx = {
        'biz_cc_id': biz_cc_id
    }
    return render(request, 'core/base_vue.html', ctx)


def set_language(request):
    next = None
    if request.method == 'GET':
        next = request.GET.get('next', None)
    elif request.method == 'POST':
        next = request.POST.get('next', None)

    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = HttpResponseRedirect(next)

    if request.method == 'GET':
        lang_code = request.GET.get('language', None)
        if lang_code and check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session["blueking_language"] = lang_code
            max_age = 60 * 60 * 24 * 365
            expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                                 "%a, %d-%b-%Y %H:%M:%S GMT")
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code, max_age, expires)
    return response
