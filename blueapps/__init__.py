# -*- coding: utf-8 -*-
VERSION = '2.5.1'
__version__ = VERSION


RUN_VER = ""


def get_run_ver():
    from django.conf import settings
    try:
        return settings.RUN_VER
    except AttributeError:
        return RUN_VER
