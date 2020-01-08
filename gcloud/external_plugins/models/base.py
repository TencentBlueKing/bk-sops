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

from pipeline.contrib.external_plugins.models import source_cls_factory as base_source_cls_factory

source_cls_factory = {}


class PackageSourceManager(models.Manager):

    @staticmethod
    def get_base_source_cls(source_type):
        """
        @summary: 获取 base source
        @param source_type:
        @return:
        """
        return base_source_cls_factory[source_type]

    def get_base_source_fields(self, source_type):
        """
        @summary: 获取 base source 的数据库字段
        @param source_type:
        @return:
        """
        source_model = self.get_base_source_cls(source_type)
        all_fields = [field.name for field in source_model._meta.get_fields()]
        return all_fields

    def divide_details_parts(self, source_type, details):
        """
        @summary: divide details into two parts
            base_kwargs: fields in base model(e.g. fields of pipeline.contrib.external_plugins.models.GitRepoSource)
            original_kwargs: field in origin model but not in base model(e.g. repo_address、desc)
        @param source_type:
        @param details:
        @return:
        """
        all_fields = self.get_base_source_fields(source_type)
        original_kwargs = {}
        base_kwargs = {}
        for key, value in details.items():
            if key in all_fields:
                base_kwargs[key] = value
            else:
                original_kwargs[key] = value
        return original_kwargs, base_kwargs

    @transaction.atomic()
    def add_base_source(self, name, source_type, packages, **kwargs):
        base_source_cls = self.get_base_source_cls(source_type)
        base_source = base_source_cls.objects.create_source(name=name, packages=packages, from_config=False, **kwargs)
        return base_source

    def delete_base_source(self, package_source_id, source_type):
        base_source_cls = base_source_cls_factory[source_type]
        package_source = self.get(id=package_source_id)
        base_source_cls.objects.filter(id=package_source.base_source_id).delete()

    def update_base_source(self, package_source_id, source_type, packages, **kwargs):
        package_source = self.get(id=package_source_id)
        package_source.update_base_source(source_type=source_type, packages=packages, **kwargs)


class PackageSource(models.Model):
    type = models.CharField(_(u"包源类型"), max_length=64)
    base_source_id = models.IntegerField(_(u"包源模型 ID"), blank=True, null=True)

    _base_source_attr = '_base_source'

    class Meta:
        abstract = True

    @property
    def base_source(self):
        source = getattr(self, self._base_source_attr, None)
        if not source and self.base_source_id is not None:
            base_source_cls = base_source_cls_factory[self.type]
            source = base_source_cls.objects.get(id=self.base_source_id)
            setattr(self, self._base_source_attr, source)

        return source

    @property
    def imported_plugins(self):
        return self.base_source.imported_plugins

    def delete(self, using=None, keep_parents=False):
        self.delete_base_source()
        return super(PackageSource, self).delete(using=using, keep_parents=keep_parents)

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
