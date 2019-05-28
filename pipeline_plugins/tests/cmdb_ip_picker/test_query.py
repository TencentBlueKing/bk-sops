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
from mock import patch, MagicMock

from pipeline_plugins.cmdb_ip_picker import query
from pipeline_plugins.tests.utils import mock_get_client_by_request


def mock_json_response(dct):
    return dct


class MockRequest(object):
    GET = {'fields': '[]'}
    user = MagicMock()


class TestQueryCMDB(TestCase):
    def setUp(self):
        self.request = MockRequest()
        self.biz_bk_id = '2'
        self.bk_supplier_account = ''
        self.bk_supplier_id = 0

    @patch('pipeline_plugins.cmdb_ip_picker.query.JsonResponse', mock_json_response)
    @patch('pipeline_plugins.cmdb_ip_picker.query.get_client_by_request', mock_get_client_by_request)
    def test_cmdb_search_host(self):
        mock_get_client_by_request.success = True
        self.assertTrue(query.cmdb_search_host(self.request,
                                               self.biz_bk_id,
                                               self.bk_supplier_account,
                                               self.bk_supplier_id)['result'])

        mock_get_client_by_request.success = False
        self.assertFalse(query.cmdb_search_host(self.request,
                                                self.biz_bk_id,
                                                self.bk_supplier_account,
                                                self.bk_supplier_id)['result'])
