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
import functools

import ujson as json
from cachetools.keys import hashkey
from django.core.handlers.wsgi import WSGIRequest

from gcloud.core.models import Project
from gcloud.apigw.constants import PROJECT_SCOPE_CMDB_BIZ


def get_project_with(obj_id, scope):
    get_filters = {}
    if scope == PROJECT_SCOPE_CMDB_BIZ:
        get_filters.update({"bk_biz_id": obj_id, "from_cmdb": True})
    else:
        get_filters.update({"id": obj_id})

    return Project.objects.get(**get_filters)


def deal_request_args(with_project_id, *args):
    new_args = args
    project_id = None
    for idx, arg in enumerate(args):
        if isinstance(arg, WSGIRequest):
            request = arg
            if request.method == "GET":
                request_params = str(sorted(request.GET.items()))
            elif request.method == "POST":
                params = json.loads(request.body)
                request_params = str(sorted(params.items()))
            else:
                break
            request_tag = "path:{},user:{},params:{}".format(request.path, request.user.username, request_params)
            new_args = args[:idx] + (request_tag,) + args[idx + 1 :]
            if with_project_id and hasattr(request, "project"):
                project_id = request.project.id
            break
    return new_args, project_id


def api_hash_key(*args, **kwargs):
    """参考cachetools hashkey实现，对WSGIRequest参数对象进行特殊处理"""
    new_args, _ = deal_request_args(False, *args)
    return hashkey(*new_args, **kwargs)


def api_bucket_and_key(*args, **kwargs):
    new_args, project_id = deal_request_args(True, *args)
    key = hashkey(*new_args, **kwargs)
    bucket = "default" if project_id is None else project_id
    return bucket, key


class BucketTTLCache:
    """基于业务分桶的TTLCache"""

    def __init__(self, cache_cls, cache_kwargs):
        self._buckets = {}
        self.cache_cls = cache_cls
        self.cache_kwargs = cache_kwargs

    def set_value(self, bucket, key, value):
        self._buckets.setdefault(bucket, self.cache_cls(**self.cache_kwargs))[key] = value

    def get_value(self, bucket, key):
        return self._buckets[bucket][key]

    def __str__(self):
        return str(self._buckets)


def bucket_cached(bucket_cache, bucket_and_key_func, lock=None):
    """Decorator to wrap a function with a memoizing callable that saves
    results in a cache.
    """

    def decorator(func):
        if bucket_cache is None:

            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

        elif lock is None:

            def wrapper(*args, **kwargs):
                bucket, key = bucket_and_key_func(*args, **kwargs)
                try:
                    return bucket_cache.get_value(bucket, key)
                except KeyError:
                    pass  # key not found
                value = func(*args, **kwargs)
                try:
                    bucket_cache.set_value(bucket, key, value)
                except ValueError:
                    pass  # value too large
                return value

        else:

            def wrapper(*args, **kwargs):
                bucket, key = bucket_and_key_func(*args, **kwargs)
                try:
                    with lock:
                        return bucket_cache.get_value(bucket, key)
                except KeyError:
                    pass  # key not found
                value = func(*args, **kwargs)
                try:
                    with lock:
                        bucket_cache.set_value(bucket, key, value)
                except ValueError:
                    pass  # value too large
                return value

        return functools.update_wrapper(wrapper, func)

    return decorator
