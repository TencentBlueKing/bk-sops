# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import datetime
import sys
import importlib
from urllib.parse import urlparse

from django.utils.translation import ugettext_lazy as _

from blueapps.conf.log import get_logging_config_dict
from blueapps.conf.default_settings import *  # noqa
from blueapps.opentelemetry.utils import inject_logging_trace_info
from gcloud.exceptions import ApiRequestError
from pipeline.celery.queues import ScalableQueues
from bamboo_engine.config import Settings as BambooSettings
import env

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

APP_NAME = _("标准运维")
OPEN_VER = env.RUN_VER

# 区分社区版和其他open版本
if OPEN_VER == "open":
    OPEN_VER = env.OPEN_VER
    if not OPEN_VER:
        raise Exception("OPEN_VER is not set when RUN_VER is open")

# 请在这里加入你的自定义 APP
INSTALLED_APPS += (
    "gcloud.core",
    "gcloud.tasktmpl3",
    "gcloud.taskflow3",
    "gcloud.resources",
    "gcloud.contrib.analysis",
    "gcloud.contrib.appmaker",
    "gcloud.contrib.function",
    "gcloud.contrib.audit",
    "gcloud.contrib.develop",
    "gcloud.contrib.collection",
    "gcloud.contrib.operate_record",
    "gcloud.apigw",
    "gcloud.common_template",
    "gcloud.label",
    "gcloud.contrib.cleaner",
    "gcloud.periodictask",
    "gcloud.external_plugins",
    "gcloud.contrib.admin",
    "gcloud.iam_auth",
    "gcloud.project_constants",
    "gcloud.analysis_statistics",
    "gcloud.analysis_statistics.data_migrate",
    "gcloud.clocked_task",
    "gcloud.template_base",
    "gcloud.user_custom_config",
    "pipeline",
    "pipeline.component_framework",
    "pipeline.variable_framework",
    "pipeline.engine",
    "pipeline.log",
    "pipeline.contrib.statistics",
    "pipeline.contrib.periodic_task",
    "pipeline.contrib.external_plugins",
    "pipeline.django_signal_valve",
    "pipeline_plugins",
    "pipeline_plugins.components",
    "pipeline_plugins.variables",
    "pipeline.eri",
    "pipeline_web.core",
    "pipeline_web.label",
    "pipeline_web.plugin_management",
    "data_migration",
    "weixin.core",
    "weixin",
    "version_log",
    "files",
    "corsheaders",
    "rest_framework",
    "django_filters",
    "iam",
    "iam.contrib.iam_migration",
    "bksops_iam_migrations",
    "drf_yasg",
    "plugin_service",
    "django_dbconn_retry",
    "blueapps.opentelemetry.instrument_app",
    "apigw_manager.apigw",
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
#     # Auth middleware
#     'blueapps.account.middlewares.RioLoginRequiredMiddleware',
#     'blueapps.account.middlewares.WeixinLoginRequiredMiddleware',
#     'blueapps.account.middlewares.LoginRequiredMiddleware',
#     # exception middleware
#     'blueapps.core.exceptions.middleware.AppExceptionMiddleware'
# )

# 自定义中间件
MIDDLEWARE += (
    "weixin.core.middlewares.WeixinAuthenticationMiddleware",
    "weixin.core.middlewares.WeixinLoginMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "gcloud.core.middlewares.TimezoneMiddleware",
    "gcloud.core.middlewares.ObjectDoesNotExistExceptionMiddleware",
    "iam.contrib.django.middlewares.AuthFailedExceptionMiddleware",
    "pipeline_plugins.middlewares.PluginApiRequestHandleMiddleware",
    "apigw_manager.apigw.authentication.ApiGatewayJWTGenericMiddleware",  # JWT 认证
    "apigw_manager.apigw.authentication.ApiGatewayJWTAppMiddleware",  # JWT 透传的应用信息
    "apigw_manager.apigw.authentication.ApiGatewayJWTUserMiddleware",  # JWT 透传的用户信息
)

AUTHENTICATION_BACKENDS += ("apigw_manager.apigw.authentication.UserModelBackend",)

if env.IS_PAAS_V3:
    BK_APIGW_NAME = "bk-sops"
    BK_APP_CODE = os.getenv("BKPAAS_APP_ID")
    BK_APP_SECRET = os.getenv("BKPAAS_APP_SECRET")
    BK_API_URL_TMPL = env.BK_APIGW_URL_TMPL
    BK_APIGW_MANAGER_MAINTAINERS = env.BK_APIGW_MANAGER_MAINTAINERS

    api_host = urlparse(env.BKAPP_APIGW_API_HOST)
    BK_APIGW_API_SERVER_HOST = api_host.netloc
    BK_APIGW_API_SERVER_SUB_PATH = api_host.path.lstrip("/")

    callback_host = urlparse(env.BKAPP_APIGW_CALLBACK_HOST)
    BK_APIGW_CALLBACK_SERVER_HOST = callback_host.netloc
    BK_APIGW_CALLBACK_SERVER_SUB_PATH = callback_host.path.lstrip("/")

    BK_APIGW_RESOURCE_DOCS_ARCHIVE_FILE = os.path.join(BASE_DIR, "gcloud", "apigw", "docs", "apigw-docs.tgz")

# 默认数据库AUTO字段类型
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = ()
if env.BKAPP_CORS_ALLOW:
    MIDDLEWARE = ("corsheaders.middleware.CorsMiddleware",) + MIDDLEWARE
    CORS_ALLOW_CREDENTIALS = True
    CORS_ORIGIN_WHITELIST = env.BKAPP_CORS_WHITELIST.split(",")
else:
    CORS_ALLOW_CREDENTIALS = False

if env.BKAPP_PYINSTRUMENT_ENABLE:
    MIDDLEWARE += ("pyinstrument.middleware.ProfilerMiddleware",)

MIDDLEWARE = (
    "gcloud.core.middlewares.HttpRedirectMiddleware",
    "gcloud.core.middlewares.TraceIDInjectMiddleware",
    "weixin.core.middlewares.WeixinProxyPatchMiddleware",
) + MIDDLEWARE

# 所有环境的日志级别可以在这里配置
LOG_LEVEL = "INFO"

# load logging settings
LOGGING = get_logging_config_dict(locals())

# 静态资源文件(js,css等）在APP上线更新后, 由于浏览器有缓存,
# 可能会造成没更新的情况. 所以在引用静态资源的地方，都把这个加上
# Django模板中：<script src="/a.js?v="></script>
# mako模板中：<script src="/a.js?v=${ STATIC_VERSION }"></script>
# 如果静态资源修改了以后，上线前改这个版本号即可

STATIC_VERSION = "3.26.13"
DEPLOY_DATETIME = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# CELERY 开关，使用时请改为 True，修改项目目录下的 Procfile 文件，添加以下两行命令：
# python manage.py celery worker -l info
# python manage.py celery beat -l info
# 不使用时，请修改为 False，并删除项目目录下的 Procfile 文件中 celery 配置
IS_USE_CELERY = True

# CELERY 并发数，默认为 2，可以通过环境变量或者 Procfile 设置
CELERYD_CONCURRENCY = env.BK_CELERYD_CONCURRENCY

# CELERY 配置，申明任务的文件路径，即包含有 @task 装饰器的函数文件
CELERY_IMPORTS = ()

# celery settings
if IS_USE_CELERY:
    INSTALLED_APPS = locals().get("INSTALLED_APPS", [])
    INSTALLED_APPS += ("django_celery_beat", "django_celery_results")
    CELERY_ENABLE_UTC = False
    CELERY_TASK_SERIALIZER = "pickle"
    CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"

TEMPLATE_DATA_SALT = "821a11587ea434eb85c2f5327a90ae54"
OLD_COMMUNITY_TEMPLATE_DATA_SALT = "e5483c1ccde63392bd439775bba6a7ae"

LOGGING["loggers"]["pipeline"] = {
    "handlers": ["root"],
    "level": LOG_LEVEL,
    "propagate": True,
}

# 初始化管理员列表，列表中的人员将拥有预发布环境和正式环境的管理员权限
# 注意：请在首次提测和上线前修改，之后的修改将不会生效
INIT_SUPERUSER = []

# 国际化配置
USE_TZ = True
TIME_ZONE = "Asia/Shanghai"
LANGUAGE_CODE = "zh-hans"
SITE_ID = 1
# 设定使用根目录的locale
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)
# 设定是否使用header的Accept-Language，如果设置为True，
# 程序会自动分析访客使用的语言，来显示相应的翻译结果
LOCALEURL_USE_ACCEPT_LANGUAGE = True
# 界面可选语言

