# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os
import re
import shutil
from abc import abstractmethod
from urllib.parse import urlparse

import boto3
from django.conf import settings
from git import Repo
from pipeline.contrib.external_plugins.models.base import GIT, S3

from gcloud.external_plugins.exceptions import ForbiddenExternalPluginSourceError

reader_cls_factory = {}

# 远程 Git 包源地址允许的协议:
# - 始终允许 https;
# - http / git / ssh 仅在非安全收敛模式(EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT=False)下允许。
GIT_SCHEMES_SECURE = frozenset({"https"})
GIT_SCHEMES_LOOSE = frozenset({"http", "https", "git", "ssh"})
# SCP 形式: user@host:path; host 段不含 '/', 且 ':' 后不能再是 ':' 以排除 ext::/fd:: 传输助手。
SCP_LIKE_GIT_URL_RE = re.compile(r"^[A-Za-z0-9._\-]+@[A-Za-z0-9._\-]+:(?!:)[^\s]+$")


def validate_git_repo_address(repo_address):
    """校验远程 Git 包源地址, 阻断 git 危险传输协议导致的命令执行 / 本地文件读取(RCE/LFI)。

    始终拒绝:
      * ``ext::`` / ``fd::`` 等 git 传输助手(``ext::sh -c '...'`` 可直接 RCE);
      * ``file://`` 本地仓库;
      * 以 ``-`` 开头的地址(会被 git 当作命令行选项, 造成参数注入);
      * 协议不在允许列表中的地址。

    当 ``settings.EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT`` 为真时, 仅允许 ``https``。
    """
    if not isinstance(repo_address, str):
        raise ForbiddenExternalPluginSourceError("repo_address must be a string")

    address = repo_address.strip()
    if not address:
        raise ForbiddenExternalPluginSourceError("repo_address can not be empty")

    # 选项注入: git clone 会把以 '-' 开头的参数当作选项
    if address.startswith("-"):
        raise ForbiddenExternalPluginSourceError("repo_address can not start with '-'")

    # git 传输助手(ext::/fd:: 等)一律拒绝
    if "::" in address:
        raise ForbiddenExternalPluginSourceError("git transport helper in repo_address is not allowed")

    secure_only = getattr(settings, "EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT", False)
    allowed_schemes = GIT_SCHEMES_SECURE if secure_only else GIT_SCHEMES_LOOSE

    try:
        parsed = urlparse(address)
    except ValueError:
        raise ForbiddenExternalPluginSourceError("invalid repo_address: {}".format(address))

    scheme = parsed.scheme.lower()
    if scheme:
        if scheme not in allowed_schemes:
            raise ForbiddenExternalPluginSourceError("unsupported repo_address scheme: {}".format(scheme))
        if not parsed.netloc:
            raise ForbiddenExternalPluginSourceError("repo_address must contain a host")
        return address

    # 无显式协议时仅允许 SCP 形式(git@host:path), 且安全收敛模式下不允许
    if not secure_only and SCP_LIKE_GIT_URL_RE.match(address):
        return address

    raise ForbiddenExternalPluginSourceError("unsupported repo_address: {}".format(address))


def validate_git_branch(branch):
    """校验 git 分支名, 阻断以 ``-`` 开头的分支名被 git 当作选项造成参数注入。"""
    if branch is None:
        return branch
    if not isinstance(branch, str):
        raise ForbiddenExternalPluginSourceError("branch must be a string")
    if branch.strip().startswith("-"):
        raise ForbiddenExternalPluginSourceError("branch can not start with '-'")
    return branch


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
        repo_address = validate_git_repo_address(self.source_info["repo_address"])
        branch = validate_git_branch(self.source_info["branch"])
        Repo.clone_from(repo_address, self.to_path, branch=branch)
        shutil.rmtree(os.path.join(self.to_path, ".git"))
        shutil.rmtree(os.path.join(self.to_path, ".idea"))


@reader
class S3Reader(SourceReader):
    type = S3

    @classmethod
    def download_s3_dir(cls, client, paginator, bucket, local, source_dir=""):
        """
        @summary: 把S3 中的目录source_dir按照目录层级下载到本地local目录
        @param client: S3 client
        @param paginator: S3 client 的 paginator
        @param local: 本地目录
        @param bucket: S3 bucket
        @param source_dir: S3 子目录，为空则下载bucket所有文件
        @return: None
        """
        for page in paginator.paginate(Bucket=bucket, Delimiter="/", Prefix=source_dir):
            # iter dirs (e.g. /)
            # iter dirs (e.g. /first1)
            # iter dirs (e.g. /first1/second1)
            for subdir in page.get("CommonPrefixes", []):
                cls.download_s3_dir(client, paginator, bucket, local, subdir.get("Prefix"))
            # iter files (e.g. /first1/second1/file.py)
            for _file in page.get("Contents", []):
                key = _file.get("Key", "")
                if key[:1] in "/\\":
                    full_path = os.path.join(local, key[1:])
                else:
                    full_path = os.path.join(local, key)
                if not os.path.exists(os.path.dirname(full_path)):
                    os.makedirs(os.path.dirname(full_path))
                client.download_file(Bucket=bucket, Key=key, Filename=full_path)

    def read(self):
        client = boto3.client(
            "s3",
            endpoint_url=self.source_info["service_address"],
            aws_access_key_id=self.source_info["access_key"],
            aws_secret_access_key=self.source_info["secret_key"],
        )
        paginator = client.get_paginator("list_objects")
        self.__class__.download_s3_dir(client, paginator, self.source_info["bucket"], self.to_path)
