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

from gcloud import err_code
from gcloud.core.decorators import check_is_superuser
from gcloud.core.tasks import migrate_pipeline_parent_data_task


@check_is_superuser()
def delete_cache_key(request, key):
    cache.delete(key)
    return JsonResponse({"result": True, "code": err_code.SUCCESS.code, "data": "success"})


@check_is_superuser()
def get_cache_key(request, key):
    data = cache.get(key)
    return JsonResponse({"result": True, "code": err_code.SUCCESS.code, "data": data})


@check_is_superuser()
def get_settings(request):
    data = {s: getattr(settings, s) for s in dir(settings)}
    return JsonResponse({"result": True, "code": err_code.SUCCESS.code, "data": data})


@check_is_superuser()
def migrate_pipeline_parent_data(request):
    """
    @summary: 将 pipeline 的 schedule_parent_data 从 _backend(redis) 迁移到 _candidate_backend(mysql)
    @param request:
    @return:
    """
    migrate_pipeline_parent_data_task.apply_async()
    return JsonResponse({"reuslt": True, "data": None, "message": "migrte start."})