# max body size
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400


def _(s):
    return s  # noqa


LANGUAGES = (
    ("en", _("English")),
    ("zh-hans", _("简体中文")),
)
USE_I18N = True
USE_L10N = True

LANGUAGE_SESSION_KEY = "blueking_language"
LANGUAGE_COOKIE_NAME = "blueking_language"

HAYSTACK_CONNECTIONS = {
    "default": {"ENGINE": "haystack.backends.simple_backend.SimpleEngine"},
}

# 通知公告域名
PUSH_URL = env.BK_PUSH_URL

# remove disabled apps
if locals().get("DISABLED_APPS"):
    INSTALLED_APPS = locals().get("INSTALLED_APPS", [])
    DISABLED_APPS = locals().get("DISABLED_APPS", [])

    INSTALLED_APPS = [_app for _app in INSTALLED_APPS if _app not in DISABLED_APPS]

    _keys = (
        "AUTHENTICATION_BACKENDS",
        "DATABASE_ROUTERS",
        "FILE_UPLOAD_HANDLERS",
        "MIDDLEWARE",
        "PASSWORD_HASHERS",
        "TEMPLATE_LOADERS",
        "STATICFILES_FINDERS",
        "TEMPLATE_CONTEXT_PROCESSORS",
    )

    import itertools

    for _app, _key in itertools.product(DISABLED_APPS, _keys):
        if locals().get(_key) is None:
            continue
        locals()[_key] = tuple([_item for _item in locals()[_key] if not _item.startswith(_app + ".")])

