# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import os
import sys
import time

from django.conf.global_settings import *
from conf.settings_custom import *

RUN_VER = 'community'

# ==============================================================================
# 应用基本信息配置 (请按照说明修改)
# ==============================================================================
# 在蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 中获取 APP_ID 和 APP_TOKEN 的值
APP_ID = 'testdisk'
APP_TOKEN = '61be1ce3-121a-49b4-b0bf-ab8c26735aa8'
BK_PAAS_HOST = 'http://paas.class.o.qcloud.com'

APP_ID = os.environ.get('APP_ID', APP_ID)
APP_TOKEN = os.environ.get('APP_TOKEN', APP_TOKEN)
BK_PAAS_HOST = os.environ.get('BK_PAAS_HOST', BK_PAAS_HOST)
BK_PAAS_INNER_HOST = os.environ.get('BK_PAAS_INNER_HOST', BK_PAAS_HOST)

BK_URL = BK_PAAS_HOST

APP_CODE = APP_ID
SECRET_KEY = APP_TOKEN

# 是否启用celery任务
IS_USE_CELERY = True
# 本地开发的 celery 的消息队列（RabbitMQ）信息
BROKER_URL_DEV = 'amqp://guest:guest@127.0.0.1:5672/'

# ==============================================================================
# 应用运行环境配置信息
# ==============================================================================
ENVIRONMENT = os.environ.get('BK_ENV', 'development')
# 应用访问路径
SITE_URL = '/'
# 运行模式， DEVELOP(开发模式)， TEST(测试模式)， PRODUCT(正式模式)
RUN_MODE = 'DEVELOP'
if ENVIRONMENT.endswith('production'):
    RUN_MODE = 'PRODUCT'
    DEBUG = False
    SITE_URL = '/o/%s/' % APP_ID
elif ENVIRONMENT.endswith('testing'):
    RUN_MODE = 'TEST'
    DEBUG = False
    SITE_URL = '/t/%s/' % APP_ID
else:
    RUN_MODE = 'DEVELOP'
    DEBUG = False

try:
    import pymysql

    pymysql.install_as_MySQLdb()
except:
    pass

# ===============================================================================
# 应用基本信息
# ===============================================================================
# 应用密钥
CSRF_COOKIE_PATH = SITE_URL
ALLOWED_HOSTS = ['*']
# ==============================================================================
# Middleware and apps
# ==============================================================================
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'account.middlewares.LoginMiddleware',  # 登录鉴权中间件
    'django.middleware.locale.LocaleMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # OTHER 3rd Party App
    'account',
)

INSTALLED_APPS += INSTALLED_APPS_CUSTOM
MIDDLEWARE_CLASSES += MIDDLEWARE_CLASSES_CUSTOM

# 项目路径
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT, PROJECT_MODULE_NAME = os.path.split(PROJECT_PATH)
BASE_DIR = os.path.dirname(os.path.dirname(PROJECT_PATH))
PYTHON_BIN = os.path.dirname(sys.executable)

# 国际化配置
USE_TZ = True
TIME_ZONE = 'Asia/Shanghai'
LANGUAGE_CODE = 'zh-cn'
SITE_ID = 1
# 设定使用根目录的locale
LOCALE_PATHS = (os.path.join(PROJECT_ROOT, 'locale'),)
# 设定是否使用header的Accept-Language，如果设置为True，
# 程序会自动分析访客使用的语言，来显示相应的翻译结果
LOCALEURL_USE_ACCEPT_LANGUAGE = True
# 界面可选语言
_ = lambda s: s
LANGUAGES = (
    ('en', _(u'English')),
    ('zh-cn', _(u'简体中文')),
)
USE_I18N = True
USE_L10N = True

LANGUAGE_SESSION_KEY = 'blueking_language'
LANGUAGE_COOKIE_NAME = 'blueking_language'

# ===============================================================================
# 静态资源设置
# ===============================================================================
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
# STATICFILES_DIRS = (
#     os.path.join(PROJECT_ROOT, 'static'),
# )
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)
# 应用本地静态资源目录
STATIC_URL = '%sstatic/' % SITE_URL
# APP静态资源目录url
REMOTE_STATIC_URL = '%sstatic/remote/' % SITE_URL

ROOT_URLCONF = 'urls'

PROJECT_DIR, PROJECT_MODULE_NAME = os.path.split(PROJECT_ROOT)

# ==============================================================================
# Templates
# ==============================================================================

