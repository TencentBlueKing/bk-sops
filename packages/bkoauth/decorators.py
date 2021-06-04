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

import os
from functools import wraps

from django.http import JsonResponse
from django.utils.decorators import available_attrs
from .utils import FancyDict

try:
    from bkoauth.jwt_client import JWTClient, jwt_invalid_view
except ImportError:
    from packages.bkoauth.jwt_client import JWTClient, jwt_invalid_view


def apigw_required(view_func):
    """apigw装饰器
    """

    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):

        request.jwt = JWTClient(request)
        if "BKAPP_API_JWT_EXEMPT" in os.environ:
            request.jwt.user = FancyDict({"bk_username": request.META.get("HTTP_BK_USERNAME")})
            request.jwt.app = FancyDict({"bk_app_code": request.META.get("HTTP_BK_APP_CODE")})

        else:
            if not request.jwt.is_valid:
                return jwt_invalid_view(request)

        result = view_func(request, *args, **kwargs)

        # 如果返回的是dict且request中有trace_id，则在响应中加上
        if isinstance(result, dict):
            if hasattr(request, "trace_id"):
                result["trace_id"] = request.trace_id
            result = JsonResponse(result)
        return result

    return _wrapped_view
