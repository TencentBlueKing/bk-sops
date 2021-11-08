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

import logging

from django.conf import settings
from django.contrib import auth
from django.core.cache import caches

from blueapps.account.components.bk_token.forms import AuthenticationForm
from blueapps.account.conf import ConfFixture
from blueapps.account.handlers.response import ResponseHandler

try:
    from django.utils.deprecation import MiddlewareMixin
except Exception:  # pylint: disable=broad-except
    MiddlewareMixin = object


logger = logging.getLogger("component")
cache = caches["login_db"]


class LoginRequiredMiddleware(MiddlewareMixin):
    def process_view(self, request, view, args, kwargs):
        """
        Login paas by two ways
        1. views decorated with 'login_exempt' keyword
        2. User has logged in calling auth.login
        """
        if hasattr(request, "is_wechat") and request.is_wechat():
            return None

        if hasattr(request, "is_bk_jwt") and request.is_bk_jwt():
            return None

        if hasattr(request, "is_rio") and request.is_rio():
            return None

        if getattr(view, "login_exempt", False):
            return None

        # 先做数据清洗再执行逻辑
        form = AuthenticationForm(request.COOKIES)
        if form.is_valid():
            bk_token = form.cleaned_data["bk_token"]
            session_key = request.session.session_key
            if session_key:
                # 确认 cookie 中的 ticket 和 cache 中的是否一致
                cache_session = cache.get(session_key)
                is_match = cache_session and bk_token == cache_session.get("bk_token")
                if is_match and request.user.is_authenticated:
                    return None

            user = auth.authenticate(request=request, bk_token=bk_token)
            if user is not None and user.username != request.user.username:
                auth.login(request, user)

            if user is not None and request.user.is_authenticated:
                # 登录成功，重新调用自身函数，即可退出
                cache.set(
                    session_key, {"bk_token": bk_token}, settings.LOGIN_CACHE_EXPIRED
                )
                return self.process_view(request, view, args, kwargs)

        handler = ResponseHandler(ConfFixture, settings)
        return handler.build_401_response(request)

    def process_response(self, request, response):
        return response
