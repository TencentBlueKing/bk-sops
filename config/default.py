# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from blueapps.conf.log import get_logging_config_dict
from blueapps.conf.default_settings import *  # noqa

# 这里是默认的 INSTALLED_APPS，大部分情况下，不需要改动
# 如果你已经了解每个默认 APP 的作用，确实需要去掉某些 APP，请去掉下面的注释，然后修改
# INSTALLED_APPS = (
#     'bkoauth',
#     # 框架自定义命令
#     'blueapps.contrib.bk_commands',
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.sites',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     # account app
#     'blueapps.account',
# )

DEFAULT_OPEN_VER = 'community'
OPEN_VER = os.environ.get('RUN_VER', 'open')

# 区分社区版和企业版
if OPEN_VER == 'open':
    OPEN_VER = os.environ.get('OPEN_VER', DEFAULT_OPEN_VER)
    if not OPEN_VER:
        raise Exception('OPEN_VER is not set when RUN_VER is open')

# 请在这里加入你的自定义 APP
INSTALLED_APPS += (
    'guardian',
    'gcloud.core',
    'gcloud.config',
    'gcloud.tasktmpl3',
    'gcloud.taskflow3',
    'gcloud.webservice3',
    'gcloud.contrib.analysis',
    'gcloud.contrib.appmaker',
    'gcloud.contrib.function',
    'gcloud.contrib.audit',
    'gcloud.apigw',
    'gcloud.commons.template',
    'gcloud.periodictask',
    'pipeline',
    'pipeline.component_framework',
    'pipeline.variables',
    'pipeline.engine',
    'pipeline.log',
    'pipeline.contrib.statistics',
    'pipeline.contrib.periodic_task',
    'django_signal_valve',
    'pipeline_plugins',
    'pipeline_plugins.components',
    'pipeline_plugins.variables',
    'data_migration'
)

# 这里是默认的中间件，大部分情况下，不需要改动
# 如果你已经了解每个默认 MIDDLEWARE 的作用，确实需要去掉某些 MIDDLEWARE，或者改动先后顺序，请去掉下面的注释，然后修改
# MIDDLEWARE = (
#     # request instance provider
#     'blueapps.middleware.request_provider.RequestProvider',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     # 跨域检测中间件， 默认关闭
#     # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
#     # 蓝鲸静态资源服务
#     'whitenoise.middleware.WhiteNoiseMiddleware',
#     # reload weixin settings
#     'blueapps.middleware.wechatsettings.ReloadSettingsMiddleware',
#     # Auth middleware
#     'blueapps.account.middlewares.WeixinLoginRequiredMiddleware',
#     'blueapps.account.middlewares.LoginRequiredMiddleware',
#     # exception middleware
#     'blueapps.core.exceptions.middleware.AppExceptionMiddleware'
# )

# 自定义中间件
MIDDLEWARE += (
    'django.middleware.locale.LocaleMiddleware',
    'gcloud.core.middlewares.UnauthorizedMiddleware',
    'gcloud.core.middlewares.GCloudPermissionMiddleware',
    'gcloud.core.middlewares.TimezoneMiddleware',
)

# 所有环境的日志级别可以在这里配置
# LOG_LEVEL = 'INFO'

# 静态资源文件(js,css等）在APP上线更新后, 由于浏览器有缓存,
# 可能会造成没更新的情况. 所以在引用静态资源的地方，都把这个加上
# Django模板中：<script src="/a.js?v="></script>
# mako模板中：<script src="/a.js?v=${ STATIC_VERSION }"></script>
# 如果静态资源修改了以后，上线前改这个版本号即可
STATIC_VERSION = '3.04'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# CELERY 开关，使用时请改为 True，修改项目目录下的 Procfile 文件，添加以下两行命令：
# python manage.py celery worker -l info
# python manage.py celery beat -l info
# 不使用时，请修改为 False，并删除项目目录下的 Procfile 文件中 celery 配置
IS_USE_CELERY = True

# CELERY 并发数，默认为 2，可以通过环境变量或者 Procfile 设置
CELERYD_CONCURRENCY = os.getenv('BK_CELERYD_CONCURRENCY', 2)

# CELERY 配置，申明任务的文件路径，即包含有 @task 装饰器的函数文件
CELERY_IMPORTS = (
)

