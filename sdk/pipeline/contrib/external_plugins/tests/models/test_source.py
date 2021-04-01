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

from pipeline.contrib.external_plugins.models import FileSystemSource, GitRepoSource, S3Source
from pipeline.contrib.external_plugins.models.base import FILE_SYSTEM, GIT, S3, ExternalPackageSource


class SourceTestCase(TestCase):
    def test_source_cls(self):
        self.assertTrue(issubclass(GitRepoSource, ExternalPackageSource))
        self.assertTrue(issubclass(S3Source, ExternalPackageSource))
        self.assertTrue(issubclass(FileSystemSource, ExternalPackageSource))

    def test_source_type(self):
        self.assertEqual(GitRepoSource.type(), GIT)
        self.assertEqual(S3Source.type(), S3)
        self.assertEqual(FileSystemSource.type(), FILE_SYSTEM)
