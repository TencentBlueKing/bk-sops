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

TEST_PROJECT_ID = "123"  # do not change this to non number
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_APP_CODE = "app_code"
TEST_TASKFLOW_ID = "2"
TEST_TASKFLOW_URL = "url"


class StartTaskAPITest(APITest):
    def url(self):
        return "/apigw/start_task/{task_id}/{project_id}/"

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    def test_start_task__task_is_started(self):
        taskflow_instance = MagicMock()
        taskflow_instance.objects.is_task_started = MagicMock(return_value=True)

        with mock.patch(APIGW_START_TASK_TASKFLOW_INSTANCE, taskflow_instance):
            response = self.client.post(
                path=self.url().format(task_id=TEST_TASKFLOW_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps({}),
                content_type="application/json",
                HTTP_BK_APP_CODE=TEST_APP_CODE,
            )

            taskflow_instance.objects.is_task_started.assert_called_once_with(
                project_id=TEST_PROJECT_ID, id=TEST_TASKFLOW_ID
            )

            data = json.loads(response.content)

            if "trace_id" in data:
                data.pop("trace_id")
            self.assertFalse(data["result"])
            self.assertEqual(data["message"], "task already started")

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    def test_start_task(self):
        assert_return = {"result": True, "task_url": TEST_TASKFLOW_URL, "code": 0}
        taskflow_instance = MagicMock()
        taskflow_instance.objects.is_task_started = MagicMock(return_value=False)
        taskflow_instance.task_url = MagicMock(return_value=TEST_TASKFLOW_URL)
        prepare_and_start_task = MagicMock()

        with mock.patch(APIGW_START_TASK_TASKFLOW_INSTANCE, taskflow_instance):
            with mock.patch(APIGW_START_TASK_PREPARE_AND_START_TASK, prepare_and_start_task):
                response = self.client.post(
                    path=self.url().format(task_id=TEST_TASKFLOW_ID, project_id=TEST_PROJECT_ID),
                    data=json.dumps({}),
                    content_type="application/json",
                    HTTP_BK_APP_CODE=TEST_APP_CODE,
                )

                taskflow_instance.objects.is_task_started.assert_called_once_with(
                    project_id=TEST_PROJECT_ID, id=TEST_TASKFLOW_ID
                )
                prepare_and_start_task.apply_async.assert_called_once_with(
                    kwargs=dict(task_id=TEST_TASKFLOW_ID, project_id=TEST_PROJECT_ID, username=""),
                    queue="task_prepare_api",
                    routing_key="task_prepare_api",
                )

                data = json.loads(response.content)

            if "trace_id" in data:
                data.pop("trace_id")

            self.assertEqual(data, assert_return)
