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

from pipeline.contrib.external_plugins.models.base import S3, FILE_SYSTEM

writer_cls_factory = {}


def writer(cls):
    writer_cls_factory[cls.type] = cls
    return cls


class SourceWriter(object):
    def __init__(self, from_path, base_source):
        self.from_path = from_path
        self.base_source = base_source

    @abstractmethod
    def write(self, sub_dir=None):
        raise NotImplementedError()


@writer
class S3Writer(SourceWriter):
    type = S3

    @classmethod
    def upload_s3_dir(cls, client, bucket, local, target_dir=''):
        """
        @summary: 把本地local目录按照目录层级上传到S3 中的目录target_dir
        @param client: S3 client
        @param bucket: S3 bucket
        @param local: 本地目录，必须是绝对路径
        @param target_dir: S3 目标子目录，为空则上传到根目录
        @return:
        """
        if local != '' and local[:1] not in '/\\':
            local = os.path.sep + local
        for root, _, files in os.walk(local):
            subdir = root.split(local)[1]
            for _file in files:
                full_path = os.path.join(target_dir, subdir, _file)
                # transfer absolute path to relative
                if full_path[0] in '/\\':
                    full_path = full_path[1:]
                local_path = os.path.join(root, _file)
                client.upload_file(Filename=local_path, Bucket=bucket, Key=full_path)

    def write(self, sub_dir=None):
        if os.path.exists(self.from_path):
            client = boto3.client('s3',
                                  endpoint_url=self.base_source.service_address,
                                  aws_access_key_id=self.base_source.access_key,
                                  aws_secret_access_key=self.base_source.secret_key)
            if sub_dir is None:
                sub_dir = ['']
            for sub in sub_dir:
                from_path = os.path.join(self.from_path, sub)
                self.__class__.upload_s3_dir(client, self.base_source.bucket, from_path)


@writer
class FileSystemWriter(SourceWriter):
    type = FILE_SYSTEM

    def write(self, sub_dir=None):
        if os.path.exists(self.from_path):
            if sub_dir is None:
                sub_dir = ['']
            for sub in sub_dir:
                from_path = os.path.join(self.from_path, sub)
                shutil.move(from_path, self.base_source.path)
