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

from django.test import TestCase

from gcloud.core.models import EnvironmentVariables
from gcloud.apigw.whitelist import EnvWhitelist


class EnvWhitelistTestcase(TestCase):

    def test_init(self):
        transient_list = {'app1', 'app2'}
        env_key = 'ENV_KEY'
        whitelist = EnvWhitelist(transient_list, env_key)

        self.assertEqual(whitelist.transient_list, transient_list)
        self.assertEqual(whitelist.env_key, env_key)

    def test_has(self):
        transient_list = {'app1', 'app2'}
        env_key = 'ENV_KEY'

        transient_pass_list = EnvWhitelist(transient_list, env_key=env_key)
        self.assertTrue(transient_pass_list.has('app1'))
        self.assertTrue(transient_pass_list.has('app2'))
        self.assertFalse(transient_pass_list.has('app3'))

        EnvironmentVariables.objects.create(key=env_key, value='app3,app4')
        env_pass_list = EnvWhitelist(transient_list, env_key=env_key)
        self.assertTrue(env_pass_list.has('app3'))
        self.assertTrue(env_pass_list.has('app4'))
        self.assertFalse(env_pass_list.has('app5'))
