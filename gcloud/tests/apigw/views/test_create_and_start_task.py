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


import jsonschema
import ujson as json

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.taskflow3.models import TaskFlowInstance

from .utils import APITest

TEST_APP_CODE = "app_code"
TEST_TEMPLATE_ID = "1"
TEST_DATA = "data"
TEST_TASKFLOW_ID = "2"
TEST_TASKFLOW_URL = "url"
TEST_TASKFLOW_PIPELINE_TREE = "pipeline_tree"
TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_PIPELINE_TREE = {"constants": {"key1": {"value": ""}}}
TEST_USERNAME = "username"


class CreateAndStartTaskAPITest(APITest):
    def url(self):
        return "/apigw/create_and_start_task/{template_id}/{project_id}/"

    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(return_value=TEST_DATA))
    @mock.patch(TASKINSTANCE_CREATE, MagicMock(return_value=MockTaskFlowInstance(id=TEST_TASKFLOW_ID)))
    @mock.patch(APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_and_start_task__success(self):

        pt = MockPipelineTemplate(id=1, name="pt")

        tmpl = MockCommonTemplate(id=1, pipeline_template=pt)

        proj = MockProject(
            project_id=TEST_PROJECT_ID,
            name=TEST_PROJECT_NAME,
            bk_biz_id=TEST_BIZ_CC_ID,
            from_cmdb=True,
        )
        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            with mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
                assert_data = {
                    "task_id": TEST_TASKFLOW_ID,
                    "task_url": TEST_TASKFLOW_URL,
                    "pipeline_tree": TEST_TASKFLOW_PIPELINE_TREE,
                }
                response = self.client.post(
                    path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                    data=json.dumps(
                        {
                            "name": "name",
                            "constants": {},
                            "template_source": "common",
                            "flow_type": "common",
                            "exclude_task_nodes_id": "exclude_task_nodes_id",
                        }
                    ),
                    content_type="application/json",
                    HTTP_BK_APP_CODE=TEST_APP_CODE,
                    HTTP_BK_USERNAME=TEST_USERNAME
                )

                TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.assert_called_once_with(
                    tmpl, {"name": "name", "creator": "", "description": ""}, {}, "exclude_task_nodes_id"
                )

                TaskFlowInstance.objects.create.assert_called_once_with(
                    project=proj,
                    category=tmpl.category,
                    pipeline_instance=TEST_DATA,
                    template_id=TEST_TEMPLATE_ID,
                    template_source="common",
                    create_method="api",
                    flow_type="common",
                    create_info=TEST_APP_CODE,
                    current_flow="execute_task",
                    engine_ver=1,
                )

                data = json.loads(response.content)

                self.assertTrue(data["result"], msg=data)
                self.assertEqual(data["data"], assert_data)

#     @mock.patch(
#         PROJECT_GET,
#         MagicMock(
#             return_value=MockProject(
#                 project_id=TEST_PROJECT_ID,
#                 name=TEST_PROJECT_NAME,
#                 bk_biz_id=TEST_BIZ_CC_ID,
#                 from_cmdb=True,
#             )
#         ),
#     )
#     @mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet()))
#     @mock.patch(APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock(side_effect=jsonschema.ValidationError("")))
#     def test_create_and_start_task__validate_fail(self):
#         response = self.client.post(
#             path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
#             data=json.dumps({"name": "name", "constants": {}, "exclude_task_node_id": "exclude_task_node_id"}),
#             content_type="application/json",
#             HTTP_BK_APP_CODE=TEST_APP_CODE,
#             HTTP_BK_USERNAME=TEST_USERNAME
#         )

#         data = json.loads(response.content)

#         self.assertFalse(data["result"])
#         self.assertTrue("message" in data)

#     @mock.patch(
#         PROJECT_GET,
#         MagicMock(
#             return_value=MockProject(
#                 project_id=TEST_PROJECT_ID,
#                 name=TEST_PROJECT_NAME,
#                 bk_biz_id=TEST_BIZ_CC_ID,
#                 from_cmdb=True,
#             )
#         ),
#     )
#     @mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet()))
#     @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(side_effect=Exception))
#     @mock.patch(APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
#     def test_create_and_start_task__create_pipeline_raise(self):
#         response = self.client.post(
#             path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
#             data=json.dumps({"name": "name", "constants": {}, "exclude_task_node_id": "exclude_task_node_id"}),
#             content_type="application/json",
#             HTPP_BK_APP_CODE=TEST_APP_CODE,
#             HTTP_BK_USERNAME=TEST_USERNAME
#         )

#         data = json.loads(response.content)

#         self.assertFalse(data["result"])
#         self.assertTrue("message" in data)

#     @mock.patch(
#         PROJECT_GET,
#         MagicMock(
#             return_value=MockProject(
#                 project_id=TEST_PROJECT_ID,
#                 name=TEST_PROJECT_NAME,
#                 bk_biz_id=TEST_BIZ_CC_ID,
#             )
#         ),
#     )
#     @mock.patch(COMMONTEMPLATE_GET, MagicMock(return_value=MockQuerySet()))
#     @mock.patch(APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
#     @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(return_value=MockQuerySet()))
#     @mock.patch(TASKINSTANCE_CREATE, MagicMock(side_effect=Exception))
#     def test_create_and_start_task__create_taskinstance_raise(self):
#         response = self.client.post(
#             path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
#             data=json.dumps({"name": "name", "constants": {}, "exclude_task_node_id": "exclude_task_node_id"}),
#             content_type="application/json",
#             HTTP_BK_APP_CODE=TEST_APP_CODE,
#             HTTP_BK_USERNAME=TEST_USERNAME
#         )
#         data = json.loads(response.content)

#         self.assertFalse(data["result"])
#         self.assertTrue("message" in data)
