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
TEST_ACTION = "TEST_ACTION"
TEST_DATA = {"data": "data"}
TEST_INPUTS = {"inputs": "inputs"}
TEST_FLOW_ID = "TEST_FLOW_ID"
GET_NODE_DATA_RETURN = {"data": "GET_NODE_DATA_RETURN_DATA", "result": True}


class OperateNodeAPITest(APITest):
    def url(self):
        return "/apigw/operate_node/{project_id}/{task_id}/"

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
    def test_opearte_node__invalid_req(self):
        response = self.client.post(
            path=self.url().format(
                project_id=TEST_PROJECT_ID, task_id=TEST_TASKFLOW_ID
            ),
            data="invalid_json",
            content_type="application/json",
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
    @patch(
        TASKINSTANCE_GET,
        MagicMock(return_value=MockTaskFlowInstance(id=TEST_TASKFLOW_ID)),
    )
    def test_operate_node__invalid_data(self):
        response = self.client.post(
            path=self.url().format(
                project_id=TEST_PROJECT_ID, task_id=TEST_TASKFLOW_ID
            ),
            data=json.dumps({"data": "data"}),
            content_type="application/json",
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
    @patch(
        TASKINSTANCE_GET,
        MagicMock(return_value=MockTaskFlowInstance(id=TEST_TASKFLOW_ID)),
    )
    def test_operate_node__invalid_inputs(self):
        response = self.client.post(
            path=self.url().format(
                project_id=TEST_PROJECT_ID, task_id=TEST_TASKFLOW_ID
            ),
            data=json.dumps({"inputs": "inputs"}),
            content_type="application/json",
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
    def trest_operate_node__success(self):
        task_instance = MagicMock()
        task_instance.id = TEST_TASKFLOW_ID
        task_instance.nodes_action = MagicMock(return_value=NODES_ACTION_RETURN)

        with patch(
            TASKINSTANCE_GET, MagicMock(return_value=task_instance),
        ):

            response = self.client.get(
                path=self.url().format(
                    project_id=TEST_PROJECT_ID, task_id=TEST_TASKFLOW_ID
                ),
                data={
                    "node_id": TEST_NODE_ID,
                    "action": TEST_COMPONENT_CODE,
                    "data": TEST_DATA,
                    "inputs": TEST_INPUTS,
                    "flow_id": TEST_FLOW_ID,
                },
            )

        data = json.loads(response.content)

        self.assertTrue(data["result"])
        self.assertEqual(data["code"], err_code.SUCCESS.code)
        self.assertEqual(data["data"], NODES_ACTION_RETURN["data"])

        task_instance.nodes_action.assert_called_once_with(
            TEST_ACTION,
            TEST_NODE_ID,
            "",
            data=TEST_DATA,
            inputs=TEST_INPUTS,
            flow_id=TEST_FLOW_ID,
        )
