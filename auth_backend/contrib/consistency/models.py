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

from __future__ import absolute_import, unicode_literals

import logging
import traceback

import ujson as json
from django.db import models

from auth_backend.resources.base import resource_type_lib

logger = logging.getLogger('root')


class RegisterFailInstanceArchiveManager(models.Manager):

    def record_fail_register(self, resource, instance, scope_id):
        instance_id = resource.resource_id(instance)
        return self.create(
            resource_type=resource.rtype,
            instances=json.dumps([instance_id]),
            scope_id=scope_id if scope_id else ''
        )

    def record_fail_batch_register(self, resource, instances, scope_id):
        instance_ids = [resource.resource_id(inst) for inst in instances]
        return self.create(
            resource_type=resource.rtype,
            instances=json.dumps(instance_ids),
            scope_id=scope_id if scope_id else ''
        )


class RegisterFailInstanceArchive(models.Model):

    resource_type = models.CharField("资源类型", max_length=128)
    instances = models.TextField("资源信息")
    scope_id = models.CharField("作用域 ID", max_length=128)

    objects = RegisterFailInstanceArchiveManager()

    def register(self):
        try:
            resource = resource_type_lib[self.resource_type]
            result = resource.batch_register_instance(
                instances=json.loads(self.instances),
                scope_id=self.scope_id if self.scope_id else None
            )
        except Exception:
            logger.error('error occurred when re register {}, err: {}'.format(
                self,
                traceback.format_exc()
            ))
            return {'result': False, 'message': 'error occurred when re register'}

        logger.info('{} register result: {}'.format(self, result))
        self.delete()
        return result

    def __repr__(self):
        return '<RegisterFailInstanceArchive>({} {}-{})'.format(
            self.resource_type,
            self.scope_id,
            self.instances
        )

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()
