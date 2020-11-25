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


from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud import err_code

from .utils import APITest

TEST_PROJECT_ID = "1"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "2"
TEST_TASKFLOW_ID = "3"
TEST_NODE_ID = "TEST_NODE_ID"
TEST_COMPONENT_CODE = "TEST_COMPONENT_CODE"
TEST_LOOP = "TEST_LOOP"
GET_NODE_DATA_RETURN = {"result": True, "data": "data", "message": "message"}


class GetTaskNodeDataAPITest(APITest):
    def url(self):
        return "/apigw/get_task_node_data/{project_id}/{task_id}/"

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
        TASKINSTANCE_GET,
        MagicMock(return_value=MockTaskFlowInstance(id=TEST_TASKFLOW_ID)),
    )
    def test_get_task_node_data__subprocess_stack_invalid(self):
        response = self.client.get(
            path=self.url().format(
                project_id=TEST_PROJECT_ID, task_id=TEST_TASKFLOW_ID
            ),
            data={
                "node_id": TEST_NODE_ID,
                "component_code": TEST_COMPONENT_CODE,
                "loop": TEST_LOOP,
                "subprocess_stack": "invalid array",
            },
        )

        data = json.loads(response.content)

        self.assertFalse(data["result"])
        self.assertTrue("message" in data)
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)

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
    def test_get_task_node_data__success(self):
        task_instance = MagicMock()
        task_instance.id = TEST_TASKFLOW_ID
        task_instance.get_node_data = MagicMock(return_value=GET_NODE_DATA_RETURN)

        with patch(
            TASKINSTANCE_GET, MagicMock(return_value=task_instance),
        ):

            response = self.client.get(
                path=self.url().format(
                    project_id=TEST_PROJECT_ID, task_id=TEST_TASKFLOW_ID
                ),
                data={
                    "node_id": TEST_NODE_ID,
                    "component_code": TEST_COMPONENT_CODE,
                    "loop": TEST_LOOP,
                },
            )

        data = json.loads(response.content)

        self.assertTrue(data["result"])
        self.assertEqual(data["code"], err_code.SUCCESS.code)
        self.assertEqual(data["data"], GET_NODE_DATA_RETURN["data"])

        task_instance.get_node_data.assert_called_once_with(
            TEST_NODE_ID, "", TEST_COMPONENT_CODE, [], TEST_LOOP
        )
