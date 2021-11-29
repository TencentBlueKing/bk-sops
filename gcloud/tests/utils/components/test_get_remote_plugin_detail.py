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
from gcloud.tests.mock_settings import TEMPLATENODE_STATISTICS_FILTER
from gcloud.tests.mock import MagicMock
from gcloud.utils.components import PluginServiceApiClient
from gcloud.utils.components import get_remote_plugin_detail_list
from gcloud.analysis_statistics.models import TemplateNodeStatistics

GET_PAAS_PLUGIN_INFO = "gcloud.utils.components.PluginServiceApiClient.get_paas_plugin_info"
TEST_API_RESULT = {
    "result": True,
    "results": [{"code": "code1", "name": "name1"}, {"code": "code2", "name": "name2"}],
    "count": 2,
}
TEST_REMOTE_PLUGINS = [("code1", "1.0.0"), ("code2", "1.0.1")]
TEST_LIMIT = 100
TEST_OFFSET = 0


class MockTemplateNodeStatistics(MagicMock):
    def values_list(self, *args, **kwargs):
        return TEST_REMOTE_PLUGINS


class TestGetRemotePluginDetailList(TestCase):
    def test_call_success(self):
        with mock.patch("gcloud.utils.components.env.USE_PLUGIN_SERVICE", "1"):
            with mock.patch(TEMPLATENODE_STATISTICS_FILTER, MagicMock(return_value=MockTemplateNodeStatistics())):
                with mock.patch(GET_PAAS_PLUGIN_INFO, MagicMock(return_value=TEST_API_RESULT)):
                    plugin_info = get_remote_plugin_detail_list(limit=TEST_LIMIT, offset=TEST_OFFSET)
                    TemplateNodeStatistics.objects.filter.assert_called_once_with(is_remote=True)
                    PluginServiceApiClient.get_paas_plugin_info.assert_called_once_with(
                        search_term=None, environment="prod", limit=TEST_LIMIT, offset=TEST_OFFSET
                    )
                    self.assertEqual(
                        plugin_info,
                        [
                            {
                                "name": "name1",
                                "code": "code1",
                                "version": "1.0.0",
                                "group_name": "第三方插件",
                                "is_remote": True,
                            },
                            {
                                "name": "name2",
                                "code": "code2",
                                "version": "1.0.1",
                                "group_name": "第三方插件",
                                "is_remote": True,
                            },
                        ],
                    )
