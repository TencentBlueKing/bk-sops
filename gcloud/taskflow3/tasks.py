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
__author__ = "蓝鲸智云"
__copyright__ = "Copyright (c) 2012-2018 Tencent. All Rights Reserved."

import logging

from celery import task

from gcloud.taskflow3.models import TaskFlowInstance
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
