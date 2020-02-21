# -*- coding: utf-8 -*-
import logging
import random
import time

from django.conf import settings
from django.contrib import auth
from django.utils.deprecation import MiddlewareMixin

from blueapps.account.conf import ConfFixture
from blueapps.account.handlers.response import ResponseHandler
from blueapps.account.components.weixin.forms import WeixinAuthenticationForm

logger = logging.getLogger('component')


class WeixinLoginRequiredMiddleware(MiddlewareMixin):
    def process_view(self, request, view, args, kwargs):
        """
        可通过登录认证的方式，仅有两种
        1. 带有 login_exemp 标识的 view 函数
        2. 用户已成功 auth.login
        """
        # 框架前置中间件，已将识别的客户端信息填充进 request
        if not request.is_wechat():
            return None

        logger.debug('当前请求客户端为微信端')
        login_exempt = getattr(view, 'login_exempt', False)
        if not (login_exempt or request.user.is_authenticated):

            form = WeixinAuthenticationForm(request.GET)

            if form.is_valid():
                code = form.cleaned_data['code']
                state = form.cleaned_data['state']
                logger.debug(
                    u"微信请求链接，检测到微信验证码，code：%s，state：%s" % (
                        code,
                        state
                    )
                )

                if self.valid_state(request, state):
                    user = auth.authenticate(request=request, code=code,
                                             is_wechat=True)
                    if user:
                        # 登录成功，重新调用自身函数，即可退出
                        auth.login(request, user)
                        return self.process_view(request, view, args, kwargs)
            else:
                logger.debug(
                    u"微信请求链接，未检测到微信验证码，url：%s，params：%s" % (
                        request.path_info, request.GET)
                )

            self.set_state(request)
            handler = ResponseHandler(ConfFixture, settings)
            return handler.build_weixin_401_response(request)
        return None

    def process_response(self, request, response):
        return response

    def set_state(self, request, length=32):
        """
        生成随机数 state，表示客户端的当前状态，根据 oauth2.0 标准，在请求授权码时需要
        附带上的参数，认证服务器的回应必须一模一样包含这个参数，此处将 state 设置在
        session
        """
        allowed_chars = ('abcdefghijkmnpqrstuvwxyz'
                         'ABCDEFGHIJKLMNPQRSTUVWXYZ'
                         '0123456789')
        state = ''.join(random.choice(allowed_chars)
                        for _ in range(length))
        request.session['WEIXIN_OAUTH_STATE'] = state
        request.session['WEIXIN_OAUTH_STATE_TIMESTAMP'] = time.time()
        return True

    def valid_state(self, request, state, expires_in=60):
        """
        验证微信认证服务器返回的 code & state 是否合法
        """
        raw_state = request.session.get('WEIXIN_OAUTH_STATE')
        raw_timestamp = request.session.get('WEIXIN_OAUTH_STATE_TIMESTAMP')

        if not raw_state or raw_state != state:
            logger.warning(
                (u"验证 WEIXIN 服务器返回信息，state 不一致，"
                 u"WEIXIN_OAUTH_STATE=%s，state=%s") % (
                    raw_state, state
                )
            )
            return False

        if not raw_timestamp or time.time() - raw_timestamp > expires_in:
            logger.warning(
                (u"验证 WEIXIN 服务器返回信息，state 过期，"
                 u"WEIXIN_OAUTH_STATE_TIMESTAMP=%s") % (
                    raw_timestamp
                )
            )
            return False

        request.session['WEIXIN_OAUTH_STATE'] = None
        request.session['WEIXIN_OAUTH_STATE_TIMESTAMP'] = None
        return True
