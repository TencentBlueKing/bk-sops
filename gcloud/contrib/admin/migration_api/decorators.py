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

from functools import wraps

from django.conf import settings
from django.http import HttpResponseForbidden

import env


def require_migrate_token(view_func):
    @wraps(view_func)
    def decorator(request, *args, **kwargs):
        if not env.MIGRATE_ALLOW or not (request.META.get("HTTP_SOPS_MIGRATE_TOKEN") == settings.MIGRATE_TOKEN):
            return HttpResponseForbidden("invalid migarte token")

        return view_func(request, *args, **kwargs)

    return decorator
