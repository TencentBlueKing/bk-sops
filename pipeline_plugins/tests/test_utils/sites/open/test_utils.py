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

import mock

from cryptography.fernet import Fernet
from django.test import TestCase
from django.conf import settings

from pipeline_plugins.components.utils.sites.open.utils import get_node_callback_url


class UtilsTestCase(TestCase):

    def test_get_node_callback_url(self):
        node_id = 'node_id'
        f = Fernet(settings.CALLBACK_KEY)
        expect_prefix = "%s/taskflow/api/nodes/callback" % settings.APP_HOST
        url = get_node_callback_url(node_id)
        actual_prefix, token = url[:-1].rsplit('/', 1)
        self.assertEqual(expect_prefix, actual_prefix)
        self.assertEqual(node_id, f.decrypt(bytes(token)))

        with mock.patch('gcloud.conf.settings.RUN_MODE', 'PRODUCT'):
            expect_prefix = "%s/taskflow/api/nodes/callback" % settings.APP_HOST
            url = get_node_callback_url(node_id)
            actual_prefix, token = url[:-1].rsplit('/', 1)
            self.assertEqual(expect_prefix, actual_prefix)
            self.assertEqual(node_id, f.decrypt(bytes(token)))
