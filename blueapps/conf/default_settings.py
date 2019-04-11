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

from __future__ import absolute_import

import re

from blueapps.conf.environ import *  # noqa
from blueapps.conf.database import get_default_database_config_dict

ROOT_URLCONF = 'urls'

SITE_ID = 1

INSTALLED_APPS = (
    'bkoauth',
    # 框架自定义命令
    'blueapps.contrib.bk_commands',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # account app
    'blueapps.account',
)

MIDDLEWARE = (
    # request instance provider
    'blueapps.middleware.request_provider.RequestProvider',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 跨域检测中间件， 默认关闭
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # 蓝鲸静态资源服务
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # Auth middleware
    'blueapps.account.middlewares.RioLoginRequiredMiddleware',
    'blueapps.account.middlewares.WeixinLoginRequiredMiddleware',
    'blueapps.account.middlewares.LoginRequiredMiddleware',
    # exception middleware
    'blueapps.core.exceptions.middleware.AppExceptionMiddleware'
)

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
try:
    import pymysql

    pymysql.install_as_MySQLdb()
    # Patch version info to forcely pass Django client check
    setattr(pymysql, 'version_info', (1, 2, 6, "final", 0))
except ImportError as e:
    raise ImportError("PyMySQL is not installed: %s" % e)

DATABASES = {
    'default': get_default_database_config_dict(locals())
}

# Cache

CACHES = {
    'db': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache',
    },
    'dummy': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'locmem': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

CACHES['default'] = CACHES['dummy']

# Template

MAKO_DIR_NAME = 'mako_templates'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (
            os.path.join(BASE_DIR, 'templates'),
        ),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blueapps.template.context_processors.blue_settings'
            ],
        },
    },
    {
        'BACKEND': 'blueapps.template.backends.mako.MakoTemplates',
        'DIRS': (
            os.path.join(BASE_DIR, MAKO_DIR_NAME),
        ),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blueapps.template.context_processors.blue_settings'
            ],
            # mako templates cache, None means not using cache
            'module_directory': os.path.join(os.path.dirname(BASE_DIR),
                                             'templates_module', APP_CODE)
        },
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

ALLOWED_HOSTS = ['*']
TIME_ZONE = 'Asia/Shanghai'
LANGUAGE_CODE = 'zh-hans'
USE_I18N = True
USE_L10N = True

# Authentication & Authorization

SESSION_COOKIE_AGE = 60
AUTH_USER_MODEL = 'account.User'

AUTHENTICATION_BACKENDS = (
    'blueapps.account.backends.WeixinBackend',
    'blueapps.account.backends.UserBackend',
)

RE_MOBILE = re.compile(r'Mobile|Android|iPhone|iPad|iPod', re.IGNORECASE)
RE_WECHAT = re.compile(r'MicroMessenger', re.IGNORECASE)

# CSRF Config
CSRF_COOKIE_NAME = APP_CODE + '_csrftoken'
