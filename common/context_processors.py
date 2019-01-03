# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
context_processor for common(setting)

** 除setting外的其他context_processor内容，均采用组件的方式(string)
"""
from django.conf import settings


def mysetting(request):
    return {
            'MEDIA_URL': settings.MEDIA_URL,                              # MEDIA_URL
            'STATIC_URL': settings.STATIC_URL,                            # 本地静态文件访问
            'APP_PATH': request.get_full_path(),                             # 当前页面，主要为了login_required做跳转用
            'RUN_MODE': settings.RUN_MODE,                                # 运行模式
            'APP_CODE': settings.APP_CODE,                                   # 在蓝鲸系统中注册的  "应用编码"
            'SITE_URL': settings.SITE_URL,                                     # URL前缀
            'REMOTE_STATIC_URL': settings.REMOTE_STATIC_URL,   # 远程静态资源url
            'STATIC_VERSION': settings.STATIC_VERSION,               # 静态资源版本号,用于指示浏览器更新缓存
            'BK_URL': settings.BK_URL,                                          # 蓝鲸平台URL
            'NICK': request.session.get('nick', ''),                             # 用户昵称
            'AVATAR': request.session.get('avatar', ''),
            'USERNAME': request.user.username,
            }
