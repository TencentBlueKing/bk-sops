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


import ujson as json


from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest

TEST_PROJECT_ID = "123"  # do not change this to non number
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_APP_CODE = "app_code"
TEST_TASKFLOW_ID = "2"


class StartTaskAPITest(APITest):
    def url(self):
        return "/apigw/start_task/{task_id}/{project_id}/"

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
    def test_start_task(self):
        assert_return = {"result": True}
        task = MockTaskFlowInstance(task_action_return=assert_return)

        with mock.patch(TASKINSTANCE_GET, MagicMock(return_value=task)):
            response = self.client.post(
                path=self.url().format(
                    task_id=TEST_TASKFLOW_ID, project_id=TEST_PROJECT_ID
                ),
                data=json.dumps({}),
                content_type="application/json",
                HTTP_BK_APP_CODE=TEST_APP_CODE,
            )

            task.task_action.assert_called_once_with("start", "")

            data = json.loads(response.content)

            self.assertEqual(data, assert_return)
