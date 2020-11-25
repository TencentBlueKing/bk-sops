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

from django.db.models.signals import post_save
from django.dispatch import receiver

from gcloud.external_plugins.models import SyncTask
from gcloud.external_plugins.tasks import sync_task


logger = logging.getLogger('celery')


@receiver(post_save, sender=SyncTask)
def sync_task_post_save_handler(sender, instance, created, **kwargs):
    if created:
        sync_task.delay(task_id=instance.id)
