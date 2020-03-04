# -*- coding: utf-8 -*-
from django.conf import settings

from blueapps.account.utils import load_backend
from blueapps.account.conf import ConfFixture, AUTH_USER_MODEL


def get_user_model():
    """
    返回平台对应版本 User Proxy Model
    """
    return load_backend(ConfFixture.USER_MODEL)


def get_bk_login_ticket(request):
    form_cls = 'AuthenticationForm'
    context = [request.COOKIES, request.GET]

    if request.is_rio():
        form_cls = 'RioAuthenticationForm'
        context.insert(0, request.META)

    elif request.is_wechat():
        form_cls = 'WeixinAuthenticationForm'

    AuthenticationForm = load_backend("forms.{}".format(form_cls))

    for form in (AuthenticationForm(c) for c in context):
        if form.is_valid():
            return form.cleaned_data

    return {}


if AUTH_USER_MODEL == settings.AUTH_USER_MODEL:
    from django.contrib import auth
    auth.get_user_model = get_user_model

default_app_config = 'blueapps.account.apps.AccountConfig'
