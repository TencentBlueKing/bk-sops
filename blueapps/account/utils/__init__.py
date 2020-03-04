# -*- coding: utf-8 -*-
from django.utils.module_loading import import_string


def load_backend(backend):
    path = 'blueapps.account.components.{backend}'.format(backend=backend)
    return import_string(path)
