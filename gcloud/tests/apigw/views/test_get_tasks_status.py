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

import copy
import ujson as json

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud import err_code
from gcloud.core.utils import format_datetime

from .utils import APITest

TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"


class GetTasksStatusAPITest(APITest):
    def url(self):
        return "/apigw/get_tasks_status/{project_id}/"

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    def test_get_tasks_status__success_with_children_status(self):
        task = MockTaskFlowInstance(get_status_return={"children": "children"})
        status = copy.deepcopy(task.get_status())

        with patch(TASKFLOW_OBJECTS_FILTER, MagicMock(return_value=[task])):
            response = self.client.post(
                path=self.url().format(project_id=TEST_PROJECT_ID),
                data=json.dumps({"task_id_list": [1, 2, 3], "include_children_status": True}),
                content_type="application/json",
            )

            data = json.loads(response.content)

            self.assertTrue(data["result"])
            self.assertEqual(data["code"], err_code.SUCCESS.code)
            self.assertEqual(
                data["data"],
                [
                    {
                        "id": task.id,
                        "name": task.name,
                        "status": status,
                        "create_time": format_datetime(task.create_time),
                        "start_time": format_datetime(task.start_time),
                        "finish_time": format_datetime(task.finish_time),
                        "url": task.url,
                    }
                ],
            )

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    def test_get_tasks_status__success_without_children_status(self):
        task = MockTaskFlowInstance(get_status_return={"children": "children"})
        status = copy.deepcopy(task.get_status())
        status.pop("children")

        with patch(TASKFLOW_OBJECTS_FILTER, MagicMock(return_value=[task])):
            response = self.client.post(
                path=self.url().format(project_id=TEST_PROJECT_ID),
                data=json.dumps({"task_id_list": [1, 2, 3]}),
                content_type="application/json",
            )

            data = json.loads(response.content)

            self.assertTrue(data["result"])
            self.assertEqual(data["code"], err_code.SUCCESS.code)
            self.assertEqual(
                data["data"],
                [
                    {
                        "id": task.id,
                        "name": task.name,
                        "status": status,
                        "create_time": format_datetime(task.create_time),
                        "start_time": format_datetime(task.start_time),
                        "finish_time": format_datetime(task.finish_time),
                        "url": task.url,
                    }
                ],
            )

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    def test_get_tasks_status__invalid_json(self):
        task = MockTaskFlowInstance()

        with patch(TASKFLOW_OBJECTS_FILTER, MagicMock(return_value=[task])):
            response = self.client.post(
                path=self.url().format(project_id=TEST_PROJECT_ID),
                data="invalid json",
                content_type="application/json",
            )

            data = json.loads(response.content)

            self.assertFalse(data["result"])
            self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
            self.assertTrue("message" in data)

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    def test_get_tasks_status__invalid_task_id_list(self):
        task = MockTaskFlowInstance()

        with patch(TASKFLOW_OBJECTS_FILTER, MagicMock(return_value=[task])):
            response = self.client.post(
                path=self.url().format(project_id=TEST_PROJECT_ID),
                data=json.dumps({"task_id_list": "not a list"}),
                content_type="application/json",
            )

            data = json.loads(response.content)

            self.assertFalse(data["result"])
            self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
            self.assertTrue("message" in data)
