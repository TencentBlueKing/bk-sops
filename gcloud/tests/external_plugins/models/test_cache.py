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

from django.test import TestCase

from pipeline.contrib.external_plugins.models import (
    GIT,
    S3,
    FILE_SYSTEM,
    S3Source,
    FileSystemSource
)

from gcloud.tests.external_plugins.mock import *  # noqa
from gcloud.tests.external_plugins.mock_settings import *  # noqa
from gcloud.external_plugins import exceptions
from gcloud.external_plugins.models.cache import CachePackageSource


class TestCachePackageSource(TestCase):
    def setUp(self):
        self.CACHE_SOURCE_NAME = 'CACHE_S3_SOURCE'
        self.UPDATE_CACHE_SOURCE_NAME = 'CACHE_FILE_SYSTEM_SOURCE'
        self.SOURCE_TYPE = S3
        self.UPDATE_SOURCE_TYPE = FILE_SYSTEM
        self.SOURCE_PACKAGES = {
            'root_package_1': {
                'version': '',
                'modules': ['test1', 'test2']
            },
            'root_package_2': {
                'version': '',
                'modules': ['test3', 'test4']
            },
            'root_package_3': {
                'version': '',
                'modules': ['test5', 'test6']
            }
        }
        self.UPDATED_SOURCE_PACKAGES = {
            'root_package_1': {
                'version': '',
                'modules': ['test1', 'test2']
            },
        }
        self.SOURCE_KWARGS = {
            'service_address': 'service_address',
            'bucket': 'bucket',
            'access_key': 'access_key',
            'secret_key': 'secret_key',
        }
        self.UPDATED_SOURCE_KWARGS = {
            'path': '/tmp'
        }
        self.cache_source = CachePackageSource.objects.add_cache_source(
            name=self.CACHE_SOURCE_NAME,
            source_type=self.SOURCE_TYPE,
            packages=self.SOURCE_PACKAGES,
            **self.SOURCE_KWARGS
        )

    def tearDown(self):
        caches = CachePackageSource.objects.all()
        for cache in caches:
            cache.delete()

    def test_base_source(self):
        base_source = S3Source.objects.get(id=self.cache_source.base_source_id)
        self.assertEquals(self.cache_source.base_source, base_source)
        self.assertEquals(base_source.packages, self.SOURCE_PACKAGES)

    def test_get_base_source(self):
        self.assertEquals(CachePackageSource.objects.get_base_source(), self.cache_source.base_source)

    def test_add_cache_source__exception(self):
        self.assertRaises(exceptions.CacheSourceTypeError,
                          CachePackageSource.objects.add_cache_source,
                          name=self.CACHE_SOURCE_NAME,
                          source_type=GIT,
                          packages=self.SOURCE_PACKAGES,
                          **self.SOURCE_KWARGS
                          )
        self.assertRaises(exceptions.MultipleCacheSourceError,
                          CachePackageSource.objects.add_cache_source,
                          name=self.CACHE_SOURCE_NAME,
                          source_type=self.SOURCE_TYPE,
                          packages=self.SOURCE_PACKAGES,
                          **self.SOURCE_KWARGS
                          )

    def test_name(self):
        self.assertEquals(self.cache_source.name, self.CACHE_SOURCE_NAME)

    def test_packages(self):
        self.assertEquals(self.cache_source.packages, self.SOURCE_PACKAGES)

    def test_details(self):
        self.assertEquals(self.cache_source.details, self.SOURCE_KWARGS)

    def test_write__type_error(self):
        self.cache_source.type = 'error_type'
        self.assertRaises(exceptions.CacheSourceTypeError, self.cache_source.write)

    @patch(GCLOUD_EXTERNAL_PLUGINS_MODELS_CACHE_WRITER_CLS_FACTORY, MockClsFactory())
    def test_write(self):
        self.assertIsNone(self.cache_source.write())

    def test_update_base_source(self):
        CachePackageSource.objects.update_base_source(
            package_source_id=self.cache_source.id,
            source_type=self.UPDATE_SOURCE_TYPE,
            packages=self.UPDATED_SOURCE_PACKAGES,
            **self.UPDATED_SOURCE_KWARGS
        )
        self.cache_source = CachePackageSource.objects.get(id=self.cache_source.id)
        self.assertEquals(self.cache_source.base_source.packages, self.UPDATED_SOURCE_PACKAGES)
        base_source = FileSystemSource.objects.get(id=self.cache_source.base_source_id)
        self.assertEquals(self.cache_source.base_source, base_source)

    def test_get_base_source__none(self):
        CachePackageSource.objects.get(id=self.cache_source.id).delete()
        self.assertEquals(CachePackageSource.objects.get_base_source(), None)
