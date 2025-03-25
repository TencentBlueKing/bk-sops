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

context_processor for common(setting)
** 除setting外的其他context_processor内容，均采用组件的方式(string)
"""
import json
import logging
import os

from bkcrypto.asymmetric.configs import KeyConfig as AsymmetricKeyConfig
from django.utils.translation import gettext_lazy as _

import env
from gcloud.conf import settings
from gcloud.core.api_adapter import is_user_auditor, is_user_functor
from gcloud.core.models import EnvironmentVariables
from gcloud.core.project import get_default_project_for_user
from gcloud.utils.crypto import get_default_asymmetric_key_config

logger = logging.getLogger("root")


def get_cur_pos_from_url(request):
    """
    @summary: 返回公共变量给前端导航
    """
    site_url = settings.SITE_URL
    app_path = request.path
    # 首页
    if app_path == site_url:
        cur_pos = ""
    else:
        relative_path = app_path.split(site_url, 1)[1]
        path_list = relative_path.split("/")
        cur_pos = path_list[0]
    return cur_pos


def mysetting(request):
    # 嵌入CICD，隐藏头部
    language = request.COOKIES.get("blueking_language", "zh-cn")
    doc_lang_mappings = {"zh-cn": "ZH", "en": "EN"}
    run_ver_key = "BKAPP_RUN_VER_NAME" if language == "zh-cn" else "BKAPP_RUN_VER_NAME_{}".format(language.upper())
    file_manager_type = "BKAPP_FILE_MANAGER_TYPE"
    hide_header = int(request.GET.get("hide_header", "0") == "1")
    is_superuser = int(request.user.is_superuser)
    is_functor = int(is_user_functor(request))
    is_auditor = int(is_user_auditor(request))
    default_project = get_default_project_for_user(request.user.username, request.user.tenant_id)
    project_timezone = request.session.get("blueking_timezone", settings.TIME_ZONE)
    cur_pos = get_cur_pos_from_url(request)
    frontend_entry_url = "{}bk_sops".format(settings.STATIC_URL) if settings.RUN_VER == "open" else "/static/bk_sops"
    default_asymmetric_key_config: AsymmetricKeyConfig = get_default_asymmetric_key_config(
        settings.BKCRYPTO_ASYMMETRIC_CIPHER_TYPE
    )
    try:
        enable_notice_center = int(EnvironmentVariables.objects.get_var("ENABLE_NOTICE_CENTER", 0))
    except Exception:
        enable_notice_center = 0

    ctx = {
        "MEDIA_URL": settings.MEDIA_URL,  # MEDIA_URL
        "STATIC_URL": settings.STATIC_URL,  # 本地静态文件访问
        "BK_PAAS_HOST": settings.BK_PAAS_HOST,
        "BK_CC_HOST": settings.BK_CC_HOST,
        "BK_JOB_HOST": settings.BK_JOB_HOST,
        "BK_IAM_SAAS_HOST": settings.BK_IAM_SAAS_HOST,
        "BK_IAM_APPLY_URL": settings.BK_IAM_SAAS_HOST.strip("/") + "/apply-join-user-group",
        "BK_IAM_APP_CODE": settings.BK_IAM_APP_CODE,
        "BK_USER_MANAGE_HOST": settings.BK_USER_MANAGE_HOST,
        "BK_PAAS_ESB_HOST": settings.BK_PAAS_ESB_API_HOST,
        "APP_PATH": request.get_full_path(),  # 当前页面，主要为了login_required做跳转用
        "LOGIN_URL": getattr(settings, "BK_LOGIN_URL", os.getenv("BKPAAS_LOGIN_URL")),  # 登录链接
        "RUN_MODE": settings.RUN_MODE,  # 运行模式
        "APP_CODE": settings.APP_CODE,  # 在蓝鲸系统中注册的  "应用编码"
        "APP_NAME": settings.APP_NAME,  # 应用名称
        "SITE_URL": settings.SITE_URL,  # URL前缀
        "REMOTE_STATIC_URL": settings.REMOTE_STATIC_URL,  # 远程静态资源url
        "STATIC_VERSION": settings.STATIC_VERSION,  # 静态资源版本号,用于指示浏览器更新缓存
        "BK_URL": settings.BK_URL,  # 蓝鲸平台URL
        "gettext": _,  # 国际化
        "_": _,  # 国际化
        "LANGUAGES": settings.LANGUAGES,  # 国际化
        # 自定义变量
        "PERIODIC_TASK_SHORTEST_TIME": settings.PERIODIC_TASK_SHORTEST_TIME,
        "OPEN_VER": settings.OPEN_VER,
        "RUN_VER": settings.RUN_VER,
        "RUN_VER_NAME": EnvironmentVariables.objects.get_var(run_ver_key, settings.RUN_VER_NAME),
        "REMOTE_ANALYSIS_URL": settings.REMOTE_ANALYSIS_URL,
        "REMOTE_API_URL": settings.REMOTE_API_URL,
        "ENABLE_TEMPLATE_MARKET": settings.ENABLE_TEMPLATE_MARKET,
        "TEMPLATE_MARKET_HOST": settings.TEMPLATE_MARKET_HOST,
        "TEMPLATE_MARKET_DOC_URL": settings.TEMPLATE_MARKET_DOC_URL,
        "USERNAME": request.user.username,
        # 'NICK': request.session.get('nick', ''),          # 用户昵称
        "NICK": request.user.username,  # 用户昵称
        "AVATAR": request.session.get("avatar", ""),  # 用户头像
        "CUR_POS": cur_pos,
        "ASYMMETRIC_CIPHER_TYPE": settings.BKCRYPTO_ASYMMETRIC_CIPHER_TYPE,
        "ASYMMETRIC_PUBLIC_KEY": json.dumps(default_asymmetric_key_config.public_key_string)[1:-1],
        "ASYMMETRIC_PREFIX": f"{settings.BKCRYPTO_ASYMMETRIC_CIPHER_TYPE.lower()}_str:::",
        # TODO 等待移除
        "RSA_PUB_KEY": settings.RSA_PUB_KEY,
        "STATIC_VER": settings.STATIC_VER[settings.RUN_MODE],
        "import_v1_flag": 1 if settings.IMPORT_V1_TEMPLATE_FLAG else 0,
        "HIDE_HEADER": hide_header,
        "IS_SUPERUSER": is_superuser,
        "IS_FUNCTOR": is_functor,
        "IS_AUDITOR": is_auditor,
        "PROJECT_TIMEZONE": project_timezone,
        "DEFAULT_PROJECT_ID": default_project.id if default_project else "",
        "FILE_UPLOAD_ENTRY": env.BKAPP_FILE_UPLOAD_ENTRY,
        "MEMBER_SELECTOR_DATA_HOST": settings.BK_MEMBER_SELECTOR_DATA_HOST,
        "BK_STATIC_URL": frontend_entry_url,
        "BK_DOC_URL": settings.BK_DOC_URL.format(doc_lang_mappings.get(language, "ZH")),
        "FEEDBACK_URL": settings.FEEDBACK_URL,
        "FILE_MANAGER_TYPE": EnvironmentVariables.objects.get_var(file_manager_type, env.BKAPP_FILE_MANAGER_TYPE),
        "MAX_NODE_EXECUTE_TIMEOUT": settings.MAX_NODE_EXECUTE_TIMEOUT,
        "BK_PLUGIN_DEVELOP_URL": settings.BK_PLUGIN_DEVELOP_URL,
        "ENABLE_IPV6": settings.ENABLE_IPV6,
        "BK_DOMAIN": env.BKPAAS_BK_DOMAIN,
        # 是否开启通知中心
        "ENABLE_NOTICE_CENTER": enable_notice_center,
        "BK_PAAS_SHARED_RES_URL": env.BKPAAS_SHARED_RES_URL,
        "TASK_LIST_STATUS_FILTER_DAYS": settings.TASK_LIST_STATUS_FILTER_DAYS,
        "MESSAGE_HELPER_URL": settings.MESSAGE_HELPER_URL,
        "TASK_STATUS_DISPLAY_VERSION": settings.TASK_STATUS_DISPLAY_VERSION,
    }

    # custom context config
    custom_context = getattr(settings, "CUSTOM_HOME_RENDER_CONTEXT", {})
    if isinstance(custom_context, dict):
        ctx.update(custom_context)

    return ctx
