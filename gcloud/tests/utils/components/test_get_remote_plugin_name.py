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

from gcloud.tests import mock
from gcloud.tests.mock import MagicMock
from gcloud.utils.components import PluginServiceApiClient
from gcloud.utils.components import get_remote_plugin_name

GET_PAAS_PLUGIN_INFO = "gcloud.utils.components.PluginServiceApiClient.get_paas_plugin_info"
TEST_RESULT = {
    "result": True,
    "results": [{"code": "code1", "name": "name1"}, {"code": "code2", "name": "name2"}],
    "count": 2,
}
TEST_LIMIT = 100
TEST_OFFSET = 0


class TestGetRemotePluginName(TestCase):
    def test_call_success(self):
        with mock.patch("gcloud.utils.components.env.USE_PLUGIN_SERVICE", "1"):
            with mock.patch(GET_PAAS_PLUGIN_INFO, MagicMock(return_value=TEST_RESULT)):
                plugin_info = get_remote_plugin_name(limit=TEST_LIMIT, offset=TEST_OFFSET)
                PluginServiceApiClient.get_paas_plugin_info.assert_called_once_with(
                    search_term=None, environment="prod", limit=TEST_LIMIT, offset=TEST_OFFSET
                )
                self.assertEqual(plugin_info, {"code1": "name1", "code2": "name2"})