# load logging settings
LOGGING = get_logging_config_dict(locals())

# 初始化管理员列表，列表中的人员将拥有预发布环境和正式环境的管理员权限
# 注意：请在首次提测和上线前修改，之后的修改将不会生效
INIT_SUPERUSER = []

# 国际化配置
USE_TZ = True
TIME_ZONE = 'Asia/Shanghai'
LANGUAGE_CODE = 'zh-hans'
SITE_ID = 1
# 设定使用根目录的locale
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)
# 设定是否使用header的Accept-Language，如果设置为True，
# 程序会自动分析访客使用的语言，来显示相应的翻译结果
LOCALEURL_USE_ACCEPT_LANGUAGE = True
# 界面可选语言
_ = lambda s: s  # noqa
LANGUAGES = (
    ('en', _(u'English')),
    ('zh-hans', _(u'简体中文')),
)
USE_I18N = True
USE_L10N = True

LANGUAGE_SESSION_KEY = 'blueking_language'
LANGUAGE_COOKIE_NAME = 'blueking_language'

AUTHENTICATION_BACKENDS += (
    'guardian.backends.ObjectPermissionBackend',
    'gcloud.core.backends.GCloudPermissionBackend',
)

ver_settings = importlib.import_module('config.sites.%s.ver_settings' % OPEN_VER)

for _setting in dir(ver_settings):
    if _setting.upper() == _setting:
        locals()[_setting] = getattr(ver_settings, _setting)

# 本地开发环境日志级别
LOG_LEVEL_DEVELOP = 'INFO'
# 测试环境日志级别
LOG_LEVEL_TEST = 'INFO'
# 正式环境日志级别
LOG_LEVEL_PRODUCT = 'INFO'  # 'ERROR'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

# 通知公告域名
PUSH_URL = os.environ.get('BK_PUSH_URL', '')

# db cache
# create cache table by execute:
# python manage.py createcachetable django_cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache"
    },
    "dbcache": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache"
    },
    "dummy": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
}

# 创建默认模版的系统用户信息
SYSTEM_USERNAME = 'system_user'
SYSTEM_USER_CH = u"系统用户"

# 针对CC接口数据相关的缓存时间(单位s)
DEFAULT_CACHE_TIME_FOR_CC = 5

# 针对本地用户信息更新标志缓存的时间
DEFAULT_CACHE_TIME_FOR_USER_UPDATE = 5

# 针对平台用户接口缓存的时间
DEFAULT_CACHE_TIME_FOR_AUTH = 5

# CC系统名称
ESB_COMPONENT_CC = 'cc'

# 蓝鲸PASS平台URL
BK_PAAS_HOST = os.getenv('BK_PAAS_HOST', BK_URL)

# 用于 用户认证、用户信息获取 的蓝鲸主机
BK_PAAS_INNER_HOST = os.getenv('BK_PAAS_INNER_HOST', BK_PAAS_HOST)

# cc、job域名
BK_CC_HOST = os.environ.get('BK_CC_HOST')
BK_JOB_HOST = os.environ.get('BK_JOB_HOST')

PIPELINE_TEMPLATE_CONTEXT = 'gcloud.tasktmpl3.utils.get_template_context'
PIPELINE_INSTANCE_CONTEXT = 'gcloud.taskflow3.utils.get_instance_context'

# ESB 默认版本配置 '' or 'v2'
DEFAULT_BK_API_VER = 'v2'

# tastypie 配置
TASTYPIE_DEFAULT_FORMATS = ['json']

TEMPLATES[0]['OPTIONS']['context_processors'] += (
    'gcloud.core.context_processors.mysetting',
)

STATIC_VER = {
    'DEVELOP': 'dev',
    'PRODUCT': 'prod',
    'STAGING': 'stag'
}

# pipeline settings

COMPONENT_PATH = ['components.collections.sites.%s' % RUN_VER]
VARIABLE_PATH = ['variables.collections.sites.%s' % RUN_VER]

PIPELINE_PARSER_CLASS = 'pipeline_web.parser.WebPipelineAdapter'

PIPELINE_RERUN_MAX_TIMES = 50

from pipeline.celery.settings import *  # noqa
