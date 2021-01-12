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

from django.dispatch import receiver

from pipeline.engine.signals import activity_failed
from pipeline.models import PipelineInstance
from pipeline.signals import post_pipeline_finish, post_pipeline_revoke

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.signals import taskflow_finished, taskflow_revoked
from gcloud.taskflow3.tasks import send_taskflow_message
from gcloud.shortcuts.message import ATOM_FAILED, TASK_FINISHED

logger = logging.getLogger("celery")


@receiver(post_pipeline_finish, sender=PipelineInstance)
def pipeline_finish_handler(sender, instance_id, **kwargs):
    _finish_taskflow_and_send_signal(instance_id, taskflow_finished)
    taskflow = TaskFlowInstance.objects.get(pipeline_instance__instance_id=instance_id)
    send_taskflow_message.delay(taskflow=taskflow, msg_type=TASK_FINISHED)


@receiver(post_pipeline_revoke, sender=PipelineInstance)
def pipeline_revoke_handler(sender, instance_id, **kwargs):
    _finish_taskflow_and_send_signal(instance_id, taskflow_revoked)


def _finish_taskflow_and_send_signal(instance_id, sig):
    qs = TaskFlowInstance.objects.filter(pipeline_instance__instance_id=instance_id).only("id")
    if not qs:
        logger.error("pipeline archive handler get taskflow error, pipeline_instance_id={}".format(instance_id))
        return

    task_id = qs[0].id

    TaskFlowInstance.objects.filter(id=task_id).update(current_flow="finished")
    sig.send(TaskFlowInstance, task_id=task_id)


@receiver(activity_failed)
def pipeline_fail_handler(sender, pipeline_id, pipeline_activity_id, **kwargs):
    try:
        taskflow = TaskFlowInstance.objects.get(pipeline_instance__instance_id=pipeline_id)
    except TaskFlowInstance.DoesNotExist:
        logger.error("pipeline finished handler get taskflow error, pipeline_instance_id=%s" % pipeline_id)
        return

    try:
        activity_name = taskflow.get_act_web_info(pipeline_activity_id)["name"]
        send_taskflow_message.delay(taskflow=taskflow, msg_type=ATOM_FAILED, node_name=activity_name)
    except Exception as e:
        logger.exception("pipeline_fail_handler[taskflow_id=%s] send message error: %s" % (taskflow.id, e))
    return
