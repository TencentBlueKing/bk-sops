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

from copy import deepcopy
from abc import abstractmethod

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

source_cls_factory = {}


def sync_source(cls):
    source_cls_factory[cls.type()] = cls
    return cls


class RootPackageManager(models.Manager):
    def create_packages_for_source(self, source, root_packages):
        packages = [RootPackage(name=package, source_type=source.type(), source_id=source.id) for package in
                    root_packages]
        return self.bulk_create(packages, batch_size=5000)

    def delete_packages_in_source(self, source):
        return self.filter(source_type=source.type(), source_id=source.id).delete()

    def packages_for_source(self, source):
        return self.filter(source_type=source.type(), source_id=source.id).all()


class RootPackage(models.Model):
    name = models.CharField(_(u'包名'), max_length=128)
    source_type = models.CharField(_(u"包源类型"), max_length=64)
    source_id = models.IntegerField(_(u"同步源 ID"))

    objects = RootPackageManager()


class SyncPackageSourceManager(models.Manager):
    @transaction.atomic()
    def create_source(self, name, root_packages, **kwargs):
        create_kwargs = deepcopy(kwargs)
        create_kwargs.update({'name': name})
        source = self.create(**create_kwargs)
        RootPackage.objects.create_packages_for_source(source=source, root_packages=root_packages)
        return source

    @transaction.atomic()
    def delete_source(self, source_id):
        source = self.get(id=source_id)
        RootPackage.objects.delete_packages_in_source(source)
        return source.delete()


class SyncPackageSource(models.Model):
    name = models.CharField(_(u'同步源名'), max_length=128)

    objects = SyncPackageSourceManager()

    class Meta:
        abstract = True

    @staticmethod
    @abstractmethod
    def type():
        raise NotImplementedError()

    @abstractmethod
    def details(self):
        raise NotImplementedError()

    @property
    def root_packages(self):
        return RootPackage.objects.packages_for_source(self)

    def delete(self, using=None, keep_parents=False):
        RootPackage.objects.delete_packages_in_source(self)
        super(SyncPackageSource, self).delete(using=using, keep_parents=keep_parents)
