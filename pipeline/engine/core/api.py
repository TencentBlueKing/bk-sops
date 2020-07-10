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

import socket

import kombu
from celery import current_app
from django.conf import settings as django_settings
from redis.exceptions import ConnectionError

from pipeline.celery.settings import CELERY_QUEUES
from pipeline.conf import settings
from pipeline.django_signal_valve import valve
from pipeline.engine import signals
from pipeline.engine.core import data
from pipeline.engine.exceptions import RabbitMQConnectionError
from pipeline.engine.models import FunctionSwitch, PipelineProcess


def freeze():
    # turn on switch
    FunctionSwitch.objects.freeze_engine()


def unfreeze():
    # turn off switch
    FunctionSwitch.objects.unfreeze_engine()

    # resend signal
    valve.open_valve(signals)

    # unfreeze process
    frozen_process_list = PipelineProcess.objects.filter(is_frozen=True)
    for process in frozen_process_list:
        process.unfreeze()


def workers(connection=None):
    try:
        worker_list = data.cache_for("__pipeline__workers__")
    except ConnectionError as e:
        raise e

    if not worker_list:
        tries = 0
        try:
            while tries < 2:
                kwargs = {
                    "timeout": tries + 1
                }
                if connection:
                    kwargs["connection"] = connection

                worker_list = current_app.control.ping(**kwargs)

                if worker_list:
                    break
                tries += 1
        except socket.error as err:
            raise RabbitMQConnectionError(err)

        if worker_list:
            data.expire_cache("__pipeline__workers__", worker_list, settings.PIPELINE_WORKER_STATUS_CACHE_EXPIRES)

    return worker_list


def stats():
    inspect = current_app.control.inspect()

    stats = {"workers": {}, "queues": {}}

    worker_stats = inspect.stats()
    active_queues = inspect.active_queues()

    if worker_stats:

        for name, stat in worker_stats.items():
            stats["workers"].setdefault(name, {"stat": {}, "queues": {}})["stat"] = stat

    if active_queues:

        for name, queues in active_queues.items():
            stats["workers"].setdefault(name, {"stat": {}, "queues": {}})["queues"] = queues

    if not hasattr(django_settings, "BROKER_VHOST"):
        stats["queues"] = "can not find BROKER_VHOST in django settings"

        return stats

    with kombu.Connection(django_settings.BROKER_URL) as conn:
        client = conn.get_manager()

        if not hasattr(client, "get_queue"):
            stats["queues"] = "broker does not support queues info query"

            return stats

        for queue in CELERY_QUEUES:
            stats["queues"][queue.name] = client.get_queue(django_settings.BROKER_VHOST, queue.name)

    return stats
