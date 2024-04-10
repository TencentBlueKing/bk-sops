# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import time
import traceback
from contextlib import contextmanager
from time import monotonic

from blueapps.contrib.celery_tools.periodic import periodic_task
from celery import current_app
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.utils import timezone
from pipeline.contrib.periodic_task.djcelery.tzcrontab import TzAwareCrontab
from pipeline.engine.core.data.api import _backend, _candidate_backend
from pipeline.engine.core.data.redis_backend import RedisDataBackend

from gcloud import exceptions
from gcloud.conf import settings
from gcloud.core.project import sync_projects_from_cmdb

logger = logging.getLogger("celery")

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
def cmdb_business_sync_task():
    task_id = cmdb_business_sync_task.request.id
    with redis_lock(LOCK_ID, task_id) as acquired:
        if acquired:
            logger.info("Start sync business from cmdb...")
            try:
                sync_projects_from_cmdb(username=settings.SYSTEM_USE_API_ACCOUNT, use_cache=False)
            except exceptions.APIError as e:
                logger.error(
                    "An error occurred when sync cmdb business, message: {msg}, trace: {trace}".format(
                        msg=str(e), trace=traceback.format_exc()
                    )
                )
        else:
            logger.info("Can not get sync_business lock, sync operation abandon")


@periodic_task(run_every=TzAwareCrontab(**settings.EXPIRED_SESSION_CLEAN_CRON))
def clean_django_sessions():
    """
    Clean expired sessions from the database.
    采用小批量删除方式，防止存量数据过大的情况
    """
    logger.info("Start clean django sessions...")
    start_time = time.time()
    try:
        max_clean_num = settings.MAX_EXPIRED_SESSION_CLEAN_NUM
        session_keys = list(
            Session.objects.filter(expire_date__lt=timezone.now()).values_list("session_key", flat=True)[:max_clean_num]
        )
        result = Session.objects.filter(session_key__in=session_keys).delete()
        logger.info(f"Clean django sessions result: {result}, cost time: {time.time() - start_time}")
    except Exception as e:
        logger.exception(f"Clean django sessions error: {e}")


@current_app.task
def migrate_pipeline_parent_data_task():
    """
    将 pipeline 的 schedule_parent_data 从 _backend(redis) 迁移到 _candidate_backend(mysql)
    """
    if not isinstance(_backend, RedisDataBackend):
        logger.error("[migrate_pipeline_parent_data] _backend should be RedisDataBackend")
        return

    if _candidate_backend is None:
        logger.error(
            "[migrate_pipeline_parent_data]_candidate_backend is None, "
            "please set env variable(BKAPP_PIPELINE_DATA_CANDIDATE_BACKEND) first"
        )
        return

    r = settings.redis_inst
    pipeline_data_keys = list(r.scan_iter("*_schedule_parent_data"))
    keys_len = len(pipeline_data_keys)
    logger.info("[migrate_pipeline_parent_data] start to migrate {} keys.".format(keys_len))
    for i, key in enumerate(pipeline_data_keys, 1):
        try:
            logger.info("[migrate_pipeline_parent_data] process[{}/{}]".format(i, keys_len))
            value = _backend.get_object(key)
            _candidate_backend.set_object(key, value)
            r.expire(key, 60 * 60 * 24)  # expire in 1 day
        except Exception:
            logger.exception("[migrate_pipeline_parent_data] {} key migrate err.".format(i))

    logger.info("[migrate_pipeline_parent_data] migrate done!")
