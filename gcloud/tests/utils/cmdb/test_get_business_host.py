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
from mock import MagicMock, patch

from django.test import TestCase

from gcloud.utils.cmdb import get_business_host


class GetBusinessHostTestCase(TestCase):
    def setUp(self):

        mock_client = MagicMock()
        mock_client.cc.list_biz_hosts = "list_biz_hosts"
        self.get_client_by_user_patcher = patch(
            "gcloud.utils.cmdb.get_client_by_user", MagicMock(return_value=mock_client)
        )
        self.get_client_by_user_patcher.start()

        self.username = "username_token"
        self.bk_biz_id = "bk_biz_id_token"
        self.supplier_account = "supplier_account_token"
        self.host_fields = "host_fileds_token"
        self.ip_list = "ip_list_token"
        self.list_biz_hosts_return = "list_biz_hosts_token"

    def tearDown(self):
        self.get_client_by_user_patcher.stop()

    def test__get_hosts_without_ip_list(self):
        mock_batch_request = MagicMock(return_value=self.list_biz_hosts_return)
        with patch("gcloud.utils.cmdb.batch_request", mock_batch_request):
            hosts = get_business_host(self.username, self.bk_biz_id, self.supplier_account, self.host_fields)

        self.assertEqual(hosts, self.list_biz_hosts_return)
        mock_batch_request.assert_called_once_with(
            "list_biz_hosts",
            {"bk_biz_id": self.bk_biz_id, "bk_supplier_account": self.supplier_account, "fields": self.host_fields},
        )

    def test__get_hosts_with_ip_list(self):
        mock_batch_request = MagicMock(return_value=self.list_biz_hosts_return)
        with patch("gcloud.utils.cmdb.batch_request", mock_batch_request):
            hosts = get_business_host(
                self.username, self.bk_biz_id, self.supplier_account, self.host_fields, self.ip_list
            )

        self.assertEqual(hosts, self.list_biz_hosts_return)
        mock_batch_request.assert_called_once_with(
            "list_biz_hosts",
            {
                "bk_biz_id": self.bk_biz_id,
                "bk_supplier_account": self.supplier_account,
                "fields": self.host_fields,
                "host_property_filter": {
                    "condition": "AND",
                    "rules": [{"field": "bk_host_innerip", "operator": "in", "value": self.ip_list}],
                },
            },
        )
