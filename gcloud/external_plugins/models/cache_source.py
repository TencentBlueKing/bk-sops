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

import boto3
from django.db import transaction

from pipeline.contrib.external_plugins.models.base import S3, FILE_SYSTEM

from gcloud.external_plugins import exceptions, CACHE_TEMP_PATH
from gcloud.external_plugins.models.package_base import PackageSource, PackageSourceManager


def upload_s3_dir(client, bucket, local, target_dir=''):
    """
    @summary: 把本地local目录按照目录层级上传到S3 中的目录target_dir
    @param client: S3 client
    @param bucket: S3 bucket
    @param local: 本地目录
    @param target_dir: S3 目标子目录，为空则上传到根目录
    @return:
    """
    if local != '' and local[:1] not in '/\\':
        local = local.append(os.path.sep)
    for root, _, files in os.walk(local):
        subdir = root.split(local)[1]
        for _file in files:
            full_path = os.path.join(target_dir, subdir, _file)
            local_path = os.path.join(root, _file)
            client.upload_file(Filename=local_path, Bucket=bucket, Key=full_path)


class CachePackageSourceManager(PackageSourceManager):
    @transaction.atomic()
    def add_cache_source(self, name, source_type, packages, **kwargs):
        if self.all().count() > 0:
            raise exceptions.MultipleCacheSourceError('Can not add multiple cache source')

        if source_type not in [S3, FILE_SYSTEM]:
            raise exceptions.CacheSourceTypeError('Source type[%s] does not support as cache source' % source_type)

        base_source = super(CachePackageSourceManager, self).add_base_source(name, source_type, packages, **kwargs)
        return self.create(type=source_type, base_source_id=base_source.id)

    def get_base_source(self):
        count = self.all().count()
        if count > 1:
            raise exceptions.MultipleCacheSourceError('Can not add multiple cache source')
        if count == 0:
            return None
        cache_source = self.all().first()
        return cache_source.base_source


class CachePackageSource(PackageSource):

    objects = CachePackageSourceManager()

    @property
    def name(self):
        return self.base_source.name

    @property
    def packages(self):
        return self.base_source.packages

    @property
    def details(self):
        return self.base_source.details()

    def writer(self):
        if self.type == FILE_SYSTEM:
            shutil.move(CACHE_TEMP_PATH, self.base_source.path)
        elif self.type == S3:
            cache_path = CACHE_TEMP_PATH
            if not os.path.exists(cache_path):
                os.makedirs(cache_path)
            client = boto3.client('s3',
                                  endpoint_url=self.base_source.service_address,
                                  aws_access_key_id=self.base_source.access_key,
                                  aws_secret_access_key=self.base_source.secret_key)
            upload_s3_dir(client, self.base_source.bucket, cache_path)
        else:
            raise exceptions.CacheSourceTypeError('Source type[%s] does not support as cache source' % self.type)
