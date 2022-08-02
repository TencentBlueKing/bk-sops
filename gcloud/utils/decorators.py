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
import time
from functools import wraps

from django.http.response import JsonResponse

from gcloud import err_code
from .validate import RequestValidator


def request_validate(validator_cls):

    if not issubclass(validator_cls, RequestValidator):
        raise TypeError("validator_cls must be subclass of {}".format("gcloud.utils.validate.RequestValidator"))

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            is_valid, err = validator_cls().validate(request, *args, **kwargs)
            if not is_valid:
                return JsonResponse(
                    {"result": False, "message": err, "data": None, "code": err_code.REQUEST_PARAM_INVALID.code}
                )

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def time_record(logger):
    """记录装饰函数的执行时间，并打印到日志中"""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(*args, **kwargs):
            start_time = time.time()
            result = view_func(*args, **kwargs)
            end_time = time.time()
            logger.info(f"[{view_func.__name__} time_record] cost time: {end_time - start_time}, result: {result}")
            return result

        return _wrapped_view

    return decorator
