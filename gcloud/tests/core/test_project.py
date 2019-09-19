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

from gcloud.core import project
from gcloud.core.models import Business, Project

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class CaseData(object):

    @staticmethod
    def sync_projects_from_cmdb_business_data():
        return {
            'biz_list': [{
                'bk_biz_name': 'name_1',
                'bk_supplier_account': 'supplier_account',
                'bk_supplier_id': 0,
                'time_zone': 'time_zone',
                'life_cycle': 'life_cycle',
                'bk_data_status': 'enable',
                'bk_biz_id': 1,
                'bk_biz_maintainer': 'm1,m2,m3'
            }, {
                'bk_biz_name': 'name_4',
                'bk_supplier_account': 'supplier_account',
                'bk_supplier_id': 0,
                'time_zone': 'time_zone',
                'life_cycle': 'life_cycle',
                'bk_data_status': 'enable',
                'bk_biz_id': 4,
                'bk_biz_maintainer': 'm2,m3'
            }, {
                'bk_biz_name': 'name_5',
                'bk_supplier_account': 'supplier_account',
                'bk_supplier_id': 0,
                'time_zone': 'time_zone',
                'life_cycle': 'life_cycle',
                'bk_data_status': 'enable',
                'bk_biz_id': 5,
                'bk_biz_maintainer': 'm3'
            }]
        }


class ProjectModelTestCase(TestCase):

    def tearDown(self):
        Business.objects.all().delete()

    @patch(CORE_PROJECT_GET_USER_BUSINESS_LIST, MagicMock(return_value=[]))
    @patch(CORE_MODEL_PROJECT_SYNC_PROJECT, MagicMock(return_value=[]))
    @patch(CORE_MODEL_USER_DEFAULT_PROJECT_INIT_USER_DEFAULT_PROJECT, MagicMock())
    def test_sync_projects_from_cmdb__empty_business_list(self):
        project.sync_projects_from_cmdb('user')

        Project.objects.sync_project_from_cmdb_business.assert_called_once_with({})

    @patch(CORE_PROJECT_GET_USER_BUSINESS_LIST,
           MagicMock(return_value=CaseData.sync_projects_from_cmdb_business_data()['biz_list']))
    @patch(CORE_MODEL_BUSINESS_UPDATE_OR_CREATE, MagicMock())
    @patch(CORE_MODEL_PROJECT_SYNC_PROJECT, MagicMock(return_value=['token_0', 'token_1']))
    @patch(CORE_MODEL_USER_DEFAULT_PROJECT_INIT_USER_DEFAULT_PROJECT, MagicMock())
    def test_sync_projects_from_cmdb(self):
        Business.objects.create(cc_id=5, cc_name='name_5', cc_owner='owner', cc_company='company')
        project.sync_projects_from_cmdb('user')

        Business.objects.update_or_create.assert_has_calls([
            mock.call(cc_id=1, defaults={
                'cc_name': 'name_1',
                'cc_owner': 'supplier_account',
                'cc_company': 0,
                'time_zone': 'time_zone',
                'life_cycle': 'life_cycle',
                'status': 'enable'
            }),
            mock.call(cc_id=4, defaults={
                'cc_name': 'name_4',
                'cc_owner': 'supplier_account',
                'cc_company': 0,
                'time_zone': 'time_zone',
                'life_cycle': 'life_cycle',
                'status': 'enable'
            }),
            mock.call(cc_id=5, defaults={
                'cc_name': 'name_5',
                'cc_owner': 'supplier_account',
                'cc_company': 0,
                'time_zone': 'time_zone',
                'life_cycle': 'life_cycle',
                'status': 'enable'
            })
        ])

        Project.objects.sync_project_from_cmdb_business.assert_called_once_with({
            1: {
                'cc_name': 'name_1',
                'time_zone': 'time_zone',
                'creator': 'user'
            },
            4: {
                'cc_name': 'name_4',
                'time_zone': 'time_zone',
                'creator': 'user'
            },
            5: {
                'cc_name': 'name_5',
                'time_zone': 'time_zone',
                'creator': 'user'
            }
        })
