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
import json
import time
import socket
import logging

from celery import task
from django.conf import settings

from pipeline.engine.models import PipelineProcess
from pipeline.eri.models import State, Process
from pipeline.eri.runtime import BambooDjangoRuntime

import metrics
from gcloud.taskflow3.domains.node_timeout_strategy import node_timeout_handler
from gcloud.taskflow3.models import (
    TaskFlowInstance,
    AutoRetryNodeStrategy,
    EngineConfig,
    TimeoutNodeConfig,
    TimeoutNodesRecord,
)
from gcloud.taskflow3.domains.dispatchers.node import NodeCommandDispatcher
from gcloud.shortcuts.message import send_task_flow_message

logger = logging.getLogger("celery")

HOST_NAME = socket.gethostname()


@task
def send_taskflow_message(task_id, msg_type, node_name=""):
    try:
        taskflow = TaskFlowInstance.objects.get(id=task_id)
        send_task_flow_message(taskflow, msg_type, node_name)
    except Exception as e:
        logger.exception("send_task_flow_message[taskflow_id=%s] send message error: %s" % (task_id, e))
    else:
        logger.info("send_taskflow_message[taskflow_id=%s] task finished" % task_id)


@task
def prepare_and_start_task(task_id, project_id, username):
    try:
        task = TaskFlowInstance.objects.get(id=task_id, project_id=project_id)
    except TaskFlowInstance.DoesNotExist:
        logger.exception(
            "[prepare_and_start_task] celery get task for (task_id={}, project_id={}) fail.".format(task_id, project_id)
        )
        return

    result = task.task_action("start", username)
    logger.info(
        "[prepare_and_start_task] celery start task (task_id={}, project_id={}) result: {}".format(
            task_id, project_id, result
        )
    )


def _ensure_node_can_retry(node_id, engine_ver):
    count = 0
    while count < 3:
        if engine_ver == EngineConfig.ENGINE_VER_V1:
            if PipelineProcess.objects.filter(current_node_id=node_id, is_sleep=True).exists():
                return True
        elif engine_ver == EngineConfig.ENGINE_VER_V2:
            if BambooDjangoRuntime().get_sleep_process_info_with_current_node_id(node_id):
                return True
        else:
            raise ValueError("invalid engine_ver: %s" % engine_ver)

        time.sleep(0.1)
        count += 1

    return False


@task
@metrics.setup_histogram(metrics.TASKFLOW_NODE_AUTO_RETRY_TASK_DURATION)
def auto_retry_node(taskflow_id, root_pipeline_id, node_id, retry_times, engine_ver):
    lock_name = "%s-%s-%s" % (root_pipeline_id, node_id, retry_times)
    if not settings.redis_inst.set(name=lock_name, value=1, nx=True, ex=5):
        metrics.TASKFLOW_NODE_AUTO_RETRY_LOCK_ACCUIRE_FAIL.labels(hostname=HOST_NAME).inc(1)
        logger.warning("[auto_retry_node] lock %s accuire failed, operation give up" % lock_name)
        return

    # wait process enter a valid state
    can_retry = _ensure_node_can_retry(node_id=node_id, engine_ver=engine_ver)
    if not can_retry:
        settings.redis_inst.delete(lock_name)
        logger.warning("[auto_retry_node] task(%s) node(%s) ensure_node_can_retry timeout" % (taskflow_id, node_id))
        return

    dispatcher = NodeCommandDispatcher(engine_ver=engine_ver, node_id=node_id, taskflow_id=taskflow_id)

    result = dispatcher.dispatch(command="retry", operator="system", inputs={})

    if not result["result"]:
        logger.warning("[auto_retry_node] task(%s) node(%s) auto retry failed: %s" % (taskflow_id, node_id, result))

    AutoRetryNodeStrategy.objects.filter(root_pipeline_id=root_pipeline_id, node_id=node_id).update(
        retry_times=retry_times + 1
    )
    settings.redis_inst.delete(lock_name)


@task(acks_late=True)
def dispatch_timeout_nodes(record_id: int):
    record = TimeoutNodesRecord.objects.get(id=record_id)
    nodes = json.loads(record.timeout_nodes)
    metrics.TASKFLOW_TIMEOUT_NODES_NUMBER.labels(hostname=HOST_NAME).set(len(nodes))
    for node in nodes:
        node_id, version = node.split("_")
        execute_node_timeout_strategy.apply_async(
            kwargs={"node_id": node_id, "version": version},
            queue="timeout_node_execute",
            routing_key="timeout_node_execute",
        )


@task(ignore_result=True)
@metrics.setup_histogram(metrics.TASKFLOW_TIMEOUT_NODES_PROCESSING_TIME)
def execute_node_timeout_strategy(node_id, version):
    timeout_config = (
        TimeoutNodeConfig.objects.filter(node_id=node_id).only("task_id", "root_pipeline_id", "action").first()
    )
    task_id, action, root_pipeline_id = (
        timeout_config.task_id,
        timeout_config.action,
        timeout_config.root_pipeline_id,
    )
    task_inst = TaskFlowInstance.objects.get(pk=task_id)

    # 判断当前节点是否符合策略执行要求
    is_process_current_node = Process.objects.filter(
        root_pipeline_id=root_pipeline_id, current_node_id=node_id
    ).exists()
    node_match = State.objects.filter(node_id=node_id, version=version).exists()
    if not (node_match and is_process_current_node):
        message = (
            f"[execute_node_timeout_strategy] node {node_id} with version {version} in task {task_id} has been passed."
        )
        logger.error(message)
        return {"result": False, "message": message, "data": None}

    handler = node_timeout_handler[action]
    action_result = handler.deal_with_timeout_node(task_inst, node_id)
    logger.info(
        f"[execute_node_timeout_strategy] node {node_id} with version {version} in task {task_id} "
        f"action result is: {action_result}."
    )

    return action_result
