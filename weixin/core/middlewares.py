# -*- coding: utf-8 -*-
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser

from .accounts import WeixinAccount
from .models import BkWeixinUser


def get_user(request):
    user = None
    user_id = request.session.get('weixin_user_id')
    if user_id:
        try:
            user = BkWeixinUser.objects.get(pk=user_id)
        except BkWeixinUser.DoesNotExist:
            user = None
    return user or AnonymousUser()


class WeixinAuthenticationMiddleware(object):

    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Weixin authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE_CLASSES setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'weixin.core.middleware.WeixinAuthenticationMiddleware'."
        )
        setattr(request, 'weixin_user', SimpleLazyObject(lambda: get_user(request)))


class WeixinLoginMiddleware(object):
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
