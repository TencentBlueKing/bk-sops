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


import ujson as json

from pipeline.utils.collections import FancyDict

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud import err_code

from .utils import APITest

TEST_PROJECT_ID = "1"
TEST_PROJECT_NAME = "name"
TEST_BIZ_CC_ID = "2"
TEST_BIZ_NAME = "biz_name"
TEST_BIZ_DEVELOPERS = "TEST_BIZ_DEVELOPERS"
TEST_BIZ_MAINTAINER = "TEST_BIZ_MAINTAINER"
TEST_BIZ_TESTER = "TEST_BIZ_TESTER"
TEST_BIZ_PRODUCTOR = "TEST_BIZ_PRODUCTOR"


class GetUserProjectDetailAPITest(APITest):
    def url(self):
        return "/apigw/get_user_project_detail/{project_id}/"

    @patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID,
                name=TEST_PROJECT_NAME,
                bk_biz_id=TEST_BIZ_CC_ID,
                from_cmdb=True,
            )
        ),
    )
    @patch(
        APIGW_GET_USER_PROJECT_DETAIL_GET_BUSINESS_DETAIL,
        MagicMock(side_effect=Exception()),
    )
    def test_get_user_project_detail__get_business_detail_raise(self):
        response = self.client.get(path=self.url().format(project_id=TEST_PROJECT_ID))

        data = json.loads(response.content)

        self.assertFalse(data["result"])
        self.assertTrue("message" in data)
        self.assertEqual(data["code"], err_code.UNKNOWN_ERROR.code)

    @patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID,
                name=TEST_PROJECT_NAME,
                bk_biz_id=TEST_BIZ_CC_ID,
                from_cmdb=True,
            )
        ),
    )
    @patch(
        APIGW_GET_USER_PROJECT_DETAIL_GET_BUSINESS_DETAIL,
        MagicMock(
            return_value=FancyDict(
                bk_biz_id=TEST_BIZ_CC_ID,
                bk_biz_name=TEST_BIZ_NAME,
                bk_biz_developer=TEST_BIZ_DEVELOPERS,
                bk_biz_maintainer=TEST_BIZ_MAINTAINER,
                bk_biz_tester=TEST_BIZ_TESTER,
                bk_biz_productor=TEST_BIZ_PRODUCTOR,
            )
        ),
    )
    def test_get_user_project_detail__success(self):
        response = self.client.get(path=self.url().format(project_id=TEST_PROJECT_ID))

        data = json.loads(response.content)

        self.assertTrue(data["result"])
        self.assertEqual(data["code"], err_code.SUCCESS.code)
        self.assertEqual(
            data["data"],
            {
                "project_id": TEST_PROJECT_ID,
                "project_name": TEST_PROJECT_NAME,
                "from_cmdb": True,
                "bk_biz_id": TEST_BIZ_CC_ID,
                "bk_biz_name": TEST_BIZ_NAME,
                "bk_biz_developer": TEST_BIZ_DEVELOPERS,
                "bk_biz_maintainer": TEST_BIZ_MAINTAINER,
                "bk_biz_tester": TEST_BIZ_TESTER,
                "bk_biz_productor": TEST_BIZ_PRODUCTOR,
            },
        )
