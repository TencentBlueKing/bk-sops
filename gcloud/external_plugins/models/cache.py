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

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from gcloud.external_plugins import exceptions, CACHE_TEMP_PATH
from gcloud.external_plugins.models.base import PackageSource, PackageSourceManager
from gcloud.external_plugins.protocol.writers import writer_cls_factory

CACHE = 'cache'


class CachePackageSourceManager(PackageSourceManager):
    @transaction.atomic()
    def add_cache_source(self, name, source_type, packages, desc='', **kwargs):
        if source_type not in writer_cls_factory:
            raise exceptions.CacheSourceTypeError('Source type[%s] does not support as cache source' % source_type)

        if self.all().count() > 0:
            raise exceptions.MultipleCacheSourceError('Can not add multiple cache source')

        base_source = super(CachePackageSourceManager, self).add_base_source(name, source_type, packages, **kwargs)
        return self.create(type=source_type, base_source_id=base_source.id, desc=desc)

    def get_base_source(self):
        count = self.all().count()
        if count > 1:
            raise exceptions.MultipleCacheSourceError('Can not add multiple cache source')
        if count == 0:
            return None
        return self.all().first().base_source


class CachePackageSource(PackageSource):
    desc = models.TextField(_(u"包源说明"), max_length=1000, blank=True)

    objects = CachePackageSourceManager()

    class Meta:
        verbose_name = _(u"远程包源缓存 CachePackageSource")
        verbose_name_plural = _(u"远程包源缓存 CachePackageSource")
        ordering = ['-id']

    @property
    def category(self):
        return CACHE

    @property
    def name(self):
        return self.base_source.name

    @property
    def packages(self):
        return self.base_source.packages

    @property
    def details(self):
        return self.base_source.details()

    def write(self, sub_dir=None):
        if self.type not in writer_cls_factory:
            raise exceptions.CacheSourceTypeError('Source type[%s] does not support as cache source' % self.type)
        writer = writer_cls_factory[self.type](CACHE_TEMP_PATH, self.base_source)
        writer.write(sub_dir)
