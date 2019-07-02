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

import abc

from django.conf import settings
from django.utils.module_loading import import_string

from bkiam.client import BkIAMClient

from auth_backend.resources.migrations import exceptions


class ResourceMigration(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, diff):
        self.diff = diff

    @abc.abstractmethod
    def apply(self):
        pass

    @staticmethod
    def get_migration(diff):
        path = getattr(settings, 'AUTH_BACKEND_RESOURCE_MIGRATION_CLASS', None)
        if not path:
            return DummyResourceMigration(diff)

        return import_string(path)(diff)


class DummyResourceMigration(ResourceMigration):
    def apply(self):
        return


class BKIAMResourceMigration(ResourceMigration):
    SYSTEM_EXIST_CODE = 1901409
    RESOURCE_NOT_EXIST_CODE = 1901002

    def __init__(self, diff):
        self.client = BkIAMClient()
        super(BKIAMResourceMigration, self).__init__(diff)

    def apply(self):
        for operation in self.diff:
            getattr(self, operation['operation'])(operation['data'])

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
