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
from pipeline.contrib.external_plugins.utils.importer.s3 import CONFIG, S3ModuleImporter

GET_FILE_RETURN = "GET_FILE_RETURN"
GET_SOURCE_RETURN = "a=1"
IS_PACKAGE_RETURN = True
_FETCH_OBJ_CONTENT_RETURN = "_FETCH_OBJ_CONTENT_RETURN"


class S3ModuleImporterTestCase(TestCase):
    def setUp(self):
        self.service_address = "https://test-s3-address/"
        self.service_address_without_slash = "https://test-s3-address"
        self.not_secure_service_address = "http://no-secure-address/"
        self.bucket = "bucket"
        self.access_key = "access_key"
        self.secret_key = "secret_key"
        self.fullname = "module1.module2.module3"
        self.module_url = "https://test-s3-address/bucket/module1/module2/module3.py"
        self.package_url = "https://test-s3-address/bucket/module1/module2/module3/__init__.py"
        self.module_key = "module1/module2/module3.py"
        self.package_key = "module1/module2/module3/__init__.py"

    @patch(BOTO3_RESOURCE, mock_s3_resource)
    def test__init__(self):
        importer = S3ModuleImporter(
            name="name",
            modules=[],
            service_address=self.service_address,
            bucket=self.bucket,
            access_key=self.access_key,
            secret_key=self.secret_key,
        )
        self.assertEqual(self.service_address, importer.service_address)
        self.assertEqual(
            importer.s3,
            mock_s3_resource(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                endpoint_url=self.service_address,
                config=CONFIG,
            ),
        )

        importer = S3ModuleImporter(
            name="name",
            modules=[],
            service_address=self.service_address_without_slash,
            bucket=self.bucket,
            access_key=self.access_key,
            secret_key=self.secret_key,
        )
        self.assertEqual(self.service_address, importer.service_address)
        self.assertEqual(
            importer.s3,
            mock_s3_resource(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                endpoint_url=self.service_address,
                config=CONFIG,
            ),
        )

        self.assertRaises(
            ValueError,
            S3ModuleImporter,
            name="name",
            modules=[],
            service_address=self.not_secure_service_address,
            bucket=self.bucket,
            access_key=self.access_key,
            secret_key=self.secret_key,
        )

        importer = S3ModuleImporter(
            name="name",
            modules=[],
            service_address=self.not_secure_service_address,
            bucket=self.bucket,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure_only=False,
        )
        self.assertEqual(self.not_secure_service_address, importer.service_address)
        self.assertEqual(
            importer.s3,
            mock_s3_resource(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                endpoint_url=self.not_secure_service_address,
                config=CONFIG,
            ),
        )

    def test_is_package(self):
        importer = S3ModuleImporter(
            name="name",
            modules=[],
            service_address=self.service_address,
            bucket=self.bucket,
            access_key=self.access_key,
            secret_key=self.secret_key,
        )

        with patch(UTILS_IMPORTER_S3__FETCH_OBJ_CONTENT, MagicMock(return_value="")):
            self.assertTrue(importer.is_package("a.b.c"))

        with patch(UTILS_IMPORTER_S3__FETCH_OBJ_CONTENT, MagicMock(return_value=None)):
            self.assertFalse(importer.is_package("a.b.c"))

    @patch(UTILS_IMPORTER_S3_GET_FILE, MagicMock(return_value=GET_FILE_RETURN))
    @patch(UTILS_IMPORTER_S3_GET_SOURCE, MagicMock(return_value=GET_SOURCE_RETURN))
    def test_get_code(self):
        expect_code = compile(GET_SOURCE_RETURN, GET_FILE_RETURN, "exec")
        importer = S3ModuleImporter(
            name="name",
            modules=[],
            service_address=self.service_address,
            bucket=self.bucket,
            access_key=self.access_key,
            secret_key=self.secret_key,
        )

        self.assertEqual(expect_code, importer.get_code(self.fullname))

    @patch(UTILS_IMPORTER_S3_IS_PACKAGE, MagicMock(return_value=IS_PACKAGE_RETURN))
    @patch(UTILS_IMPORTER_S3__FETCH_OBJ_CONTENT, MagicMock(return_value=_FETCH_OBJ_CONTENT_RETURN))
    def test_get_source(self):
        importer = S3ModuleImporter(
            name="name",
            modules=[],
            service_address=self.service_address,
            bucket=self.bucket,
            access_key=self.access_key,
            secret_key=self.secret_key,
        )

        self.assertEqual(_FETCH_OBJ_CONTENT_RETURN, importer.get_source(self.fullname))
        importer._fetch_obj_content.assert_called_once_with(importer._obj_key(self.fullname, is_pkg=IS_PACKAGE_RETURN))

    @patch(UTILS_IMPORTER_S3_IS_PACKAGE, MagicMock(return_value=IS_PACKAGE_RETURN))
    @patch(UTILS_IMPORTER_S3__FETCH_OBJ_CONTENT, MagicMock(return_value=None))
    def test_get_source__fetch_none(self):
        importer = S3ModuleImporter(
            name="name",
            modules=[],
            service_address=self.service_address,
            bucket=self.bucket,
            access_key=self.access_key,
            secret_key=self.secret_key,
        )

        self.assertRaises(ImportError, importer.get_source, self.fullname)
        importer._fetch_obj_content.assert_called_once_with(importer._obj_key(self.fullname, is_pkg=IS_PACKAGE_RETURN))

    @patch(UTILS_IMPORTER_S3_IS_PACKAGE, MagicMock(return_value=IS_PACKAGE_RETURN))
    def test_get_path(self):
        importer = S3ModuleImporter(
            name="name",
            modules=[],
            service_address=self.service_address,
            bucket=self.bucket,
            access_key=self.access_key,
            secret_key=self.secret_key,
        )

        self.assertEqual(importer.get_path(self.fullname), ["https://test-s3-address/bucket/module1/module2/module3"])

    def test_get_file(self):
        importer = S3ModuleImporter(
            name="name",
            modules=[],
            service_address=self.service_address,
            bucket=self.bucket,
            access_key=self.access_key,
            secret_key=self.secret_key,
        )

        with patch(UTILS_IMPORTER_S3_IS_PACKAGE, MagicMock(return_value=False)):
            self.assertEqual(importer.get_file(self.fullname), self.module_url)

        with patch(UTILS_IMPORTER_S3_IS_PACKAGE, MagicMock(return_value=True)):
            self.assertEqual(importer.get_file(self.fullname), self.package_url)

    def test__obj_key(self):
        importer = S3ModuleImporter(
            name="name",
            modules=[],
            service_address=self.service_address,
            bucket=self.bucket,
            access_key=self.access_key,
            secret_key=self.secret_key,
        )

        self.assertEqual("module1/module2/module3/__init__.py", importer._obj_key(self.fullname, is_pkg=True))
        self.assertEqual("module1/module2/module3.py", importer._obj_key(self.fullname, is_pkg=False))

    def test__fetch_obj_content__no_cache(self):
        importer = S3ModuleImporter(
            name="name",
            modules=[],
            service_address=self.service_address,
            bucket=self.bucket,
            access_key=self.access_key,
            secret_key=self.secret_key,
            use_cache=False,
        )

        first_obj_content = "first_obj_content"
        second_obj_content = "second_obj_content"

        with patch(UTILS_IMPORTER_S3__GET_S3_OBJ_CONTENT, MagicMock(return_value=first_obj_content)):
            self.assertEqual(importer._fetch_obj_content(self.module_key), first_obj_content)
            self.assertEqual(importer.obj_cache, {})

        with patch(UTILS_IMPORTER_S3__GET_S3_OBJ_CONTENT, MagicMock(return_value=second_obj_content)):
            self.assertEqual(importer._fetch_obj_content(self.module_key), second_obj_content)
            self.assertEqual(importer.obj_cache, {})

        with patch(UTILS_IMPORTER_S3__GET_S3_OBJ_CONTENT, MagicMock(return_value=None)):
            self.assertIsNone(importer._fetch_obj_content(self.module_key))
            self.assertEqual(importer.obj_cache, {})

    def test__fetch_obj_content__use_cache(self):
        importer = S3ModuleImporter(
            name="name",
            modules=[],
            service_address=self.service_address,
            bucket=self.bucket,
            access_key=self.access_key,
            secret_key=self.secret_key,
        )

        first_obj_content = "first_obj_content"
        second_obj_content = "second_obj_content"

        with patch(UTILS_IMPORTER_S3__GET_S3_OBJ_CONTENT, MagicMock(return_value=first_obj_content)):
            self.assertEqual(importer._fetch_obj_content(self.module_key), first_obj_content)
            self.assertEqual(importer.obj_cache[self.module_key], first_obj_content)

        with patch(UTILS_IMPORTER_S3__GET_S3_OBJ_CONTENT, MagicMock(return_value=second_obj_content)):
            self.assertEqual(importer._fetch_obj_content(self.module_key), first_obj_content)
            self.assertEqual(importer.obj_cache[self.module_key], first_obj_content)

        with patch(UTILS_IMPORTER_S3__GET_S3_OBJ_CONTENT, MagicMock(return_value=None)):
            self.assertIsNone(importer._fetch_obj_content(self.package_key))
            self.assertIsNone(importer.obj_cache[self.package_key])

        with patch(UTILS_IMPORTER_S3__GET_S3_OBJ_CONTENT, MagicMock(return_value=first_obj_content)):
            self.assertIsNone(importer._fetch_obj_content(self.package_key))
            self.assertIsNone(importer.obj_cache[self.package_key])
