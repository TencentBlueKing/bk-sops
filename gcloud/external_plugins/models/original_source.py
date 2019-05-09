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

import os
import shutil
from abc import abstractmethod

import boto3
from git import Repo
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from pipeline.contrib.external_plugins.models.fields import JSONTextField
from pipeline.contrib.external_plugins.models import (
    GIT,
    S3,
    FILE_SYSTEM,
)

from gcloud.external_plugins import exceptions, CACHE_TEMP_PATH
from gcloud.external_plugins.models.package_base import PackageSource, PackageSourceManager
from gcloud.external_plugins.models.cache_source import CachePackageSource

source_cls_factory = {}


def decor_original_source(cls):
    source_cls_factory[cls.original_type()] = cls
    return cls


class OriginalPackageSourceManager(PackageSourceManager):
    @transaction.atomic()
    def add_original_source(self, name, source_type, packages, original_kwargs=None, **base_kwargs):
        full_kwargs = {}
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
        return original_source_cls.objects.create(type=source_type,
                                                  name=name,
                                                  packages=packages,
                                                  **full_kwargs)

    def update_original_source(self, package_id, packages, original_kwargs=None, **base_kwargs):
        full_kwargs = {}
        if original_kwargs is not None:
            full_kwargs.update(original_kwargs)
        package = self.filter(id=package_id)
        super(OriginalPackageSourceManager, self).update_package_source(package_id,
                                                                        package[0].type,
                                                                        packages,
                                                                        **base_kwargs)
        package.update(**full_kwargs)


class OriginalPackageSource(PackageSource):
    name = models.CharField(_(u"包源"), max_length=128)
    desc = models.TextField(_(u"包源说明"), max_length=1000, blank=True)
    packages = JSONTextField(_(u"模块配置"))

    objects = OriginalPackageSourceManager()

    class Meta:
        abstract = True

    @staticmethod
    @abstractmethod
    def original_type():
        raise NotImplementedError()

    @abstractmethod
    def reader(self):
        raise NotImplementedError()

    def update_base_source(self, source_type, packages, **kwargs):
        if source_type != self.type:
            raise exceptions.OriginalSourceTypeError('Original source type cannot be updated')
        super(OriginalPackageSource, self).update_base_source(source_type, packages, **kwargs)


@decor_original_source
class GitRepoOriginalSource(OriginalPackageSource):
    repo_address = models.TextField(_(u"仓库链接"))
    repo_raw_address = models.TextField(_(u"文件托管仓库链接"), help_text=_(u"可以通过web直接访问源文件的链接前缀"))
    branch = models.CharField(_(u"分支名"), max_length=128)

    @staticmethod
    def original_type():
        return GIT

    def details(self):
        return {
            'repo_address': self.repo_address,
            'repo_raw_address': self.repo_raw_address,
            'branch': self.branch
        }

    def reader(self):
        cache_path = os.path.join(CACHE_TEMP_PATH, self.name)
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)
        os.makedirs(cache_path)
        Repo.clone_from(self.repo_address, cache_path, branch=self.branch)


def download_s3_dir(client, paginator, bucket, local, source_dir=''):
    """
    @summary: 把S3 中的目录source_dir按照目录层级下载到本地local目录
    @param client: S3 client
    @param paginator: S3 client 的 paginator
    @param local: 本地目录
    @param bucket: S3 bucket
    @param source_dir: S3 子目录，为空则下载所有文件
    @return: None
    """
    for result in paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=source_dir):
        if result.get('CommonPrefixes') is not None:
            for subdir in result.get('CommonPrefixes'):
                download_s3_dir(client, paginator, bucket, local, subdir.get('Prefix'))
        for _file in result.get('Contents', []):
            if _file.get('Key', '')[:1] in '/\\':
                full_path = os.path.join(local, _file.get('Key')[1:])
            else:
                full_path = os.path.join(local, _file.get('Key'))
            if not os.path.exists(os.path.dirname(full_path)):
                os.makedirs(os.path.dirname(full_path))
            client.download_file(bucket, _file.get('Key'), full_path)


@decor_original_source
class S3OriginalSource(OriginalPackageSource):
    service_address = models.TextField(_(u"对象存储服务地址"))
    bucket = models.TextField(_(u"bucket 名"))
    access_key = models.TextField(_(u"access key"))
    secret_key = models.TextField(_(u"secret key"))

    @staticmethod
    def original_type():
        return S3

    def details(self):
        return {
            'service_address': self.service_address,
            'bucket': self.bucket,
            'access_key': self.access_key,
            'secret_key': self.secret_key,
        }

    def reader(self):
        cache_path = os.path.join(CACHE_TEMP_PATH, self.name)
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
        client = boto3.client('s3',
                              endpoint_url=self.service_address,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key)
        paginator = client.get_paginator('list_objects')
        download_s3_dir(client, paginator, self.bucket, cache_path)


@decor_original_source
class FileSystemOriginalSource(OriginalPackageSource):
    path = models.TextField(_(u"文件系统路径"))

    @staticmethod
    def original_type():
        return FILE_SYSTEM

    def details(self):
        return {
            'path': self.path
        }

    def reader(self):
        raise exceptions.OriginalSourceTypeError('FileSystem original source does not support to be cached')
