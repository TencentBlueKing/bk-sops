# -*- coding: utf-8 -*-
from functools import wraps


def login_exempt(view_func):
    """"Mark a view function as being exempt from login view protection"""
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    wrapped_view.login_exempt = True
    return wraps(view_func)(wrapped_view)
