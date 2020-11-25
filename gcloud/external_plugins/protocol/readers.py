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

import boto3
from git import Repo

from pipeline.contrib.external_plugins.models.base import GIT, S3

reader_cls_factory = {}


def reader(cls):
    reader_cls_factory[cls.type] = cls
    return cls


class SourceReader(object):
    def __init__(self, to_path, **kwargs):
        if os.path.exists(to_path):
            shutil.rmtree(to_path)
        os.makedirs(to_path)
        self.to_path = to_path
        self.source_info = kwargs

    @abstractmethod
    def read(self):
        raise NotImplementedError()


@reader
class GitReader(SourceReader):
    type = GIT

    def read(self):
        Repo.clone_from(self.source_info['repo_address'], self.to_path, branch=self.source_info['branch'])
        shutil.rmtree(os.path.join(self.to_path, '.git'))
        shutil.rmtree(os.path.join(self.to_path, '.idea'))


@reader
class S3Reader(SourceReader):
    type = S3

    @classmethod
    def download_s3_dir(cls, client, paginator, bucket, local, source_dir=''):
        """
        @summary: 把S3 中的目录source_dir按照目录层级下载到本地local目录
        @param client: S3 client
        @param paginator: S3 client 的 paginator
        @param local: 本地目录
        @param bucket: S3 bucket
        @param source_dir: S3 子目录，为空则下载bucket所有文件
        @return: None
        """
        for page in paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=source_dir):
            # iter dirs (e.g. /)
            # iter dirs (e.g. /first1)
            # iter dirs (e.g. /first1/second1)
            for subdir in page.get('CommonPrefixes', []):
                cls.download_s3_dir(client, paginator, bucket, local, subdir.get('Prefix'))
            # iter files (e.g. /first1/second1/file.py)
            for _file in page.get('Contents', []):
                key = _file.get('Key', '')
                if key[:1] in '/\\':
                    full_path = os.path.join(local, key[1:])
                else:
                    full_path = os.path.join(local, key)
                if not os.path.exists(os.path.dirname(full_path)):
                    os.makedirs(os.path.dirname(full_path))
                client.download_file(Bucket=bucket, Key=key, Filename=full_path)

    def read(self):
        client = boto3.client('s3',
                              endpoint_url=self.source_info['service_address'],
                              aws_access_key_id=self.source_info['access_key'],
                              aws_secret_access_key=self.source_info['secret_key'])
        paginator = client.get_paginator('list_objects')
        self.__class__.download_s3_dir(client, paginator, self.source_info['bucket'], self.to_path)
