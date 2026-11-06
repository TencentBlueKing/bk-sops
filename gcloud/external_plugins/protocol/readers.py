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

import ipaddress
import logging
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

logger = logging.getLogger(__name__)

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


def validate_s3_service_address(service_address):
    """校验 S3 包源地址, 防止 SSRF 攻击。

    始终拒绝:
      * 非 HTTP/HTTPS 协议;
      * 本地地址 (127.0.0.1, localhost, ::1);
      * 元数据服务 (169.254.169.254);
      * IP 地址 (公网/私网均拒绝, 只允许域名);
      * 不在 ``settings.S3_ALLOWED_DOMAINS`` 白名单中的域名。
    """
    if not isinstance(service_address, str):
        raise ForbiddenExternalPluginSourceError("service_address must be a string")

    address = service_address.strip()
    if not address:
        raise ForbiddenExternalPluginSourceError("service_address cannot be empty")

    # 1. 预检查：拒绝 URL 中的危险字符（在解析前检查，防止被 urlparse 分割到不同部分）
    # 排除协议部分的检查（http:// 或 https://）
    url_without_scheme = address.split('://', 1)[-1] if '://' in address else address

    # 1.1 检查反斜杠
    if '\\' in url_without_scheme:
        raise ForbiddenExternalPluginSourceError(
            "反斜杠字符不允许出现在 URL 中，检测到可能的 URL 解析绕过攻击"
        )

    # 1.2 检查其他特殊字符（# 等）- 在 @ 之前检查
    dangerous_chars = ['#', '|', ' ', '\t', '\n', '\r']
    for char in dangerous_chars:
        if char in url_without_scheme:
            raise ForbiddenExternalPluginSourceError(
                f"URL 中不允许包含特殊字符 {repr(char)}，检测到可能的 URL 解析绕过攻击"
            )

    # 1.3 检查 @ 符号（userinfo）- 放在最后，因为它有专门的错误信息
    if '@' in url_without_scheme:
        raise ForbiddenExternalPluginSourceError(
            "URL 中不允许包含用户认证信息（username@host），检测到可能的 URL 解析绕过攻击"
        )

    # 2. 解析 URL
    try:
        parsed = urlparse(address)
    except Exception as e:
        raise ForbiddenExternalPluginSourceError(f"Invalid service_address: {address}") from e

    # 3. 协议检查：允许 HTTPS 和 HTTP（内网场景需要 HTTP）
    scheme = parsed.scheme.lower()
    if scheme not in ('https', 'http'):
        raise ForbiddenExternalPluginSourceError(
            f"Only HTTPS or HTTP is allowed for S3 service_address, got: {scheme}://"
        )

    # 4. netloc 检查
    netloc = parsed.netloc
    if not netloc:
        raise ForbiddenExternalPluginSourceError("Missing netloc in service_address")

    # 5. 主机名检查
    hostname = parsed.hostname
    if not hostname:
        raise ForbiddenExternalPluginSourceError("Missing hostname in service_address")

    # 6. 禁止本地地址
    if hostname.lower() in ['localhost', '127.0.0.1', '::1', '[::1]']:
        raise ForbiddenExternalPluginSourceError("Localhost addresses are not allowed")

    # 7. 禁止元数据服务
    if hostname == '169.254.169.254':
        raise ForbiddenExternalPluginSourceError("Metadata service address (169.254.169.254) is not allowed")

    # 8. 拒绝所有 IP 地址（只允许域名）
    try:
        ipaddress.ip_address(hostname)
        # 如果能解析为 IP 地址（无论公网/私网），直接拒绝
        raise ForbiddenExternalPluginSourceError(
            f"IP addresses are not allowed for S3 service_address. "
            f"Please use domain names instead: {hostname}"
        )
    except ValueError:
        # 不是 IP 地址，是域名，继续进行域名白名单检查
        pass
    except ForbiddenExternalPluginSourceError:
        # 重新抛出已有的 ForbiddenExternalPluginSourceError
        raise

    # 9. 白名单检查
    allowed_domains = getattr(settings, 'S3_ALLOWED_DOMAINS', [
        's3.amazonaws.com',
        's3.*.amazonaws.com',
        's3-*.amazonaws.com',
    ])

    # 支持通配符的域名匹配
    domain_allowed = False
    for allowed_pattern in allowed_domains:
        if allowed_pattern == '*':
            # 通配符允许所有（不推荐用于生产环境）
            domain_allowed = True
            break

        if allowed_pattern.startswith('*.'):
            # 后缀通配符匹配 (e.g., *.amazonaws.com)
            suffix = allowed_pattern[2:]  # "amazonaws.com"

            # 检查两种情况:
            # 1. 精确匹配 suffix: amazonaws.com
            if hostname == suffix:
                domain_allowed = True
                break

            # 2. 子域名匹配 (需要完整的标签分隔)
            if hostname.endswith('.' + suffix):
                domain_allowed = True
                break

        elif '*' in allowed_pattern:
            # 中间通配符匹配 (e.g., s3.*.amazonaws.com, s3-*.amazonaws.com)
            pattern_re = allowed_pattern.replace('.', r'\.').replace('*', '[a-zA-Z0-9-]+')
            pattern_re = f"^{pattern_re}$"
            if re.match(pattern_re, hostname):
                domain_allowed = True
                break
        elif hostname == allowed_pattern or hostname.endswith('.' + allowed_pattern):
            # 精确匹配或子域名匹配
            domain_allowed = True
            break

    if not domain_allowed:
        logger.warning(
            f"S3 service_address domain not in allowed list: {hostname}, "
            f"allowed_domains: {allowed_domains}"
        )
        raise ForbiddenExternalPluginSourceError(
            f"S3 域名 '{hostname}' 不在白名单中，请联系管理员将其添加到 S3_ALLOWED_DOMAINS 配置中"
        )

    return True


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
        # SSRF 防护：校验 service_address
        service_address = self.source_info.get("service_address")
        validate_s3_service_address(service_address)

        client = boto3.client(
            "s3",
            endpoint_url=service_address,
            aws_access_key_id=self.source_info["access_key"],
            aws_secret_access_key=self.source_info["secret_key"],
        )
        paginator = client.get_paginator("list_objects")
        self.__class__.download_s3_dir(client, paginator, self.source_info["bucket"], self.to_path)
