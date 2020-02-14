# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import importlib

import ujson as json
from django.conf import settings

from gcloud.shortcuts.message.common import (
    title_and_content_for_atom_failed,
    title_and_content_for_flow_finished,
    title_and_content_for_periodic_task_start_fail
)

logger = logging.getLogger('root')
_message_module = importlib.import_module('gcloud.shortcuts.message.sites.%s.send_msg' % settings.RUN_VER)

ATOM_FAILED = 'atom_failed'
TASK_FINISHED = 'task_finished'


def send_task_flow_message(taskflow, msg_type, node_name=''):
    template = taskflow.template
    pipeline_inst = taskflow.pipeline_instance
    executor = pipeline_inst.executor

    notify_type = json.loads(template.notify_type)
    receivers_list = template.get_notify_receivers_list(executor)
    receivers = ','.join(receivers_list)

    if msg_type == 'atom_failed':
        title, content = title_and_content_for_atom_failed(taskflow, pipeline_inst, node_name, executor)
    elif msg_type == 'task_finished':
        title, content = title_and_content_for_flow_finished(taskflow, pipeline_inst, node_name, executor)
    else:
        return False

    logger.info('taskflow[id={flow_id}] will send {msg_type} message({notify_type}) to: {receivers}'.format(
        flow_id=taskflow.id,
        msg_type=msg_type,
        notify_type=notify_type,
        receivers=receivers
    ))
    _message_module.send_message(executor, notify_type, receivers, title, content)

    return True


def send_periodic_task_message(template, periodic_task, history):
    notify_type = json.loads(template.notify_type)
    receivers_list = template.get_notify_receivers_list(periodic_task.creator)
    receivers = ','.join(receivers_list)

    title, content = title_and_content_for_periodic_task_start_fail(template, periodic_task, history)

    logger.info('periodic task of template[id={template_id}] will send message({notify_type}) to: {receivers}'.format(
        template_id=template.id,
        notify_type=notify_type,
        receivers=receivers
    ))
    _message_module.send_message(periodic_task.creator, notify_type, receivers, title, content)

    return True
