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

superuser command
"""

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

from gcloud.core.decorators import check_is_superuser


@check_is_superuser()
def delete_cache_key(request, key):
    cache.delete(key)
    return JsonResponse({'result': True, 'data': 'success'})


@check_is_superuser()
def get_cache_key(request, key):
    data = cache.get(key)
    return JsonResponse({'result': True, 'data': data})


@check_is_superuser()
def get_settings(request):
    data = {s: getattr(settings, s) for s in dir(settings)}
    return JsonResponse({'result': True, 'data': data})
