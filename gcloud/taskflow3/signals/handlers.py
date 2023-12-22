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

import datetime
import logging

from bamboo_engine import states as bamboo_engine_states
from bk_monitor_report.reporter import MonitorReporter
from django.conf import settings
from django.dispatch import receiver
from pipeline.core.pipeline import Pipeline
from pipeline.engine.signals import activity_failed, pipeline_end, pipeline_revoke
from pipeline.eri.signals import (
    execute_interrupt,
    post_set_state,
    pre_service_execute,
    pre_service_schedule,
    schedule_interrupt,
)
from pipeline.models import PipelineInstance
from pipeline.signals import post_pipeline_finish, post_pipeline_revoke

import env
from gcloud.shortcuts.message import ATOM_FAILED, TASK_FINISHED
from gcloud.taskflow3.celery.tasks import auto_retry_node, send_taskflow_message, task_callback
from gcloud.taskflow3.models import (
    AutoRetryNodeStrategy,
    EngineConfig,
    TaskCallBackRecord,
    TaskFlowInstance,
    TimeoutNodeConfig,
)
from gcloud.taskflow3.signals import taskflow_finished, taskflow_revoked

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
        _check_and_callback(task_id, task_success=task_success)
        try:
            send_taskflow_message.delay(task_id=task_id, msg_type=TASK_FINISHED)
        except Exception as e:
            logger.exception("send_taskflow_message[taskflow_id=%s] task delay error: %s" % (task_id, e))

    if sig is taskflow_revoked:
        _check_and_callback(task_id, task_success=False)


def _send_node_fail_message(node_id, pipeline_id):
    try:
        taskflow = TaskFlowInstance.objects.get(pipeline_instance__instance_id=pipeline_id)
    except TaskFlowInstance.DoesNotExist:
        logger.error("pipeline finished handler get taskflow error, pipeline_instance_id=%s" % pipeline_id)
        return

    _check_and_callback(taskflow.id, task_success=False)

    if taskflow.is_child_taskflow is False:
        try:
            activity = taskflow.get_act_web_info(node_id)
            node_name = activity["name"] if activity else node_id
            send_taskflow_message.delay(task_id=taskflow.id, msg_type=ATOM_FAILED, node_name=node_name)
        except Exception as e:
            logger.exception("pipeline_fail_handler[taskflow_id=%s] task delay error: %s" % (taskflow.id, e))


def _check_and_callback(taskflow_id, *args, **kwargs):
    if not TaskCallBackRecord.objects.filter(task_id=taskflow_id).exists():
        return
    try:
        task_callback.apply_async(
            kwargs=dict(task_id=taskflow_id, **kwargs),
            queue="task_callback",
            routing_key="task_callback",
        )
    except Exception as e:
        logger.exception(f"[_check_and_callback] task_callback delay error: {e}")


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
            countdown=strategy.interval,
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

    try:
        # 切换到边界事件
        # _node_timeout_info_update(settings.redis_inst, to_state, node_id, version)
        pass
    except Exception:
        logger.exception("node_timeout_info_update error")


def _report_interrupt_event(name, content, dimension):
    if not env.BK_MONITOR_REPORT_ENABLE:
        return
    reporter = MonitorReporter(
        data_id=env.BK_MONITOR_REPORT_DATA_ID,
        access_token=env.BK_MONITOR_REPORT_ACCESS_TOKEN,
        target=env.BK_MONITOR_REPORT_TARGET,
        url=env.BK_MONITOR_REPORT_URL,
    )
    reporter.report_event(name=name, content=content, dimension=dimension)


@receiver(execute_interrupt)
def execute_interrupt_handler(sender, event, **kwargs):
    _report_interrupt_event(
        name="execute_interrupt",
        content="node({}) execute interrupt".format(event.node_id),
        dimension={"name": event.name, "process_id": event.process_id, "traceback": event.exception_traceback},
    )


@receiver(schedule_interrupt)
def schedule_interrupt_handler(sender, event, **kwargs):
    _report_interrupt_event(
        name="schedule_interrupt",
        content="node({}) schedule interrupt".format(event.node_id),
        dimension={"name": event.name, "process_id": event.process_id, "traceback": event.exception_traceback},
    )


@receiver(pre_service_execute)
def pre_service_execute_handler(sender, service, data, parent_data, **kwargs):
    if "__executor_proxy" in data.inputs:
        parent_data.inputs.executor = data.inputs.__executor_proxy


@receiver(pre_service_schedule)
def pre_service_schedule_handler(sender, service, data, parent_data, callback_data, **kwargs):
    if "__executor_proxy" in data.inputs:
        parent_data.inputs.executor = data.inputs.__executor_proxy
