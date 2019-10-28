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
from contextlib import contextmanager

from django.core.cache import cache
from celery.five import monotonic
from celery.decorators import periodic_task

from gcloud import exceptions
from gcloud.conf import settings
from gcloud.core.project import sync_projects_from_cmdb

from pipeline.contrib.periodic_task.djcelery.tzcrontab import TzAwareCrontab

loggger = logging.getLogger('celery')

LOCK_EXPIRE = 60 * 10
LOCK_ID = 'cmdb_business_sync_lock'


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


@periodic_task(run_every=TzAwareCrontab(minute='*/2'))
def cmdb_business_sync_task(task_id):
    with redis_lock(LOCK_ID, task_id) as acquired:
        if acquired:
            loggger.info('Start sync business from cmdb...')
            try:
                sync_projects_from_cmdb(username=settings.SYSTEM_USE_API_ACCOUNT, use_cache=False)
            except exceptions.APIError as e:
                loggger.error('An error occurred when sync cmdb business, message: {msg}, trace: {trace}'.format(
                    msg=str(e),
                    trace=traceback.format_exc()))
        else:
            loggger.info('Can not get sync_business lock, sync operation abandon')
