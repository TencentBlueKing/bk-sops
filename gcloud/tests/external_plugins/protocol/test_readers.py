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
    validate_s3_service_address,
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
        self.service_address = "https://s3.amazonaws.com"
        self.access_key = "access_key"
        self.secret_key = "secret_key"
        self.bucket = "bucket"

    @patch(OS_PATH_EXISTS, MagicMock(return_value=False))
    @patch(OS_MAKEDIRS, MagicMock(return_value=True))
    @patch(SHUTIL_RMTREE, MagicMock(return_value=True))
    @override_settings(S3_ALLOWED_DOMAINS=['s3.amazonaws.com'])
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


class TestValidateS3ServiceAddress(TestCase):
    """SSRF 防护测试：S3 service_address 地址校验"""

    # ========== 应该通过的用例 ==========
    @override_settings(S3_ALLOWED_DOMAINS=['s3.amazonaws.com', 's3.*.amazonaws.com', 's3-*.amazonaws.com'])
    def test_allow_aws_s3_standard_endpoints(self):
        """允许标准 AWS S3 端点"""
        valid_addresses = [
            "https://s3.amazonaws.com",
            "https://s3.us-west-2.amazonaws.com",
            "https://s3-us-east-1.amazonaws.com",
            "https://s3-ap-southeast-1.amazonaws.com",
        ]
        for addr in valid_addresses:
            try:
                result = validate_s3_service_address(addr)
                self.assertTrue(result)
            except ForbiddenExternalPluginSourceError as e:
                self.fail(f"Address '{addr}' should be allowed but got: {e}")

    @override_settings(S3_ALLOWED_DOMAINS=['minio.company.com', 's3.amazonaws.com'])
    def test_allow_custom_s3_compatible_services(self):
        """允许配置的自建 S3 兼容服务"""
        result = validate_s3_service_address("https://minio.company.com")
        self.assertTrue(result)

    @override_settings(S3_ALLOWED_DOMAINS=['*.s3.internal', 's3.amazonaws.com'])
    def test_allow_subdomain_matching(self):
        """允许子域名匹配"""
        result = validate_s3_service_address("https://bucket.s3.internal")
        self.assertTrue(result)

    # ========== 应该拒绝的用例 ==========
    @override_settings(S3_ALLOWED_DOMAINS=['s3.amazonaws.com', 's3.*.amazonaws.com'])
    def test_allow_http_protocol(self):
        """允许 HTTP 协议（内网场景需要）"""
        result = validate_s3_service_address("http://s3.amazonaws.com")
        self.assertTrue(result)

    @override_settings(S3_ALLOWED_DOMAINS=['minio.internal.com'])
    def test_allow_http_for_internal_services(self):
        """允许内网 HTTP 服务"""
        result = validate_s3_service_address("http://minio.internal.com")
        self.assertTrue(result)

    @override_settings(S3_ALLOWED_DOMAINS=['s3.amazonaws.com'])
    def test_reject_unsupported_protocols(self):
        """拒绝不支持的协议（FTP、FILE等）"""
        unsupported_protocols = [
            "ftp://s3.amazonaws.com",
            "file:///etc/passwd",
            "gopher://s3.amazonaws.com",
        ]
        for addr in unsupported_protocols:
            with self.assertRaises(ForbiddenExternalPluginSourceError) as ctx:
                validate_s3_service_address(addr)
            self.assertIn("Only HTTPS or HTTP", str(ctx.exception))

    @override_settings(S3_ALLOWED_DOMAINS=['s3.amazonaws.com'])
    def test_reject_localhost_addresses(self):
        """拒绝本地地址"""
        localhost_variants = [
            "https://localhost",
            "https://127.0.0.1",
            "https://::1",
            "https://[::1]",
        ]
        for addr in localhost_variants:
            with self.assertRaises(ForbiddenExternalPluginSourceError) as ctx:
                validate_s3_service_address(addr)
            # localhost 会被 "Missing hostname" 拒绝，IP 地址会被 "IP addresses are not allowed" 拒绝
            error_msg = str(ctx.exception).lower()
            self.assertTrue(
                "not allowed" in error_msg or "missing hostname" in error_msg,
                f"Unexpected error message for {addr}: {ctx.exception}"
            )

    @override_settings(S3_ALLOWED_DOMAINS=['s3.amazonaws.com'])
    def test_reject_private_ip_addresses(self):
        """拒绝私网 IP 地址"""
        private_ips = [
            "https://10.0.0.1",
            "https://10.255.255.255",
            "https://172.16.0.1",
            "https://172.31.255.255",
            "https://192.168.0.1",
            "https://192.168.255.255",
        ]
        for addr in private_ips:
            with self.assertRaises(ForbiddenExternalPluginSourceError) as ctx:
                validate_s3_service_address(addr)
            self.assertIn("IP addresses are not allowed", str(ctx.exception))

    @override_settings(S3_ALLOWED_DOMAINS=['s3.amazonaws.com'])
    def test_reject_metadata_service(self):
        """拒绝 AWS 元数据服务"""
        with self.assertRaises(ForbiddenExternalPluginSourceError) as ctx:
            validate_s3_service_address("https://169.254.169.254")
        self.assertIn("Metadata service", str(ctx.exception))

    @override_settings(S3_ALLOWED_DOMAINS=['s3.amazonaws.com'])
    def test_reject_unlisted_domains(self):
        """拒绝不在白名单中的域名"""
        with self.assertRaises(ForbiddenExternalPluginSourceError) as ctx:
            validate_s3_service_address("https://evil.attacker.com")
        self.assertIn("不在白名单中", str(ctx.exception))

    @override_settings(S3_ALLOWED_DOMAINS=['*.amazonaws.com', 's3.amazonaws.com'])
    def test_reject_domain_suffix_injection(self):
        """拒绝域名后缀注入攻击

        防护: *.amazonaws.com 模式应该匹配:
        - s3.amazonaws.com ✓
        - bucket.s3.amazonaws.com ✓
        - amazonaws.com ✓

        但不应该匹配:
        - evil.amazonaws.com.attacker.com ✗ (后缀注入)
        """
        # 这是关键的安全测试
        with self.assertRaises(ForbiddenExternalPluginSourceError) as ctx:
            validate_s3_service_address("https://evil.amazonaws.com.attacker.com")
        self.assertIn("不在白名单中", str(ctx.exception))

    @override_settings(S3_ALLOWED_DOMAINS=['*.amazonaws.com'])
    def test_allow_wildcard_subdomain_matching(self):
        """允许通配符子域名正确匹配"""
        valid_cases = [
            "https://s3.amazonaws.com",  # 直接子域名
            "https://bucket.s3.amazonaws.com",  # 多级子域名
            "https://my.bucket.s3.amazonaws.com",  # 更多级子域名
            "https://amazonaws.com",  # 基域名本身
        ]
        for addr in valid_cases:
            try:
                result = validate_s3_service_address(addr)
                self.assertTrue(result, f"Address {addr} should be allowed")
            except ForbiddenExternalPluginSourceError as e:
                self.fail(f"Address '{addr}' should be allowed but got: {e}")

    @override_settings(S3_ALLOWED_DOMAINS=['s3.amazonaws.com'])
    def test_reject_missing_hostname(self):
        """拒绝缺少主机名的地址"""
        with self.assertRaises(ForbiddenExternalPluginSourceError) as ctx:
            validate_s3_service_address("https://")
        self.assertIn("Missing hostname", str(ctx.exception))

    @override_settings(S3_ALLOWED_DOMAINS=['s3.amazonaws.com'])
    def test_reject_empty_address(self):
        """拒绝空地址"""
        with self.assertRaises(ForbiddenExternalPluginSourceError) as ctx:
            validate_s3_service_address("")
        self.assertIn("cannot be empty", str(ctx.exception))

    @override_settings(S3_ALLOWED_DOMAINS=['s3.amazonaws.com'])
    def test_reject_non_string_address(self):
        """拒绝非字符串地址"""
        with self.assertRaises(ForbiddenExternalPluginSourceError) as ctx:
            validate_s3_service_address(123)
        self.assertIn("must be a string", str(ctx.exception))

    @override_settings(S3_ALLOWED_DOMAINS=['s3.amazonaws.com'])
    def test_reject_dns_rebinding_attempt(self):
        """拒绝 DNS 重绑定攻击"""
        # 虽然看起来是有效域名，但实际是 SSRF 探针
        with self.assertRaises(ForbiddenExternalPluginSourceError) as ctx:
            validate_s3_service_address("https://s32924a.0a5ef482.dns.iegsec.online")
        self.assertIn("不在白名单中", str(ctx.exception))

    # ========== S3Reader 集成测试 ==========
    @patch(OS_PATH_EXISTS, MagicMock(return_value=False))
    @patch(OS_MAKEDIRS, MagicMock(return_value=True))
    @patch(SHUTIL_RMTREE, MagicMock(return_value=True))
    @override_settings(S3_ALLOWED_DOMAINS=['s3.amazonaws.com'])
    def test_s3reader_rejects_ssrf_before_boto3_call(self):
        """S3Reader 在调用 boto3 前拒绝 SSRF"""
        details = {
            "service_address": "https://169.254.169.254",  # 元数据服务
            "access_key": "AKIA...",
            "secret_key": "...",
            "bucket": "bucket",
        }
        s3_reader = S3Reader("/local/cache/", **details)

        # 应该在 boto3.client() 之前拒绝，所以不需要 mock boto3
        with self.assertRaises(ForbiddenExternalPluginSourceError):
            s3_reader.read()

    @patch(OS_PATH_EXISTS, MagicMock(return_value=False))
    @patch(OS_MAKEDIRS, MagicMock(return_value=True))
    @patch(SHUTIL_RMTREE, MagicMock(return_value=True))
    @override_settings(S3_ALLOWED_DOMAINS=['s3.amazonaws.com'])
    def test_s3reader_accepts_valid_endpoint(self):
        """S3Reader 接受合法的 S3 端点"""
        details = {
            "service_address": "https://s3.amazonaws.com",
            "access_key": "AKIA...",
            "secret_key": "...",
            "bucket": "bucket",
        }
        s3_reader = S3Reader("/local/cache/", **details)

        mock_s3 = MockBoto3()
        with patch(GCLOUD_EXTERNAL_PLUGINS_PROTOCOL_READERS_BOTO3, mock_s3):
            # 验证通过校验后继续执行
            s3_reader.read()
            # 验证 boto3 确实被调用了（检查 files 列表不为空）
            self.assertIsNotNone(mock_s3.files)
