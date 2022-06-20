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

from gcloud.user_custom_config.constants import get_options_by_fileds, UserConfOption


class TestGetOptionsByFields(TestCase):
    def test_get_success_by_none(self):
        data = get_options_by_fileds()
        self.assertEqual(data, UserConfOption)

    def test_get_success_by_exist_field(self):
        data = get_options_by_fileds(["task_template_ordering"])
        self.assertEqual(data, UserConfOption)
