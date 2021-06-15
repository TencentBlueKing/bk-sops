# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from django.utils.decorators import available_attrs
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from version_log.models import VersionLogVisited
import version_log.config as config

"""
@summary: 装饰器
@usage：
          >>> from version_log.decorators import update_log_view
          >>> @update_log_view
          >>> def home(request):
          >>>     pass
"""
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps

logger = logging.getLogger(__name__)


def update_log_view(view_func):
    """
    版本更新检查装饰器,如果用户未访问过最新版本日志页面, 会自动跳转日志查看页面
    """
    def wrapped_view(*args, **kwargs):
        username = ''
        for arg in args:
            if hasattr(arg, 'user'):
                username = arg.user.username
                break
        # 不在缓存中及 username 为空时, 不跳转
        if username in (config.USER_CACHE, ''):
            return view_func(*args, **kwargs)

        # 有过访问记录, 不跳转
        if VersionLogVisited.objects.has_visit_latest(username, config.LATEST_VERSION):
            return view_func(*args, **kwargs)

        # 如果最新版本通知开启且缓存和数据库中用户对应版本不是最新，则跳转版本日志页面
        VersionLogVisited.objects.update_visit_version(username, config.LATEST_VERSION)
        if config.LATEST_VERSION is not None:
            # 非 debug 环境才加访问缓存, 便于 dev 时查看测试
            if settings.DEBUG:
                config.USER_CACHE.add(username)
            return redirect(reverse('version_log_page'))

        # 正常情况:用户已经看过最新日志,正常返回视图函数
        return view_func(*args, **kwargs)

    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)