# db cache
# create cache table by execute:
# python manage.py createcachetable django_cache
CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.db.DatabaseCache", "LOCATION": "django_cache"},
    "login_db": {"BACKEND": "django.core.cache.backends.db.DatabaseCache", "LOCATION": "account_cache"},
    "locmem": {"BACKEND": "gcloud.utils.cache.LocMemCache", "LOCATION": "django_cache"},
    "dummy": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
}

# 针对CC接口数据相关的缓存时间(单位s)
DEFAULT_CACHE_TIME_FOR_CC = 5

# 针对本地用户信息更新标志缓存的时间
DEFAULT_CACHE_TIME_FOR_USER_UPDATE = 5

# 针对平台用户接口缓存的时间
DEFAULT_CACHE_TIME_FOR_AUTH = 5

# 蓝鲸PASS平台URL
BK_PAAS_HOST = env.BK_PAAS_HOST

# 用于 用户认证、用户信息获取 的蓝鲸主机
BK_PAAS_INNER_HOST = env.BK_PAAS_INNER_HOST

# AJAX 请求弹窗续期登陆设置
IS_AJAX_PLAIN_MODE = True

# init admin list
INIT_SUPERUSER = ["admin"]

# cc、job、iam、 nodeman域名
BK_CC_HOST = env.BK_CC_HOST
BK_JOB_HOST = env.BK_JOB_HOST
BK_NODEMAN_HOST = env.BK_NODEMAN_HOST

