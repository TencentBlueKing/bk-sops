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

from gcloud.user_custom_config.models import UserCustomProjectConfig

TEST_USER = "test_user"
TEST_NOT_EXIST_USERCONF = "user1"
TEST_PROJECT_ID = 12345


class TestUserConf(TestCase):
    def test_set_userconf(self):
        user_conf = UserCustomProjectConfig.objects.set_userconf(
            username=TEST_USER, project_id=TEST_PROJECT_ID, task_template_ordering="id"
        )
        self.assertEqual(user_conf.task_template_ordering, "id")
        self.assertEqual(user_conf.username, TEST_USER)
        self.assertEqual(user_conf.project_id, TEST_PROJECT_ID)

    def test_get_conf(self):
        user_conf = UserCustomProjectConfig.objects.set_userconf(username=TEST_USER, project_id=TEST_PROJECT_ID)
        self.assertEqual(user_conf.task_template_ordering, "-id")
        self.assertEqual(user_conf.username, TEST_USER)
        self.assertEqual(user_conf.project_id, TEST_PROJECT_ID)
