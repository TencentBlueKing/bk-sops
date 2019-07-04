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

from __future__ import absolute_import

import logging
import traceback

from auth_backend.resources.base import ObjectResource

from django.db.models.signals import post_save, post_delete

logger = logging.getLogger('root')


class DjangoModelResource(ObjectResource):

    def __init__(self, auto_register=True, tomb_field=None, *args, **kwargs):
        super(DjangoModelResource, self).__init__(*args, **kwargs)
        self.auto_register = auto_register
        self.tomb_field = tomb_field

        if auto_register:
            # register django model action handlers
            self._dispatch_handlers()

    def post_save_handler(self, sender, instance, created, **kwargs):
        try:
            if created:
                self.register_instance(instance)
                return

            if self.tomb_field and getattr(instance, self.tomb_field):
                self.delete_instance(instance)
                return

            self.update_instance(instance)
        except Exception:
            logger.error('{name} resource post save handler raise error: {exc}'.format(
                name=self.name,
                exc=traceback.format_exc()
            ))

    def post_delete_handler(self, sender, instance, **kwargs):
        try:
            self.delete_instance(instance)
        except Exception:
            logger.error('{name} resource post delete handler raise error: {exc}'.format(
                name=self.name,
                exc=traceback.format_exc()
            ))

    def _dispatch_handlers(self):
        post_save.connect(receiver=self.post_save_handler, sender=self.resource_cls)
        post_delete.connect(receiver=self.post_delete_handler, sender=self.resource_cls)

    def clean_instances(self, instances):
        if instances is None:
            return None

        if isinstance(instances, list):
            cleaned = []
            for inst in instances:
                if isinstance(inst, self.resource_cls):
                    cleaned.append(inst)
                else:
                    id_filter = {
                        self.inspect.resource_id_f: inst
                    }
                    cleaned.append(self.resource_cls.objects.get(**id_filter))
            return cleaned
        elif isinstance(instances, self.resource_cls):
            return instances
        else:
            id_filter = {
                self.inspect.resource_id_f: instances
            }
            return self.resource_cls.objects.get(**id_filter)
