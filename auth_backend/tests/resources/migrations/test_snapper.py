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

from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from mock import MagicMock, patch

from auth_backend.resources.migrations.snapper import ResourceStateSnapper
from auth_backend.tests.mock_path import *  # noqa


class ResourceStateSnapperTestCase(TestCase):
    def test_take_snapshot(self):
        resource_type_a = MagicMock()
        resource_type_a.snapshot = MagicMock(return_value='a_snapshot')
        resource_type_a.scope_type = 'system'

        resource_type_b = MagicMock()
        resource_type_b.snapshot = MagicMock(return_value='b_snapshot')
        resource_type_b.scope_type = 'system'

        resource_type_c = MagicMock()
        resource_type_c.snapshot = MagicMock(return_value='c_snapshot')
        resource_type_c.scope_type = 'business'

        resource_type_lib = {
            'a': resource_type_a,
            'b': resource_type_b,
            'c': resource_type_c
        }

        with patch(SNAPPER_RESOURCE_TYPE_LIB, resource_type_lib):
            expect = {}
            for resource in list(resource_type_lib.values()):
                resource_snapshot = resource.snapshot()
                expect.setdefault(resource.scope_type, []).append(resource_snapshot)

            snapper = ResourceStateSnapper()
            snapshot = snapper.take_snapshot()
            self.assertEqual(expect, snapshot)
