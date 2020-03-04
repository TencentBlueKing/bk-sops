# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.urls import resolve
from django.conf import settings


class BkuiPageMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # 判断是否发生404的问题，及BKUI的
        if response.status_code == 404 and settings.IS_BKUI_HISTORY_MODE:
            home_view_func = resolve('/')
            return home_view_func.func(request)

        return response
