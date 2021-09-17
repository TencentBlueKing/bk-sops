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
import time
from contextlib import contextmanager
from uuid import uuid4

from django.conf import settings
from redis.exceptions import LockError

MAX_RETRY = getattr(settings, "REDIS_LOCK_MAX_RETRY", None) or 500


@contextmanager
def redis_lock(redis_instance, key):
    lock_key = "lock_{}".format(key)
    lock_id = str(uuid4())
    try:
        lock_acquired = acquire_redis_lock(redis_instance, lock_key, lock_id)
        err = (
            None
            if lock_acquired
            else LockError(f"Unable to acquire redis lock in max tries, lock key: {lock_key}, lock_id: {lock_id}")
        )
        yield lock_acquired, err
    finally:
        release_redis_lock(redis_instance, lock_key, lock_id)


def acquire_redis_lock(redis_instance, lock_key, lock_id):
    cnt = 1
    while cnt < MAX_RETRY:
        if redis_instance.set(lock_key, lock_id, ex=5, nx=True):
            return True
        cnt += 1
        time.sleep(0.01)
    return False


def release_redis_lock(redis_instance, lock_key, lock_id):
    lock_value = redis_instance.get(lock_key)
    # 兼容不同模式的redis
    lock_value = lock_value.decode() if isinstance(lock_value, bytes) else lock_value
    if lock_value == lock_id:
        redis_instance.delete(lock_key)
