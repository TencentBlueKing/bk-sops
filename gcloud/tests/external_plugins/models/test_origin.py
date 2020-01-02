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
    GitRepoSource,
    S3Source,
    FileSystemSource
)

from gcloud.tests.external_plugins.mock import *  # noqa
from gcloud.tests.external_plugins.mock_settings import *  # noqa
from gcloud.external_plugins import exceptions
from gcloud.external_plugins.models.origin import (
    GitRepoOriginalSource,
    S3OriginalSource,
    FileSystemOriginalSource
)


class TestGitRepoOriginalSource(TestCase):
    def setUp(self):
        self.ORIGINAL_SOURCE_NAME = 'ORIGINAL_GIT_SOURCE'
        self.SOURCE_TYPE = GIT
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
        self.ORIGINAL_KWARGS = {
            'repo_address': 'repo_address',
        }
        self.SOURCE_KWARGS = {
            'repo_raw_address': 'repo_raw_address',
            'branch': 'master'
        }
        self.UPDATED_ORIGINAL_KWARGS = {
            'repo_address': 'new_address',
        }
        self.UPDATED_SOURCE_KWARGS = {
            'repo_raw_address': 'new_address',
            'branch': 'dev'
        }
        self.original_source = GitRepoOriginalSource.objects.add_original_source(
            name=self.ORIGINAL_SOURCE_NAME,
            source_type=self.SOURCE_TYPE,
            packages=self.SOURCE_PACKAGES,
            original_kwargs=self.ORIGINAL_KWARGS,
            **self.SOURCE_KWARGS
        )

    def tearDown(self):
        GitRepoOriginalSource.objects.delete_base_source(self.original_source.id,
                                                         self.original_source.type)
        GitRepoOriginalSource.objects.filter(id=self.original_source.id).delete()

    def test_add_original_source__cls(self):
        self.assertIsInstance(self.original_source, GitRepoOriginalSource)

    def test_base_source(self):
        base_source = GitRepoSource.objects.get(id=self.original_source.base_source_id)
        self.assertEquals(self.original_source.base_source, base_source)
        self.assertEquals(base_source.packages, self.SOURCE_PACKAGES)

    def test_get_base_source_fields(self):
        self.assertEquals(set(GitRepoOriginalSource.objects.get_base_source_fields(self.SOURCE_TYPE)),
                          {'id', 'name', 'from_config', 'packages', 'repo_raw_address', 'branch'})

    def test_divide_details_parts(self):
        details = {}
        details.update(self.ORIGINAL_KWARGS)
        details.update(self.SOURCE_KWARGS)
        original_kwargs, base_kwargs = GitRepoOriginalSource.objects.divide_details_parts(self.SOURCE_TYPE, details)
        self.assertEquals(original_kwargs, self.ORIGINAL_KWARGS)
        self.assertEquals(base_kwargs, self.SOURCE_KWARGS)

    def test_details(self):
        details = {}
        details.update(self.ORIGINAL_KWARGS)
        details.update(self.SOURCE_KWARGS)
        self.assertEquals(self.original_source.details, details)

    def test_original_type(self):
        self.assertEquals(self.original_source.original_type(), self.SOURCE_TYPE)

    @patch(GCLOUD_EXTERNAL_PLUGINS_MODELS_ORIGIN_READER_CLS_FACTORY, MockClsFactory())
    def test_read(self):
        self.assertIsNone(self.original_source.read())

    def test_update_base_source(self):
        GitRepoOriginalSource.objects.update_original_source(
            package_source_id=self.original_source.id,
            packages=self.UPDATED_SOURCE_PACKAGES,
            original_kwargs=self.UPDATED_ORIGINAL_KWARGS,
            **self.UPDATED_SOURCE_KWARGS
        )
        self.original_source = GitRepoOriginalSource.objects.get(id=self.original_source.id)
        self.assertEquals(self.original_source.base_source.packages, self.UPDATED_SOURCE_PACKAGES)
        self.assertEquals(self.original_source.repo_address, self.UPDATED_ORIGINAL_KWARGS['repo_address'])


