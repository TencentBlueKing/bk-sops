# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import pkgutil
import sys

from importlib import import_module
from django.utils._os import npath, upath


def autodiscover_items(module):
    """
    Given a path to discover, auto register all items
    """
    # Workaround for a Python 3.2 bug with pkgutil.iter_modules
    module_dir = upath(module.__path__[0])
    sys.path_importer_cache.pop(module_dir, None)
    modules = [name for _, name, is_pkg in
               pkgutil.iter_modules([npath(module_dir)])
               if not is_pkg and not name.startswith('_')]
    for name in modules:
        __import__("%s.%s" % (module.__name__, name))


def autodiscover_collections(path):
    """
    Auto-discover INSTALLED_APPS modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.
    """
    from django.apps import apps

    for app_config in apps.get_app_configs():
        # Attempt to import the app's module.
        try:

            _module = import_module('%s.%s' %
                                    (app_config.name, path))
            autodiscover_items(_module)
        except ImportError as e:
            if not e.message == 'No module named %s' % path:
                pass
