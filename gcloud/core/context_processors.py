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

context_processor for common(setting)
** 除setting外的其他context_processor内容，均采用组件的方式(string)
"""

import os
import logging

from django.utils.translation import ugettext_lazy as _

from gcloud.conf import settings
from gcloud.core.api_adapter import is_user_functor, is_user_auditor
from gcloud.core.project import get_default_project_for_user

logger = logging.getLogger("root")


def get_cur_pos_from_url(request):
    """
    @summary: 返回公共变量给前端导航
    """
    site_url = settings.SITE_URL
    app_path = request.path
    # 首页
    if app_path == site_url:
        cur_pos = ''
    else:
        relative_path = app_path.split(site_url, 1)[1]
        path_list = relative_path.split('/')
        cur_pos = path_list[0]
    return cur_pos


def mysetting(request):
    # 嵌入CICD，隐藏头部
    hide_header = int(request.GET.get('hide_header', '0') == '1')
    is_superuser = int(request.user.is_superuser)
    is_functor = int(is_user_functor(request))
    is_auditor = int(is_user_auditor(request))
    default_project = get_default_project_for_user(request.user.username)
    project_timezone = request.session.get('blueking_timezone', settings.TIME_ZONE)
    cur_pos = get_cur_pos_from_url(request)
    ctx = {
        'MEDIA_URL': settings.MEDIA_URL,  # MEDIA_URL
        'STATIC_URL': settings.STATIC_URL,  # 本地静态文件访问
        'BK_PAAS_HOST': settings.BK_PAAS_HOST,
        'BK_CC_HOST': settings.BK_CC_HOST,
        'BK_JOB_HOST': settings.BK_JOB_HOST,
        'BK_IAM_SAAS_HOST': settings.BK_IAM_SAAS_HOST,
        'BK_USER_MANAGE_HOST': settings.BK_USER_MANAGE_HOST,
        'APP_PATH': request.get_full_path(),  # 当前页面，主要为了login_required做跳转用
        'LOGIN_URL': settings.LOGIN_URL,  # 登录链接
        'RUN_MODE': settings.RUN_MODE,  # 运行模式
        'APP_CODE': settings.APP_CODE,  # 在蓝鲸系统中注册的  "应用编码"
        'APP_NAME': settings.APP_NAME,  # 应用名称
        'SITE_URL': settings.SITE_URL,  # URL前缀
        'REMOTE_STATIC_URL': settings.REMOTE_STATIC_URL,  # 远程静态资源url
        'STATIC_VERSION': settings.STATIC_VERSION,  # 静态资源版本号,用于指示浏览器更新缓存
        'BK_URL': settings.BK_URL,  # 蓝鲸平台URL
        'gettext': _,  # 国际化
        '_': _,  # 国际化
        'LANGUAGES': settings.LANGUAGES,  # 国际化

        # 自定义变量
        'OPEN_VER': settings.OPEN_VER,
        'RUN_VER': settings.RUN_VER,
        'RUN_VER_NAME': settings.RUN_VER_NAME,
        'REMOTE_ANALYSIS_URL': settings.REMOTE_ANALYSIS_URL,
        'REMOTE_API_URL': settings.REMOTE_API_URL,
        'USERNAME': request.user.username,
        # 'NICK': request.session.get('nick', ''),          # 用户昵称
        'NICK': request.user.username,  # 用户昵称
        'AVATAR': request.session.get('avatar', ''),  # 用户头像
        'CUR_POS': cur_pos,
        'RSA_PUB_KEY': settings.RSA_PUB_KEY,
        'STATIC_VER': settings.STATIC_VER[settings.RUN_MODE],

        'import_v1_flag': 1 if settings.IMPORT_V1_TEMPLATE_FLAG else 0,
        'HIDE_HEADER': hide_header,
        'IS_SUPERUSER': is_superuser,
        'IS_FUNCTOR': is_functor,
        'IS_AUDITOR': is_auditor,
        'PROJECT_TIMEZONE': project_timezone,
        'DEFAULT_PROJECT_ID': default_project.id if default_project else '',
        'FILE_UPLOAD_ENTRY': os.getenv('BKAPP_FILE_UPLOAD_ENTRY', '')
    }

    return ctx
