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

from .base import ObjectResource

from django.db.models.signals import post_save, post_delete


class DjangoModelResource(ObjectResource):

    def __init__(self, *args, **kwargs):
        super(DjangoModelResource, self).__init__(*args, **kwargs)

        # register django model action handlers
        self._dispatch_handlers()

    def _post_save_handler(self, sender, instance, created, **kwargs):
        if created:
            self.register_instance(instance)
        else:
            self.update_instance(instance)

    def _post_delete_handler(self, sender, instance, **kwargs):
        self.delete_instance(instance)

    def _dispatch_handlers(self):
        post_save.connect(receiver=self._post_save_handler, sender=self.resource_cls)
        post_delete.connect(receiver=self._post_delete_handler, sender=self.resource_cls)
