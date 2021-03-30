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

import django
from django.shortcuts import redirect
import version_log.config as config
from version_log.models import VersionLogVisited

# 兼容低版本Django
if django.VERSION < (1, 10):
    from django.core.urlresolvers import reverse
    MiddlewareMixin = object
else:
    from django.urls import reverse
    from django.utils.deprecation import MiddlewareMixin


class VersionLogMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        """根据用户是否看过最新版本日志，判断是否需要跳转到版本日志页"""

        # 是否是用户请求的页面
        # 防止接口请求、302、403等被重定向到日志页面
        is_user_page = (
            request.method == "GET"
            and response.status_code == 200
            and "text/html" in response["Content-Type"]
        )

        # 是否有版本日志
        has_version = config.LATEST_VERSION is not None

        try:
            # 用户名是否为空
            is_user_empty = not request.user.username
            # 用户是否以及被加入缓存
            user_in_cache = request.user.username in config.USER_CACHE
        except AttributeError:
            # 获取不到用户，说明没有登录
            is_user_empty = True
            user_in_cache = False

        # 不需要处理的情况，直接返回
        if not is_user_page or not config.LATEST_VERSION_INFORM or user_in_cache or is_user_empty or not has_version:
            return response

        username = request.user.username
        config.USER_CACHE.add(username)
        # 判断是是否有新版本需要通知
        if VersionLogVisited.objects.has_visit_latest(username, config.LATEST_VERSION):
            return response

        # 如果最新版本通知开启且缓存和数据库中用户对应版本不是最新，则跳转版本日志页面
        VersionLogVisited.objects.update_visit_version(username, config.LATEST_VERSION)

        if config.LATEST_VERSION_INFORM_TYPE == "redirect":
            # 重定向模式，重定向到版本日志页面
            return redirect(reverse('version_log_page'))
        elif config.LATEST_VERSION_INFORM_TYPE == "popup":
            # 弹窗模式，通过Cookie控制应用页面弹窗
            response.set_cookie("SHOW_VERSION_LOG", "True", path="/")

        return response
