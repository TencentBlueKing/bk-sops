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

from django.db.models.signals import post_save
from django.dispatch import receiver

from pipeline.signals import post_pipeline_finish, post_pipeline_revoke
from pipeline.models import PipelineInstance

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3 import signals as task_template_signals
from gcloud.analysis_statistics.tasks import (
    taskflowinstance_post_save_statistics_task,
    tasktemplate_post_save_statistics_task,
    pipeline_archive_statistics_task,
)

logger = logging.getLogger("root")


@receiver(post_save, sender=TaskFlowInstance)
def task_flow_post_save_handler(sender, instance, created, **kwargs):
    """
    @summary:TemplateNodeStatistics和TemplateStatistics的更新
    """
    try:
        task_instance_id = instance.id
        taskflowinstance_post_save_statistics_task.delay(task_instance_id, created)
    except Exception:
        logger.exception(
            ("[task_flow_post_save_handler]instance_id={instance_id} send message error").format(
                instance_id=instance.id
            )
        )


@receiver(task_template_signals.post_template_save_commit, sender=TaskTemplate)
def task_template_post_save_commit_handler(sender, project_id, template_id, is_deleted, **kwargs):
    """
    @summary:TaskflowStatistics以及TemplateVariableStatistics的更新
    """
    if is_deleted:
        return
    try:
        tasktemplate_post_save_statistics_task.delay(template_id)
    except Exception:
        logger.exception(
            ("[task_template_post_save_commit_handler]template_id={task_template_id} send message error").format(
                task_template_id=template_id
            )
        )


@receiver(post_pipeline_finish, sender=PipelineInstance)
def pipeline_instance_finish_handler(sender, instance_id, **kwargs):
    """
    @summary:TaskflowExecutedNodeStatistics执行状态更新为已完成
    """
    try:
        pipeline_archive_statistics_task.delay(instance_id=instance_id)
    except Exception:
        logger.exception(
            ("[pipeline_instance_finish_handler]instance_id={instance_id} send message error").format(
                instance_id=instance_id
            )
        )


@receiver(post_pipeline_revoke, sender=PipelineInstance)
def pipeline_instance_revoke_handler(sender, instance_id, **kwargs):
    """
    @summary:TaskflowExecutedNodeStatistics执行状态更新为已撤销
    """
    try:
        pipeline_archive_statistics_task.delay(instance_id=instance_id)
    except Exception:
        logger.exception(
            ("[pipeline_instance_revoke_handler]instance_id={instance_id} send message error").format(
                instance_id=instance_id
            )
        )
