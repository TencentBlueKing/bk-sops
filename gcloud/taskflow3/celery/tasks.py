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

import time
import logging

from celery import task
from django.conf import settings

from pipeline.engine.models import PipelineProcess
from pipeline.eri.runtime import BambooDjangoRuntime

from gcloud.taskflow3.models import TaskFlowInstance, AutoRetryNodeStrategy, EngineConfig
from gcloud.taskflow3.domains.dispatchers.node import NodeCommandDispatcher
from gcloud.shortcuts.message import send_task_flow_message


logger = logging.getLogger("celery")


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
            raise Exception("invalid engine_ver: %s" % engine_ver)

        time.sleep(0.1)

    return False


@task
def auto_retry_node(taskflow_id, root_pipeline_id, node_id, retry_times, engine_ver):
    lock_name = "%s-%s-%s" % (root_pipeline_id, node_id, retry_times)
    if not settings.redis_inst.set(name=lock_name, value=1, nx=True, ex=5):
        logger.warning("[auto_retry_node] lock %s accuire failed, operation give up" % lock_name)

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
