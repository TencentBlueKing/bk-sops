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

import json

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest

TEST_PROJECT_ID = "123"
TEST_BIZ_CC_ID = "123"
TEST_TASKFLOW_ID = "2"
TEST_NODE_ID = "node0df0431f8f553925af01a94854bd"
TEST_VERSION = "23ac8c29f62b3337aafcf1f538d277f8"
TEST_TRACE_ID = "trace_id"
TEST_PLUGIN_CODE = "plugin_code"

NODE_LOG_DATA_SOURCE_FACTORY = "gcloud.apigw.views.get_task_node_log.NodeLogDataSourceFactory"
PLUGIN_SERVICE_API_CLIENT = "gcloud.apigw.views.get_task_plugin_log.PluginServiceApiClient"
GET_EXECUTION_DATA_FOR_NODE = "gcloud.apigw.log_auth.get_execution_data_for_node"

PROJECT_GET_MOCK = mock.patch(
    PROJECT_GET,
    MagicMock(
        return_value=MockProject(
            project_id=TEST_PROJECT_ID,
            name="biz name",
            bk_biz_id=TEST_BIZ_CC_ID,
            from_cmdb=True,
        )
    ),
)


def mock_node_log_data_source(logs="log content"):
    data_source = MagicMock()
    data_source.fetch_node_logs = MagicMock(return_value={"result": True, "data": {"logs": logs, "page_info": {}}})
    factory = MagicMock()
    factory.data_source = data_source
    return MagicMock(return_value=factory)


class GetTaskLogRouteAPITest(APITest):
    """确保网关日志接口从 URL 路径中取到 task_id 与 project_id，避免路由与视图签名不一致导致接口整体不可用"""

    def url(self):
        return "/apigw/{api_name}/{task_id}/{project_id}/"

    @PROJECT_GET_MOCK
    def test_get_task_node_log__task_bound_to_project_in_path(self):
        taskflow = MockTaskFlowInstance()
        taskflow.has_node = MagicMock(return_value=True)
        taskinstance_get = MagicMock(return_value=taskflow)
        with mock.patch(TASKINSTANCE_GET, taskinstance_get), mock.patch(
            NODE_LOG_DATA_SOURCE_FACTORY, mock_node_log_data_source()
        ):
            response = self.client.get(
                path=self.url().format(
                    api_name="get_task_node_log", task_id=TEST_TASKFLOW_ID, project_id=TEST_BIZ_CC_ID
                ),
                data={"node_id": TEST_NODE_ID, "version": TEST_VERSION},
            )

        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        taskinstance_get.assert_called_once_with(id=TEST_TASKFLOW_ID, project_id=TEST_PROJECT_ID)

    @PROJECT_GET_MOCK
    @mock.patch(TASKINSTANCE_GET, MagicMock(side_effect=TaskFlowInstance.DoesNotExist()))
    def test_get_task_node_log__task_not_in_project(self):
        response = self.client.get(
            path=self.url().format(api_name="get_task_node_log", task_id=TEST_TASKFLOW_ID, project_id=TEST_BIZ_CC_ID),
            data={"node_id": TEST_NODE_ID, "version": TEST_VERSION},
        )

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertIn("does not exist", data["message"])

    @PROJECT_GET_MOCK
    def test_get_task_plugin_log__task_bound_to_project_in_path(self):
        taskflow = MockTaskFlowInstance()
        taskflow.has_node = MagicMock(return_value=True)
        taskinstance_get = MagicMock(return_value=taskflow)
        plugin_client = MagicMock()
        plugin_client.get_plugin_logs = MagicMock(return_value={"result": True, "data": {"logs": []}})
        execution_data = MagicMock(outputs={"trace_id": TEST_TRACE_ID}, inputs={"plugin_code": TEST_PLUGIN_CODE})
        with mock.patch(TASKINSTANCE_GET, taskinstance_get), mock.patch(
            PLUGIN_SERVICE_API_CLIENT, plugin_client
        ), mock.patch(GET_EXECUTION_DATA_FOR_NODE, MagicMock(return_value=(execution_data, None))):
            response = self.client.get(
                path=self.url().format(
                    api_name="get_task_plugin_log", task_id=TEST_TASKFLOW_ID, project_id=TEST_BIZ_CC_ID
                ),
                data={"node_id": TEST_NODE_ID, "plugin_code": TEST_PLUGIN_CODE, "trace_id": TEST_TRACE_ID},
            )

        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        taskinstance_get.assert_called_once_with(id=TEST_TASKFLOW_ID, project_id=TEST_PROJECT_ID)
        plugin_client.get_plugin_logs.assert_called_once_with(TEST_PLUGIN_CODE, TEST_TRACE_ID, None)
