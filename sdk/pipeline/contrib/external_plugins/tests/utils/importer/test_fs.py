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
from pipeline.contrib.external_plugins.utils.importer.fs import FSModuleImporter

GET_FILE_RETURN = "GET_FILE_RETURN"
GET_SOURCE_RETURN = "a=1"
IS_PACKAGE_RETURN = True
_FETCH_FILE_RETURN = "_FETCH_FILE_RETURN"


class FSModuleImporterTestCase(TestCase):
    def setUp(self):
        self.path = "/usr/imp/custom_components/"
        self.path_without_salsh = "/usr/imp/custom_components"
        self.fullname = "module1.module2.module3"
        self.module_url = "/usr/imp/custom_components/module1/module2/module3.py"
        self.package_url = "/usr/imp/custom_components/module1/module2/module3/__init__.py"

    def test__init__(self):
        importer = FSModuleImporter(name="name", modules=[], path=self.path)
        self.assertEqual(self.path, importer.path)

        importer = FSModuleImporter(name="name", modules=[], path=self.path_without_salsh)
        self.assertEqual(self.path, importer.path)

    def test_is_package(self):
        importer = FSModuleImporter(name="name", modules=[], path=self.path)

        with patch(OS_PATH_EXISTS, MagicMock(return_value=True)):
            self.assertTrue(importer.is_package(self.fullname))

        with patch(OS_PATH_EXISTS, MagicMock(return_value=False)):
            self.assertFalse(importer.is_package(self.fullname))

    @patch(UTILS_IMPORTER_FS_GET_FILE, MagicMock(return_value=GET_FILE_RETURN))
    @patch(UTILS_IMPORTER_FS_GET_SOURCE, MagicMock(return_value=GET_SOURCE_RETURN))
    def test_get_code(self):
        expect_code = compile(GET_SOURCE_RETURN, GET_FILE_RETURN, "exec")
        importer = FSModuleImporter(name="name", modules=[], path=self.path)

        self.assertEqual(expect_code, importer.get_code(self.fullname))

    @patch(UTILS_IMPORTER_FS_IS_PACKAGE, MagicMock(return_value=IS_PACKAGE_RETURN))
    @patch(UTILS_IMPORTER_FS__FETCH_FILE_CONTENT, MagicMock(return_value=_FETCH_FILE_RETURN))
    def test_get_source(self):
        importer = FSModuleImporter(name="name", modules=[], path=self.path)

        self.assertEqual(_FETCH_FILE_RETURN, importer.get_source(self.fullname))
        importer._fetch_file_content.assert_called_once_with(
            importer._file_path(self.fullname, is_pkg=IS_PACKAGE_RETURN)
        )

    @patch(UTILS_IMPORTER_FS_IS_PACKAGE, MagicMock(return_value=IS_PACKAGE_RETURN))
    @patch(UTILS_IMPORTER_FS__FETCH_FILE_CONTENT, MagicMock(return_value=None))
    def test_get_source__fetch_none(self):
        importer = FSModuleImporter(name="name", modules=[], path=self.path)

        self.assertRaises(ImportError, importer.get_source, self.fullname)
        importer._fetch_file_content.assert_called_once_with(
            importer._file_path(self.fullname, is_pkg=IS_PACKAGE_RETURN)
        )

    def test_get_path(self):
        importer = FSModuleImporter(name="name", modules=[], path=self.path)

        self.assertEqual(importer.get_path(self.fullname), ["/usr/imp/custom_components/module1/module2/module3"])

    def test_get_file(self):
        importer = FSModuleImporter(name="name", modules=[], path=self.path)

        with patch(UTILS_IMPORTER_FS_IS_PACKAGE, MagicMock(return_value=True)):
            self.assertEqual(importer.get_file(self.fullname), self.package_url)

        with patch(UTILS_IMPORTER_FS_IS_PACKAGE, MagicMock(return_value=False)):
            self.assertEqual(importer.get_file(self.fullname), self.module_url)

    def test__file_path(self):
        importer = FSModuleImporter(name="name", modules=[], path=self.path)

        self.assertEqual(importer._file_path(self.fullname, is_pkg=True), self.package_url)
        self.assertEqual(importer._file_path(self.fullname, is_pkg=False), self.module_url)

    def test__fetch_file__nocache(self):
        importer = FSModuleImporter(name="name", modules=[], path=self.path, use_cache=False)

        first_file_content = "first_file_content"
        second_file_content = "second_file_content"

        with patch(UTILS_IMPORTER_FS__GET_FILE_CONTENT, MagicMock(return_value=first_file_content)):
            self.assertEqual(importer._fetch_file_content(self.module_url), first_file_content)
            self.assertEqual(importer.file_cache, {})

        with patch(UTILS_IMPORTER_FS__GET_FILE_CONTENT, MagicMock(return_value=second_file_content)):
            self.assertEqual(importer._fetch_file_content(self.module_url), second_file_content)
            self.assertEqual(importer.file_cache, {})

        with patch(UTILS_IMPORTER_FS__GET_FILE_CONTENT, MagicMock(return_value=None)):
            self.assertIsNone(importer._fetch_file_content(self.module_url))
            self.assertEqual(importer.file_cache, {})

    def test__fetch_file__use_cache(self):
        importer = FSModuleImporter(name="name", modules=[], path=self.path)

        first_file_content = "first_file_content"
        second_file_content = "second_file_content"

        with patch(UTILS_IMPORTER_FS__GET_FILE_CONTENT, MagicMock(return_value=first_file_content)):
            self.assertEqual(importer._fetch_file_content(self.module_url), first_file_content)
            self.assertEqual(importer.file_cache[self.module_url], first_file_content)

        with patch(UTILS_IMPORTER_FS__GET_FILE_CONTENT, MagicMock(return_value=second_file_content)):
            self.assertEqual(importer._fetch_file_content(self.module_url), first_file_content)
            self.assertEqual(importer.file_cache[self.module_url], first_file_content)

        with patch(UTILS_IMPORTER_FS__GET_FILE_CONTENT, MagicMock(return_value=None)):
            self.assertIsNone(importer._fetch_file_content(self.package_url))
            self.assertEqual(importer.file_cache[self.package_url], None)

        with patch(UTILS_IMPORTER_FS__GET_FILE_CONTENT, MagicMock(return_value=second_file_content)):
            self.assertIsNone(importer._fetch_file_content(self.package_url))
            self.assertEqual(importer.file_cache[self.package_url], None)
