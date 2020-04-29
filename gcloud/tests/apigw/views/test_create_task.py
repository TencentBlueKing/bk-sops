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


import copy
import ujson as json
import jsonschema

from pipeline.exceptions import PipelineException

from gcloud import err_code
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.apigw.views import create_task
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest

TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_DATA = "data"
TEST_APP_CODE = "app_code"
TEST_TEMPLATE_ID = "1"
TEST_TASKFLOW_ID = "2"
TEST_TASKFLOW_URL = "url"
TEST_TASKFLOW_PIPELINE_TREE = "pipeline_tree"
TEST_PIPELINE_TREE = {"constants": {"key1": {"value": ""}}}


class CreateTaskAPITest(APITest):
    def url(self):
        return "/apigw/create_task/{template_id}/{project_id}/"

    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(return_value=(True, TEST_DATA)))
    @mock.patch(
        TASKINSTANCE_CREATE, MagicMock(return_value=MockTaskFlowInstance(id=TEST_TASKFLOW_ID)),
    )
    @mock.patch(APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_task__success(self):
        pt1 = MockPipelineTemplate(id=1, name="pt1")

        tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)
        proj = MockProject(
            project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
        )

        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            with mock.patch(
                TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl)),
            ):
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
                            "exclude_task_nodes_id": "exclude_task_nodes_id",
                            "flow_type": "common",
                        }
                    ),
                    content_type="application/json",
                    HTTP_BK_APP_CODE=TEST_APP_CODE,
                )

                TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.assert_called_once_with(
                    tmpl, {"name": "name", "creator": "", "description": ""}, {}, "exclude_task_nodes_id",
                )

                TaskFlowInstance.objects.create.assert_called_once_with(
                    project=proj,
                    category=tmpl.category,
                    pipeline_instance=TEST_DATA,
                    template_id=TEST_TEMPLATE_ID,
                    template_source="project",
                    create_method="api",
                    create_info=TEST_APP_CODE,
                    flow_type="common",
                    current_flow="execute_task",
                )

                data = json.loads(response.content)

                self.assertTrue(data["result"], msg=data)
                self.assertEqual(data["data"], assert_data)

                TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.reset_mock()
                TaskFlowInstance.objects.create.reset_mock()

            pt1 = MockPipelineTemplate(id=1, name="pt1")

            tmpl = MockCommonTemplate(id=1, pipeline_template=pt1)

            with mock.patch(
                COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl)),
            ):
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
                            "exclude_task_nodes_id": "exclude_task_nodes_id",
                            "template_source": "common",
                            "flow_type": "common",
                        }
                    ),
                    content_type="application/json",
                    HTTP_BK_APP_CODE=TEST_APP_CODE,
                )

                TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.assert_called_once_with(
                    tmpl, {"name": "name", "creator": "", "description": ""}, {}, "exclude_task_nodes_id",
                )

                TaskFlowInstance.objects.create.assert_called_once_with(
                    project=proj,
                    category=tmpl.category,
                    pipeline_instance=TEST_DATA,
                    template_id=TEST_TEMPLATE_ID,
                    template_source="common",
                    create_method="api",
                    create_info=TEST_APP_CODE,
                    flow_type="common",
                    current_flow="execute_task",
                )

                data = json.loads(response.content)

                self.assertTrue(data["result"], msg=data)
                self.assertEqual(data["data"], assert_data)

    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(return_value=(True, TEST_DATA)))
    @mock.patch(
        TASKINSTANCE_CREATE, MagicMock(return_value=MockTaskFlowInstance(id=TEST_TASKFLOW_ID)),
    )
    @mock.patch(APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    @mock.patch(APIGW_CREATE_TASK_NODE_NAME_HANDLE, MagicMock())
    @mock.patch(APIGW_CREATE_TASK_VALIDATE_WEB_PIPELINE_TREE, MagicMock())
    @mock.patch(TASKINSTANCE_CREATE_PIPELINE_INSTANCE, MagicMock(return_value=TEST_DATA))
    def test_create_task__success_with_tree(self):
        pt1 = MockPipelineTemplate(id=1, name="pt1")

        tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)
        proj = MockProject(
            project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
        )

        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            with mock.patch(
                TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl)),
            ):
                assert_data = {
                    "task_id": TEST_TASKFLOW_ID,
                    "task_url": TEST_TASKFLOW_URL,
                    "pipeline_tree": copy.deepcopy(TEST_TASKFLOW_PIPELINE_TREE),
                }
                response = self.client.post(
                    path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                    data=json.dumps(
                        {
                            "name": "name",
                            "constants": {"key1": "value1", "key2": "value2"},
                            "pipeline_tree": TEST_PIPELINE_TREE,
                            "flow_type": "common",
                        }
                    ),
                    content_type="application/json",
                    HTTP_BK_APP_CODE=TEST_APP_CODE,
                )

                TaskFlowInstance.objects.create_pipeline_instance.assert_called_once_with(
                    template=tmpl,
                    name="name",
                    creator="",
                    description="",
                    pipeline_tree={"constants": {"key1": {"value": "value1"}}},
                )

                TaskFlowInstance.objects.create.assert_called_once_with(
                    project=proj,
                    category=tmpl.category,
                    pipeline_instance=TEST_DATA,
                    template_id=TEST_TEMPLATE_ID,
                    template_source="project",
                    create_method="api",
                    create_info=TEST_APP_CODE,
                    flow_type="common",
                    current_flow="execute_task",
                )

                data = json.loads(response.content)

                self.assertTrue(data["result"], msg=data)
                self.assertEqual(data["data"], assert_data)

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    @mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet()))
    @mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet()))
    @mock.patch(
        APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock(side_effect=jsonschema.ValidationError("")),
    )
    def test_create_task__validate_fail(self):
        response = self.client.post(
            path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
            data=json.dumps({"name": "name", "constants": {}, "exclude_task_node_id": "exclude_task_node_id", }),
            content_type="application/json",
        )

        data = json.loads(response.content)

        self.assertFalse(data["result"])
        self.assertTrue("message" in data)

        response = self.client.post(
            path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
            data=json.dumps(
                {
                    "name": "name",
                    "constants": {},
                    "exclude_task_node_id": "exclude_task_node_id",
                    "template_source": "common",
                }
            ),
            content_type="application/json",
        )

        data = json.loads(response.content)

        self.assertFalse(data["result"])
        self.assertTrue("message" in data)

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    @mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet()))
    @mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet()))
    @mock.patch(APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_task__without_app_code(self):
        response = self.client.post(
            path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
            data=json.dumps({"constants": {}, "name": "test", "exclude_task_node_id": "exclude_task_node_id", }),
            content_type="application/json",
        )

        data = json.loads(response.content)

        self.assertFalse(data["result"])
        self.assertTrue("message" in data)

        response = self.client.post(
            path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
            data=json.dumps(
                {
                    "constants": {},
                    "name": "test",
                    "exclude_task_node_id": "exclude_task_node_id",
                    "template_source": "common",
                }
            ),
            content_type="application/json",
        )

        data = json.loads(response.content)

        self.assertFalse(data["result"])
        self.assertTrue("message" in data)

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(side_effect=PipelineException()))
    @mock.patch(APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_task__create_pipeline_raise(self):
        pt1 = MockPipelineTemplate(id=1, name="pt1")

        tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)

        with mock.patch(
            TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl)),
        ):
            response = self.client.post(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps({"name": "name", "constants": {}, "exclude_task_node_id": "exclude_task_node_id", }),
                content_type="application/json",
                HTTP_BK_APP_CODE=TEST_APP_CODE,
            )

            data = json.loads(response.content)

            self.assertFalse(data["result"])
            self.assertTrue("message" in data)

        pt1 = MockPipelineTemplate(id=1, name="pt1")

        tmpl = MockCommonTemplate(id=1, pipeline_template=pt1)

        with mock.patch(
            COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl)),
        ):
            response = self.client.post(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps(
                    {
                        "name": "name",
                        "constants": {},
                        "exclude_task_node_id": "exclude_task_node_id",
                        "template_source": "common",
                    }
                ),
                content_type="application/json",
                HTTP_BK_APP_CODE=TEST_APP_CODE,
            )

            data = json.loads(response.content)

            self.assertFalse(data["result"])
            self.assertTrue("message" in data)

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(return_value=(False, "")))
    @mock.patch(APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_task__create_pipeline_fail(self):
        pt1 = MockPipelineTemplate(id=1, name="pt1")

        tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)

        with mock.patch(
            TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl)),
        ):
            response = self.client.post(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps({"name": "name", "constants": {}, "exclude_task_node_id": "exclude_task_node_id", }),
                content_type="application/json",
                HTTP_BK_APP_CODE=TEST_APP_CODE,
            )

            data = json.loads(response.content)

            self.assertFalse(data["result"])
            self.assertTrue("message" in data)

        pt1 = MockPipelineTemplate(id=1, name="pt1")

        tmpl = MockCommonTemplate(id=1, pipeline_template=pt1)

        with mock.patch(
            COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl)),
        ):
            response = self.client.post(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps(
                    {
                        "name": "name",
                        "constants": {},
                        "exclude_task_node_id": "exclude_task_node_id",
                        "template_source": "common",
                    }
                ),
                content_type="application/json",
                HTTP_BK_APP_CODE=TEST_APP_CODE,
            )

            data = json.loads(response.content)

            self.assertFalse(data["result"])
            self.assertTrue("message" in data)

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    @mock.patch(APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    @mock.patch(APIGW_CREATE_TASK_NODE_NAME_HANDLE, MagicMock())
    @mock.patch(APIGW_CREATE_TASK_VALIDATE_WEB_PIPELINE_TREE, MagicMock(side_effect=Exception()))
    def test_create_task__validate_pipeline_tree_error(self):
        pt1 = MockPipelineTemplate(id=1, name="pt1")

        tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)

        with mock.patch(
            TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl)),
        ):
            response = self.client.post(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps(
                    {
                        "name": "name",
                        "pipeline_tree": TEST_PIPELINE_TREE,
                        "exclude_task_node_id": "exclude_task_node_id",
                    }
                ),
                content_type="application/json",
                HTTP_BK_APP_CODE=TEST_APP_CODE,
            )

            data = json.loads(response.content)

            self.assertFalse(data["result"])
            self.assertTrue("message" in data)
            self.assertEqual(data["code"], err_code.UNKNOW_ERROR.code)

            create_task.pipeline_node_name_handle.assert_called_once_with(TEST_PIPELINE_TREE)
            create_task.validate_web_pipeline_tree.assert_called_once_with(TEST_PIPELINE_TREE)
            create_task.pipeline_node_name_handle.reset_mock()
            create_task.validate_web_pipeline_tree.reset_mock()

        pt1 = MockPipelineTemplate(id=1, name="pt1")

        tmpl = MockCommonTemplate(id=1, pipeline_template=pt1)

        with mock.patch(
            COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl)),
        ):
            response = self.client.post(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps(
                    {
                        "name": "name",
                        "pipeline_tree": TEST_PIPELINE_TREE,
                        "exclude_task_node_id": "exclude_task_node_id",
                        "template_source": "common",
                    }
                ),
                content_type="application/json",
                HTTP_BK_APP_CODE=TEST_APP_CODE,
            )

            data = json.loads(response.content)

            self.assertFalse(data["result"])
            self.assertTrue("message" in data)
            self.assertEqual(data["code"], err_code.UNKNOW_ERROR.code)

            create_task.pipeline_node_name_handle.assert_called_once_with(TEST_PIPELINE_TREE)
            create_task.validate_web_pipeline_tree.assert_called_once_with(TEST_PIPELINE_TREE)

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    @mock.patch(APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    @mock.patch(APIGW_CREATE_TASK_NODE_NAME_HANDLE, MagicMock())
    @mock.patch(APIGW_CREATE_TASK_VALIDATE_WEB_PIPELINE_TREE, MagicMock())
    @mock.patch(
        TASKINSTANCE_CREATE_PIPELINE_INSTANCE, MagicMock(side_effect=PipelineException()),
    )
    def test_create_task__create_pipeline_instance_error(self):
        pt1 = MockPipelineTemplate(id=1, name="pt1")

        tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)

        with mock.patch(
            TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl)),
        ):
            response = self.client.post(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps(
                    {
                        "name": "name",
                        "pipeline_tree": TEST_PIPELINE_TREE,
                        "exclude_task_node_id": "exclude_task_node_id",
                    }
                ),
                content_type="application/json",
                HTTP_BK_APP_CODE=TEST_APP_CODE,
            )

            data = json.loads(response.content)

            self.assertFalse(data["result"])
            self.assertTrue("message" in data)
            self.assertEqual(data["code"], err_code.UNKNOW_ERROR.code)

            TaskFlowInstance.objects.create_pipeline_instance.assert_called_once_with(
                template=tmpl, name="name", creator="", description="", pipeline_tree=TEST_PIPELINE_TREE,
            )
            TaskFlowInstance.objects.create_pipeline_instance.reset_mock()

        pt1 = MockPipelineTemplate(id=1, name="pt1")

        tmpl = MockCommonTemplate(id=1, pipeline_template=pt1)

        with mock.patch(
            COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl)),
        ):
            response = self.client.post(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps(
                    {
                        "name": "name",
                        "pipeline_tree": TEST_PIPELINE_TREE,
                        "exclude_task_node_id": "exclude_task_node_id",
                        "template_source": "common",
                    }
                ),
                content_type="application/json",
                HTTP_BK_APP_CODE=TEST_APP_CODE,
            )

            data = json.loads(response.content)

            self.assertFalse(data["result"])
            self.assertTrue("message" in data)
            self.assertEqual(data["code"], err_code.UNKNOW_ERROR.code)

            TaskFlowInstance.objects.create_pipeline_instance.assert_called_once_with(
                template=tmpl, name="name", creator="", description="", pipeline_tree=TEST_PIPELINE_TREE,
            )
