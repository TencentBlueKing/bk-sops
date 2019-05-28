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

import traceback

from pipeline.conf import settings
from pipeline.engine.exceptions import InvalidDataBackendError
from django.utils.module_loading import import_string

__all__ = [
    'set_object',
    'get_object',
    'del_object',
    'expire_cache',
    'cache_for',
    'set_schedule_data',
    'get_schedule_parent_data',
    'delete_parent_data',
]

__backend = None

if not __backend:
    try:
        backend_cls = import_string(settings.PIPELINE_DATA_BACKEND)
        __backend = backend_cls()
    except ImportError as e:
        raise InvalidDataBackendError('data backend(%s) import error with exception: %s' % (
            settings.PIPELINE_DATA_BACKEND, traceback.format_exc(e)))


def set_object(key, obj):
    return __backend.set_object(key, obj)


def get_object(key):
    return __backend.get_object(key)


def del_object(key):
    return __backend.del_object(key)


def expire_cache(key, value, expires):
    return __backend.expire_cache(key, value, expires)


def cache_for(key):
    return __backend.cache_for(key)


def set_schedule_data(schedule_id, parent_data):
    return __backend.set_object('%s_schedule_parent_data' % schedule_id, parent_data)


def get_schedule_parent_data(schedule_id):
    return __backend.get_object('%s_schedule_parent_data' % schedule_id)


def delete_parent_data(schedule_id):
    return __backend.del_object('%s_schedule_parent_data' % schedule_id)
