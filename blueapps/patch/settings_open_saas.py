# coding=utf-8
import os
from blueapps.patch.log import get_paas_v2_logging_config_dict
from config.default import *  # noqa
from config import APP_CODE, SECRET_KEY

# IS_LOCAL,V2和V3的判断方式不同,V2用BK_ENV
IS_LOCAL = not os.getenv('BK_ENV', False)

# ESB component
if not locals().get('ESB_SDK_NAME'):
    ESB_SDK_NAME = 'blueking.component'

# 蓝鲸PASS平台URL
BK_PAAS_HOST = os.getenv('BK_PAAS_HOST', BK_URL)

# 蓝鲸开发者页面
BK_DEV_URL = '%s/app/list/' % BK_PAAS_HOST

# 兼容component的APP_ID,APP_TOKEN
APP_CODE = APP_ID = os.environ.get('APP_ID', APP_CODE)
SECRET_KEY = APP_TOKEN = os.environ.get('APP_TOKEN', SECRET_KEY)

# 用于 用户认证、用户信息获取 的蓝鲸主机
BK_PAAS_INNER_HOST = os.getenv('BK_PAAS_INNER_HOST', BK_PAAS_HOST)

# PAASV2对外版不需要bkoauth,DISABLED_APPS加入bkoauth
INSTALLED_APPS = (INSTALLED_APPS[0: INSTALLED_APPS.index('bkoauth')] +  # noqa
                  INSTALLED_APPS[INSTALLED_APPS.index('bkoauth') + 1:])

# PAASV2对外版不需要whitenoise,MIDDLEWARE中去除'whitenoise.middleware.WhiteNoiseMiddleware'
MIDDLEWARE = (MIDDLEWARE[0: MIDDLEWARE.index('whitenoise.middleware.'
                                             'WhiteNoiseMiddleware')] +  # noqa
              MIDDLEWARE[MIDDLEWARE.index('whitenoise.middleware.'
                                          'WhiteNoiseMiddleware') + 1:])

# BROKER_URL
if 'BK_BROKER_URL' in os.environ:
    BROKER_URL = os.getenv('BK_BROKER_URL')

# SITE_URL,STATIC_URL,,FORCE_SCRIPT_NAME
# 测试环境
if os.getenv('BK_ENV') == 'testing':
    BK_URL = os.environ.get("BK_URL", "%s/console/" % BK_PAAS_HOST)
    SITE_URL = os.environ.get("BK_SITE_URL", '/t/%s/' % APP_CODE)
    STATIC_URL = '%sstatic/' % SITE_URL
# 正式环境
if os.getenv('BK_ENV') == 'production':
    BK_URL = os.environ.get("BK_URL", "%s/console/" % BK_PAAS_HOST)
    SITE_URL = os.environ.get("BK_SITE_URL", '/o/%s/' % APP_CODE)
    STATIC_URL = '%sstatic/' % SITE_URL

# REMOTE_STATIC_URL
REMOTE_STATIC_URL = '%sremote/' % STATIC_URL

# 日志
BK_LOG_DIR = os.getenv('BK_LOG_DIR', '/data/apps/logs/')
LOGGING = get_paas_v2_logging_config_dict(
    is_local=IS_LOCAL,
    bk_log_dir=BK_LOG_DIR,
    log_level=locals().get('LOG_LEVEL', 'INFO')
)

# 请求官方 API 默认版本号，可选值为："v2" 或 ""；其中，"v2"表示规范化API，
# ""表示未规范化API.如果外面设置了该值则使用设置值,否则默认使用v2
DEFAULT_BK_API_VER = locals().get('DEFAULT_BK_API_VER', 'v2')

# STATIC_ROOT,静态文件收集文件夹,由于企业版需要用户手动收集,此处设为空,
# 同时需要设置STATICFILES_DIRS不改变
if not locals().get('STATIC_ROOT'):
    STATIC_ROOT = None
