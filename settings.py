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

请不要修改该文件
如果你需要对settings里的内容做修改，config/default.py 文件中 添加即可
如有任何疑问，请联系 【蓝鲸助手】
"""

import os

# V3判断环境的环境变量为BKPAAS_ENVIRONMENT
if 'BKPAAS_ENVIRONMENT' in os.environ:
    ENVIRONMENT = os.getenv('BKPAAS_ENVIRONMENT', 'dev')
# V2判断环境的环境变量为BK_ENV
else:
    PAAS_V2_ENVIRONMENT = os.environ.get('BK_ENV', 'development')
    ENVIRONMENT = {
        'development': 'dev',
        'testing': 'stag',
        'production': 'prod',
    }.get(PAAS_V2_ENVIRONMENT)
DJANGO_CONF_MODULE = 'config.{env}'.format(env=ENVIRONMENT)

try:
    _module = __import__(DJANGO_CONF_MODULE, globals(), locals(), ['*'])
except ImportError as e:
    raise ImportError("Could not import config '%s' (Is it on sys.path?): %s"
                      % (DJANGO_CONF_MODULE, e))

for _setting in dir(_module):
    if _setting == _setting.upper():
        locals()[_setting] = getattr(_module, _setting)

# celery settings

IS_USE_CELERY = locals().get('IS_USE_CELERY', [])
if IS_USE_CELERY:
    INSTALLED_APPS = locals().get('INSTALLED_APPS', [])
    import djcelery

    INSTALLED_APPS += (
        'djcelery',
    )
    djcelery.setup_loader()
    CELERY_ENABLE_UTC = False
    CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

# remove disabled apps

if 'DISABLED_APPS' in locals():
    INSTALLED_APPS = locals().get('INSTALLED_APPS', [])
    DISABLED_APPS = locals().get('DISABLED_APPS', [])

    INSTALLED_APPS = [_app for _app in INSTALLED_APPS
                      if _app not in DISABLED_APPS]

    _keys = ('AUTHENTICATION_BACKENDS',
             'DATABASE_ROUTERS',
             'FILE_UPLOAD_HANDLERS',
             'MIDDLEWARE',
             'PASSWORD_HASHERS',
             'TEMPLATE_LOADERS',
             'STATICFILES_FINDERS',
             'TEMPLATE_CONTEXT_PROCESSORS')

    import itertools

    for _app, _key in itertools.product(DISABLED_APPS, _keys):
        locals()[_key] = tuple([_item for _item in locals()[_key]
                                if not _item.startswith(_app + '.')])
