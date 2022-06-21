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

from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django_prometheus.exports import ExportToDjangoView

from blueapps.account.decorators import login_exempt
from blueapps.account.middlewares import LoginRequiredMiddleware
from gcloud.core.signals import user_enter
from gcloud.conf import settings

logger = logging.getLogger("root")


def page_not_found(request, exception):
    if request.path.startswith(settings.STATIC_URL):
        return HttpResponseNotFound()

    user = LoginRequiredMiddleware().authenticate(request)

    # 未登录重定向到首页，跳到登录页面
    if not user:
        refer_url = quote(request.build_absolute_uri())
        return HttpResponseRedirect(settings.SITE_URL + "?{}={}".format(settings.PAGE_NOT_FOUND_URL_KEY, refer_url))
    request.user = user
    # not home url enter
    user_enter.send(username=user.username, sender=user.username)
    return render(request, "core/base_vue.html", {})


def home(request):
    try:
        username = request.user.username
        # home url enter
        user_enter.send(username=username, sender=username)
    except Exception:
        logger.exception("user_enter signal send failed.")
    return render(request, "core/base_vue.html")


@login_exempt
def metrics(request):
    return ExportToDjangoView(request)