# ESB 默认版本配置 '' or 'v2'
DEFAULT_BK_API_VER = "v2"
# ESB 域名配置
BK_PAAS_ESB_HOST = env.BKAPP_SOPS_PAAS_ESB_HOST

# IAM权限中心配置
BK_IAM_SYSTEM_ID = env.BKAPP_BK_IAM_SYSTEM_ID
BK_IAM_SYSTEM_NAME = env.BKAPP_BK_IAM_SYSTEM_NAME
BK_IAM_APP_CODE = env.BK_IAM_V3_APP_CODE
BK_IAM_SKIP = env.BK_IAM_SKIP
# 兼容 open_paas 版本低于 2.10.7，此时只能从环境变量 BK_IAM_HOST 中获取权限中心后台 host
BK_IAM_INNER_HOST = env.BK_IAM_INNER_HOST
# 权限中心 SaaS host
BK_IAM_SAAS_HOST = env.BK_IAM_SAAS_HOST
# 权限中心 SDK 无权限时不返回 499 的请求路径前缀配置
BK_IAM_API_PREFIX = env.BK_IAM_API_PREFIX
# 权限中心 migrations 存储 app
BK_IAM_MIGRATION_APP_NAME = "bksops_iam_migrations"

AUTH_LEGACY_RESOURCES = ["project", "common_flow", "flow", "mini_app", "periodic_task", "task"]

# 用户管理配置
BK_USER_MANAGE_HOST = env.BK_USER_MANAGE_HOST

# 人员选择数据来源
BK_MEMBER_SELECTOR_DATA_HOST = env.BK_MEMBER_SELECTOR_DATA_HOST

TEMPLATES[0]["OPTIONS"]["context_processors"] += ("gcloud.core.context_processors.mysetting",)

STATIC_VER = {"DEVELOP": "dev", "PRODUCT": "prod", "STAGING": "stag"}

# drf 配置
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}

# pipeline settings
PIPELINE_TEMPLATE_CONTEXT = "gcloud.tasktmpl3.domains.context.get_template_context"
PIPELINE_INSTANCE_CONTEXT = "gcloud.taskflow3.models.get_instance_context"

PIPELINE_PARSER_CLASS = "pipeline_web.parser.WebPipelineAdapter"

PIPELINE_RERUN_MAX_TIMES = int(env.BKAPP_PIPELINE_RERUN_MAX_TIMES)

PIPELINE_RERUN_INDEX_OFFSET = 0

# 是否只允许加载远程 https 仓库的插件
EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT = env.BKAPP_EXTERNAL_PLUGINS_SOURCE_SECURE_LOOSE == "0"

PIPELINE_DATA_BACKEND = env.BKAPP_PIPELINE_DATA_BACKEND

PIPELINE_DATA_CANDIDATE_BACKEND = env.BKAPP_PIPELINE_DATA_CANDIDATE_BACKEND

PIPELINE_DATA_BACKEND_AUTO_EXPIRE = True

BAMBOO_PERIODIC_TASK_ROOT_PIPELINE_CONTEXT_PROVIER = "gcloud.taskflow3.context.root_pipeline_context_provider"
BAMBOO_PERIODIC_TASK_SUBPROCESS_CONTEXT_PROVIER = "gcloud.taskflow3.context.subprocess_context_provider"

# pipeline mako render settings
MAKO_SANDBOX_SHIELD_WORDS = [
    "ascii",
    "bytearray",
    "bytes",
    "callable",
    "chr",
    "classmethod",
    "compile",
    "delattr",
    "dir",
    "divmod",
    "exec",
    "eval",
    "filter",
    "frozenset",
    "getattr",
    "globals",
    "hasattr",
    "hash",
    "help",
    "id",
    "input",
    "isinstance",
    "issubclass",
    "iter",
    "locals",
    "map",
    "memoryview",
    "next",
    "object",
    "open",
    "print",
    "property",
    "repr",
    "setattr",
    "staticmethod",
    "super",
    "type",
    "vars",
    "__import__",
]

