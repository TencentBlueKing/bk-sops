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
import sys
import traceback

from auth_backend.contrib.consistency import conf
from auth_backend.exceptions import AuthInvalidOperationError, AuthLookupError
from auth_backend.resources import resource_type_lib
from auth_backend.resources.interfaces import InstanceIterableResource

logger = logging.getLogger('root')

AUTH_CONFLICT_CODE = 1901409


def register_legacy_instances(legacy_resources):
    # check before legacy data register begin
    for resource_type in legacy_resources:
        resource = resource_type_lib.get(resource_type)
        if not resource:
            raise AuthLookupError('Can\'t find resource [{type}] from resource libs.'.format(type=resource_type))

        if not issubclass(resource.__class__, InstanceIterableResource):
            raise AuthInvalidOperationError('Can\'t perform legacy register for resource: [{type}], make sure the '
                                            'resource implement InstanceIterableResource '
                                            'interface.'.format(type=resource_type))

    step = conf.BATCH_REGISTER_SIZE

    for resource_type in legacy_resources:
        resource = resource_type_lib[resource_type]
        num_of_instances = resource.count()

        if num_of_instances == 0:
            sys.stdout.write('Can\' not find instances for [{type}], skip it\n'.format(type=resource_type))
            continue

        sys.stdout.write('Start to register [{len}] legacy data for [{type}]...\n'.format(len=num_of_instances,
                                                                                          type=resource_type))

        cursor = 0

        while cursor <= num_of_instances:
            instances = resource.slice(start=cursor, end=cursor + step)
            if not instances:
                break

            try:
                result = resource.batch_register_instance(instances)
            except Exception:
                warning_msg = '[{type}] resource [{start}, {end}] batch instance register failed: {trace}'.format(
                    type=resource_type,
                    start=cursor,
                    end=cursor + step,
                    trace=traceback.format_exc()
                )
                sys.stdout.write('[WARNING] {msg}\n'.format(msg=warning_msg))
                logger.warning(warning_msg)
            else:
                if not result.get('result') and result.get('code') != AUTH_CONFLICT_CODE:
                    raise AuthInvalidOperationError('[{type}] instances register error, register result: {result}; '
                                                    'cursor: {cursor}; step: {step}'
                                                    'instances count: {len}'.format(type=resource_type,
                                                                                    result=result,
                                                                                    cursor=cursor,
                                                                                    step=step,
                                                                                    len=num_of_instances))

                sys.stdout.write('[{type}] {success_num} instances register success\n'.format(
                    success_num=len(instances),
                    type=resource_type))

            cursor += step

        sys.stdout.write('[{type}] instances register finished\n\n'.format(len=num_of_instances,
                                                                           type=resource_type))
