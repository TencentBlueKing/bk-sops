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

import os
import shutil
from abc import abstractmethod

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from pipeline.contrib.external_plugins.models.fields import JSONTextField
from pipeline.contrib.external_plugins.models import (
    GIT,
    S3,
    FILE_SYSTEM,
)

from gcloud.external_plugins import exceptions, CACHE_TEMP_PATH
from gcloud.external_plugins.models.base import PackageSource, PackageSourceManager
from gcloud.external_plugins.models.cache import CachePackageSource
from gcloud.external_plugins.protocol.readers import reader_cls_factory

source_cls_factory = {}
ORIGIN = 'origin'


def original_source(cls):
    source_cls_factory[cls.original_type()] = cls
    return cls


class OriginalPackageSourceManager(PackageSourceManager):
    @transaction.atomic()
    def add_original_source(self, name, source_type, packages, original_kwargs=None, **base_kwargs):
        full_kwargs = {
            'type': source_type,
            'name': name,
            'packages': packages
        }
        if original_kwargs is not None:
            full_kwargs.update(original_kwargs)
        full_kwargs.update(base_kwargs)
        # 未开启缓存机制，需要创建 base source
        if not CachePackageSource.objects.get_base_source():
            base_source = super(OriginalPackageSourceManager, self).add_base_source(name,
                                                                                    source_type,
                                                                                    packages,
                                                                                    **base_kwargs)
            full_kwargs['base_source_id'] = base_source.id
        original_source_cls = source_cls_factory[source_type]
        return original_source_cls.objects.create(**full_kwargs)

    def update_original_source(self, package_source_id, packages, original_kwargs=None, **base_kwargs):
        full_kwargs = {'packages': packages}
        if original_kwargs is not None:
            full_kwargs.update(original_kwargs)
        full_kwargs.update(base_kwargs)
        # use filter instead of get,because it will be updated later
        package_objs = self.filter(id=package_source_id)
        package_obj = package_objs[0]
        # 未开启缓存机制，需要更新 base source
        if not CachePackageSource.objects.get_base_source():
            # 新增时也未开启缓存，直接更新 base source
            if package_obj.base_source_id:
                super(OriginalPackageSourceManager, self).update_base_source(package_source_id,
                                                                             package_obj.type,
                                                                             packages,
                                                                             **base_kwargs)
            # 新增时开启了缓存，需要初始化 base source
            else:
                base_source = super(OriginalPackageSourceManager, self).add_base_source(package_obj.name,
                                                                                        package_obj.type,
                                                                                        packages,
                                                                                        **base_kwargs)
                full_kwargs['base_source_id'] = base_source.id
        else:
            super(OriginalPackageSourceManager, self).delete_base_source(package_source_id,
                                                                         package_obj.type)
            full_kwargs['base_source_id'] = None
        package_objs.update(**full_kwargs)


class OriginalPackageSource(PackageSource):
    name = models.CharField(_(u"包源"), max_length=128)
    desc = models.TextField(_(u"包源说明"), max_length=1000, blank=True)
    packages = JSONTextField(_(u"模块配置"))

    objects = OriginalPackageSourceManager()

    class Meta:
        abstract = True

    @property
    def category(self):
        return ORIGIN

    @staticmethod
    @abstractmethod
    def original_type():
        raise NotImplementedError()

    @property
    @abstractmethod
    def details(self):
        raise NotImplementedError()

    def prepare_cache_path(self):
        cache_path = os.path.join(CACHE_TEMP_PATH, self.name)
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)
        os.makedirs(cache_path)
        return cache_path

    def update_base_source(self, source_type, packages, **kwargs):
        if source_type != self.type:
            raise exceptions.OriginalSourceTypeError('Original source type cannot be updated')
        super(OriginalPackageSource, self).update_base_source(source_type, packages, **kwargs)

    def read(self):
        cache_path = self.prepare_cache_path()
        reader = reader_cls_factory[self.original_type()](cache_path, **self.details)
        reader.read()


@original_source
class GitRepoOriginalSource(OriginalPackageSource):
    repo_address = models.TextField(_(u"仓库链接"))
    repo_raw_address = models.TextField(_(u"文件托管仓库链接"), help_text=_(u"可以通过web直接访问源文件的链接前缀"))
    branch = models.CharField(_(u"分支名"), max_length=128)

    class Meta:
        verbose_name = _(u"GIT远程包源 GitRepoOriginalSource")
        verbose_name_plural = _(u"GIT远程包源 GitRepoOriginalSource")
        ordering = ['-id']

    @staticmethod
    def original_type():
        return GIT

    @property
    def details(self):
        return {
            'repo_address': self.repo_address,
            'repo_raw_address': self.repo_raw_address,
            'branch': self.branch
        }


@original_source
class S3OriginalSource(OriginalPackageSource):
    service_address = models.TextField(_(u"对象存储服务地址"))
    bucket = models.TextField(_(u"bucket 名"))
    access_key = models.TextField(_(u"access key"))
    secret_key = models.TextField(_(u"secret key"))

    class Meta:
        verbose_name = _(u"S3远程包源 S3OriginalSource")
        verbose_name_plural = _(u"S3远程包源 S3OriginalSource")
        ordering = ['-id']

    @staticmethod
    def original_type():
        return S3

    @property
    def details(self):
        return {
            'service_address': self.service_address,
            'bucket': self.bucket,
            'access_key': self.access_key,
            'secret_key': self.secret_key,
        }


@original_source
class FileSystemOriginalSource(OriginalPackageSource):
    path = models.TextField(_(u"文件系统路径"))

    class Meta:
        verbose_name = _(u"FS远程包源 FileSystemOriginalSource")
        verbose_name_plural = _(u"FS远程包源 FileSystemOriginalSource")
        ordering = ['-id']

    @staticmethod
    def original_type():
        return FILE_SYSTEM

    @property
    def details(self):
        return {
            'path': self.path
        }

    def read(self):
        raise exceptions.OriginalSourceTypeError('FileSystem original source does not support to be cached')
