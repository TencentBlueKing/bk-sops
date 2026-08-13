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


import ujson as json
from django.test import modify_settings
from pipeline.utils.collections import FancyDict

from gcloud import err_code
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest


@modify_settings(
    MIDDLEWARE={
        "append": "gcloud.tests.apigw.views.utils.MockApiGatewayJWTPayloadMiddleware",
    }
)
class GetUserProjectListAPITest(APITest):
    def url(self):
        return "/apigw/get_user_project_list/"

    @patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    @patch("gcloud.core.models.Project.objects.filter")
    @patch("gcloud.apigw.views.get_user_project_list.get_user_projects")
    def test_admin_read_returns_all_enabled_projects(self, get_user_projects, project_filter, whitelist_has):
        project_filter.return_value = [
            FancyDict(id=1, bk_biz_id=100, name="enabled", is_disable=False),
        ]

        response = self.client.get(
            path=self.url(),
            HTTP_BK_USERNAME="tester",
            HTTP_BK_APP_CODE="po-app",
            HTTP_BK_JWT_USERNAME="tester",
            HTTP_BK_JWT_USER_VERIFIED=True,
            HTTP_X_BKSOPS_ADMIN_READ="true",
            HTTP_X_BKSOPS_AUDIT_OPERATOR="tester",
        )

        data = json.loads(response.content)

        self.assertTrue(data["result"], data)
        self.assertEqual([item["project_id"] for item in data["data"]], [1])
        get_user_projects.assert_not_called()
        project_filter.assert_called_once_with(is_disable=False)

    @patch(
        APIGW_GET_USER_PROJECT_LIST_GET_USER_PROJECT_LIST,
        MagicMock(side_effect=Exception()),
    )
    def test_get_user_project_list__raise(self):
        response = self.client.get(path=self.url())

        data = json.loads(response.content)

        self.assertFalse(data["result"])
        self.assertTrue("message" in data)
        self.assertEqual(data["code"], err_code.UNKNOWN_ERROR.code)

    def test_get_user_project_list__success(self):

        project_list = [
            FancyDict(id=1, bk_biz_id=1, name="name1", is_disable=False),
            FancyDict(id=2, bk_biz_id=2, name="name2", is_disable=False),
            FancyDict(id=3, bk_biz_id=3, name="name3", is_disable=True),
        ]

        with patch(
            APIGW_GET_USER_PROJECT_LIST_GET_USER_PROJECT_LIST,
            MagicMock(return_value=project_list),
        ):
            response = self.client.get(path=self.url(), data={"bk_username": "text"})

            data = json.loads(response.content)

            self.assertTrue(data["result"])
            self.assertEqual(data["code"], err_code.SUCCESS.code)
            self.assertEqual(
                data["data"],
                [
                    {"project_id": 1, "bk_biz_id": 1, "name": "name1"},
                    {"project_id": 2, "bk_biz_id": 2, "name": "name2"},
                ],
            )
