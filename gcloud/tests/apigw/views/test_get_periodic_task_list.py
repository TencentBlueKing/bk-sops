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

from gcloud.apigw.views.get_periodic_task_list import PERIODIC_TASK_ACTIONS
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.utils.dates import format_datetime

from .utils import APITest

MOCK_GET_PERIODIC_TASK_ALLOWED_ACTIONS = (
    "gcloud.apigw.views.get_periodic_task_list.get_periodic_task_allowed_actions_for_user"
)


TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_APP_CODE = "app_code"
TEST_USERNAME = "username"
TEST_TENANT_ID = "system"
TEST_PERIODIC_TASK_ALLOWED_ACTIONS = {
    "1": {"TEST_ACTION": True},
    "2": {"TEST_ACTION": True},
    "3": {"TEST_ACTION": True},
}
TEST_ID_LIST = ["1", "2", "3"]


class GetPeriodicTaskListAPITest(APITest):
    def url(self):
        return "/apigw/get_periodic_task_list/{project_id}/"

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
    def test_get_periodic_task_list(self):
        pt1 = MockPeriodicTask(id="1")
        pt2 = MockPeriodicTask(id="2")
        pt3 = MockPeriodicTask(id="3")

        periodic_tasks = [pt1, pt2, pt3]

        assert_data = [
            {
                "id": task.id,
                "name": task.name,
                "template_id": task.template_id,
                "template_source": task.template_source,
                "creator": task.creator,
                "cron": task.cron,
                "enabled": task.enabled,
                "last_run_at": format_datetime(task.last_run_at),
                "total_run_count": task.total_run_count,
                "auth_actions": ["TEST_ACTION"],
            }
            for task in periodic_tasks
        ]
        with mock.patch(
            MOCK_GET_PERIODIC_TASK_ALLOWED_ACTIONS, MagicMock(return_value=TEST_PERIODIC_TASK_ALLOWED_ACTIONS)
        ) as mock_get_actions:
            with mock.patch(PERIODIC_TASK_FILTER, MagicMock(return_value=periodic_tasks)):
                response = self.client.get(
                    path=self.url().format(project_id=TEST_PROJECT_ID),
                    HTTP_BK_APP_CODE=TEST_APP_CODE,
                    HTTP_BK_USERNAME=TEST_USERNAME,
                )
                mock_get_actions.assert_called_once_with(
                    TEST_USERNAME, PERIODIC_TASK_ACTIONS, TEST_ID_LIST, TEST_TENANT_ID
                )
                data = json.loads(response.content)

                self.assertTrue(data["result"], msg=data)
                self.assertEqual(data["data"], assert_data)
