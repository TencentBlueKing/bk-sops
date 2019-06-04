# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import traceback
import functools

from django.http.response import JsonResponse

logger = logging.getLogger('root')


def post_form_validator(form_cls):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            form = form_cls(request.POST)
            if not form.is_valid():
                return JsonResponse(status=400, data={
                    'result': False,
                    'message': form.errors
                })
            setattr(request, 'form', form)
            return func(request, *args, **kwargs)

        return wrapper

    return decorate


def model_instance_inject(model_cls, inject_attr, field_maps):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            get_kwargs = {}

            for field, arg in field_maps.items():
                field_value = kwargs.get(arg, None)
                if field_value is None:
                    return JsonResponse({
                        'result': False,
                        'message': '[{arg}] can not be null'.format(arg=arg)
                    })
                get_kwargs[field] = field_value

            try:
                instance = model_cls.objects.get(**get_kwargs)
            except Exception as e:
                logger.error(traceback.format_exc())
                return JsonResponse({
                    'result': False,
                    'message': 'get {model_name} error: {exc}'.format(model_name=model_cls.__name__, exc=e.message)
                })

            setattr(request, inject_attr, instance)

            return func(request, *args, **kwargs)

        return wrapper

    return decorate
