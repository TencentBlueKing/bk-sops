# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.conf import settings
from django.test import TestCase
from blueapps.utils import get_client_by_user

from pipeline_plugins.components import utils
from pipeline_plugins.tests.utils import mock_get_client_by_user


return_success = True


class TestUtils(TestCase):
    def setUp(self):
        self.run_ver = settings.OPEN_VER
        self.app_code = settings.APP_CODE
        self.get_client_by_user = get_client_by_user

        setattr(settings, 'OPEN_VER', 'TEST')
        setattr(settings, 'APP_CODE', 'APP_CODE')
        utils.get_client_v1_by_user = mock_get_client_by_user

    def tearDown(self):
        setattr(settings, 'APP_CODE', self.app_code)
        setattr(settings, 'OPEN_VER', self.run_ver)
        utils.get_client_v1_by_user = self.get_client_by_user

    def test_get_ip_by_regex(self):
        self.assertEqual(utils.get_ip_by_regex('1.1.1.1,2.2.2.2,3.3.3.3'), ['1.1.1.1',
                                                                            '2.2.2.2',
                                                                            '3.3.3.3'])
