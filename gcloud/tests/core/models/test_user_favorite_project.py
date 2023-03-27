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

from django.test import TestCase

from gcloud.core.models import UserFavoriteProject


class UserFavoriteProjectTestCase(TestCase):
    def setUp(self):
        self.username = "user"
        self.project_id = 1

    def tearDown(self):
        UserFavoriteProject.objects.all().delete()

    def test_add_user_favorite_project(self):
        self.assertEqual(UserFavoriteProject.objects.count(), 0)
        UserFavoriteProject.objects.add_user_favorite_project(self.username, self.project_id)
        self.assertEqual(UserFavoriteProject.objects.count(), 1)

    def test_remove_user_favorite_project(self):
        UserFavoriteProject.objects.create(username=self.username, project_id=self.project_id)
        self.assertEqual(UserFavoriteProject.objects.count(), 1)
        UserFavoriteProject.objects.remove_user_favorite_project(self.username, self.project_id)
        self.assertEqual(UserFavoriteProject.objects.count(), 0)

    def test_get_user_favorite_projects(self):
        UserFavoriteProject.objects.create(username=self.username, project_id=1)
        UserFavoriteProject.objects.create(username=self.username, project_id=2)
        self.assertEqual(list(UserFavoriteProject.objects.get_user_favorite_projects(self.username)), [1, 2])
