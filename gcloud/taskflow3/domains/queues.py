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

from typing import List

from kombu import Exchange, Queue


class PrepareAndStartTaskQueueResolver:
    TASK_NAME = "taskflow3.tasks.celery.prepare_and_start_task"

    def __init__(self, queue: str):
        self.queue = queue

    def resolve_task_queue_and_routing_key(self) -> (str, str):
        queue_config = self.routes_config()
        return queue_config[self.TASK_NAME]["queue"], queue_config[self.TASK_NAME]["routing_key"]

    def routes_config(self) -> dict:
        suffix = "_%s" % self.queue if self.queue else ""
        return {self.TASK_NAME: {"queue": "task_prepare%s" % suffix, "routing_key": "task_prepare%s" % suffix}}

    def queues(self) -> List[Queue]:
        exchange = Exchange("default", type="direct")
        return [
            Queue(queue_config["queue"], exchange, routing_key=queue_config["routing_key"], max_priority=255)
            for queue_config in self.routes_config().values()
        ]
