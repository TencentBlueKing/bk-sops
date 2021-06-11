# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


import ujson as json

from pipeline.utils.collections import FancyDict

from gcloud import err_code
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest


class GetUserProjectListAPITest(APITest):
    def url(self):
        return "/apigw/get_user_project_list/"

    @patch(
        APIGW_GET_USER_PROJECT_LIST_GET_USER_PROJECT_LIST, MagicMock(side_effect=Exception()),
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
            APIGW_GET_USER_PROJECT_LIST_GET_USER_PROJECT_LIST, MagicMock(return_value=project_list),
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
