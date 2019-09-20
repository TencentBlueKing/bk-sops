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

from kombu import Exchange, Queue
from pipeline.constants import PIPELINE_MAX_PRIORITY

default_exchange = Exchange('default', type='direct')

# new priority queues

PIPELINE_PRIORITY_ROUTING = {
    'queue': 'pipeline_priority',
    'routing_key': 'pipeline_push_priority'
}

PIPELINE_SCHEDULE_PRIORITY_ROUTING = {
    'queue': 'service_schedule_priority',
    'routing_key': 'schedule_service_priority'
}

PIPELINE_ADDITIONAL_PRIORITY_ROUTING = {
    'queue': 'pipeline_additional_task_priority',
    'routing_key': 'additional_task_priority'
}

CELERY_ROUTES = {
    # schedule
    'pipeline.engine.tasks.service_schedule': PIPELINE_SCHEDULE_PRIORITY_ROUTING,
    # pipeline
    'pipeline.engine.tasks.batch_wake_up': PIPELINE_PRIORITY_ROUTING,
    'pipeline.engine.tasks.dispatch': PIPELINE_PRIORITY_ROUTING,
    'pipeline.engine.tasks.process_wake_up': PIPELINE_PRIORITY_ROUTING,
    'pipeline.engine.tasks.start': PIPELINE_PRIORITY_ROUTING,
    'pipeline.engine.tasks.wake_from_schedule': PIPELINE_PRIORITY_ROUTING,
    'pipeline.engine.tasks.wake_up': PIPELINE_PRIORITY_ROUTING,
    'pipeline.engine.tasks.process_unfreeze': PIPELINE_PRIORITY_ROUTING,
    # another
    'pipeline.log.tasks.clean_expired_log': PIPELINE_ADDITIONAL_PRIORITY_ROUTING,
    'pipeline.engine.tasks.node_timeout_check': PIPELINE_ADDITIONAL_PRIORITY_ROUTING,
    'pipeline.contrib.periodic_task.tasks.periodic_task_start': PIPELINE_ADDITIONAL_PRIORITY_ROUTING,
}

CELERY_QUEUES = (
    # keep old queue to process message left in broker, remove on next version
    Queue('default', default_exchange, routing_key='default'),
    Queue('pipeline', default_exchange, routing_key='pipeline_push'),
    Queue('service_schedule', default_exchange, routing_key='schedule_service'),
    Queue('pipeline_additional_task', default_exchange, routing_key='additional_task'),
    # priority queues
    Queue('pipeline_priority', default_exchange, routing_key='pipeline_push_priority',
          queue_arguments={'x-max-priority': PIPELINE_MAX_PRIORITY}),
    Queue('service_schedule_priority', default_exchange, routing_key='schedule_service_priority',
          queue_arguments={'x-max-priority': PIPELINE_MAX_PRIORITY}),
    Queue('pipeline_additional_task_priority', default_exchange, routing_key='additional_task_priority',
          queue_arguments={'x-max-priority': PIPELINE_MAX_PRIORITY})
)

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'
