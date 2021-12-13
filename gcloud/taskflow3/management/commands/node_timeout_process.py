# -*- coding: utf-8 -*-
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
import datetime
import time
import logging

from django.conf import settings
from django.core.management import BaseCommand

import metrics
from gcloud.taskflow3.celery.tasks import execute_node_timeout_strategy

logger = logging.getLogger("root")


class Command(BaseCommand):
    help = "节点执行超时扫描并处理"

    def handle(self, *args, **options):
        redis_inst = settings.redis_inst
        nodes_pool = settings.EXECUTING_NODE_POOL
        while True:
            nodes = self._pop_timeout_nodes(redis_inst, nodes_pool)
            for node in nodes:
                self._execute_node_timeout_strategy(node)
            time.sleep(1)

    @staticmethod
    @metrics.setup_histogram(metrics.TASKFLOW_TIMEOUT_NODES_SCANNING_TIME)
    def _pop_timeout_nodes(redis_inst, nodes_pool) -> list:
        """扫描正在执行的超时节点"""
        now = datetime.datetime.now().timestamp()
        timeout_nodes = [
            node.decode("utf-8") if isinstance(node, bytes) else node
            for node in redis_inst.zrangebyscore(nodes_pool, "-inf", now)
        ]
        if timeout_nodes:
            redis_inst.zrem(nodes_pool, *timeout_nodes)
        metrics.TASKFLOW_RUNNING_NODES_NUMBER.set(redis_inst.zcard(nodes_pool))
        return timeout_nodes

    @staticmethod
    @metrics.setup_counter(metrics.TASKFLOW_TIMEOUT_NODES_NUMBER)
    def _execute_node_timeout_strategy(node):
        """超时节点处理"""
        node_id, version = node.split("_")
        execute_node_timeout_strategy.apply_async(
            kwargs={"node_id": node_id, "version": version}, queue="node_timeout", routing_key="node_timeout"
        )
