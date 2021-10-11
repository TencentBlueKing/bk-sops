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


from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest, TEST_USERNAME


TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
SUCCESS_CODE = 0
TEST_APP_CODE = "test_code"


class GetTaskListAPITest(APITest):
    def url(self):
        return "/apigw/get_task_list/{project_id}/"

    @mock.patch(
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
    @mock.patch(TASKINSTANCE_GET, MagicMock(return_value=MockQuerySet()))
    def test_get_task_list__success(self):
        response = self.client.get(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data={"is_started": "true", "is_finished": "false"},
            HTTP_BK_APP_CODE=TEST_APP_CODE,
            HTTP_BK_USERNAME=TEST_USERNAME,
        )

        data = json.loads(response.content)

        self.assertTrue(data["result"])
        self.assertEqual(data["code"], SUCCESS_CODE)