class TestS3OriginalSource(TestCase):
    def setUp(self):
        self.ORIGINAL_SOURCE_NAME = 'ORIGINAL_S3_SOURCE'
        self.SOURCE_TYPE = S3
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
            'service_address': 'new_service_address',
            'bucket': 'new_bucket',
            'access_key': 'new_access_key',
            'secret_key': 'new_secret_key',
        }
        self.original_source = S3OriginalSource.objects.add_original_source(
            name=self.ORIGINAL_SOURCE_NAME,
            source_type=self.SOURCE_TYPE,
            packages=self.SOURCE_PACKAGES,
            **self.SOURCE_KWARGS
        )

    def tearDown(self):
        S3OriginalSource.objects.delete_base_source(self.original_source.id,
                                                    self.original_source.type)
        S3OriginalSource.objects.filter(id=self.original_source.id).delete()

    def test_add_original_source__cls(self):
        self.assertIsInstance(self.original_source, S3OriginalSource)

    def test_base_source(self):
        base_source = S3Source.objects.get(id=self.original_source.base_source_id)
        self.assertEquals(self.original_source.base_source, base_source)
        self.assertEquals(base_source.packages, self.SOURCE_PACKAGES)

    def test_get_base_source_fields(self):
        self.assertEquals(set(GitRepoOriginalSource.objects.get_base_source_fields(self.SOURCE_TYPE)),
                          {'id', 'name', 'from_config', 'packages', 'service_address', 'bucket', 'access_key',
                           'secret_key'})

    def test_details(self):
        details = {}
        details.update(self.SOURCE_KWARGS)
        self.assertEquals(self.original_source.details, details)

    def test_original_type(self):
        self.assertEquals(self.original_source.original_type(), self.SOURCE_TYPE)

    @patch(GCLOUD_EXTERNAL_PLUGINS_MODELS_ORIGIN_READER_CLS_FACTORY, MockClsFactory())
    def test_read(self):
        self.assertIsNone(self.original_source.read())

    def test_update_base_source(self):
        S3OriginalSource.objects.update_original_source(
            package_source_id=self.original_source.id,
            packages=self.UPDATED_SOURCE_PACKAGES,
            **self.UPDATED_SOURCE_KWARGS
        )
        self.original_source = S3OriginalSource.objects.get(id=self.original_source.id)
        self.assertEquals(self.original_source.base_source.packages, self.UPDATED_SOURCE_PACKAGES)


class TestFileSystemOriginalSource(TestCase):
    def setUp(self):
        self.ORIGINAL_SOURCE_NAME = 'ORIGINAL_FS_SOURCE'
        self.SOURCE_TYPE = FILE_SYSTEM
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
            'path': '/tmp'
        }
        self.UPDATED_SOURCE_KWARGS = {
            'path': '/dev'
        }
        self.original_source = FileSystemOriginalSource.objects.add_original_source(
            name=self.ORIGINAL_SOURCE_NAME,
            source_type=self.SOURCE_TYPE,
            packages=self.SOURCE_PACKAGES,
            **self.SOURCE_KWARGS
        )

    def tearDown(self):
        FileSystemOriginalSource.objects.delete_base_source(self.original_source.id,
                                                            self.original_source.type)
        FileSystemOriginalSource.objects.filter(id=self.original_source.id).delete()

    def test_add_original_source__cls(self):
        self.assertIsInstance(self.original_source, FileSystemOriginalSource)

    def test_base_source(self):
        base_source = FileSystemSource.objects.get(id=self.original_source.base_source_id)
        self.assertEquals(self.original_source.base_source, base_source)
        self.assertEquals(base_source.packages, self.SOURCE_PACKAGES)

    def test_get_base_source_fields(self):
        self.assertEquals(set(GitRepoOriginalSource.objects.get_base_source_fields(self.SOURCE_TYPE)),
                          {'id', 'name', 'from_config', 'packages', 'path'})

    def test_details(self):
        details = {}
        details.update(self.SOURCE_KWARGS)
        self.assertEquals(self.original_source.details, details)

    def test_original_type(self):
        self.assertEquals(self.original_source.original_type(), self.SOURCE_TYPE)

    def test_read__exception(self):
        self.assertRaises(exceptions.OriginalSourceTypeError, self.original_source.read)

    def test_update_base_source(self):
        FileSystemOriginalSource.objects.update_original_source(
            package_source_id=self.original_source.id,
            packages=self.UPDATED_SOURCE_PACKAGES,
            **self.UPDATED_SOURCE_KWARGS
        )
        self.original_source = FileSystemOriginalSource.objects.get(id=self.original_source.id)
        self.assertEquals(self.original_source.base_source.packages, self.UPDATED_SOURCE_PACKAGES)
