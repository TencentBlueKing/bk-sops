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

from .utils import APITest

TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_TASKFLOW_ID = "2"
TEST_DATA = {"state": "CREATED"}
TEST_SUBPROCESS_STACK = "[1, 2, 3]"
TEST_SUBPROCESS_ID = "subprocess_id"
DISPATCHER_RETURN = {"result": True, "code": 0, "data": TEST_DATA, "message": ""}

GET_TASK_STATUS_TASK_COMMAND_DISPATCHER = "gcloud.apigw.views.get_task_status.TaskCommandDispatcher"


class GetTaskStatusAPITest(APITest):
    def url(self):
        return "/apigw/get_task_status/{task_id}/{project_id}/"

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    def test_get_task_status__success(self):
        task = MagicMock()
        task.name = "task_name"
        dispatcher = MagicMock()
        dispatcher.get_task_status = MagicMock(return_value=DISPATCHER_RETURN)

        with mock.patch(TASKINSTANCE_GET, MagicMock(return_value=task)):
            with mock.patch(GET_TASK_STATUS_TASK_COMMAND_DISPATCHER, MagicMock(return_value=dispatcher)):
                response = self.client.get(path=self.url().format(task_id=TEST_TASKFLOW_ID, project_id=TEST_PROJECT_ID))

                data = json.loads(response.content)
                self.assertTrue(data["result"], msg=data)
                self.assertEqual(data["data"], {"name": task.name, "state": "CREATED"})

    def test_get_task_status__raise(self):
        task = MockTaskFlowInstance(get_status_raise=Exception())

        with mock.patch(TASKINSTANCE_GET, MagicMock(return_value=task)):
            response = self.client.get(path=self.url().format(task_id=TEST_TASKFLOW_ID, project_id=TEST_PROJECT_ID))

            data = json.loads(response.content)
            self.assertFalse(data["result"])
            self.assertTrue("message" in data)
