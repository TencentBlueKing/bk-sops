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

import ujson as json

from django.test import TestCase

from gcloud.tests.mock import mock
from gcloud.contrib.analysis.views import get_all_components

MOCK_GET_COMPONENTS = "gcloud.contrib.analysis.views.get_all_components"

TEST_COMPS = [
    {"code": "code1", "name": "name1", "group_name": "gpname", "is_remote": False},
    {"code": "code2", "name": "name2", "group_name": "gpname2", "is_remote": True},
]


class GetAllComp(TestCase):
    @property
    def url(self):
        return "/analysis/get_component_list/"

    def test_success(self):
        with mock.patch(MOCK_GET_COMPONENTS):
            response = self.client.get(path=self.url)
            get_all_components.assert_called_once_with()
            data = json.loads(response.content)
            self.assertEqual(data, {"result": True, "data": TEST_COMPS})
