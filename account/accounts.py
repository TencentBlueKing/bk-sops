# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
账号体系相关的基类Account.
"""
from django.conf import settings
from django.contrib.auth import logout as auth_logout, get_user_model
from django.contrib.auth.views import redirect_to_login
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.six.moves.urllib.parse import urlparse
from django.utils.translation import ugettext as _

from common.log import logger
from common.mymako import render_mako_context
from account.http import http_get
from conf import settings_custom

CACHE_PREFIX = __name__.replace('.', '_')
DEFAULT_CACHE_TIME_FOR_USER_UPDATE = settings_custom.DEFAULT_CACHE_TIME_FOR_USER_UPDATE


class AccountSingleton(object):
    """
    单例基类.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class Account(AccountSingleton):
    """
    账号体系相关的基类Account.
    提供通用的账号功能
    """

    # 平台验证用户登录态接口
    BK_LOGIN_VERIFY_URL = "%s/login/accounts/is_login/" % settings.BK_PAAS_INNER_HOST
    # 平台获取用户信息接口
    BK_GET_USER_INFO_URL = "%s/login/accounts/get_user/" % settings.BK_PAAS_INNER_HOST

    def is_bk_token_valid(self, request):
        """验证用户登录态."""
        bk_token = request.COOKIES.get(settings.BK_COOKIE_NAME, None)
        if not bk_token:
            return False, None
        ret, data = self.verify_bk_login(bk_token)
        # bk_token 无效
        if not ret:
            return False, None
        # 检查用户是否存在用户表中
        username = data.get('username', '')
        user_model = get_user_model()
        try:
            user = user_model._default_manager.get_by_natural_key(username)
        except user_model.DoesNotExist:
            user = user_model.objects.create_user(username)
        finally:
            try:
                if not cache.get('update_%s' % username):
                    ret, data = self.get_bk_user_info(bk_token)
                    # 若获取用户信息失败，则用户可登录，但用户其他信息为空
                    user.chname = data.get('chname', '')
                    user.company = data.get('company', '')
                    user.qq = data.get('qq', '')
                    user.phone = data.get('phone', '')
                    user.email = data.get('email', '')
                    user.auth_token = bk_token
                    # 用户权限更新,保持与平台同步
                    role = data.get('role', '')
                    is_admin = True if role == '1' else False
                    user.is_superuser = is_admin
                    user.is_staff = is_admin
                    user.save()
                    cache.set('update_%s' % username, True, DEFAULT_CACHE_TIME_FOR_USER_UPDATE)
            except Exception as e:
                logger.error(_(u"获取记录用户信息失败：%s") % e)
        return True, user

    def verify_bk_login(self, bk_token, use_cache=True):
        """请求平台接口验证登录是否失效"""
        CACHE_KEY = "%s_verify_bk_login_%s" % (CACHE_PREFIX, bk_token)
        data = cache.get(CACHE_KEY)

        if not (use_cache and data):
            param = {'bk_token': bk_token}
            result, resp = http_get(self.BK_LOGIN_VERIFY_URL, param)
            resp = resp if result and resp else {}
            ret = resp.get('result', False)
            # 验证失败
            if ret:
                data = True, resp.get('data', {})
            else:
                data = False, {}
                logger.info(_(u"验证用户登录token无效：%s") % resp.get('message', ''))

            cache.set(CACHE_KEY, data, 15)

        return data

    def get_bk_user_info(self, bk_token, use_cache=True):
        """请求平台接口获取用户信息"""
        CACHE_KEY = "%s_get_bk_user_info_%s" % (CACHE_PREFIX, bk_token)
        data = cache.get(CACHE_KEY)

        if not (use_cache and data):
            param = {'bk_token': bk_token}
            result, resp = http_get(self.BK_GET_USER_INFO_URL, param)
            resp = resp if result and resp else {}
            ret = resp.get('result', False) if result and resp else False
            # 获取用户信息失败
            if ret:
                data = True, resp.get('data', {})
            else:
                data = False, {}
                logger.error(_(u"请求平台接口获取用户信息失败：%s") % resp.get('message', ''))

            cache.set(CACHE_KEY, data, 15)

        return data

    def build_callback_url(self, request, jumpUrl):
        callback = request.build_absolute_uri()
        login_scheme, login_netloc = urlparse(jumpUrl)[:2]
        current_scheme, current_netloc = urlparse(callback)[:2]
        if ((not login_scheme or login_scheme == current_scheme) and
                (not login_netloc or login_netloc == current_netloc)):
            callback = request.get_full_path()
        return callback

    def _redirect_login(self, request, is_login=True):
        """
        跳转平台进行登录
        """
        if is_login:
            # 登录
            callback = self.build_callback_url(request, settings.LOGIN_URL)
        else:
            # 登出
            callback = self.http_referer(request)

        return redirect_to_login(callback, settings.LOGIN_URL, settings.REDIRECT_FIELD_NAME)

    def redirect_login(self, request):
        """
        重定向到登录页面.
        登录态验证不通过时调用
        """
        # ajax跳401
        if request.is_ajax():
            return self._redirect_401(request)
        # 非ajax请求 跳转至平台登录
        return self._redirect_login(request)

    def _redirect_401(self, request, is_login=True):
        """
        @summary: 跳转到登录弹窗
        @note: 适用场景为 1. Ajax登录失败
        """
        return HttpResponse(status=401, content=settings.LOGIN_URL)

    def http_referer(self, request):
        """
        获取 HTTP_REFERER 头，得到登出后要重新登录跳转的url
        """
        if 'HTTP_REFERER' in request.META:
            http_referer = request.META['HTTP_REFERER']
        else:
            http_referer = settings.LOGIN_REDIRECT_URL
        return http_referer

    def logout(self, request):
        """登出并重定向到登录页面."""
        auth_logout(request)
        return self._redirect_login(request, False)

    def check_failed(self, request):
        """功能开关检查失败"""
        code = request.GET.get('code', '')
        # 功能开关检查失败的提示页面
        if code == 'func_check':
            res_page = '/account/func_check_failed.html'
        else:
            res_page = '/403.html'
        return render_mako_context(request, res_page)
