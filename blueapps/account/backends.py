# -*- coding: utf-8 -*-
from blueapps.account.conf import ConfFixture
from blueapps.account.utils import load_backend

if hasattr(ConfFixture, 'USER_BACKEND'):
    UserBackend = load_backend(ConfFixture.USER_BACKEND)

if hasattr(ConfFixture, 'WEIXIN_BACKEND'):
    WeixinBackend = load_backend(ConfFixture.WEIXIN_BACKEND)

if hasattr(ConfFixture, 'RIO_BACKEND'):
    RioBackend = load_backend(ConfFixture.RIO_BACKEND)

if hasattr(ConfFixture, 'BK_JWT_BACKEND'):
    BkJwtBackend = load_backend(ConfFixture.BK_JWT_BACKEND)
