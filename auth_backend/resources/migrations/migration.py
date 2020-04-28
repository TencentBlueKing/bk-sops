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

import abc
import sys

from builtins import object
from django.conf import settings
from django.utils.module_loading import import_string
from future.utils import with_metaclass

from auth_backend.resources.migrations import exceptions
from bkiam.client import BKIAMClient


class ResourceMigration(with_metaclass(abc.ABCMeta, object)):
    def __init__(self, diff_operations):
        self.diff_operations = diff_operations

    @abc.abstractmethod
    def apply(self):
        pass

    @staticmethod
    def get_migration(diff_operations):
        path = getattr(settings, 'AUTH_BACKEND_RESOURCE_MIGRATION_CLASS', None)
        if not path:
            return DummyResourceMigration(diff_operations)

        return import_string(path)(diff_operations)


class DummyResourceMigration(ResourceMigration):
    def apply(self):
        return


class BKIAMResourceMigration(ResourceMigration):
    SYSTEM_EXIST_CODE = 1901409
    RESOURCE_NOT_EXIST_CODE = 1901002

    def __init__(self, diff_operations):
        self.client = BKIAMClient()
        super(BKIAMResourceMigration, self).__init__(diff_operations)

    def apply(self):
        for operation in self.diff_operations:
            op = operation['operation']
            data = operation['data']
            sys.stdout.write('\nPerform [{}] with data: {}'.format(op, data))
            getattr(self, op)(data)

    def register_system(self, data):
        result = self.client.register_system(**data)

        if not result['result'] and result.get('code') != self.SYSTEM_EXIST_CODE:
            raise exceptions.MigrationOperationFailedError(result['message'])

    def batch_upsert_resource_types(self, data):
        result = self.client.batch_upsert_resource_types(**data)

        if not result['result']:
            raise exceptions.MigrationOperationFailedError(result['message'])

    def delete_resource_type(self, data):
        result = self.client.delete_resource_type(**data)

        if not result['result'] and result.get('code') != self.RESOURCE_NOT_EXIST_CODE:
            raise exceptions.MigrationOperationFailedError(result['message'])
