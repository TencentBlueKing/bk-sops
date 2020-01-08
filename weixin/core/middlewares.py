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

from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser

from blueapps.account.models import UserProperty
from blueapps.account import get_user_model

from . import settings
from .accounts import WeixinAccount
from .models import BkWeixinUser, WeixinUserSession

logger = logging.getLogger('root')


def get_user(request):
    user = None
    session_key = request.COOKIES.get('weixin_user_session')
    if session_key:
        checked_user_id = WeixinUserSession.objects.check_session_key(session_key)
        if checked_user_id is False:
            logger.error("weixin user[session_key=%s] login status is expired" % session_key)
        try:
            user = BkWeixinUser.objects.get(userid=checked_user_id)
        except BkWeixinUser.DoesNotExist:
            logger.error("weixin user[user_id=%s] does not exist" % checked_user_id)
    return user or AnonymousUser()


def get_bk_user(request):
    bkuser = None
    if request.weixin_user and not isinstance(request.weixin_user, AnonymousUser):
        user_model = get_user_model()
        try:
            user_property = UserProperty.objects.get(key='wx_userid', value=request.weixin_user.userid)
        except UserProperty.DoesNotExist:
            logger.warning('user[wx_userid=%s] not in UserProperty' % request.weixin_user.userid)
        else:
            bkuser = user_model.objects.get(username=user_property.user.username)
    return bkuser or AnonymousUser()


class WeixinProxyPatchMiddleware(MiddlewareMixin):
    """
    该中间件需要被放置在所有中间件之前
    解决多级Nginx代理下原始来源Host(`X-Forwarded-Host`)被下层Nginx覆盖的问题
    解决方式：单独设置一个Header，本中间件进行覆盖替换`X-Forwarded-Host`

    # django 获取Host方式
    # django.http.request +73
    def get_host(self):
        '''Returns the HTTP host using the environment or request headers.'''
        # We try three options, in order of decreasing preference.
        if settings.USE_X_FORWARDED_HOST and (
                'HTTP_X_FORWARDED_HOST' in self.META):
            host = self.META['HTTP_X_FORWARDED_HOST']
            ...
    """
    def process_request(self, request):
        if settings.USE_WEIXIN and settings.X_FORWARDED_WEIXIN_HOST in request.META:
            # patch X-Forwaded-Host header
            request.META["HTTP_X_FORWARDED_HOST"] = request.META.get(settings.X_FORWARDED_WEIXIN_HOST)


class WeixinAuthenticationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Weixin authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE_CLASSES setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'weixin.core.middleware.WeixinAuthenticationMiddleware'."
        )
        setattr(request, 'weixin_user', SimpleLazyObject(lambda: get_user(request)))
        setattr(request, 'user', SimpleLazyObject(lambda: get_bk_user(request)))

    def process_response(self, request, response):
        """
        @summary: 移动端设置 weixin_user_session 到 cookies 中，避免 SESSION_COOKIE_AGE 时间太短导致 session 过期
        @param request:
        @param response:
        @return:
        """
        if request.session.get('weixin_user_session'):
            response.set_cookie('weixin_user_session', request.session['weixin_user_session'])
        return response


class WeixinLoginMiddleware(MiddlewareMixin):
    """weixin Login middleware."""

    def process_view(self, request, view, args, kwargs):
        """process_view."""
        weixin_account = WeixinAccount()
        # 非微信路径不验证
        if not weixin_account.is_weixin_visit(request):
            return None

        # 豁免微信登录装饰器
        if getattr(view, 'weixin_login_exempt', False):
            return None

        # 验证OK
        if request.weixin_user.is_authenticated():
            return None

        # 微信登录失效或者未通过验证，直接重定向到微信登录
        return weixin_account.redirect_weixin_login(request)