# format: module_path: alias
MAKO_SANDBOX_IMPORT_MODULES = {
    "datetime": "datetime",
    "re": "re",
    "hashlib": "hashlib",
    "random": "random",
    "time": "time",
    "os.path": "os.path",
}

if env.SOPS_MAKO_IMPORT_MODULES:
    for module_name in env.SOPS_MAKO_IMPORT_MODULES.split(","):
        try:
            __import__(module_name)
        except ImportError as e:
            err = "{} module in SOPS_MAKO_IMPORT_MODULES import error: {}".format(module_name, e)
            print(err)
            raise ImportError(err)
        MAKO_SANDBOX_IMPORT_MODULES[module_name] = module_name

BambooSettings.MAKO_SANDBOX_IMPORT_MODULES = MAKO_SANDBOX_IMPORT_MODULES
BambooSettings.MAKO_SANDBOX_SHIELD_WORDS = MAKO_SANDBOX_SHIELD_WORDS

ENABLE_EXAMPLE_COMPONENTS = False

UUID_DIGIT_STARTS_SENSITIVE = True

# engine queue setttings

# 添加通过api gateway调用的celery任务队列
API_TASK_QUEUE_NAME = "api_task_queue"
ScalableQueues.add(name=API_TASK_QUEUE_NAME)

# 添加周期任务的celery任务队列
PERIODIC_TASK_QUEUE_NAME = "periodic_task_queue"
ScalableQueues.add(name=PERIODIC_TASK_QUEUE_NAME)

from pipeline.celery.settings import *  # noqa
from pipeline.eri.celery import queues as eri_queues  # noqa
from gcloud.taskflow3.domains.queues import PrepareAndStartTaskQueueResolver  # noqa
from gcloud.taskflow3.celery import settings as taskflow3_celery_settings  # noqa
from gcloud.contrib.cleaner import settings as cleaner_settings  # noqa

API_TASK_QUEUE_NAME_V2 = "api"
PERIODIC_TASK_QUEUE_NAME_V2 = "periodic_task"
CELERY_QUEUES.extend(eri_queues.CELERY_QUEUES)
CELERY_QUEUES.extend(eri_queues.QueueResolver(API_TASK_QUEUE_NAME_V2).queues())
CELERY_QUEUES.extend(eri_queues.QueueResolver(PERIODIC_TASK_QUEUE_NAME_V2).queues())
CELERY_QUEUES.extend(PrepareAndStartTaskQueueResolver(API_TASK_QUEUE_NAME_V2).queues())
CELERY_QUEUES.extend(taskflow3_celery_settings.CELERY_QUEUES)
CELERY_QUEUES.extend(cleaner_settings.CELERY_QUEUES)

# CELERY与RabbitMQ增加60秒心跳设置项
BROKER_HEARTBEAT = 60
BROKER_POOL_LIMIT = env.CELERY_BROKER_POOL_LIMIT

SYSTEM_USE_API_ACCOUNT = "admin"

# VER settings
ver_settings = importlib.import_module("config.sites.%s.ver_settings" % OPEN_VER)
for _setting in dir(ver_settings):
    if _setting.upper() == _setting:
        locals()[_setting] = getattr(ver_settings, _setting)

# version log config
VERSION_LOG = {"FILE_TIME_FORMAT": "%Y-%m-%d", "LATEST_VERSION_INFORM": True}

# migrate api token
MIGRATE_TOKEN = env.MIGRATE_TOKEN

# keywords to shield in node log
LOG_SHIELDING_KEYWORDS = SECRET_KEY + "," + env.BKAPP_LOG_SHIELDING_KEYWORDS
LOG_SHIELDING_KEYWORDS = LOG_SHIELDING_KEYWORDS.strip().strip(",").split(",") if LOG_SHIELDING_KEYWORDS else []

# variable key blacklist
VARIABLE_KEY_BLACKLIST = env.VARIABLE_KEY_BLACKLIST.strip().strip(",").split(",") if env.VARIABLE_KEY_BLACKLIST else []

