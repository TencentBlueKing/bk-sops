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


from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.apigw.views.get_task_list import TASK_ACTIONS

from .utils import APITest, TEST_USERNAME


MOCK_FORMAT_TASK_LIST_DATA = "gcloud.apigw.views.get_task_list.format_task_list_data"
MOCK_GET_TASK_ALLOWED_ACTIONS = "gcloud.apigw.views.get_task_list.get_task_allowed_actions_for_user"

TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
SUCCESS_CODE = 0
TEST_APP_CODE = "test_code"
TEST_TASK_LIST = [{"id": "1"}, {"id": "2"}]
TEST_TASK_ID_LIST = [1, 2]
TEST_ALLOWED_ACTIONS = {
    "1": {"TEST_ACTION": True},
    "2": {"TEST_ACTION": True},
}


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
        with mock.patch(
            MOCK_FORMAT_TASK_LIST_DATA, MagicMock(return_value=(TEST_TASK_LIST, TEST_TASK_ID_LIST))
        ) as mocked_format_task_list_data:
            with mock.patch(
                MOCK_GET_TASK_ALLOWED_ACTIONS, MagicMock(return_value=TEST_ALLOWED_ACTIONS)
            ) as mocked_get_task_allowed_data:
                response = self.client.get(
                    path=self.url().format(project_id=TEST_PROJECT_ID),
                    data={"is_started": "true", "is_finished": "false"},
                    HTTP_BK_APP_CODE=TEST_APP_CODE,
                    HTTP_BK_USERNAME=TEST_USERNAME,
                )

                mocked_format_task_list_data.assert_called_once()
                mocked_get_task_allowed_data.assert_called_once_with(TEST_USERNAME, TASK_ACTIONS, TEST_TASK_ID_LIST)

                assert_data = [
                    {"id": "1", "auth_actions": ["TEST_ACTION"]},
                    {"id": "2", "auth_actions": ["TEST_ACTION"]},
                ]

                response = json.loads(response.content)

                self.assertTrue(response["result"])
                self.assertEqual(response["data"], assert_data)
                self.assertEqual(response["code"], SUCCESS_CODE)
