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
import traceback
from contextlib import contextmanager

from django.core.cache import cache
from celery import task
from celery.five import monotonic
from celery.decorators import periodic_task

from gcloud import exceptions
from gcloud.conf import settings
from gcloud.core.project import sync_projects_from_cmdb

from pipeline.engine.core.data.api import _backend, _candidate_backend
from pipeline.engine.core.data.redis_backend import RedisDataBackend
from pipeline.contrib.periodic_task.djcelery.tzcrontab import TzAwareCrontab

loggger = logging.getLogger("celery")

LOCK_EXPIRE = 60 * 10
LOCK_ID = "cmdb_business_sync_lock"


@contextmanager
def redis_lock(lock_id, task_id):
    timeout_at = monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    status = cache.add(lock_id, task_id, LOCK_EXPIRE)
    try:
        yield status
    finally:
        # advantage of using add() for atomic locking
        if monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)


@periodic_task(run_every=TzAwareCrontab(minute="*/2"))
def cmdb_business_sync_task(task_id):
    with redis_lock(LOCK_ID, task_id) as acquired:
        if acquired:
            loggger.info("Start sync business from cmdb...")
            try:
                sync_projects_from_cmdb(username=settings.SYSTEM_USE_API_ACCOUNT, use_cache=False)
            except exceptions.APIError as e:
                loggger.error(
                    "An error occurred when sync cmdb business, message: {msg}, trace: {trace}".format(
                        msg=str(e), trace=traceback.format_exc()
                    )
                )
        else:
            loggger.info("Can not get sync_business lock, sync operation abandon")


@task
def migrate_pipeline_parent_data_task():
    """
    将 pipeline 的 schedule_parent_data 从 _backend(redis) 迁移到 _candidate_backend(mysql)
    """
    if not isinstance(_backend, RedisDataBackend):
        loggger.error("[migrate_pipeline_parent_data] _backend should be RedisDataBackend")
        return

    if _candidate_backend is None:
        loggger.error(
            "[migrate_pipeline_parent_data]_candidate_backend is None, "
            "please set env variable(BKAPP_PIPELINE_DATA_CANDIDATE_BACKEND) first"
        )
        return

    r = settings.redis_inst
    pipeline_data_keys = list(r.scan_iter("*_schedule_parent_data"))
    keys_len = len(pipeline_data_keys)
    loggger.info("[migrate_pipeline_parent_data] start to migrate {} keys.".format(keys_len))
    for i, key in enumerate(pipeline_data_keys, 1):
        try:
            loggger.info("[migrate_pipeline_parent_data] process[{}/{}]".format(i, keys_len))
            value = _backend.get_object(key)
            _candidate_backend.set_object(key, value)
            r.expire(key, 60 * 60 * 24)  # expire in 1 day
        except Exception:
            loggger.exception("[migrate_pipeline_parent_data] {} key migrate err.".format(i))

    loggger.info("[migrate_pipeline_parent_data] migrate done!")
