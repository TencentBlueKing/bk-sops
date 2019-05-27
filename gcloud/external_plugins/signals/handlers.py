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

from django.db.models.signals import post_save
from django.dispatch import receiver
from celery import task

from gcloud.external_plugins.models import (
    source_cls_factory,
    CachePackageSource,
    SyncTask,
    SUCCEEDED,
    FAILED
)


logger = logging.getLogger('celery')


@receiver(post_save, sender=SyncTask)
def sync_task_post_save_handler(sender, instance, created, **kwargs):
    if created:
        sync_task.delay(task_id=instance.id)


@task
def sync_task(task_id):
    for origin_model in source_cls_factory.values():
        origins = origin_model.objects.all()
        for origin in origins:
            try:
                origin.read()
            except Exception as e:
                SyncTask.objects.filter(id=task_id).update(status=FAILED)
                logger.error('Origin package[type={origin_type, id={origin_id}}] read error: {error}'.format(
                    origin_type=origin.type,
                    origin_id=origin.id,
                    error=e.message
                ))
                return False

    caches = CachePackageSource.objects.all()
    for cache in caches:
        try:
            cache.write()
        except Exception as e:
            SyncTask.objects.filter(id=task_id).update(status=FAILED)
            logger.error('Cache package[type={origin_type, id={origin_id}}] write error: {error}'.format(
                origin_type=cache.type,
                origin_id=cache.id,
                error=e.message
            ))
            return False

    SyncTask.objects.filter(id=task_id).update(status=SUCCEEDED)
    return True
