# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase

from pipeline.contrib.external_plugins.tests.mock import *  # noqa
from pipeline.contrib.external_plugins.tests.mock_settings import *  # noqa
from pipeline.contrib.external_plugins.utils.importer.git import GitRepoModuleImporter

GET_FILE_RETURN = "GET_FILE_RETURN"
GET_SOURCE_RETURN = "a=1"
IS_PACKAGE_RETURN = False
_FILE_URL_RETURN = "_FILE_URL_RETURN"
_FETCH_REPO_FILE_RETURN = "_FETCH_REPO_FILE_RETURN"


class GitRepoModuleImporterTestCase(TestCase):
    def setUp(self):
        self.repo_raw_url = "https://test-git-repo-raw/"
        self.repo_raw_url_without_slash = "https://test-git-repo-raw"
        self.branch = "master"
        self.fullname = "module1.module2.module3"
        self.module_url = "https://test-git-repo-raw/master/module1/module2/module3.py"
        self.package_url = "https://test-git-repo-raw/master/module1/module2/module3/__init__.py"

    def test__init__(self):
        importer = GitRepoModuleImporter(name="name", modules=[], repo_raw_url=self.repo_raw_url, branch=self.branch)
        self.assertEqual(importer.repo_raw_url, self.repo_raw_url)
        self.assertEqual(importer.branch, self.branch)

        importer = GitRepoModuleImporter(
            name="name", modules=[], repo_raw_url=self.repo_raw_url_without_slash, branch=self.branch
        )
        self.assertEqual(importer.repo_raw_url, self.repo_raw_url)
        self.assertEqual(importer.branch, self.branch)

        self.assertRaises(
            ValueError,
            GitRepoModuleImporter,
            name="name",
            modules=[],
            repo_raw_url="http://repo-addr/",
            branch=self.branch,
        )

        GitRepoModuleImporter(
            name="name", modules=[], repo_raw_url="http://repo-addr/", branch=self.branch, secure_only=False
        )

    def test__file_url(self):
        importer = GitRepoModuleImporter(name="name", modules=[], repo_raw_url=self.repo_raw_url, branch=self.branch)
        self.assertEqual(importer._file_url(self.fullname, is_pkg=True), self.package_url)
        self.assertEqual(importer._file_url(self.fullname, is_pkg=False), self.module_url)

    def test__fetch_repo_file__no_cache(self):
        importer = GitRepoModuleImporter(
            name="name", modules=[], repo_raw_url=self.repo_raw_url, branch=self.branch, use_cache=False
        )
        first_resp = MockResponse(content="first_request_content")
        second_resp = MockResponse(content="second_request_content")

        with patch(REQUESTS_GET, MagicMock(return_value=first_resp)):
            self.assertEqual(importer._fetch_repo_file(self.module_url), first_resp.content)
            self.assertEqual(importer.file_cache, {})

        with patch(REQUESTS_GET, MagicMock(return_value=second_resp)):
            self.assertEqual(importer._fetch_repo_file(self.module_url), second_resp.content)
            self.assertEqual(importer.file_cache, {})

        with patch(REQUESTS_GET, MagicMock(return_value=MockResponse(ok=False))):
            self.assertIsNone(importer._fetch_repo_file(self.module_url))
            self.assertEqual(importer.file_cache, {})

    def test__fetch_repo_file__use_cache(self):
        importer = GitRepoModuleImporter(name="name", modules=[], repo_raw_url=self.repo_raw_url, branch=self.branch)
        first_resp = MockResponse(content="first_request_content")
        second_resp = MockResponse(content="second_request_content")

        with patch(REQUESTS_GET, MagicMock(return_value=first_resp)):
            self.assertEqual(importer._fetch_repo_file(self.module_url), first_resp.content)
            self.assertEqual(importer.file_cache[self.module_url], first_resp.content)

        with patch(REQUESTS_GET, MagicMock(return_value=second_resp)):
            self.assertEqual(importer._fetch_repo_file(self.module_url), first_resp.content)
            self.assertEqual(importer.file_cache[self.module_url], first_resp.content)

        with patch(REQUESTS_GET, MagicMock(return_value=MockResponse(ok=False))):
            self.assertIsNone(importer._fetch_repo_file(self.package_url))
            self.assertIsNone(importer.file_cache[self.package_url])

        with patch(REQUESTS_GET, MagicMock(return_value=second_resp)):
            self.assertIsNone(importer._fetch_repo_file(self.package_url))
            self.assertIsNone(importer.file_cache[self.package_url])

    def test_is_package(self):
        importer = GitRepoModuleImporter(name="name", modules=[], repo_raw_url=self.repo_raw_url, branch=self.branch)

        with patch(UTILS_IMPORTER_GIT__FETCH_REPO_FILE, MagicMock(return_value=None)):
            self.assertFalse(importer.is_package(self.fullname))
            importer._fetch_repo_file.assert_called_once_with(importer._file_url(self.fullname, is_pkg=True))

        with patch(UTILS_IMPORTER_GIT__FETCH_REPO_FILE, MagicMock(return_value="")):
            self.assertTrue(importer.is_package(self.fullname))
            importer._fetch_repo_file.assert_called_once_with(importer._file_url(self.fullname, is_pkg=True))

    @patch(UTILS_IMPORTER_GIT_GET_FILE, MagicMock(return_value=GET_FILE_RETURN))
    @patch(UTILS_IMPORTER_GIT_GET_SOURCE, MagicMock(return_value=GET_SOURCE_RETURN))
    def test_get_code(self):
        expect_code = compile(GET_SOURCE_RETURN, GET_FILE_RETURN, "exec")
        importer = GitRepoModuleImporter(name="name", modules=[], repo_raw_url=self.repo_raw_url, branch=self.branch)

        self.assertEqual(expect_code, importer.get_code(self.fullname))

    @patch(UTILS_IMPORTER_GIT_IS_PACKAGE, MagicMock(return_value=IS_PACKAGE_RETURN))
    @patch(UTILS_IMPORTER_GIT__FETCH_REPO_FILE, MagicMock(return_value=_FETCH_REPO_FILE_RETURN))
    def test_get_source(self):
        importer = GitRepoModuleImporter(name="name", modules=[], repo_raw_url=self.repo_raw_url, branch=self.branch)

        source = importer.get_source(self.fullname)

        self.assertEqual(source, _FETCH_REPO_FILE_RETURN)
        importer._fetch_repo_file.assert_called_once_with(importer._file_url(self.fullname, is_pkg=IS_PACKAGE_RETURN))

    @patch(UTILS_IMPORTER_GIT_IS_PACKAGE, MagicMock(return_value=IS_PACKAGE_RETURN))
    @patch(UTILS_IMPORTER_GIT__FETCH_REPO_FILE, MagicMock(return_value=None))
    def test_get_source__fetch_none(self):
        importer = GitRepoModuleImporter(name="name", modules=[], repo_raw_url=self.repo_raw_url, branch=self.branch)

        self.assertRaises(ImportError, importer.get_source, self.fullname)
        importer._fetch_repo_file.assert_called_once_with(importer._file_url(self.fullname, is_pkg=IS_PACKAGE_RETURN))

    def test_get_path(self):
        importer = GitRepoModuleImporter(name="name", modules=[], repo_raw_url=self.repo_raw_url, branch=self.branch)

        self.assertEqual(importer.get_path(self.fullname), ["https://test-git-repo-raw/master/module1/module2/module3"])

    def test_get_file(self):
        importer = GitRepoModuleImporter(name="name", modules=[], repo_raw_url=self.repo_raw_url, branch=self.branch)

        with patch(UTILS_IMPORTER_GIT_IS_PACKAGE, MagicMock(return_value=False)):
            self.assertEqual(importer.get_file(self.fullname), self.module_url)

        with patch(UTILS_IMPORTER_GIT_IS_PACKAGE, MagicMock(return_value=True)):
            self.assertEqual(importer.get_file(self.fullname), self.package_url)
