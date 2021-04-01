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

from pipeline import apps
from pipeline.tests.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa


class TestApps(TestCase):
    def test_get_client_through_sentinel__single_sentinel(self):
        settings = MagicMock()
        settings.REDIS = {
            "host": "1.1.1.1",
            "port": "123456",
        }
        rs = MagicMock()
        sentinel = MagicMock(return_value=rs)

        with patch(APPS_SETTINGS, settings):
            with patch(APPS_SENTINEL, sentinel):
                r = apps.get_client_through_sentinel()

                sentinel.assert_called_once_with([("1.1.1.1", "123456")], sentinel_kwargs={})
                rs.master_for.assert_called_once_with("mymaster")
                self.assertIsNotNone(r)

    @patch(APPS_SENTINEL, MagicMock(return_value=MagicMock()))
    def test_get_client_through_sentinel__mutiple_sentinel(self):
        settings = MagicMock()
        settings.REDIS = {
            "host": "1.1.1.1,2.2.2.2, 3.3.3.3 , 4.4.4.4",
            "port": "123456,45678,11111",
            "password": "password_token",
            "service_name": "name_token",
        }
        rs = MagicMock()
        sentinel = MagicMock(return_value=rs)

        with patch(APPS_SETTINGS, settings):
            with patch(APPS_SENTINEL, sentinel):
                r = apps.get_client_through_sentinel()

                sentinel.assert_called_once_with(
                    [("1.1.1.1", "123456"), ("2.2.2.2", "45678"), ("3.3.3.3", "11111")],
                    password="password_token",
                    sentinel_kwargs={},
                )
                rs.master_for.assert_called_once_with("name_token")
                self.assertIsNotNone(r)
