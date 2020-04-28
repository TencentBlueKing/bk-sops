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

from auth_backend.resources.base import Action, ActionCollection


class ActionCollectionTestCase(TestCase):

    def setUp(self):
        self.actions = [Action(id='view', name='name_1', is_instance_related=True),
                        Action(id='edit', name='name_2', is_instance_related=True)]

    def test_init(self):
        collection = ActionCollection(self.actions)
        for action in self.actions:
            self.assertEqual(getattr(collection, action.id).name, action.name)

    def test_iter(self):
        collection = ActionCollection(self.actions)
        for i, action in enumerate(collection):
            self.assertEqual(action.id, self.actions[i].id)
