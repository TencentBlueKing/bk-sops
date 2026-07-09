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
from mock import MagicMock, patch

from gcloud import err_code
from gcloud.tests.mock import MockProject, MockTaskFlowInstance
from gcloud.tests.mock_settings import PROJECT_GET, TASKINSTANCE_GET

from .utils import APITest

TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_TASKFLOW_ID = "2"
TEST_NODE_ID = "node_id"
TEST_TRACE_ID = "trace_id"
TEST_PLUGIN_CODE = "plugin_code"


class GetTaskNodeLogAPITest(APITest):
    def url(self):
        return "/apigw/get_task_node_log/{task_id}/{project_id}/"

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
    def test_get_task_node_log__node_not_in_task(self):
        mock_taskflow = MockTaskFlowInstance(id=TEST_TASKFLOW_ID)
        mock_taskflow.has_node = MagicMock(return_value=False)

        with patch(TASKINSTANCE_GET, MagicMock(return_value=mock_taskflow)):
            with patch(
                "gcloud.apigw.views.get_task_node_log.fetch_task_node_log",
                MagicMock(return_value={"result": True, "message": "success", "data": "log"}),
            ) as mock_fetch_log:
                response = self.client.get(
                    path=self.url().format(task_id=TEST_TASKFLOW_ID, project_id=TEST_PROJECT_ID),
                    data={"node_id": TEST_NODE_ID, "version": "legacy"},
                )

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.CONTENT_NOT_EXIST.code)
        mock_taskflow.has_node.assert_called_once_with(TEST_NODE_ID)
        mock_fetch_log.assert_not_called()


class GetTaskPluginLogAPITest(APITest):
    def url(self):
        return "/apigw/get_task_plugin_log/{task_id}/{project_id}/"

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
    def test_get_task_plugin_log__node_not_in_task(self):
        mock_taskflow = MockTaskFlowInstance(id=TEST_TASKFLOW_ID)
        mock_taskflow.has_node = MagicMock(return_value=False)

        with patch(TASKINSTANCE_GET, MagicMock(return_value=mock_taskflow)):
            with patch(
                "gcloud.apigw.views.get_task_plugin_log.fetch_task_plugin_log",
                MagicMock(return_value={"result": True, "message": "success", "data": {"logs": "log"}}),
            ) as mock_fetch_log:
                response = self.client.get(
                    path=self.url().format(task_id=TEST_TASKFLOW_ID, project_id=TEST_PROJECT_ID),
                    data={"node_id": TEST_NODE_ID, "trace_id": TEST_TRACE_ID, "plugin_code": TEST_PLUGIN_CODE},
                )

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.CONTENT_NOT_EXIST.code)
        mock_taskflow.has_node.assert_called_once_with(TEST_NODE_ID)
        mock_fetch_log.assert_not_called()

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
    def test_get_task_plugin_log__trace_id_not_in_node(self):
        mock_taskflow = MockTaskFlowInstance(id=TEST_TASKFLOW_ID)
        mock_taskflow.has_node = MagicMock(return_value=True)
        execution_data = MagicMock(outputs={"trace_id": "other_trace_id"}, inputs={"plugin_code": TEST_PLUGIN_CODE})

        with patch(TASKINSTANCE_GET, MagicMock(return_value=mock_taskflow)):
            with patch(
                "gcloud.apigw.log_auth.get_execution_data_for_node",
                MagicMock(return_value=(execution_data, None)),
            ) as mock_get_execution_data:
                with patch(
                    "gcloud.apigw.views.get_task_plugin_log.fetch_task_plugin_log",
                    MagicMock(return_value={"result": True, "message": "success", "data": {"logs": "log"}}),
                ) as mock_fetch_log:
                    response = self.client.get(
                        path=self.url().format(task_id=TEST_TASKFLOW_ID, project_id=TEST_PROJECT_ID),
                        data={"node_id": TEST_NODE_ID, "trace_id": TEST_TRACE_ID, "plugin_code": TEST_PLUGIN_CODE},
                    )

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.CONTENT_NOT_EXIST.code)
        mock_taskflow.has_node.assert_called_once_with(TEST_NODE_ID)
        mock_get_execution_data.assert_called_once_with("get_task_plugin_log", TEST_NODE_ID)
        mock_fetch_log.assert_not_called()


class GetNodeJobExecutedLogAPITest(APITest):
    def url(self):
        return "/apigw/get_node_job_executed_log/{task_id}/{project_id}/"

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
    def test_get_node_job_executed_log__node_not_in_task(self):
        mock_taskflow = MockTaskFlowInstance(id=TEST_TASKFLOW_ID)
        mock_taskflow.has_node = MagicMock(return_value=False)

        with patch(TASKINSTANCE_GET, MagicMock(return_value=mock_taskflow)):
            with patch(
                "gcloud.apigw.views.get_node_job_executed_log.fetch_node_job_executed_log",
                MagicMock(return_value={"result": True, "message": "success", "logs": "log"}),
            ) as mock_fetch_log:
                response = self.client.get(
                    path=self.url().format(task_id=TEST_TASKFLOW_ID, project_id=TEST_PROJECT_ID),
                    data={"node_id": TEST_NODE_ID},
                )

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.CONTENT_NOT_EXIST.code)
        mock_taskflow.has_node.assert_called_once_with(TEST_NODE_ID)
        mock_fetch_log.assert_not_called()
