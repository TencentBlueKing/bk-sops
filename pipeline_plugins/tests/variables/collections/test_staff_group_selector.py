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

from django.test import TestCase

from pipeline_plugins.variables.collections.common import StaffGroupSelector


class MockClient(object):
    def __init__(self, search_business_return=None):
        self.cc = MagicMock()
        self.cc.search_business = MagicMock(
            return_value={
                "code": 0,
                "result": True,
                "message": "success",
                "data": {
                    "count": 1,
                    "info": [
                        {
                            "bk_biz_developer": "developer",
                            "bk_biz_maintainer": "maintainer",
                            "bk_biz_tester": "tester",
                            "bk_biz_productor": "productor",
                        },
                    ],
                },
            }
        )


mock_staff_group = MagicMock()


class StaffGroupSelectorTestCase(TestCase):
    def setUp(self):
        self.name = "staff_group"
        self.internal_staff_group = ["bk_biz_maintainer", "bk_biz_productor", "bk_biz_developer", "bk_biz_tester"]
        self.custom_staff_group = ["1", "2", "3"]
        self.context = {}
        self.pipeline_data = {"executor": "tester", "biz_cc_id": 2, "tenant_id": "test"}
        self.supplier_account = "supplier_account_token"

        self.values_list = MagicMock(
            values_list=MagicMock(return_value=["tester1,tester2", "tester2", "tester3", "tester4"])
        )
        self.filter = MagicMock(return_value=self.values_list)
        self.staff_group_patcher = patch(
            "pipeline_plugins.variables.collections.common.StaffGroupSet.objects.filter", self.filter
        )

        self.supplier_account_for_project_patcher = patch(
            "pipeline_plugins.variables.collections.common.supplier_account_for_business",
            MagicMock(return_value=self.supplier_account),
        )

        self.get_notify_receivers_return = {
            "result": True,
            "message": "success",
            "data": "developer,maintainer,productor,tester,tester1,tester2,tester3,tester4",
        }
        self.get_notify_receivers_patcher = patch(
            "pipeline_plugins.variables.collections.common.get_notify_receivers",
            MagicMock(return_value=self.get_notify_receivers_return),
        )

        self.staff_group_patcher.start()
        self.supplier_account_for_project_patcher.start()
        self.get_notify_receivers_patcher.start()

    def tearDown(self):
        self.staff_group_patcher.stop()
        self.supplier_account_for_project_patcher.stop()
        self.get_notify_receivers_patcher.stop()

    def test_get_value_with_all_staff_names(self):
        self.custom_staff_group.extend(self.internal_staff_group)
        staff_names = StaffGroupSelector(self.name, self.custom_staff_group, self.context, self.pipeline_data)
        value = staff_names.get_value()
        self.assertEqual(value, "developer,maintainer,productor,tester,tester1,tester2,tester3,tester4")
