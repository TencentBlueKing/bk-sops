# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json

from django.test import TestCase

from blueking.component.shortcuts import ComponentClient


class TestAPI(TestCase):

    def setUp(self):
        self.client = ComponentClient(
            bk_app_code='test',
            bk_app_secret='xxx',
            common_args={
                'bk_username': 'admin',
            }
        )
        self.client.set_bk_api_ver('v2')

    def test_api(self):
        params = {
            'bk_biz_id': 1,
        }
        result = self.client.job.get_job_list(params)
        print json.dumps(result)
