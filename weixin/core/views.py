# -*- coding: utf-8 -*-
from .accounts import WeixinAccount
from .decorators import weixin_login_exempt


@weixin_login_exempt
def login(request):
    """微信登录"""
    return WeixinAccount().login(request)
