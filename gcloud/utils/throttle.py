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
import time
import logging

from django.conf import settings

from gcloud.taskflow3.models import TaskOperationTimesConfig
from gcloud.utils.redis_lock import redis_lock

logger = logging.getLogger("root")


def get_redis_with_default(redis_instance, key, default_value):
    value = redis_instance.get(key)
    if value is None:
        return default_value
    return value


def check_task_operation_throttle(project_id, operation):
    # load config
    try:
        times_config = TaskOperationTimesConfig.objects.get(project_id=project_id, operation=operation)
    except TaskOperationTimesConfig.DoesNotExist:
        # not limit if no config on project
        return True
    time_unit_mapping = {"m": 60, "h": 3600, "d": 86400}
    allowed_times = int(times_config.times)
    scope_seconds = time_unit_mapping.get(times_config.time_unit)

    # token bucket method
    cache_prefix = "task_operation_throttle"
    token_num_key = "{}_token_num_{}_{}".format(cache_prefix, project_id, operation)
    last_time_key = "{}_last_time_{}_{}".format(cache_prefix, project_id, operation)

    redis_instance = settings.redis_inst
    with redis_lock(redis_instance, "{}_{}".format(project_id, operation)) as (acquired_result, err):
        if not acquired_result:
            logger.error(err)
            return False
        token_num = float(get_redis_with_default(redis_instance, token_num_key, allowed_times))
        now = time.time()
        last_time = float(get_redis_with_default(redis_instance, last_time_key, now))
        redis_instance.set(last_time_key, now)

        token_gen_rate = allowed_times / scope_seconds
        token_num = token_num + (now - last_time) * token_gen_rate
        if token_num < 1:
            redis_instance.set(token_num_key, token_num)
            return False

        token_num = allowed_times if token_num - 1 > allowed_times else token_num - 1
        redis_instance.set(token_num_key, token_num)
        return True
