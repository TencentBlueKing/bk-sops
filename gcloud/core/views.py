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

import logging
from urllib.parse import quote

from blueapps.account import ConfFixture
from blueapps.account.decorators import login_exempt
from blueapps.account.handlers.response import ResponseHandler
from blueapps.account.middlewares import LoginRequiredMiddleware
from django.contrib.auth import logout
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.middleware.csrf import rotate_token
from django.shortcuts import render
from django_prometheus.exports import ExportToDjangoView

from gcloud.conf import settings
from gcloud.core.signals import user_enter

logger = logging.getLogger("root")


def page_not_found(request, exception):
    if request.path.startswith(settings.STATIC_URL):
        return HttpResponseNotFound()

    user = LoginRequiredMiddleware().authenticate(request)

    if user:
        request.user = user
        rotate_token(request)
        # not home url enter
        user_enter.send(username=user.username, sender=user.username)
        return render(request, "core/base_vue.html", {})

    # 未登录重定向到首页，跳到登录页面
    if hasattr(LoginRequiredMiddleware(), "is_user_forbidden"):
        user_forbidden, msg = LoginRequiredMiddleware().is_user_forbidden(request)
        if user_forbidden:
            handler = ResponseHandler(ConfFixture, settings)
            return handler.build_403_response(msg)
    refer_url = quote(request.build_absolute_uri())
    return HttpResponseRedirect(settings.SITE_URL + "?{}={}".format(settings.PAGE_NOT_FOUND_URL_KEY, refer_url))


def home(request):
    try:
        username = request.user.username
        # home url enter
        user_enter.send(username=username, sender=username)
    except Exception:
        logger.exception("user_enter signal send failed.")
    return render(request, "core/base_vue.html")


def user_exit(request):
    logout(request)
    # 验证不通过，需要跳转至统一登录平台
    request.path = request.path.replace("logout", "")
    handler = ResponseHandler(ConfFixture, settings)
    return handler.build_401_response(request)


@login_exempt
def metrics(request):
    return ExportToDjangoView(request)
