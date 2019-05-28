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

from pipeline.engine import tasks
from pipeline.engine.models import ProcessCeleryTask, ScheduleCeleryTask, NodeCeleryTask


def pipeline_ready_handler(sender, process_id, **kwargs):
    ProcessCeleryTask.objects.start_task(
        process_id=process_id,
        start_func=tasks.start.apply_async,
        kwargs={
            'args': [process_id]
        }
    )


def child_process_ready_handler(sender, child_id, **kwargs):
    ProcessCeleryTask.objects.start_task(
        process_id=child_id,
        start_func=tasks.dispatch.apply_async,
        kwargs={
            'args': [child_id]
        }
    )


def process_ready_handler(sender, process_id, current_node_id=None, call_from_child=False, **kwargs):
    ProcessCeleryTask.objects.start_task(
        process_id=process_id,
        start_func=tasks.process_wake_up.apply_async,
        kwargs={
            'args': [process_id, current_node_id, call_from_child]
        }
    )


def batch_process_ready_handler(sender, process_id_list, pipeline_id, **kwargs):
    tasks.batch_wake_up.apply_async(args=[process_id_list, pipeline_id])


def wake_from_schedule_handler(sender, process_id, activity_id, **kwargs):
    ProcessCeleryTask.objects.start_task(
        process_id=process_id,
        start_func=tasks.wake_from_schedule.apply_async,
        kwargs={
            'args': [process_id, activity_id]
        }
    )


def process_unfreeze_handler(sender, process_id, **kwargs):
    ProcessCeleryTask.objects.start_task(
        process_id=process_id,
        start_func=tasks.process_unfreeze.apply_async,
        kwargs={
            'args': [process_id]
        }
    )


def schedule_ready_handler(sender, process_id, schedule_id, countdown, **kwargs):
    ScheduleCeleryTask.objects.start_task(
        schedule_id=schedule_id,
        start_func=tasks.service_schedule.apply_async,
        kwargs={
            'args': [process_id, schedule_id],
            'countdown': countdown
        }
    )


def service_activity_timeout_monitor_start_handler(sender, node_id, version, root_pipeline_id, countdown, **kwargs):
    NodeCeleryTask.objects.start_task(
        node_id=node_id,
        start_func=tasks.node_timeout_check.apply_async,
        kwargs={
            'args': [node_id, version, root_pipeline_id],
            'countdown': countdown
        }
    )


def service_activity_timeout_monitor_end_handler(sender, node_id, version, **kwargs):
    NodeCeleryTask.objects.revoke(node_id)
