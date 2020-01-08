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

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.periodictask.models import PeriodicTaskHistory
from gcloud.commons.message import send_periodic_task_message
from pipeline.contrib.periodic_task.models import PeriodicTaskHistory as PipelinePeriodicTaskHistory
from pipeline.contrib.periodic_task.models import PeriodicTask as PipelinePeriodicTask
from pipeline.contrib.periodic_task.signals import pre_periodic_task_start, periodic_task_start_failed

logger = logging.getLogger('celery')


@receiver(pre_periodic_task_start, sender=PipelinePeriodicTask)
def pre_periodic_task_start_handler(sender, periodic_task, pipeline_instance, **kwargs):
    TaskFlowInstance.objects.create(
        business_id=periodic_task.extra_info['business_id'],
        pipeline_instance=pipeline_instance,
        category=periodic_task.extra_info['category'],
        template_id=periodic_task.extra_info['template_num_id'],
        create_method='periodic',
        create_info='',
        flow_type='common',
        current_flow='execute_task'
    )


@receiver(post_save, sender=PipelinePeriodicTaskHistory)
def periodic_task_history_post_save_handler(sender, instance, created, **kwargs):
    if created:
        PeriodicTaskHistory.objects.record_history(instance)


@receiver(periodic_task_start_failed, sender=PipelinePeriodicTask)
def periodic_task_start_failed_handler(sender, periodic_task, history, **kwargs):
    extra_info = periodic_task.extra_info
    try:
        template = TaskTemplate.objects.get(business_id=extra_info['business_id'],
                                            id=extra_info['template_num_id'])
        send_periodic_task_message(template, periodic_task, history)
    except Exception as e:
        logger.error('periodic_task_start_failed_handler[template_id=%s] send message error: %s' %
                     (extra_info['template_num_id'], e))
