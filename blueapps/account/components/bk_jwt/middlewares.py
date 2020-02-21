# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib import auth
from django.utils.deprecation import MiddlewareMixin

from blueapps.account.conf import ConfFixture
from blueapps.account.handlers.response import ResponseHandler

logger = logging.getLogger('component')


class BkJwtLoginRequiredMiddleware(MiddlewareMixin):
    def process_view(self, request, view, args, kwargs):
        """
        可通过登录认证的请求：
        1. 带有BK JWT HEADER
        2. JWT签名正确
        """
        # 框架前置中间件，已将识别的客户端信息填充进 request
        if not hasattr(request, 'is_bk_jwt') or not request.is_bk_jwt():
            return None

        logger.debug('当前请求是否经过JWT转发')
        login_exempt = getattr(view, 'login_exempt', False)

        # 每次请求都需要做校验
        if not (login_exempt or request.user.is_authenticated):
            user = auth.authenticate(request=request)
            if user:
                # 登录成功，确认登陆正常后退出
                auth.login(request, user)
                if request.user.is_authenticated:
                    return None

            handler = ResponseHandler(ConfFixture, settings)
            return handler.build_bk_jwt_401_response(request)
        return None

    def process_response(self, request, response):
        return response
