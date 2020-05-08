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

from __future__ import absolute_import, unicode_literals

import logging
import traceback

from django.dispatch import receiver

from auth_backend.backends import signals
from auth_backend.contrib.consistency.models import RegisterFailInstanceArchive

logger = logging.getLogger('root')


@receiver(signals.instance_register_fail_signal)
def instance_register_fail_handler(sender, resource, instance, scope_id, **kwargs):
    try:
        RegisterFailInstanceArchive.objects.record_fail_register(
            resource=resource,
            instance=instance,
            scope_id=scope_id
        )
    except Exception:
        logger.error('instance register fail record err: {}'.format(traceback.format_exc()))


@receiver(signals.instance_batch_register_fail_signal)
def instance_batch_register_fail_handler(sender, resource, instances, scope_id, **kwargs):
    try:
        RegisterFailInstanceArchive.objects.record_fail_batch_register(
            resource=resource,
            instances=instances,
            scope_id=scope_id
        )
    except Exception:
        logger.error('instance register fail record err: {}'.format(traceback.format_exc()))
