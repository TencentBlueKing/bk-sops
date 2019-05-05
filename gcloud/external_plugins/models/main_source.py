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

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from pipeline.contrib.external_plugins.models import source_cls_factory as base_source_cls_factory

from gcloud.external_plugins import exceptions


class MainPackageSourceManager(models.Manager):
    @transaction.atomic()
    def add_main_source(self, name, source_type, packages, **kwargs):
        if self.all().count() > 0:
            raise exceptions.MultipleMainSourceError('Can not add multiple main source')

        base_source_cls = base_source_cls_factory[source_type]
        base_source = base_source_cls.objects.create_source(name=name, packages=packages, from_config=False, **kwargs)
        return self.create(type=source_type,
                           base_source_id=base_source.id)

    def update_main_source(self, source_id, source_type, packages, **kwargs):
        main_source = self.get(id=source_id)
        main_source.update_base_source(source_type=source_type, packages=packages, **kwargs)

    def delete_main_source(self, source_id):
        main_source = self.get(id=source_id)
        main_source.delete()


class MainPackageSource(models.Model):
    type = models.CharField(_(u"包源类型"), max_length=64)
    base_source_id = models.IntegerField(_(u"包源模型 ID"))

    objects = MainPackageSourceManager()
    _base_source_attr = '_base_source'

    @property
    def base_source(self):
        source = getattr(self, self._base_source_attr, None)
        if not source:
            base_source_cls = base_source_cls_factory[self.type]
            source = base_source_cls.objects.get(id=self.base_source_id)
            setattr(self, self._base_source_attr, source)

        return source

    @property
    def name(self):
        return self.base_source.name

    @property
    def packages(self):
        return self.base_source.packages

    @property
    def details(self):
        return self.base_source.details()

    def delete(self, using=None, keep_parents=False):
        self.delete_base_source()
        return super(MainPackageSource, self).delete(using=using, keep_parents=keep_parents)

    def delete_base_source(self):
        if hasattr(self, self._base_source_attr):
            self.base_source.delete()
            delattr(self, self._base_source_attr)
        else:
            base_source_cls = base_source_cls_factory[self.type]
            base_source_cls.objects.filter(id=self.base_source_id).delete()

    def update_base_source(self, source_type, packages, **kwargs):
        if source_type != self.type:
            with transaction.atomic():
                new_base_source_cls = base_source_cls_factory[source_type]
                base_source = new_base_source_cls.objects.create_source(name=self.name,
                                                                        packages=packages,
                                                                        from_config=False,
                                                                        **kwargs)
                self.type = source_type
                self.delete_base_source()
                self.base_source_id = base_source.id
                self.save()
        else:
            base_source_cls = base_source_cls_factory[self.type]
            base_source_cls.objects.filter(id=self.base_source_id).update(
                packages=packages,
                **kwargs
            )
            if hasattr(self, self._base_source_attr):
                self.base_source.refresh_from_db()