# mako template dir
MAKO_TEMPLATE_DIR = (
    os.path.join(PROJECT_ROOT, 'templates'),
)
MAKO_TEMPLATE_MODULE_DIR = os.path.join(PROJECT_DIR, 'templates_module', APP_CODE)

if RUN_MODE is not 'DEVELOP':
    MAKO_TEMPLATE_MODULE_DIR = os.path.join(PROJECT_ROOT, 'templates_module', APP_CODE)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (
            os.path.join(PROJECT_ROOT, 'templates'),
        ),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': (
                # the context to the templates
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.template.context_processors.csrf',
                'gcloud.core.context_processors.mysetting',  # 自定义模版context，可以在页面中使用STATIC_URL等变量
                'django.template.context_processors.i18n',
            ),
        },
    },
]
# ==============================================================================
# session and cache
# ==============================================================================
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 默认为false,为true时SESSION_COOKIE_AGE无效
SESSION_COOKIE_PATH = SITE_URL  # NOTE 不要改动，否则，可能会改成和其他app的一样，这样会影响登录

# ===============================================================================
# Authentication
# ===============================================================================
AUTH_USER_MODEL = 'account.BkUser'
AUTHENTICATION_BACKENDS = (
    'account.backends.BkBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
    'gcloud.core.backends.GCloudPermissionBackend',
)

LOGIN_URL = "%s/login/?app_id=%s" % (BK_PAAS_HOST, APP_ID)
LOGOUT_URL = '%saccount/logout/' % SITE_URL
LOGIN_REDIRECT_URL = SITE_URL
REDIRECT_FIELD_NAME = "c_url"
# 验证登录的cookie名
BK_COOKIE_NAME = 'bk_token'
# 数据库初始化 管理员列表
ADMIN_USERNAME_LIST = ['admin']

# ===============================================================================
# CELERY 配置
# ===============================================================================
if IS_USE_CELERY:
    try:
        import djcelery

        INSTALLED_APPS += (
            'djcelery',  # djcelery
        )
        djcelery.setup_loader()
        CELERY_ENABLE_UTC = False
        CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
        if "celery" in sys.argv:
            DEBUG = False
        # celery 的消息队列（RabbitMQ）信息
        BROKER_URL = os.environ.get('BK_BROKER_URL', BROKER_URL_DEV)
        if RUN_MODE == 'DEVELOP':
            from celery.signals import worker_process_init


            @worker_process_init.connect
            def configure_workers(*args, **kwargs):
                import django
                django.setup()
    except:
        pass
    from pipeline.celery.settings import *

# ==============================================================================
# logging
# ==============================================================================
# 应用日志配置
BK_LOG_DIR = os.environ.get('BK_LOG_DIR', '/data/paas/apps/logs/')
LOGGING_DIR = os.path.join(BASE_DIR, 'logs', APP_ID)
LOG_CLASS = 'logging.handlers.RotatingFileHandler'
if RUN_MODE == 'DEVELOP':
    LOG_LEVEL = 'DEBUG'
elif RUN_MODE == 'TEST':
    LOGGING_DIR = os.path.join(BK_LOG_DIR, APP_ID)
    LOG_LEVEL = 'INFO'
elif RUN_MODE == 'PRODUCT':
    LOGGING_DIR = os.path.join(BK_LOG_DIR, APP_ID)
    LOG_LEVEL = 'INFO'

# 自动建立日志目录
if not os.path.exists(LOGGING_DIR):
    try:
        os.makedirs(LOGGING_DIR)
    except:
        pass

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s [%(asctime)s] %(pathname)s %(lineno)d %(funcName)s %(process)d %(thread)d \n \t %(message)s \n',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s \n'
        },
        'bare': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'root': {
            'class': LOG_CLASS,
            'formatter': 'verbose',
            'filename': os.path.join(LOGGING_DIR, '%s.log' % APP_ID),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5
        },
        'component': {
            'class': LOG_CLASS,
            'formatter': 'verbose',
            'filename': os.path.join(LOGGING_DIR, 'component.log'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5
        },
        'wb_mysql': {
            'class': LOG_CLASS,
            'formatter': 'verbose',
            'filename': os.path.join(LOGGING_DIR, 'wb_mysql.log'),
            'maxBytes': 1024 * 1024 * 4,
            'backupCount': 5
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        # the root logger ,用于整个project的logger
        'root': {
            'handlers': ['root'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'celery': {
            'handlers': ['root'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        # 组件调用日志
        'component': {
            'handlers': ['component'],
            'level': 'WARN',
            'propagate': True,
        },
        # other loggers...
        'django.db.backends': {
            'handlers': ['wb_mysql'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
