# -*- coding: utf-8 -*-
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

        if hasattr(request, 'is_bk_jwt') and request.is_bk_jwt():
            return None

        if getattr(view, 'login_exempt', False):
            return None

        form = AuthenticationForm(request.COOKIES)
        if form.is_valid():
            bk_token = form.cleaned_data['bk_token']
            user = auth.authenticate(request=request, bk_token=bk_token)
            if user:
                # Succeed to login, recall self to exit process
                if user.username != request.user.username:
                    auth.login(request, user)
                return None
        handler = ResponseHandler(ConfFixture, settings)
        return handler.build_401_response(request)

    def process_response(self, request, response):
        return response
