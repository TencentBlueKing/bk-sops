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
from mock.mock import MagicMock

from gcloud.tests.mock import mock
from gcloud.utils.components import format_component_name_with_remote

GET_REMOTE_PLUGIN_NAME = "gcloud.utils.components.get_remote_plugin_name"

TEST_REMOTE_PLUGIN_DICT = {"code1": "name1"}
TEST_COMPONENTS = [
    {"component_code": "code1", "version": "1.0", "is_remote": True, "value": 1},
    {"component_code": "code2", "version": "1.0", "is_remote": False, "value": 1},
]
TEST_COMP_NAME_DICT = {"code2": "inner-name2"}
TEST_GROUPS = [
    {"code": "code1", "name": "第三方插件-name1-1.0", "value": 1},
    {"code": "code2", "name": "inner-name2-1.0", "value": 1},
]


class TestFmtCompNameWithRemote(TestCase):
    def test_success(self):
        with mock.patch(GET_REMOTE_PLUGIN_NAME, MagicMock(return_value=TEST_REMOTE_PLUGIN_DICT)) as mocked:
            groups = format_component_name_with_remote(TEST_COMPONENTS, TEST_COMP_NAME_DICT)
            mocked.assert_called_once_with()
            self.assertEqual(groups, TEST_GROUPS)
