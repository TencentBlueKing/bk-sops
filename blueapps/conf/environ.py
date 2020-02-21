# -*- coding: utf-8 -*-
"""
blueapps environ variables from paas
"""
from __future__ import absolute_import

import os
import importlib

# 由用户初始化
from config import celery_app, RUN_VER, APP_CODE, SECRET_KEY, BASE_DIR  # noqa

try:
    from config import BK_URL
except ImportError:
    BK_URL = None

# 根据平台加载对应变量
try:
    site_mod = importlib.import_module('blueapps.conf.sites.%s' % RUN_VER)
except ImportError:
    raise ImportError(u'unknown RUN_VER: %s' % RUN_VER)
for _setting in dir(site_mod):
    if _setting.isupper():
        locals()[_setting] = getattr(site_mod, _setting)

# Inherit from paas environment
# all = [
#     'BKPAAS_LOG_NAME_PREFIX',
#     'BKPAAS_ENGINE_APP_NAME',
#     'BKPAAS_ENGINE_REGION',
#     'BKPAAS_ENVIRONMENT',
#     'BKPAAS_URL',
#     'BKPAAS_SUB_PATH',
#     'BKPAAS_REMOTE_STATIC_URL',
#     'BKPAAS_WEIXIN_URL',
#     'BKPAAS_WEIXIN_REMOTE_STATIC_URL',
# ]

# 蓝鲸平台URL
BK_URL = os.getenv('BKPAAS_URL', BK_URL)  # noqa

# 蓝鲸开发者页面
BK_DEV_URL = BK_URL

# 站点URL
SITE_URL = os.getenv('BKPAAS_SUB_PATH', '/')

# 远程静态文件URL
REMOTE_STATIC_URL = os.getenv('BKPAAS_REMOTE_STATIC_URL',
                              '%s/static_api/' % BK_URL)

# 判断是否为本地开发环境
IS_LOCAL = not os.getenv('BKPAAS_ENVIRONMENT', False)

# static root and dirs to find blueapps static
if not IS_LOCAL:
    STATIC_ROOT = 'staticfiles'
    FORCE_SCRIPT_NAME = SITE_URL

    # 开启子域名时静态文件统一使用子域名访问
    app_subdomains = os.getenv('BKPAAS_ENGINE_APP_DEFAULT_SUBDOMAINS', None)
    # 存在该变量，而且不是空字符串
    if app_subdomains is not None and app_subdomains != '':
        STATIC_URL = 'http://%s/static/' % app_subdomains.split(';')[0]
    else:
        STATIC_URL = '%sstatic/' % FORCE_SCRIPT_NAME
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATIC_URL = '/static/'

# About Log
LOG_NAME_PREFIX = os.getenv('BKPAAS_LOG_NAME_PREFIX')

# About whitenoise
WHITENOISE_STATIC_PREFIX = '/static/'

# Rabbitmq & Celery
if 'RABBITMQ_VHOST' in os.environ:
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST')
    RABBITMQ_PORT = os.getenv('RABBITMQ_PORT')
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
    RABBITMQ_USER = os.getenv('RABBITMQ_USER')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
    BROKER_URL = 'amqp://{user}:{password}@{host}:{port}/{vhost}'.format(
        user=RABBITMQ_USER,
        password=RABBITMQ_PASSWORD,
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        vhost=RABBITMQ_VHOST)

# WEIXIN Settings

# 微信 URL 前缀
WEIXIN_URL_PREFIX = 'weixin'

# APP 微信 ROOT URL
WEIXIN_SITE_URL = '%s%s/' % (SITE_URL, WEIXIN_URL_PREFIX)

# 平台微信 URL 域名
WEIXIN_BK_URL = os.getenv('BKPAAS_WEIXIN_URL', 'https://mt.bk.tencent.com')

# APP 微信本地静态资源目录
# TODO 环境变量中无WEXIN_STATIC_URL或BKPAAS_WEIXIN_STATIC_URL
WEIXIN_STATIC_URL = os.getenv('BKPAAS_WEIXIN_STATIC_URL',
                              '%sstatic/weixin/' % SITE_URL)

# APP 微信远程静态资源目录
WEIXIN_REMOTE_STATIC_URL = os.getenv('BKPAAS_WEIXIN_REMOTE_STATIC_URL',
                                     '%s/static_api/' % WEIXIN_BK_URL)
