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

from functools import wraps

from django.http.response import JsonResponse
from django.utils.decorators import available_attrs

from gcloud import err_code
from .validate import RequestValidator


def request_validate(validator_cls, data_field):

    if not issubclass(validator_cls, RequestValidator):
        raise TypeError("validator_cls must be subclass of {}".format("gcloud.utils.validate.RequestValidator"))

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):

            is_valid, err = validator_cls().validate(request, *args, **kwargs)
            if not is_valid:
                return JsonResponse(
                    {"result": False, "message": err, "data": None, "code": err_code.REQUEST_PARAM_INVALID}
                )

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
