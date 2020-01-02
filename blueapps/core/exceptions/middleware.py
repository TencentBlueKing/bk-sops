# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import json
import logging
import traceback

from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from blueapps.core.exceptions.base import BlueException

try:
    from raven.contrib.django.raven_compat.models import \
        sentry_exception_handler
# 兼容未有安装sentry的情况
except ImportError:
    sentry_exception_handler = None

logger = logging.getLogger('blueapps')


class AppExceptionMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        """
        app后台错误统一处理
        """

        # 用户自我感知的异常抛出
        if isinstance(exception, BlueException):
            logger.warning(
                (u"""捕获主动抛出异常, 具体异常堆栈->[%s] status_code->[%s] & """
                 u"""client_message->[%s] & args->[%s] """) % (
                    traceback.format_exc(),
                    exception.error_code,
                    exception.message,
                    exception.args
                )
            )

            response = JsonResponse({
                'status_code': exception.error_code,
                'message': exception.message
            })

            response.status_code = exception.error_code // 100
            return response

        # 用户未主动捕获的异常
        logger.error(
            (u"""捕获未处理异常,异常具体堆栈->[%s], 请求URL->[%s], """
             u"""请求方法->[%s] 请求参数->[%s]""") % (
                traceback.format_exc(),
                request.path,
                request.method,
                json.dumps(getattr(request, request.method, None))
            )
        )

        # 判断是否在debug模式中,
        # 在这里判断是防止阻止了用户原本主动抛出的异常
        if settings.DEBUG:
            return None

        response = JsonResponse({
            'status_code': 50000,
            'message': u"系统异常,请联系管理员处理"
        })
        response.status_code = 500

        # notify sentry
        if sentry_exception_handler is not None:
            sentry_exception_handler(request=request)

        return response
