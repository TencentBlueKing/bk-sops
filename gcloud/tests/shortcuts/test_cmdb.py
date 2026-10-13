# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from mock import MagicMock, patch

from django.test import SimpleTestCase

from gcloud.shortcuts.cmdb import get_business_group_members


class GetBusinessGroupMembersTestCase(SimpleTestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.cc.search_business = MagicMock(
            return_value={
                "result": True,
                "data": {"count": 1, "info": [{"bk_biz_maintainer": "m2,m1", "bk_biz_productor": "p2,p1"}]},
            }
        )
        self.get_client_by_user_patcher = patch(
            "gcloud.shortcuts.cmdb.get_client_by_user", MagicMock(return_value=self.client)
        )
        self.get_client_by_user_patcher.start()

        mock_environment_variables = MagicMock()
        mock_environment_variables.objects.get_var.return_value = 0
        self.environment_variables_patcher = patch(
            "gcloud.shortcuts.cmdb.EnvironmentVariables", mock_environment_variables
        )
        self.environment_variables_patcher.start()

    def tearDown(self):
        self.get_client_by_user_patcher.stop()
        self.environment_variables_patcher.stop()

    def test__no_group_return_empty(self):
        self.assertEqual(get_business_group_members(1, []), [])

    def test__keep_cmdb_return_order(self):
        # 从配置平台(CMDB)拉取的人员顺序需与接口返回顺序一致，不能被 set 去重排序打乱
        members = get_business_group_members(1, ["Maintainers", "ProductPm"])
        self.assertEqual(members, ["m2", "m1", "p2", "p1"])

    def test__order_follows_receiver_group_order(self):
        # 通知分组顺序为 ProductPm -> Maintainers 时，人员也应按该分组顺序拼接
        members = get_business_group_members(1, ["ProductPm", "Maintainers"])
        self.assertEqual(members, ["p2", "p1", "m2", "m1"])

    def test__search_business_fail_return_empty(self):
        self.client.cc.search_business = MagicMock(return_value={"result": False, "message": "fail"})
        self.assertEqual(get_business_group_members(1, ["Maintainers"]), [])
