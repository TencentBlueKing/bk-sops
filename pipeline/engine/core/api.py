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

import socket

from redis.exceptions import ConnectionError
from djcelery.app import current_app

from django_signal_valve import valve

from pipeline.conf import settings
from pipeline.engine.models import FunctionSwitch, PipelineProcess
from pipeline.engine import signals
from pipeline.engine.core import data
from pipeline.engine.exceptions import RabbitMQConnectionError


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


def workers():
    try:
        worker_list = data.cache_for('__pipeline__workers__')
    except ConnectionError as e:
        raise e

    if not worker_list:
        tries = 0
        try:
            while tries < 2:
                worker_list = current_app.control.ping(timeout=tries + 1)
                if worker_list:
                    break
                tries += 1
        except socket.error as err:
            raise RabbitMQConnectionError(err.message)

        if worker_list:
            data.expire_cache('__pipeline__workers__', worker_list, settings.PIPELINE_WORKER_STATUS_CACHE_EXPIRES)

    return worker_list
