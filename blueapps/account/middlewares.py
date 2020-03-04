# -*- coding: utf-8 -*-
from django.utils.module_loading import import_string

from blueapps.account.conf import ConfFixture


def load_middleware(middleware):
    path = 'blueapps.account.components.{middleware}'.format(
        middleware=middleware)
    return import_string(path)


if hasattr(ConfFixture, 'LOGIN_REQUIRED_MIDDLEWARE'):
    LoginRequiredMiddleware = load_middleware(
        ConfFixture.LOGIN_REQUIRED_MIDDLEWARE)

if hasattr(ConfFixture, 'WEIXIN_MIDDLEWARE'):
    WeixinLoginRequiredMiddleware = load_middleware(
        ConfFixture.WEIXIN_MIDDLEWARE)

if hasattr(ConfFixture, 'RIO_MIDDLEWARE'):
    RioLoginRequiredMiddleware = load_middleware(
        ConfFixture.RIO_MIDDLEWARE)

if hasattr(ConfFixture, 'BK_JWT_MIDDLEWARE'):
    BkJwtLoginRequiredMiddleware = load_middleware(
        ConfFixture.BK_JWT_MIDDLEWARE)
