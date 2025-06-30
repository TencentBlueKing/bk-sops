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

from gcloud.core.models import Project
from gcloud.periodictask.models import PeriodicTask
from gcloud.shortcuts.message.common import (
    title_and_content_for_atom_failed,
    title_and_content_for_clocked_task_create_fail,
    title_and_content_for_flow_finished,
    title_and_content_for_pending_processing,
    title_and_content_for_periodic_task_start_fail,
)
from gcloud.shortcuts.message.send_msg import CmsiSender, MessageSender
from gcloud.periodictask.models import PeriodicTask

logger = logging.getLogger("root")

ATOM_FAILED = "atom_failed"
TASK_FINISHED = "task_finished"
PENDING_PROCESSING = "pending_processing"


def send_task_flow_message(taskflow, msg_type, node_name=""):
    notify_types = taskflow.get_notify_type()
    # 获取消息接收人, 形如：
    # {'receiver_group':['Maintainers'],'more_receiver':'username1,username2',extra_info":{"bkchat":{fail:"",success:""}}
    notify_receivers = taskflow.get_notify_receivers()
    receivers_list = taskflow.get_stakeholders()
    receivers = ",".join(receivers_list)
    executor = taskflow.executor
    tenant_id = taskflow.project.tenant_id

    if msg_type == ATOM_FAILED:
        title, content, email_content = title_and_content_for_atom_failed(
            taskflow, taskflow.pipeline_instance, node_name, executor
        )
        notify_type = notify_types.get("fail", [])
        bkchat_receivers = notify_receivers.get("extra_info", {}).get("bkchat", {}).get("fail", "")
    elif msg_type == "task_finished":
        title, content, email_content = title_and_content_for_flow_finished(
            taskflow, taskflow.pipeline_instance, node_name, executor
        )
        notify_type = notify_types.get("success", [])
        bkchat_receivers = notify_receivers.get("extra_info", {}).get("bkchat", {}).get("success", "")
    else:
        return False
    logger.info(
        "taskflow[id={flow_id}] will send {msg_type} message({notify_type}) to: {receivers} {bkchat_receivers}".format(
            flow_id=taskflow.id,
            msg_type=msg_type,
            notify_type=notify_type,
            receivers=receivers,
            bkchat_receivers=bkchat_receivers,
        )
    )
    MessageSender().send(
        executor, notify_type, bkchat_receivers, receivers, title, content, email_content=email_content
    )

    return True


def send_periodic_task_message(periodic_task, history):
    gcloud_periodic_task = PeriodicTask.objects.get(task=periodic_task)
    notify_type = gcloud_periodic_task.get_notify_type().get("fail", [])
    receivers = gcloud_periodic_task.get_stakeholders()
    tenant_id = gcloud_periodic_task.project.tenant_id

    title, content = title_and_content_for_periodic_task_start_fail(gcloud_periodic_task, history)

    logger.info(
        "periodic task of template[id={template_id}] will send message({notify_type}) to: {receivers}".format(
            template_id=gcloud_periodic_task.template.id, notify_type=notify_type, receivers=receivers
        )
    )
    CmsiSender().send(gcloud_periodic_task.creator, notify_type, receivers, title, content)

    return True


def send_clocked_task_message(clocked_task, ex_data):
    notify_types = clocked_task.get_notify_type()
    receivers = clocked_task.get_stakeholders()
    creator = clocked_task.creator
    title, content = title_and_content_for_clocked_task_create_fail(clocked_task, ex_data)
    notify_type = notify_types.get("fail", [])
    tenant_id = Project.objects.get(id=clocked_task.project_id).tenant_id

    logger.info(
        "clocked_task[id={task_id}] will send {msg_type} message({notify_type}) to: {receivers}".format(
            task_id=clocked_task.id, msg_type="create fail", notify_type=notify_type, receivers=receivers
        )
    )
    CmsiSender().send(creator, notify_type, receivers, title, content)

    return True
