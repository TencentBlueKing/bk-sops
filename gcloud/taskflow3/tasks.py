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

from celery import task

from gcloud.commons.message import send_task_flow_message


logger = logging.getLogger('celery')


@task
def send_taskflow_message(taskflow, msg_type, atom_node_name=''):
    try:
        send_task_flow_message(taskflow, msg_type, atom_node_name)
    except Exception as e:
        logger.error('send_task_flow_message[taskflow_id=%s] send message error: %s' % (taskflow.id, e))
    else:
        logger.info('send_taskflow_message[taskflow_id=%s] task finished' % taskflow.id)
