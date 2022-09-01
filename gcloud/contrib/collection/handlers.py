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

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from gcloud.common_template.models import CommonTemplate
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.contrib.collection.models import Collection
from gcloud.periodictask.models import PeriodicTask
from gcloud.tasktmpl3.models import TaskTemplate


def _handle_collection_update(resource, instance, created, **kwargs):
    if created:
        return
    if getattr(instance, "is_deleted", False) is True:
        Collection.objects.cascade_delete(category=resource, instance_id=instance.id)
    else:
        Collection.objects.update_collection_info_name(category=resource, instance_id=instance.id, name=instance.name)


@receiver(post_save, sender=CommonTemplate)
def common_template_collection_post_save_handler(sender, instance, created, **kwargs):
    _handle_collection_update("common_flow", instance, created)


@receiver(post_save, sender=TaskTemplate)
def task_template_collection_post_save_handler(sender, instance, created, **kwargs):
    _handle_collection_update("flow", instance, created)


@receiver(post_save, sender=AppMaker)
def app_maker_collection_post_save_handler(sender, instance, created, **kwargs):
    _handle_collection_update("mini_app", instance, created)


@receiver(post_delete, sender=PeriodicTask)
def periodic_task_collection_delete_handler(sender, instance, **kwargs):
    Collection.objects.cascade_delete(category="periodic_task", instance_id=instance.id)


@receiver(post_save, sender=PeriodicTask)
def periodic_task_collection_post_save_handler(sender, instance, created, **kwargs):
    _handle_collection_update("periodic_task", instance, created)