AUTO_UPDATE_VARIABLE_MODELS = os.getenv("BKAPP_AUTO_UPDATE_VARIABLE_MODELS", "1") == "1"
AUTO_UPDATE_COMPONENT_MODELS = os.getenv("BKAPP_AUTO_UPDATE_COMPONENT_MODELS", "1") == "1"

PAGE_NOT_FOUND_URL_KEY = "page_not_found"
BLUEAPPS_SPECIFIC_REDIRECT_KEY = "page_not_found"

# 自定义插件和变量Exception类型
PLUGIN_SPECIFIC_EXCEPTIONS = (ApiRequestError,)
VARIABLE_SPECIFIC_EXCEPTIONS = (ApiRequestError,)


# SaaS统一日志配置
def logging_addition_settings(logging_dict: dict, environment="prod"):
    # formatters
    logging_dict["formatters"]["light"] = {"format": "%(message)s"}
    logging_dict["formatters"]["engine"] = {"format": "[%(asctime)s][%(levelname)s] %(message)s"}

    # handlers
    logging_dict["handlers"]["pipeline_engine_context"] = {
        "class": "pipeline.log.handlers.EngineContextLogHandler",
        "formatter": "light",
    }

    logging_dict["handlers"]["bamboo_engine_context"] = {
        "class": "pipeline.eri.log.EngineContextLogHandler",
        "formatter": "engine",
    }

    logging_dict["handlers"]["engine"] = {
        "class": "pipeline.log.handlers.EngineLogHandler",
        "formatter": "light",
    }

    logging_dict["handlers"]["pipeline_eri"] = {
        "class": "pipeline.eri.log.ERINodeLogHandler",
        "formatter": "engine",
    }

    # loggers
    logging_dict["loggers"]["iam"] = {
        "handlers": ["component"],
        "level": "INFO" if environment == "prod" else "DEBUG",
        "propagate": True,
    }

    logging_dict["loggers"]["component"] = {
        "handlers": ["component", "pipeline_engine_context", "bamboo_engine_context"],
        "level": "DEBUG",
        "propagate": True,
    }

    logging_dict["loggers"]["root"] = {
        "handlers": ["root", "pipeline_engine_context", "bamboo_engine_context"],
        "level": "INFO",
        "propagate": True,
    }

    logging_dict["loggers"]["pipeline.logging"] = {
        "handlers": ["engine"],
        "level": "INFO",
        "propagate": True,
    }

    logging_dict["loggers"]["pipeline"] = {"handlers": ["root"], "level": "INFO", "propagate": True}

    logging_dict["loggers"]["pipeline.eri.log"] = {"handlers": ["pipeline_eri"], "level": "INFO", "propagate": True}

    logging_dict["loggers"]["bamboo_engine"] = {
        "handlers": ["root", "bamboo_engine_context"],
        "level": "INFO",
        "propagate": True,
    }

    logging_dict["loggers"]["pipeline_engine"] = {
        "handlers": ["root", "pipeline_engine_context"],
        "level": "INFO",
        "propagate": True,
    }

    logging_dict["loggers"]["bk-monitor-report"] = {
        "handlers": ["root"],
        "level": "INFO",
        "propagate": True,
    }

    # 对于不开启数据库日志记录的情况，进行统一处理
    if env.NODE_LOG_DATA_SOURCE != "DATABASE":
        for logger_config in logging_dict["loggers"].values():
            logger_config["handlers"] = [
                handler
                for handler in logger_config["handlers"]
                if handler not in ["pipeline_engine_context", "bamboo_engine_context", "pipeline_eri"]
            ]
            if not logger_config["handlers"]:
                logger_config["handlers"] = ["root"]

    def handler_filter_injection(filters: list):
        for _, handler in logging_dict["handlers"].items():
            handler.setdefault("filters", []).extend(filters)

    logging_dict.setdefault("filters", {}).update(
        {"bamboo_engine_node_info_filter": {"()": "gcloud.core.logging.BambooEngineNodeInfoFilter"}}
    )
    handler_filter_injection(["bamboo_engine_node_info_filter"])

    # 日志中添加trace_id
    if env.ENABLE_OTEL_TRACE:
        trace_format = (
            "[trace_id]: %(otelTraceID)s [span_id]: %(otelSpanID)s [resource.service.name]: %(otelServiceName)s"
        )
    else:
        logging_dict.setdefault("filters", {}).update(
            {"trace_id_inject_filter": {"()": "gcloud.core.logging.TraceIDInjectFilter"}}
        )
        handler_filter_injection(["trace_id_inject_filter"])
        trace_format = "[trace_id]: %(trace_id)s"
    inject_logging_trace_info(logging_dict, ("verbose",), trace_format)


