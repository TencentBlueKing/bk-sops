# -*- coding: utf-8 -*-
"""
@created: 2017/6/7
@desc:
"""
from django.conf import settings
from django.core.management import execute_from_command_line


def bk_admin(argv=None):
    if not settings.configured:
        settings.configure()
    settings.INSTALLED_APPS += ("blueapps.contrib.bk_commands",)
    return execute_from_command_line(argv)
