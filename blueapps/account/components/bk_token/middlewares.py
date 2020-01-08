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

import logging

from django.conf import settings
from django.contrib import auth

try:
    from django.utils.deprecation import MiddlewareMixin
except Exception:
    MiddlewareMixin = object

from blueapps.account.conf import ConfFixture
from blueapps.account.handlers.response import ResponseHandler
from blueapps.account.components.bk_token.forms import AuthenticationForm

logger = logging.getLogger('component')


class LoginRequiredMiddleware(MiddlewareMixin):
    def process_view(self, request, view, args, kwargs):
        """
        Login paas by two ways
        1. views decorated with 'login_exempt' keyword
        2. User has logged in calling auth.login
        """
        if hasattr(request, 'is_wechat') and request.is_wechat():
            return None

        if getattr(view, 'login_exempt', False):
            return None

        user = LoginRequiredMiddleware.authenticate(request)
        if user:
            return None

        handler = ResponseHandler(ConfFixture, settings)
        return handler.build_401_response(request)

    def process_response(self, request, response):
        return response

    @staticmethod
    def authenticate(request):
        form = AuthenticationForm(request.COOKIES)
        if not form.is_valid():
            return None

        bk_token = form.cleaned_data['bk_token']
        # 确认 cookie 中的 bk_token 和 session 中的是否一致
        # 如果登出删除 cookie 后 session 存在 is_match 为False
        is_match = (bk_token == request.session.get('bk_token'))
        if is_match and request.user.is_authenticated:
            return request.user

        user = auth.authenticate(request=request,
                                 bk_token=bk_token)
        if user:
            # 登录成功，记录 user 信息
            auth.login(request, user)
            request.session['bk_token'] = bk_token
        return user
