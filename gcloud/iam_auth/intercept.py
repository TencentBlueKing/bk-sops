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

import logging
from functools import wraps
from abc import ABCMeta, abstractmethod

from django.utils.decorators import available_attrs

logger = logging.getLogger("root")


class ViewInterceptor(object, metaclass=ABCMeta):
    @abstractmethod
    def process(self, request, *args, **kwargs):
        raise NotImplementedError()


def iam_intercept(interceptor):

    base_class = "gcloud.iam_auth.intercept.ViewInterceptor"
    if not isinstance(interceptor, ViewInterceptor):
        raise TypeError("interceptor's class must be subclass of {}".format(base_class))

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):

            interceptor.process(request, *args, **kwargs)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
