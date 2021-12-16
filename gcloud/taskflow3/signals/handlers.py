# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import datetime

from django.conf import settings
from django.dispatch import receiver

from bamboo_engine import states as bamboo_engine_states
from pipeline.engine.signals import activity_failed
from pipeline.core.pipeline import Pipeline
from pipeline.models import PipelineInstance
from pipeline.signals import post_pipeline_finish, post_pipeline_revoke
from pipeline.eri.signals import post_set_state
from pipeline.engine.signals import pipeline_end, pipeline_revoke

from gcloud.taskflow3.models import TaskFlowInstance, AutoRetryNodeStrategy, EngineConfig, TimeoutNodeConfig
from gcloud.taskflow3.signals import taskflow_finished, taskflow_revoked
from gcloud.taskflow3.celery.tasks import send_taskflow_message, auto_retry_node
from gcloud.shortcuts.message import ATOM_FAILED, TASK_FINISHED

logger = logging.getLogger("celery")


def _finish_taskflow_and_send_signal(instance_id, sig, task_success=False):
    qs = TaskFlowInstance.objects.filter(pipeline_instance__instance_id=instance_id).only("id")
    if not qs:
        logger.error("pipeline archive handler get taskflow error, pipeline_instance_id={}".format(instance_id))
        return

    task_id = qs[0].id

    TaskFlowInstance.objects.filter(id=task_id).update(current_flow="finished")
    sig.send(TaskFlowInstance, task_id=task_id)

    if task_success:
        try:
            send_taskflow_message.delay(task_id=task_id, msg_type=TASK_FINISHED)
        except Exception as e:
            logger.exception("send_taskflow_message[taskflow_id=%s] task delay error: %s" % (task_id, e))


def _send_node_fail_message(node_id, pipeline_id):
    try:
        taskflow = TaskFlowInstance.objects.get(pipeline_instance__instance_id=pipeline_id)
    except TaskFlowInstance.DoesNotExist:
        logger.error("pipeline finished handler get taskflow error, pipeline_instance_id=%s" % pipeline_id)
        return

    try:
        activity = taskflow.get_act_web_info(node_id)
        # is not activity
        if not activity:
            return
        activity_name = activity["name"]
        send_taskflow_message.delay(task_id=taskflow.id, msg_type=ATOM_FAILED, node_name=activity_name)
    except Exception as e:
        logger.exception("pipeline_fail_handler[taskflow_id=%s] task delay error: %s" % (taskflow.id, e))


def _dispatch_auto_retry_node_task(root_pipeline_id, node_id, engine_ver):
    try:
        strategy = AutoRetryNodeStrategy.objects.get(root_pipeline_id=root_pipeline_id, node_id=node_id)
    except AutoRetryNodeStrategy.DoesNotExist:
        # auto retry not set
        return False

    # auto retry times exceed limit
    if strategy.retry_times + 1 > strategy.max_retry_times:
        return False

    try:
        auto_retry_node.apply_async(
            kwargs={
                "taskflow_id": strategy.taskflow_id,
                "root_pipeline_id": root_pipeline_id,
                "node_id": node_id,
                "retry_times": strategy.retry_times,
                "engine_ver": engine_ver,
            },
            queue="node_auto_retry",
            routing_key="node_auto_retry",
        )
    except Exception:
        logger.exception("auto retry dispatch failed, root_pipeline_id: %s, node_id: %s" % (root_pipeline_id, node_id))
        return False

    return True


@receiver(post_pipeline_finish, sender=PipelineInstance)
def pipeline_finish_handler(sender, instance_id, **kwargs):
    _finish_taskflow_and_send_signal(instance_id, taskflow_finished, True)


@receiver(post_pipeline_revoke, sender=PipelineInstance)
def pipeline_revoke_handler(sender, instance_id, **kwargs):
    _finish_taskflow_and_send_signal(instance_id, taskflow_revoked)


@receiver(activity_failed)
def pipeline_fail_handler(sender, pipeline_id, pipeline_activity_id, **kwargs):
    auto_retry_dispatched = _dispatch_auto_retry_node_task(
        root_pipeline_id=pipeline_id, node_id=pipeline_activity_id, engine_ver=EngineConfig.ENGINE_VER_V1
    )

    if auto_retry_dispatched:
        return

    _send_node_fail_message(node_id=pipeline_activity_id, pipeline_id=pipeline_id)


def _node_timeout_info_update(redis_inst, to_state, node_id, version):
    key = f"{node_id}_{version}"
    if to_state == bamboo_engine_states.RUNNING:
        now = datetime.datetime.now()
        timeout_qs = TimeoutNodeConfig.objects.filter(node_id=node_id).only("timeout")
        if not timeout_qs:
            return
        timeout_time = (now + datetime.timedelta(seconds=timeout_qs[0].timeout)).timestamp()
        redis_inst.zadd(settings.EXECUTING_NODE_POOL, mapping={key: timeout_time}, nx=True)
    elif to_state in [bamboo_engine_states.FAILED, bamboo_engine_states.FINISHED, bamboo_engine_states.SUSPENDED]:
        redis_inst.zrem(settings.EXECUTING_NODE_POOL, key)


@receiver(post_set_state)
def bamboo_engine_eri_post_set_state_handler(sender, node_id, to_state, version, root_id, parent_id, loop, **kwargs):
    if to_state == bamboo_engine_states.FAILED:
        auto_retry_dispatched = _dispatch_auto_retry_node_task(
            root_pipeline_id=root_id, node_id=node_id, engine_ver=EngineConfig.ENGINE_VER_V2
        )

        if auto_retry_dispatched:
            return

        _send_node_fail_message(node_id=node_id, pipeline_id=root_id)

    elif to_state == bamboo_engine_states.REVOKED and node_id == root_id:
        try:
            pipeline_revoke.send(sender=Pipeline, root_pipeline_id=root_id)
        except Exception:
            logger.exception("taskflow_revoked send error")

        _finish_taskflow_and_send_signal(root_id, taskflow_revoked)
    elif to_state == bamboo_engine_states.FINISHED and node_id == root_id:
        try:
            pipeline_end.send(sender=Pipeline, root_pipeline_id=root_id)
        except Exception:
            logger.exception("pipeline_end send error")

        _finish_taskflow_and_send_signal(root_id, taskflow_finished, True)

    try:
        _node_timeout_info_update(settings.redis_inst, to_state, node_id, version)
    except Exception:
        logger.exception("node_timeout_info_update error")
