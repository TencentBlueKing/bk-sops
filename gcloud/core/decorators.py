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

from functools import wraps

from django.http import HttpResponseForbidden
from django.utils.decorators import available_attrs

from gcloud.core.models import Business


def check_user_perm_of_business(permit):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            biz_cc_id = kwargs.get('biz_cc_id') or kwargs.get('bk_biz_id')
            if biz_cc_id is None:
                params = getattr(request, request.method)
                biz_cc_id = params.get('biz_cc_id') or params.get('bk_biz_id')
            try:
                biz = Business.objects.get(cc_id=biz_cc_id)
            except Business.DoesNotExist:
                return HttpResponseForbidden()
            if not request.user.has_perm(permit, biz):
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def check_is_superuser():
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_superuser:
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
