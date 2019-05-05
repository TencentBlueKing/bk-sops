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

from django.test import TestCase

from pipeline.contrib.external_plugins.models import (
    GIT,
    FILE_SYSTEM,
    GitRepoSource,
    FileSystemSource
)

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.external_plugins import exceptions
from gcloud.external_plugins.models.main_source import MainPackageSource

MAIN_SOURCE_NAME = 'MAIN_SOURCE_NAME'
SOURCE_TYPE = GIT
UPDATED_SOURCE_TYPE = FILE_SYSTEM
SOURCE_PACKAGES = {
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
UPDATED_SOURCE_PACKAGES = {
    'root_package_1': {
        'version': '',
        'modules': ['test1', 'test2']
    },
}
SOURCE_KWARGS = {
    'repo_raw_address': 'address',
    'branch': 'master'
}
UPDATED_SOURCE_KWARGS = {
    'repo_raw_address': 'new_address',
    'branch': 'dev'
}
FILE_SYSTEM_KWARGS = {
    'path': '/path/to/module'
}


class MainPackageSourceTestCase(TestCase):
    def setUp(self):
        main_source = MainPackageSource.objects.add_main_source(name=MAIN_SOURCE_NAME,
                                                                source_type=SOURCE_TYPE,
                                                                packages=SOURCE_PACKAGES,
                                                                **SOURCE_KWARGS)
        self.main_source = main_source

    def tearDown(self):
        self.main_source = None
        GitRepoSource.objects.all().delete()
        MainPackageSource.objects.all().delete()

    def test_objects_add_main_source__success(self):
        MainPackageSource.objects.all().delete()
        GitRepoSource.objects.all().delete()

        main_source = MainPackageSource.objects.add_main_source(name=MAIN_SOURCE_NAME,
                                                                source_type=SOURCE_TYPE,
                                                                packages=SOURCE_PACKAGES,
                                                                **SOURCE_KWARGS)
        base_source = GitRepoSource.objects.get(name=MAIN_SOURCE_NAME)

        self.assertEqual(base_source.name, MAIN_SOURCE_NAME)
        self.assertEqual(base_source.packages, SOURCE_PACKAGES)
        self.assertEqual(base_source.repo_raw_address, SOURCE_KWARGS['repo_raw_address'])
        self.assertEqual(base_source.branch, SOURCE_KWARGS['branch'])
        self.assertEqual(main_source.type, SOURCE_TYPE)
        self.assertEqual(main_source.base_source_id, base_source.id)

    def test_objects_add_main_source__raise_multiple_error(self):
        self.assertRaises(exceptions.MultipleMainSourceError,
                          MainPackageSource.objects.add_main_source,
                          name=MAIN_SOURCE_NAME,
                          source_type=SOURCE_TYPE,
                          packages=SOURCE_PACKAGES,
                          **SOURCE_KWARGS)

    def test_objects_update_main_source(self):
        setattr(self.main_source, 'update_base_source', MagicMock())
        with patch(MAIN_PACKAGE_SOURCE_GET, MagicMock(return_value=self.main_source)):
            MainPackageSource.objects.update_main_source(source_id=self.main_source.id,
                                                         source_type=SOURCE_TYPE,
                                                         packages=SOURCE_PACKAGES,
                                                         **SOURCE_KWARGS)

            self.main_source.update_base_source.assert_called_once_with(source_type=SOURCE_TYPE,
                                                                        packages=SOURCE_PACKAGES,
                                                                        **SOURCE_KWARGS)

    def test_objects_delete_main_source(self):
        setattr(self.main_source, 'delete', MagicMock())
        with patch(MAIN_PACKAGE_SOURCE_GET, MagicMock(return_value=self.main_source)):
            MainPackageSource.objects.delete_main_source(source_id=self.main_source.id)

            self.main_source.delete.assert_called_once()

    def test_base_source(self):
        self.assertIsNone(getattr(self.main_source, MainPackageSource._base_source_attr, None))
        expect_base_source = GitRepoSource.objects.get(name=MAIN_SOURCE_NAME)
        actual_base_source = self.main_source.base_source
        self.assertEqual(type(actual_base_source), type(expect_base_source))
        self.assertEqual(actual_base_source.id, expect_base_source.id)

        self.assertIsNotNone(getattr(self.main_source, MainPackageSource._base_source_attr, None))
        expect_base_source.delete()
        self.assertEqual(actual_base_source.id, self.main_source.base_source.id)

    def test_name(self):
        base_source = GitRepoSource.objects.get(name=MAIN_SOURCE_NAME)

        self.assertEqual(self.main_source.name, base_source.name)

    def test_packages(self):
        base_source = GitRepoSource.objects.get(name=MAIN_SOURCE_NAME)

        self.assertEqual(self.main_source.packages, base_source.packages)

    def test_details(self):
        base_source = GitRepoSource.objects.get(name=MAIN_SOURCE_NAME)

        self.assertEqual(self.main_source.details, base_source.details())

    def test_delete(self):
        setattr(self.main_source, 'delete_base_source', MagicMock())

        self.main_source.delete()
        self.main_source.delete_base_source.assert_called_once()

    def test_delete_base_source__with_cache(self):
        self.main_source.base_source  # noqa

        self.main_source.delete_base_source()
        self.assertIsNone(getattr(self.main_source, MainPackageSource._base_source_attr, None))
        self.assertRaises(GitRepoSource.DoesNotExist, GitRepoSource.objects.get, name=MAIN_SOURCE_NAME)

    def test_delete_base_source__no_cache(self):
        self.main_source.delete_base_source()
        self.assertRaises(GitRepoSource.DoesNotExist, GitRepoSource.objects.get, name=MAIN_SOURCE_NAME)

    def test_update_base_source__same_type(self):
        self.main_source.base_source  # noqa
        self.main_source.update_base_source(source_type=SOURCE_TYPE,
                                            packages=UPDATED_SOURCE_PACKAGES,
                                            **UPDATED_SOURCE_KWARGS)

        self.main_source.base_source.packages = UPDATED_SOURCE_PACKAGES
        self.main_source.base_source.repo_raw_address = UPDATED_SOURCE_KWARGS['repo_raw_address']
        self.main_source.base_source.branch = UPDATED_SOURCE_KWARGS['branch']

    def test_update_base_source__different_type(self):
        self.main_source.update_base_source(source_type=UPDATED_SOURCE_TYPE,
                                            packages=UPDATED_SOURCE_PACKAGES,
                                            **FILE_SYSTEM_KWARGS)

        self.assertIsInstance(self.main_source.base_source, FileSystemSource)
        self.main_source.base_source.packages = UPDATED_SOURCE_PACKAGES
        self.main_source.base_source.path = FILE_SYSTEM_KWARGS['path']
