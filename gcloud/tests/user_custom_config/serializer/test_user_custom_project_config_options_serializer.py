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

from gcloud.user_custom_config.serializer import UserCustomProjectConfigOptionsSerializer
from gcloud.user_custom_config.constants import UserConfOption

TEST_FAIL_DATA = {"configs": "aaaa"}
TEST_SUC_DATA = {"configs": ",".join(UserConfOption.keys())}


class TestUserCustomProjectConfigOptionsSerializer(TestCase):
    def test_valid_false(self):
        test_ser = UserCustomProjectConfigOptionsSerializer(data=TEST_FAIL_DATA)
        valid_result = test_ser.is_valid(raise_exception=False)
        self.assertFalse(valid_result)

    def test_valid_true(self):
        test_ser = UserCustomProjectConfigOptionsSerializer(data=TEST_SUC_DATA)
        valid_result = test_ser.is_valid(raise_exception=False)
        self.assertTrue(valid_result)
