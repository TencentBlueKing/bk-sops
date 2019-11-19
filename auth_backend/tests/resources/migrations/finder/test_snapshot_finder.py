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

import os

from django.test import TestCase
from django.conf import settings

from auth_backend.resources.migrations.finder import ResourceSnapshotFinder


class TestUseFinder(ResourceSnapshotFinder):
    pass


class ResourceSnapshotFinderTestCase(TestCase):
    def setUp(self):
        self.snapshot_name = 'TOKEN'
        self.finder = TestUseFinder(self.snapshot_name)

    def test_snapshot_dir(self):
        self.assertEqual(self.finder.snapshot_dir, 'auth_backend/resource_snapshots')

    def test_basedir(self):
        self.assertEqual(self.finder.basedir, os.path.join(settings.BASE_DIR, self.finder.snapshot_dir))

    def test_filename(self):
        self.assertEqual(self.finder.filename, "%s.json" % self.finder.snapshot_name)

    def test_path(self):
        self.assertEqual(self.finder.path, os.path.join(self.finder.basedir, self.finder.filename))
