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
import time
import socket
from functools import wraps

from prometheus_client import Gauge, Histogram, Counter


HOST_NAME = socket.gethostname()


def setup_histogram(*histograms):
    def wrapper(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                for h in histograms:
                    h.labels(hostname=HOST_NAME).observe(time.time() - start)

        return _wrapper

    return wrapper


def setup_counter(*counters):
    def wrapper(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            for c in counters:
                c.inc(1)
            return func(*args, **kwargs)

        return _wrapper

    return wrapper


# taskflow metrics
TASKFLOW_TIMEOUT_NODES_NUMBER = Gauge(
    "taskflow_timeout_nodes_number", "amount of timeout nodes", labelnames=["hostname"]
)
TASKFLOW_RUNNING_NODES_NUMBER = Gauge(
    "taskflow_running_nodes_number", "amount of running nodes", labelnames=["hostname"]
)
TASKFLOW_TIMEOUT_NODES_SCANNING_TIME = Histogram(
    "taskflow_timeout_nodes_scanning_time", "time to scan timeout nodes", labelnames=["hostname"]
)
TASKFLOW_TIMEOUT_NODES_PROCESSING_TIME = Histogram(
    "taskflow_timeout_nodes_processing_time", "time to process timeout nodes", labelnames=["hostname"]
)
TASKFLOW_NODE_AUTO_RETRY_TASK_DURATION = Histogram(
    "taskflow_node_auto_retry_task_duration", "time to process node auto retry task", labelnames=["hostname"]
)
TASKFLOW_NODE_AUTO_RETRY_LOCK_ACCUIRE_FAIL = Counter(
    "taskflow_node_auto_retry_lock_accuire_fail", "node auto retry lock fetch fail count", labelnames=["hostname"]
)
