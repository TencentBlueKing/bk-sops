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

from django.contrib import auth
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.utils.translation import check_for_language
from django.shortcuts import render

from blueapps.account.components.bk_token.forms import AuthenticationForm
from gcloud.core.signals import user_enter
from gcloud.conf import settings

logger = logging.getLogger("root")


def page_not_found(request, exception):
    if request.is_ajax() or request.path.startswith(settings.STATIC_URL):
        return HttpResponseNotFound()

    user = _user_authenticate(request)

    # 未登录重定向到首页，跳到登录页面
    if not user:
        return HttpResponseRedirect(
            settings.SITE_URL + "?{}={}".format(settings.PAGE_NOT_FOUND_URL_KEY, request.build_absolute_uri())
        )
    request.user = user
    return render(request, "core/base_vue.html", {})


def _user_authenticate(request):
    # 先做数据清洗再执行逻辑
    form = AuthenticationForm(request.COOKIES)
    if not form.is_valid():
        return None

    bk_token = form.cleaned_data["bk_token"]
    # 确认 cookie 中的 bk_token 和 session 中的是否一致
    # 如果登出删除 cookie 后 session 存在 is_match 为False
    is_match = bk_token == request.session.get("bk_token")
    if is_match and request.user.is_authenticated:
        return request.user

    user = auth.authenticate(request=request, bk_token=bk_token)
    if user:
        # 登录成功，记录 user 信息
        auth.login(request, user)
        request.session["bk_token"] = bk_token
    return user


def home(request):
    try:
        username = request.user.username
        user_enter.send(username=username, sender=username)
    except Exception:
        logger.exception("user_enter signal send failed.")
    return render(request, "core/base_vue.html")


def set_language(request):
    request_params = getattr(request, request.method)
    next_url = request_params.get("next", None) or request.META.get("HTTP_REFERER", "/")
    response = HttpResponseRedirect(next_url)

    if request.method == "GET":
        lang_code = request.GET.get("language", None)
        if lang_code and check_for_language(lang_code):
            if hasattr(request, "session"):
                request.session["blueking_language"] = lang_code
            max_age = 60 * 60 * 24 * 365
            expires = datetime.datetime.strftime(
                datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT",
            )
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code, max_age, expires)
    return response
