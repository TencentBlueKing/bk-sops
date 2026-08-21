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

from django.test import TestCase, override_settings
from pipeline.contrib.external_plugins.models.base import FILE_SYSTEM, GIT, S3

from gcloud.external_plugins.exceptions import ForbiddenExternalPluginSourceError
from gcloud.external_plugins.protocol.readers import (
    GitReader,
    S3Reader,
    SourceReader,
    reader,
    reader_cls_factory,
    validate_git_branch,
    validate_git_repo_address,
)
from gcloud.tests.external_plugins.mock import *  # noqa
from gcloud.tests.external_plugins.mock_settings import *  # noqa


class TestSourceReader(TestCase):
    def setUp(self):
        self.TEST_TYPE = "TEST"

    def test_cls_factory(self):
        self.assertEqual(reader_cls_factory[GIT], GitReader)
        self.assertEqual(reader_cls_factory[S3], S3Reader)
        self.assertNotIn(FILE_SYSTEM, reader_cls_factory)

    def test_reader(self):
        @reader
        class TestReader(SourceReader):
            type = self.TEST_TYPE

            def read(self):
                pass

        self.assertEqual(reader_cls_factory[self.TEST_TYPE], TestReader)
        reader_cls_factory.pop(self.TEST_TYPE)

    @patch(OS_PATH_EXISTS, MagicMock(return_value=False))
    @patch(OS_MAKEDIRS, MagicMock(return_value=True))
    @patch(SHUTIL_RMTREE, MagicMock(return_value=True))
    def test_not_implement_read_raise(self):
        with self.assertRaises(NotImplementedError):

            class ErrorReader(SourceReader):
                type = "ERROR"

            ErrorReader("/local/", **{"test": 1}).read()


class TestGitReader(TestCase):
    def setUp(self):
        self.to_path = "/local/cache/"
        self.repo_address = "https://github.com/example/repo.git"
        self.branch = "master"

    @patch(OS_PATH_EXISTS, MagicMock(return_value=False))
    @patch(OS_MAKEDIRS, MagicMock(return_value=True))
    @patch(SHUTIL_RMTREE, MagicMock(return_value=True))
    def test_read(self):
        details = {
            "repo_address": self.repo_address,
            "branch": self.branch,
        }
        git_reader = GitReader(self.to_path, **details)

        mock_git = MockGitRepo()
        with patch(GCLOUD_EXTERNAL_PLUGINS_PROTOCOL_READERS_REPO, mock_git):
            git_reader.read()
            details.update({"to_path": self.to_path})
            self.assertEqual(mock_git.repo_info, details)


class TestS3Reader(TestCase):
    def setUp(self):
        self.to_path = "/local/cache/"
        self.service_address = "service_address"
        self.access_key = "access_key"
        self.secret_key = "secret_key"
        self.bucket = "bucket"

    @patch(OS_PATH_EXISTS, MagicMock(return_value=False))
    @patch(OS_MAKEDIRS, MagicMock(return_value=True))
    @patch(SHUTIL_RMTREE, MagicMock(return_value=True))
    def test_read(self):
        details = {
            "service_address": self.service_address,
            "access_key": self.access_key,
            "secret_key": self.secret_key,
            "bucket": self.bucket,
        }
        s3_reader = S3Reader(self.to_path, **details)

        mock_s3 = MockBoto3()
        files = (
            "file0",
            "first1/file1",
            "first1/second1/file11",
            "first1/second2/file12",
            "first2/file2",
            "first2/second1/file21",
            "first2/second2/file22",
        )
        with patch(GCLOUD_EXTERNAL_PLUGINS_PROTOCOL_READERS_BOTO3, mock_s3):
            s3_reader.read()
            self.assertEqual(set(mock_s3.files), set(["%s%s" % (self.to_path, _file) for _file in files]))


class TestValidateGitRepoAddress(TestCase):
    """RCE-2: 阻断远程 Git 包源地址中的危险传输协议/参数注入。"""

    @override_settings(EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT=False)
    def test_allow_normal_addresses(self):
        for addr in [
            "https://github.com/example/repo.git",
            "http://gitlab.internal/group/repo.git",
            "git://example.com/repo.git",
            "ssh://git@example.com/repo.git",
            "git@github.com:example/repo.git",
        ]:
            self.assertEqual(validate_git_repo_address(addr), addr)

    @override_settings(EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT=False)
    def test_reject_dangerous_addresses(self):
        for addr in [
            "ext::sh -c 'touch /tmp/pwn'",
            "fd::17/foo",
            "file:///etc/passwd",
            "-oProxyCommand=id",
            "--upload-pack=touch /tmp/pwn",
            "",
            "   ",
            "ftp://example.com/repo.git",
            "just-a-path/without-scheme",
        ]:
            with self.assertRaises(ForbiddenExternalPluginSourceError):
                validate_git_repo_address(addr)

    @override_settings(EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT=True)
    def test_secure_restrict_https_only(self):
        self.assertEqual(
            validate_git_repo_address("https://github.com/example/repo.git"),
            "https://github.com/example/repo.git",
        )
        for addr in [
            "http://github.com/example/repo.git",
            "git://example.com/repo.git",
            "ssh://git@example.com/repo.git",
            "git@github.com:example/repo.git",
        ]:
            with self.assertRaises(ForbiddenExternalPluginSourceError):
                validate_git_repo_address(addr)

    def test_validate_git_branch(self):
        self.assertEqual(validate_git_branch("master"), "master")
        self.assertIsNone(validate_git_branch(None))
        with self.assertRaises(ForbiddenExternalPluginSourceError):
            validate_git_branch("-oProxyCommand=id")

    @patch(OS_PATH_EXISTS, MagicMock(return_value=False))
    @patch(OS_MAKEDIRS, MagicMock(return_value=True))
    @patch(SHUTIL_RMTREE, MagicMock(return_value=True))
    @override_settings(EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT=False)
    def test_reader_rejects_dangerous_address_before_clone(self):
        details = {"repo_address": "ext::sh -c 'id'", "branch": "master"}
        git_reader = GitReader("/local/cache/", **details)

        mock_git = MockGitRepo()
        with patch(GCLOUD_EXTERNAL_PLUGINS_PROTOCOL_READERS_REPO, mock_git):
            with self.assertRaises(ForbiddenExternalPluginSourceError):
                git_reader.read()
            # clone 不应被触发, repo_info 维持初始空字典
            self.assertEqual(mock_git.repo_info, {})