def monitor_report_config():
    boot_cmd = " ".join(sys.argv)
    if "celery worker" in boot_cmd:
        try:
            q_conf_index = sys.argv.index("-Q")
        except ValueError as e:
            sys.stdout.write(
                "[!]can't found -Q option in command: %s, skip celery monitor report config: %s\n" % (boot_cmd, e)
            )
            return

        try:
            queues = sys.argv[q_conf_index + 1]
        except IndexError as e:
            sys.stdout.write(
                "[!]can't found -Q value in command: %s, skip celery monitor report config: %s\n" % (boot_cmd, e)
            )
            return

        # 只对存在以下队列的情况进行上报
        monitor_queues = ["er_execute", "er_schedule", "timeout_node"]
        if not any([monitor_queue in queues for monitor_queue in monitor_queues]):
            sys.stdout.write("[!]can't found er queue in command: %s, skip celery monitor report config\n" % boot_cmd)
            return

        from bk_monitor_report import MonitorReporter  # noqa
        from bk_monitor_report.contrib.celery import MonitorReportStep  # noqa
        from blueapps.core.celery import celery_app  # noqa

        reporter = MonitorReporter(
            data_id=env.BK_MONITOR_REPORT_DATA_ID,  # 监控 Data ID
            access_token=env.BK_MONITOR_REPORT_ACCESS_TOKEN,  # 自定义上报 Token
            target=env.BK_MONITOR_REPORT_TARGET,  # 上报唯一标志符
            url=env.BK_MONITOR_REPORT_URL,  # 上报地址
            report_interval=env.BK_MONITOR_REPORT_INTERVAL,  # 上报周期，秒
            chunk_size=env.BK_MONITOR_REPORT_CHUNK_SIZE,  # 上报指标分块大小
        )

        # 针对多进程worker需要做特殊梳理，在worker进程中进行reporter start
        prefork_config_check = [("-P", "-P prefork"), ("--pool", "--pool=prefork")]
        if any([config[0] in boot_cmd and config[1] not in boot_cmd for config in prefork_config_check]):
            MonitorReportStep.setup_reporter(reporter)
            celery_app.steps["worker"].add(MonitorReportStep)
        else:
            from celery.signals import worker_process_init  # noqa

            worker_process_init.connect(reporter.start, weak=False)

    elif "gunicorn wsgi" or "node_timeout_process" in boot_cmd:
        from bk_monitor_report import MonitorReporter  # noqa

        reporter = MonitorReporter(
            data_id=env.BK_MONITOR_REPORT_DATA_ID,  # 监控 Data ID
            access_token=env.BK_MONITOR_REPORT_ACCESS_TOKEN,  # 自定义上报 Token
            target=env.BK_MONITOR_REPORT_TARGET,  # 上报唯一标志符
            url=env.BK_MONITOR_REPORT_URL,  # 上报地址
            report_interval=env.BK_MONITOR_REPORT_INTERVAL,  # 上报周期，秒
            chunk_size=env.BK_MONITOR_REPORT_CHUNK_SIZE,  # 上报指标分块大小
        )
        reporter.start()

    else:
        sys.stdout.write("[!]unknown boot cmd: %s, skip monitor report config\n" % boot_cmd)


