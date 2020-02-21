# -*- coding: utf-8 -*-
from django.utils.deprecation import MiddlewareMixin


class NullMiddleware(MiddlewareMixin):
    pass


class NullBackend(object):

    def authenticate(self, **kwargs):
        return None
