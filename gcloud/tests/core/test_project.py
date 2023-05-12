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
from django.db import IntegrityError
from django.test import TestCase

from gcloud.core import project
from gcloud.core.models import Business, Project
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class CaseData(object):
    @staticmethod
    def sync_projects_from_cmdb_business_data():
        return {
            "biz_list": [
                {
                    "bk_biz_name": "name_1",
                    "bk_supplier_account": "supplier_account",
                    "bk_supplier_id": 0,
                    "time_zone": "time_zone",
                    "life_cycle": "life_cycle",
                    "bk_data_status": "enable",
                    "bk_biz_id": 1,
                    "bk_biz_maintainer": "m1,m2,m3",
                },
                {
                    "bk_biz_name": "name_4",
                    "bk_supplier_account": "supplier_account",
                    "bk_supplier_id": 0,
                    "time_zone": "time_zone",
                    "life_cycle": "life_cycle",
                    "bk_data_status": "enable",
                    "bk_biz_id": 4,
                    "bk_biz_maintainer": "m2,m3",
                },
                {
                    "bk_biz_name": "name_5",
                    "bk_supplier_account": "supplier_account",
                    "bk_supplier_id": 0,
                    "time_zone": "time_zone",
                    "life_cycle": "life_cycle",
                    "bk_data_status": "enable",
                    "bk_biz_id": 5,
                    "bk_biz_maintainer": "m3",
                },
            ]
        }


class ProjectModelTestCase(TestCase):
    def tearDown(self):
        Business.objects.all().delete()
        Project.objects.all().delete()

    @classmethod
    def generate_business_update_or_create_params_list(cls, biz_list):
        return [
            dict(
                cc_id=biz["bk_biz_id"],
                defaults={
                    "cc_name": biz["bk_biz_name"],
                    "cc_owner": biz["bk_supplier_account"],
                    "cc_company": biz["bk_supplier_id"],
                    "time_zone": biz["time_zone"],
                    "life_cycle": biz["life_cycle"],
                    "status": biz["bk_data_status"],
                },
            )
            for biz in biz_list
        ]

    @classmethod
    def generate_business_update_or_create_calls(cls, biz_list):
        return [
            mock.call(**update_or_create_params)
            for update_or_create_params in cls.generate_business_update_or_create_params_list(biz_list)
        ]

    @patch(CORE_PROJECT_GET_USER_BUSINESS_LIST, MagicMock(return_value=[]))
    @patch(CORE_MODEL_PROJECT_SYNC_PROJECT, MagicMock(return_value=[]))
    @patch(CORE_MODEL_USER_DEFAULT_PROJECT_INIT_USER_DEFAULT_PROJECT, MagicMock())
    def test_sync_projects_from_cmdb__empty_business_list(self):
        project.sync_projects_from_cmdb("user")

        Project.objects.sync_project_from_cmdb_business.assert_called_once_with({})

    @patch(
        CORE_PROJECT_GET_USER_BUSINESS_LIST,
        MagicMock(return_value=CaseData.sync_projects_from_cmdb_business_data()["biz_list"]),
    )
    @patch(CORE_MODEL_BUSINESS_UPDATE_OR_CREATE, MagicMock())
    @patch(CORE_MODEL_USER_DEFAULT_PROJECT_INIT_USER_DEFAULT_PROJECT, MagicMock())
    @patch(CORE_MODEL_PROJECT_UPDATE_BUSINESS_PROJECT_STATUS, MagicMock())
    def test_sync_projects_from_cmdb__project_exist(self):
        Business.objects.create(cc_id=5, cc_name="name_5", cc_owner="owner", cc_company="company")
        with patch(CORE_MODEL_PROJECT_SYNC_PROJECT, MagicMock(side_effect=IntegrityError)):
            project.sync_projects_from_cmdb("user")
            Project.objects.update_business_project_status.assert_called_once_with(
                archived_cc_ids=set(), active_cc_ids={1, 4, 5}
            )
            self.assertEqual(len(Project.objects.all()), 0)
        project.sync_projects_from_cmdb("user")
        self.assertEqual(len(Project.objects.all()), 3)

    @patch(
        CORE_PROJECT_GET_USER_BUSINESS_LIST,
        MagicMock(return_value=CaseData.sync_projects_from_cmdb_business_data()["biz_list"]),
    )
    @patch(CORE_MODEL_BUSINESS_UPDATE_OR_CREATE, MagicMock())
    @patch(CORE_MODEL_PROJECT_SYNC_PROJECT, MagicMock(return_value=["token_0", "token_1"]))
    @patch(CORE_MODEL_USER_DEFAULT_PROJECT_INIT_USER_DEFAULT_PROJECT, MagicMock())
    def test_sync_projects_from_cmdb(self):
        Business.objects.create(cc_id=5, cc_name="name_5", cc_owner="owner", cc_company="company")
        project.sync_projects_from_cmdb("user")

        Business.objects.update_or_create.assert_has_calls(
            self.generate_business_update_or_create_calls(CaseData.sync_projects_from_cmdb_business_data()["biz_list"])
        )

        Project.objects.sync_project_from_cmdb_business.assert_called_once_with(
            {
                1: {"cc_name": "name_1", "time_zone": "time_zone", "creator": "user"},
                4: {"cc_name": "name_4", "time_zone": "time_zone", "creator": "user"},
                5: {"cc_name": "name_5", "time_zone": "time_zone", "creator": "user"},
            }
        )

    @patch(
        CORE_PROJECT_GET_USER_BUSINESS_LIST,
        MagicMock(return_value=CaseData.sync_projects_from_cmdb_business_data()["biz_list"][:-1]),
    )
    @patch(CORE_MODEL_BUSINESS_UPDATE_OR_CREATE, MagicMock())
    @patch(CORE_MODEL_PROJECT_SYNC_PROJECT, MagicMock(return_value=["token_0", "token_1"]))
    @patch(CORE_MODEL_USER_DEFAULT_PROJECT_INIT_USER_DEFAULT_PROJECT, MagicMock())
    @patch(CORE_MODEL_PROJECT_UPDATE_BUSINESS_PROJECT_STATUS, MagicMock())
    def test_sync_projects_from_cmdb__business_deleted(self):

        project_values_list_qs = MagicMock()
        project_values_list_qs.values_list = MagicMock(return_value=[1, 4, 5])
        biz_list = CaseData.sync_projects_from_cmdb_business_data()["biz_list"]
        with patch(CORE_PROJECT_GET_USER_BUSINESS_LIST, MagicMock(return_value=biz_list)):
            with patch(PROJECT_FILTER, MagicMock(return_value=project_values_list_qs)):
                project.sync_projects_from_cmdb("user")

        # 模拟从 CC 删除最后一个业务
        with patch(CORE_PROJECT_GET_USER_BUSINESS_LIST, MagicMock(return_value=biz_list[:-1])):
            with patch(PROJECT_FILTER, MagicMock(return_value=project_values_list_qs)):
                project.sync_projects_from_cmdb("user")

        Business.objects.update_or_create.assert_has_calls(
            self.generate_business_update_or_create_calls(biz_list + biz_list[:-1])
        )

        Project.objects.update_business_project_status.assert_has_calls(
            [
                mock.call(archived_cc_ids=set(), active_cc_ids={1, 4, 5}),
                # cc_id=5 的业务被删除，需要归档
                mock.call(archived_cc_ids={5}, active_cc_ids={1, 4}),
            ]
        )