# 自定义上报监控配置
if env.BK_MONITOR_REPORT_ENABLE:
    monitor_report_config()

CELERY_SEND_EVENTS = env.CELERY_SEND_EVENTS

ENABLE_OTEL_TRACE = env.ENABLE_OTEL_TRACE

BK_APP_OTEL_INSTRUMENT_DB_API = env.BK_APP_OTEL_INSTRUMENT_DB_API

# 系统访问地址
BK_SOPS_HOST = env.BK_SOPS_HOST

# REDIS 过期时间节点池 KEY
EXECUTING_NODE_POOL = "sops_executing_node_pool"

# 节点超时最长配置时间
MAX_NODE_EXECUTE_TIMEOUT = 60 * 60 * 24

# 蓝鲸插件开发地址
BK_PLUGIN_DEVELOP_URL = env.BK_PLUGIN_DEVELOP_URL

# 蓝鲸插件授权过滤 APP
PLUGIN_DISTRIBUTOR_NAME = env.PLUGIN_DISTRIBUTOR_NAME or APP_CODE

# IAM APIGW 地址
BK_IAM_APIGW_HOST = env.BK_IAM_APIGW_HOST

# 节点日志持久化时间
LOG_PERSISTENT_DAYS = env.BK_NODE_LOG_PERSISTENT_DAYS

# 启动节点日志数据源拉取
NODE_LOG_DATA_SOURCE = env.NODE_LOG_DATA_SOURCE
NODE_LOG_DATA_SOURCE_CONFIG = env.NODE_LOG_DATA_SOURCE_CONFIG
PAASV3_APIGW_API_TOKEN = env.PAASV3_APIGW_API_TOKEN

# requests请求尝试重试次数
REQUEST_RETRY_NUMBER = env.REQUEST_RETRY_NUMBER

# 请求默认重定向配置
NEED_HTTP_REDIRECT = env.NEED_HTTP_REDIRECT
DEFAULT_REDIRECT_HOST = env.DEFAULT_REDIRECT_HOST
REDIRECT_HOSTS = env.REDIRECT_HOSTS.split(",") if env.REDIRECT_HOSTS else []
NOT_REDIRECT_HOSTS = env.NOT_REDIRECT_HOSTS.split(",") if env.NOT_REDIRECT_HOSTS else []

# 数据清理相关
EXPIRED_TASK_CLEAN = env.EXPIRED_TASK_CLEAN
EXPIRED_TASK_CLEAN_NUM_LIMIT = env.EXPIRED_TASK_CLEAN_NUM_LIMIT
TASK_EXPIRED_MONTH = env.TASK_EXPIRED_MONTH
MAX_EXPIRED_SESSION_CLEAN_NUM = env.MAX_EXPIRED_SESSION_CLEAN_NUM
EXPIRED_SESSION_CLEAN_CRON = env.EXPIRED_SESSION_CLEAN_CRON

# V2引擎任务清理配置
ENABLE_CLEAN_EXPIRED_V2_TASK = env.ENABLE_CLEAN_EXPIRED_V2_TASK
CLEAN_EXPIRED_V2_TASK_CRON = env.CLEAN_EXPIRED_V2_TASK_CRON
V2_TASK_VALIDITY_DAY = env.V2_TASK_VALIDITY_DAY
CLEAN_EXPIRED_V2_TASK_BATCH_NUM = env.CLEAN_EXPIRED_V2_TASK_BATCH_NUM
CLEAN_EXPIRED_V2_TASK_INSTANCE = env.CLEAN_EXPIRED_V2_TASK_INSTANCE

# 是否启动swagger ui
ENABLE_SWAGGER_UI = env.ENABLE_SWAGGER_UI

# 流程最高嵌套层数
TEMPLATE_MAX_RECURSIVE_NUMBER = env.TEMPLATE_MAX_RECURSIVE_NUMBER
