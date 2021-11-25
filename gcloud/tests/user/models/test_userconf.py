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

from gcloud.conf.user.models import UserConf
from gcloud.conf.user.constants import UserConfOption

TEST_EXIST_USERCONF = "test_user"
TEST_NOT_EXIST_USERCONF = "user1"
TEST_EXIST_FIELD = "tasktmpl_ordering"
TEST_NOT_EXIST_FIELD = "test_filed"
TEST_PROJECT_ID = 12345


class TestUserConf(TestCase):
    def setUp(self):
        self.test_user_conf = UserConf.objects.create(username=TEST_EXIST_USERCONF, project_id=TEST_PROJECT_ID)
        self.test_user_conf.save()

    def tearDown(self):
        UserConf.objects.all().delete()

    def test_set_userconf_with_exist_userconf(self):
        success, msg = UserConf.objects.set_userconf(
            TEST_EXIST_USERCONF, TEST_PROJECT_ID, TEST_EXIST_FIELD, "test_value"
        )
        self.assertTrue(success)
        self.assertEqual(msg, None)

    def test_set_userconf_with_not_exist_userconf(self):
        success, msg = UserConf.objects.set_userconf(
            TEST_NOT_EXIST_USERCONF, TEST_PROJECT_ID, TEST_EXIST_FIELD, "test_value"
        )
        self.assertTrue(success)
        self.assertEqual(msg, None)

    def test_set_userconf_with_not_exist_field(self):
        success, msg = UserConf.objects.set_userconf(
            TEST_EXIST_USERCONF, TEST_PROJECT_ID, TEST_NOT_EXIST_FIELD, "test_value"
        )
        self.assertFalse(success)
        self.assertEqual(msg, f"Field:{TEST_NOT_EXIST_FIELD} is not exists!")

    def test_get_conf_by_user_with_right_field(self):
        success, content = UserConf.objects.get_conf_by_user(TEST_EXIST_USERCONF, TEST_PROJECT_ID, [TEST_EXIST_FIELD])
        self.assertTrue(success)
        self.assertEqual(
            content,
            {
                TEST_EXIST_FIELD: {
                    "name": TEST_EXIST_FIELD,
                    "value": "-id",
                    "options": UserConfOption.get(TEST_EXIST_FIELD, {}),
                }
            },
        )

    def test_get_conf_by_user_with_err_field(self):
        success, content = UserConf.objects.get_conf_by_user(
            TEST_EXIST_USERCONF, TEST_PROJECT_ID, [TEST_NOT_EXIST_FIELD]
        )
        self.assertFalse(success)
        self.assertEqual(content, f"Field:{TEST_NOT_EXIST_FIELD} is not exists!")
