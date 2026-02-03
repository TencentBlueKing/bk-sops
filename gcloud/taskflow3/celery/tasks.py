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
import logging
import socket
import time

from celery import current_app
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from pipeline.engine.models import PipelineProcess
from pipeline.eri.models import Process, State
from pipeline.eri.runtime import BambooDjangoRuntime

import env
import metrics
from gcloud.constants import CallbackStatus
from gcloud.core.trace import CallFrom, start_trace
from gcloud.shortcuts.message import send_task_flow_message
from gcloud.taskflow3.domains.callback import TaskCallBacker
from gcloud.taskflow3.domains.dispatchers.node import NodeCommandDispatcher
from gcloud.taskflow3.domains.node_timeout_strategy import node_timeout_handler
from gcloud.taskflow3.models import (
    AutoRetryNodeStrategy,
    EngineConfig,
    TaskFlowInstance,
    TaskFlowRelation,
    TimeoutNodeConfig,
    TimeoutNodesRecord,
)

logger = logging.getLogger("celery")

HOST_NAME = socket.gethostname()


@current_app.task
def send_taskflow_message(task_id, msg_type, node_name="", use_root=False):
    try:
        taskflow = TaskFlowInstance.objects.get(id=task_id)
        if use_root and taskflow.is_child_taskflow:
            logger.info("send_task_flow_message[taskflow_id=%s] is_child_taskflow, try to find root taskflow.", task_id)
            root_task_id = TaskFlowRelation.objects.get(task_id=task_id).root_task_id
            taskflow = TaskFlowInstance.objects.get(id=root_task_id)
            logger.info(
                "send_task_flow_message[taskflow_id=%s] use root taskflow[id=%s] to send message", task_id, root_task_id
            )

        send_task_flow_message(taskflow, msg_type, node_name)
    except Exception as e:
        logger.exception("send_task_flow_message[taskflow_id=%s] send message error: %s" % (task_id, e))
    else:
        logger.info("send_taskflow_message[taskflow_id=%s] task finished" % task_id)


@current_app.task
def prepare_and_start_task(task_id, project_id, username, tenant_id):
    try:
        task = TaskFlowInstance.objects.get(id=task_id, project_id=project_id, project__tenant_id=tenant_id)
    except TaskFlowInstance.DoesNotExist:
        logger.exception(
            "[prepare_and_start_task] celery get task for (task_id={}, project_id={}) fail.".format(task_id, project_id)
        )
        return

    with start_trace(
        span_name="prepare_and_start_task",
        propagate=True,
        project_id=task.project.id,
        call_from=CallFrom.BACKEND.value,
    ):
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


@current_app.task
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

    # 如果是独立子任务，自动重试时更新父任务节点状态
    if engine_ver == EngineConfig.ENGINE_VER_V2:
        try:
            task_instance = TaskFlowInstance.objects.get(id=taskflow_id)
            task_instance.change_parent_task_node_state_to_running()
        except TaskFlowInstance.DoesNotExist:
            logger.exception("[auto_retry_node] get task for (task_id={}) fail.".format(taskflow_id))
            pass

    dispatcher = NodeCommandDispatcher(engine_ver=engine_ver, node_id=node_id, taskflow_id=taskflow_id)

    result = dispatcher.dispatch(command="retry", operator="system", inputs={})

    if not result["result"]:
        logger.warning("[auto_retry_node] task(%s) node(%s) auto retry failed: %s" % (taskflow_id, node_id, result))

    AutoRetryNodeStrategy.objects.filter(root_pipeline_id=root_pipeline_id, node_id=node_id).update(
        retry_times=retry_times + 1
    )
    settings.redis_inst.delete(lock_name)


@current_app.task(acks_late=True)
def dispatch_timeout_nodes(record_id: int):
    record = TimeoutNodesRecord.objects.get(id=record_id)
    nodes = json.loads(record.timeout_nodes)
    metrics.TASKFLOW_TIMEOUT_NODES_NUMBER.labels(hostname=HOST_NAME).set(len(nodes))
    for node in nodes:
        # TODO 支持 node 自解析
        node_id, version = node.split("_")
        execute_node_timeout_strategy.apply_async(
            kwargs={"node_id": node_id, "version": version},
            queue="timeout_node_execute",
            routing_key="timeout_node_execute",
        )


