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

from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler


class BkWSGIHandler(WSGIHandler):
    def __call__(self, environ, start_response):
        script_name = environ.get("HTTP_X_SCRIPT_NAME")
        if script_name is not None:
            if script_name == "/":
                # '/'的含义：独立域名，不启用script_name
                script_name = ""
            environ["SCRIPT_NAME"] = script_name
            settings.FORCE_SCRIPT_NAME = settings.SITE_URL = "%s/" % script_name.rstrip("/")

            # 如果没有独立域名的配置，需要不断的适配，否则可以直接使用
            if not settings.STATIC_URL.startswith("http"):
                settings.STATIC_URL = "%sstatic/" % settings.SITE_URL
        return super(BkWSGIHandler, self).__call__(environ, start_response)
