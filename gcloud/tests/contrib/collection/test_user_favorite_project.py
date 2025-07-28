# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from unittest.mock import MagicMock

from django.test import TestCase

from gcloud.contrib.collection.models import Collection


class UserFavoriteProjectTestCase(TestCase):
    def setUp(self):
        self.username = "user"
        self.instance_id = 2
        self.project_id = 1

        self.mock_project = MagicMock()
        self.mock_project.id = 1
        self.mock_project.name = "mock_project"

    def tearDown(self):
        Collection.objects.all().delete()

    def test_add_user_favorite_project(self):
        self.assertEqual(Collection.objects.count(), 0)
        Collection.objects.add_user_favorite_project(self.username, self.mock_project)
        self.assertEqual(Collection.objects.count(), 1)

    def test_remove_user_favorite_project(self):
        Collection.objects.create(category="project", username=self.username, instance_id=self.instance_id)
        self.assertEqual(Collection.objects.count(), 1)
        Collection.objects.remove_user_favorite_project(self.username, self.instance_id)
        self.assertEqual(Collection.objects.count(), 0)

    def test_get_user_favorite_projects(self):
        Collection.objects.create(category="project", username=self.username, instance_id=1)
        Collection.objects.create(category="project", username=self.username, instance_id=2)
        self.assertEqual(list(Collection.objects.get_user_favorite_projects(self.username)), [1, 2])