@current_app.task(ignore_result=True)
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
        message = _(
            f"超时策略激活失败: 节点[ID: {node_id}], 版本[{version}], 任务[ID: {task_id}] 现已通过 | execute_node_timeout_strategy"
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


@current_app.task
def task_callback(task_id, retry_times=0, *args, **kwargs):
    tcb = TaskCallBacker(task_id, *args, **kwargs)
    if not tcb.check_record_existence():
        message = f"[task_callback] task_id {task_id} does not in TaskCallBackRecord."
        logger.error(message)
        return
    try:
        result = tcb.callback()
    except Exception as e:
        logger.exception(f"[task_callback] task_id {task_id}, retry_times {retry_times} callback error: {e}")
        result = False

    if result is None:
        return

    if not result and retry_times < settings.REQUEST_RETRY_NUMBER:
        task_callback.apply_async(
            kwargs=dict(task_id=task_id, retry_times=retry_times + 1, **kwargs),
            queue="task_callback",
            routing_key="task_callback",
            countdown=1,
        )
        return
    tcb.update_record(
        extra_info=json.dumps({**tcb.extra_info, **kwargs}),
        status=CallbackStatus.SUCCESS.value if result else CallbackStatus.FAIL.value,
        callback_time=timezone.now(),
    )


def is_sleep_process_error(callback_result):
    """
    检查 callback_result 的 message 中是否包含 sleep process 相关的错误信息
    :param callback_result: 回调结果字典
    :return: bool
    """
    message = callback_result.get("message", "")
    if not message:
        return False
    message_lower = message.lower()
    # 检查是否包含 "can not find sleep process with current node id" 类似的子串
    return "can not find sleep process" in message_lower and "current node" in message_lower


def is_schedule_not_found_error(callback_result):
    """
    检查 callback_result 的 message 中是否包含 Schedule 不存在的错误信息
    :param callback_result: 回调结果字典
    :return: bool
    """
    message = callback_result.get("message", "")
    if not message:
        return False
    message_lower = message.lower()
    # 检查是否包含 "Schedule matching query does not exist" 或 "schedule" 和 "does not exist" 类似的子串
    return "schedule matching query does not exist" in message_lower or (
        "schedule" in message_lower and "does not exist" in message_lower
    )


@current_app.task
def async_node_callback_retry(
    engine_ver, node_id, node_version, callback_data, taskflow_id=None, project_id=None, retry_times=0
):
    """
    异步重试 node_callback，用于处理 sleep process 相关错误的情况
    :param engine_ver: 引擎版本
    :param node_id: 节点ID
    :param node_version: 节点版本
    :param callback_data: 回调数据
    :param taskflow_id: 任务流ID（可选）
    :param project_id: 项目ID（可选）
    :param retry_times: 当前重试次数，最多重试3次
    """
    MAX_ASYNC_RETRY_TIMES = 3

    logger.info(
        "[async_node_callback_retry] retry_times: {}, engine_ver: {}, node_id: {}, node_version: {}".format(
            retry_times, engine_ver, node_id, node_version
        )
    )

    dispatcher = NodeCommandDispatcher(engine_ver=engine_ver, node_id=node_id, taskflow_id=taskflow_id)

    with start_trace(
        "async_node_callback_retry", propagate=True, project_id=project_id, call_from=CallFrom.BACKEND.value
    ):
        callback_result = dispatcher.dispatch(command="callback", operator="", version=node_version, data=callback_data)

        logger.info(
            "[async_node_callback_retry] result of callback call(engine_ver: {} node_id: {}, "
            "taskflow_id: {}, node_version: {}, retry_times: {}): {}".format(
                engine_ver, node_id, taskflow_id, node_version, retry_times, callback_result
            )
        )

        # 如果成功，直接返回
        if callback_result.get("result"):
            logger.info(
                "[async_node_callback_retry] callback success after async retry, "
                "engine_ver: {}, node_id: {}, taskflow_id: {}, retry_times: {}".format(
                    engine_ver, node_id, taskflow_id, retry_times
                )
            )
            return callback_result

        # 如果失败且错误信息中包含 sleep process 相关错误，且未达到最大重试次数，继续异步重试
        if is_sleep_process_error(callback_result) and retry_times < MAX_ASYNC_RETRY_TIMES:
            logger.warning(
                "[async_node_callback_retry] Sleep process error detected, scheduling next async retry. "
                "engine_ver: {}, node_id: {}, taskflow_id: {}, node_version: {}, retry_times: {}, message: {}. ".format(
                    engine_ver,
                    node_id,
                    taskflow_id,
                    node_version,
                    retry_times,
                    callback_result.get("message", ""),
                )
            )
            async_node_callback_retry.apply_async(
                kwargs=dict(
                    engine_ver=engine_ver,
                    node_id=node_id,
                    node_version=node_version,
                    callback_data=callback_data,
                    taskflow_id=taskflow_id,
                    project_id=project_id,
                    retry_times=retry_times + 1,
                ),
                queue="task_callback",
                routing_key="task_callback",
                countdown=env.ASYNC_NODE_CALLBACK_RETRY_INTERVAL,
            )
        else:
            logger.error(
                "[async_node_callback_retry] callback failed after async retry, "
                "engine_ver: {}, node_id: {}, taskflow_id: {},retry_times: {}, result: {}".format(
                    engine_ver, node_id, taskflow_id, retry_times, callback_result
                )
            )

        return callback_result
