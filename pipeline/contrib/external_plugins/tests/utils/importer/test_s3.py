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

import boto3
from django.test import TestCase

from pipeline.contrib.external_plugins.tests.mock import *  # noqa
from pipeline.contrib.external_plugins.tests.mock_settings import *  # noqa
from pipeline.contrib.external_plugins.utils.importer.s3 import S3ModuleImporter


class S3ModuleImporterTestCase(TestCase):

    def setUp(self):
        self.service_address = 'https://test-s3-address/'
        self.service_address_without_slash = 'https://test-s3-address'
        self.not_secure_service_address = 'http://no-secure-address/'
        self.bucket = 'bucket'
        self.access_key = 'access_key'
        self.secret_key = 'secret_key'

    @patch(BOTO3_RESOURCE, mock_s3_resource)
    def test__init__(self):
        importer = S3ModuleImporter(modules=[],
                                    service_address=self.service_address,
                                    bucket=self.bucket,
                                    access_key=self.access_key,
                                    secret_key=self.secret_key)
        self.assertEqual(self.service_address, importer.service_address)
        self.assertEqual(importer.s3, mock_s3_resource('s3',
                                                       aws_access_key_id=self.access_key,
                                                       aws_secret_access_key=self.secret_key,
                                                       endpoint_url=self.service_address))

        importer = S3ModuleImporter(modules=[],
                                    service_address=self.service_address_without_slash,
                                    bucket=self.bucket,
                                    access_key=self.access_key,
                                    secret_key=self.secret_key)
        self.assertEqual(self.service_address, importer.service_address)
        self.assertEqual(importer.s3, mock_s3_resource('s3',
                                                       aws_access_key_id=self.access_key,
                                                       aws_secret_access_key=self.secret_key,
                                                       endpoint_url=self.service_address))

        self.assertRaises(ValueError,
                          S3ModuleImporter,
                          modules=[],
                          service_address=self.not_secure_service_address,
                          bucket=self.bucket,
                          access_key=self.access_key,
                          secret_key=self.secret_key)

        importer = S3ModuleImporter(modules=[],
                                    service_address=self.not_secure_service_address,
                                    bucket=self.bucket,
                                    access_key=self.access_key,
                                    secret_key=self.secret_key)
        self.assertEqual(self.not_secure_service_address, importer.service_address)
        self.assertEqual(importer.s3, mock_s3_resource('s3',
                                                       aws_access_key_id=self.access_key,
                                                       aws_secret_access_key=self.secret_key,
                                                       endpoint_url=self.service_address))

    def test_is_package(self):
        pass

    def test_get_code(self):
        pass

    def test_get_source(self):
        pass

    def test_get_path(self):
        pass

    def test_get_file(self):
        pass

    def test__obj_key(self):
        pass

    def test__fetch_obj_content(self):
        pass
