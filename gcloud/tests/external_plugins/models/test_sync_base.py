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

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from gcloud.external_plugins.models import RootPackage, GitRepoSyncSource


class RootPackageTestCase(TestCase):

    def tearDown(self):
        RootPackage.objects.all().delete()

    def test_objects_create_packages_for_source(self):
        source_type = 'git'
        root_packages = {'1', '2', '3', '4', '5'}
        source = MockSyncPackageSource(id=1, type=source_type)
        RootPackage.objects.create_packages_for_source(source=source, root_packages=root_packages)
        packages = RootPackage.objects.all()
        self.assertEqual(packages.count(), len(root_packages))
        self.assertEqual({pkg.name for pkg in packages}, root_packages)
        self.assertEqual({pkg.source_type for pkg in packages}, {source_type})
        self.assertEqual({pkg.source_id for pkg in packages}, {source.id})

    def test_objects_delete_packages_in_source(self):
        pkg1 = RootPackage.objects.create(name='1', source_type='git', source_id=1)
        pkg2 = RootPackage.objects.create(name='2', source_type='git', source_id=2)
        pkg3 = RootPackage.objects.create(name='3', source_type='s3', source_id=1)
        pkg4 = RootPackage.objects.create(name='4', source_type='fs', source_id=1)

        source = MockSyncPackageSource(id=1, type='git')
        RootPackage.objects.delete_packages_in_source(source)
        self.assertRaises(RootPackage.DoesNotExist, RootPackage.objects.get, id=pkg1.id)

        expect_packages = [pkg2, pkg3, pkg4]
        packages = RootPackage.objects.all()
        self.assertEqual(len(expect_packages), len(packages))
        for expect, actual in zip(expect_packages, packages):
            self.assertEqual(expect.id, actual.id)
            self.assertEqual(expect.name, actual.name)
            self.assertEqual(expect.source_type, actual.source_type)
            self.assertEqual(expect.source_id, actual.source_id)

    def test_objects_packages_for_source(self):
        pkg1 = RootPackage.objects.create(name='1', source_type='git', source_id=1)
        pkg2 = RootPackage.objects.create(name='2', source_type='git', source_id=1)
        RootPackage.objects.create(name='2', source_type='git', source_id=2)
        RootPackage.objects.create(name='3', source_type='s3', source_id=1)
        RootPackage.objects.create(name='4', source_type='fs', source_id=1)

        source = MockSyncPackageSource(id=1, type='git')
        expect_packages = [pkg1, pkg2]
        packages = RootPackage.objects.packages_for_source(source)
        self.assertEqual(len(expect_packages), len(packages))
        for expect, actual in zip(expect_packages, packages):
            self.assertEqual(expect.id, actual.id)
            self.assertEqual(expect.name, actual.name)
            self.assertEqual(expect.source_type, actual.source_type)
            self.assertEqual(expect.source_id, actual.source_id)


class SyncPackageSourceTestCase(TestCase):
    SOURCE_NAME = 'test source'
    ROOT_PACKAGES = ['1', '2', '3']
    CREATE_KWARGS = {
        'repo_address': 'address',
        'branch': 'master'
    }

    def tearDown(self):
        GitRepoSyncSource.objects.all().delete()

    @patch(ROOT_PACKAGES_CREATE_PACKAGES_FOR_SOURCE, MagicMock())
    def test_objects_create_source(self):
        source = GitRepoSyncSource.objects.create_source(name=self.SOURCE_NAME,
                                                         root_packages=self.ROOT_PACKAGES,
                                                         **self.CREATE_KWARGS)

        RootPackage.objects.create_packages_for_source.assert_called_once_with(source=source,
                                                                               root_packages=self.ROOT_PACKAGES)
        self.assertEqual(source.name, self.SOURCE_NAME)
        self.assertEqual(source.repo_address, self.CREATE_KWARGS['repo_address'])
        self.assertEqual(source.branch, self.CREATE_KWARGS['branch'])

    @patch(ROOT_PACKAGES_CREATE_PACKAGES_FOR_SOURCE, MagicMock())
    @patch(ROOT_PACKAGES_DELETE_PACKAGES_IN_SOURCE, MagicMock())
    def test_objects_delete_source(self):
        source = GitRepoSyncSource.objects.create_source(name=self.SOURCE_NAME,
                                                         root_packages=self.ROOT_PACKAGES,
                                                         **self.CREATE_KWARGS)
        with patch(GIT_REPO_SOURCE_GET, MagicMock(return_value=source)):
            GitRepoSyncSource.objects.delete_source(source_id=source.id)

            RootPackage.objects.delete_packages_in_source.assert_called_once_with(source)

        self.assertRaises(GitRepoSyncSource.DoesNotExist, GitRepoSyncSource.objects.get, id=source.id)

    @patch(ROOT_PACKAGES_PACKAGES_FOR_SOURCE, MagicMock(return_value=ROOT_PACKAGES))
    def test_root_packages(self):
        source = GitRepoSyncSource.objects.create_source(name=self.SOURCE_NAME,
                                                         root_packages=self.ROOT_PACKAGES,
                                                         **self.CREATE_KWARGS)

        self.assertEqual(source.root_packages, self.ROOT_PACKAGES)
        RootPackage.objects.packages_for_source.assert_called_once_with(source)
