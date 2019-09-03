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

from mock import MagicMock

from django.test import TestCase

from auth_backend.backends import utils


class BackendUtilsTestCase(TestCase):

    def test_resource_id_for__no_parent(self):
        resource = MagicMock()
        resource.parent = None
        resource.rtype = 'child'
        resource.resource_id = MagicMock(return_value='child_id')

        instance = MagicMock()

        self.assertEqual(utils.resource_id_for(resource, instance),
                         [{'resource_type': 'child', 'resource_id': 'child_id'}])

    def test_resource_id_for__with_parent(self):
        parent_resource = MagicMock()
        parent_resource.parent = None
        parent_resource.rtype = 'parent'
        parent_resource.resource_id = MagicMock(return_value='parent_id')

        child_resource = MagicMock()
        child_resource.parent = parent_resource
        child_resource.rtype = 'child'
        child_resource.resource_id = MagicMock(return_value='child_id')

        instance = MagicMock()

        self.assertEqual(utils.resource_id_for(child_resource, instance),
                         [{'resource_type': 'parent', 'resource_id': 'parent_id'},
                          {'resource_type': 'child', 'resource_id': 'child_id'}])
