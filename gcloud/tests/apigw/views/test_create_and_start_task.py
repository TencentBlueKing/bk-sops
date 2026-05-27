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


import jsonschema
import ujson as json

from gcloud import err_code
from gcloud.apigw.schemas import APIGW_CREATE_AND_START_TASK_PARAMS
from gcloud.apigw.views import create_and_start_task
from gcloud.apigw.views.task_node_selector import TaskNodeSelectionValidationError
from gcloud.constants import TaskCreateMethod
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

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
TEST_PRE_PARE_AND_START_TASK = MagicMock()


class CreateAndStartTaskAPITest(APITest):
    def url(self):
        return "/apigw/create_and_start_task/{template_id}/{project_id}/"

    def test_create_and_start_task_schema_accepts_template_schemes_id(self):
        jsonschema.validate(
            {"name": "name", "template_schemes_id": ["scheme_1"]},
            APIGW_CREATE_AND_START_TASK_PARAMS,
        )

        jsonschema.validate(
            {"name": "name", "template_schemes_id": "scheme_1"},
            APIGW_CREATE_AND_START_TASK_PARAMS,
        )

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(
                {"name": "name", "template_schemes_id": [1]},
                APIGW_CREATE_AND_START_TASK_PARAMS,
            )

    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(return_value=TEST_DATA))
    @mock.patch(TASKINSTANCE_CREATE, MagicMock(return_value=MockTaskFlowInstance(id=TEST_TASKFLOW_ID)))
    @mock.patch(APIGW_CREATE_ADN_STATRT_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_and_start_task__success_with_template_schemes_id(self):
        pipeline_tree = {"activities": {"node_1": {}, "node_2": {}}, "constants": {}}
        resolved_exclude_task_nodes_id = ["node_2"]
        pt = MockPipelineTemplate(id=1, name="pt")
        tmpl = MockCommonTemplate(id=1, pipeline_template=pt, pipeline_tree=pipeline_tree)
        proj = MockProject(
            project_id=TEST_PROJECT_ID,
            name=TEST_PROJECT_NAME,
            bk_biz_id=TEST_BIZ_CC_ID,
            from_cmdb=True,
        )

        TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.reset_mock()
        TaskFlowInstance.objects.create.reset_mock()

        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            with mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
                with mock.patch(APIGW_CREATE_AND_START_TASK_PREPARE_AND_START_TASK, TEST_PRE_PARE_AND_START_TASK):
                    with mock.patch.object(
                        create_and_start_task,
                        "resolve_exclude_task_nodes_id",
                        MagicMock(return_value=resolved_exclude_task_nodes_id),
                    ) as resolve_exclude_task_nodes_id:
                        response = self.client.post(
                            path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                            data=json.dumps(
                                {
                                    "name": "name",
                                    "constants": {},
                                    "template_source": "common",
                                    "flow_type": "common",
                                    "template_schemes_id": ["scheme_1"],
                                }
                            ),
                            content_type="application/json",
                            HTTP_BK_APP_CODE=TEST_APP_CODE,
                        )

        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)

        resolve_exclude_task_nodes_id.assert_called_once()
        resolver_args = resolve_exclude_task_nodes_id.call_args[0]
        resolver_kwargs = resolve_exclude_task_nodes_id.call_args[1]
        self.assertEqual(resolver_args[0], tmpl)
        self.assertEqual(resolver_args[1], pipeline_tree)
        self.assertEqual(resolver_args[2]["template_schemes_id"], ["scheme_1"])
        self.assertEqual(resolver_args[2]["exclude_task_nodes_id"], [])
        self.assertEqual(resolver_kwargs, {})

        TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.assert_called_once_with(
            tmpl, {"name": "name", "creator": "", "description": ""}, {}, resolved_exclude_task_nodes_id
        )

    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(return_value=TEST_DATA))
    @mock.patch(TASKINSTANCE_CREATE, MagicMock(return_value=MockTaskFlowInstance(id=TEST_TASKFLOW_ID)))
    @mock.patch(APIGW_CREATE_ADN_STATRT_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_and_start_task__success_with_template_schemes_id_string(self):
        pipeline_tree = {"activities": {"node_1": {}, "node_2": {}}, "constants": {}}
        resolved_exclude_task_nodes_id = ["node_2"]
        pt = MockPipelineTemplate(id=1, name="pt")
        tmpl = MockCommonTemplate(id=1, pipeline_template=pt, pipeline_tree=pipeline_tree)
        proj = MockProject(
            project_id=TEST_PROJECT_ID,
            name=TEST_PROJECT_NAME,
            bk_biz_id=TEST_BIZ_CC_ID,
            from_cmdb=True,
        )

        TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.reset_mock()
        TaskFlowInstance.objects.create.reset_mock()

        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            with mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
                with mock.patch(APIGW_CREATE_AND_START_TASK_PREPARE_AND_START_TASK, TEST_PRE_PARE_AND_START_TASK):
                    with mock.patch.object(
                        create_and_start_task,
                        "resolve_exclude_task_nodes_id",
                        MagicMock(return_value=resolved_exclude_task_nodes_id),
                    ) as resolve_exclude_task_nodes_id:
                        response = self.client.post(
                            path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                            data=json.dumps(
                                {
                                    "name": "name",
                                    "constants": {},
                                    "template_source": "common",
                                    "flow_type": "common",
                                    "template_schemes_id": "scheme_1",
                                }
                            ),
                            content_type="application/json",
                            HTTP_BK_APP_CODE=TEST_APP_CODE,
                        )

        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)

        resolve_exclude_task_nodes_id.assert_called_once()
        resolver_args = resolve_exclude_task_nodes_id.call_args[0]
        resolver_kwargs = resolve_exclude_task_nodes_id.call_args[1]
        self.assertEqual(resolver_args[2]["template_schemes_id"], ["scheme_1"])
        self.assertEqual(resolver_kwargs, {})

    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(return_value=TEST_DATA))
    @mock.patch(TASKINSTANCE_CREATE, MagicMock(return_value=MockTaskFlowInstance(id=TEST_TASKFLOW_ID)))
    @mock.patch(APIGW_CREATE_ADN_STATRT_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_and_start_task__success_with_direct_exclude_task_nodes_id_list(self):
        pt = MockPipelineTemplate(id=1, name="pt")
        tmpl = MockCommonTemplate(id=1, pipeline_template=pt)
        proj = MockProject(
            project_id=TEST_PROJECT_ID,
            name=TEST_PROJECT_NAME,
            bk_biz_id=TEST_BIZ_CC_ID,
            from_cmdb=True,
        )

        TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.reset_mock()
        TaskFlowInstance.objects.create.reset_mock()

        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            with mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
                with mock.patch(APIGW_CREATE_AND_START_TASK_PREPARE_AND_START_TASK, TEST_PRE_PARE_AND_START_TASK):
                    response = self.client.post(
                        path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                        data=json.dumps(
                            {
                                "name": "name",
                                "constants": {},
                                "template_source": "common",
                                "flow_type": "common",
                                "exclude_task_nodes_id": ["node_1"],
                            }
                        ),
                        content_type="application/json",
                        HTTP_BK_APP_CODE=TEST_APP_CODE,
                    )

        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.assert_called_once_with(
            tmpl, {"name": "name", "creator": "", "description": ""}, {}, ["node_1"]
        )

    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(return_value=TEST_DATA))
    @mock.patch(TASKINSTANCE_CREATE, MagicMock(return_value=MockTaskFlowInstance(id=TEST_TASKFLOW_ID)))
    @mock.patch(APIGW_CREATE_ADN_STATRT_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_and_start_task__template_schemes_id_validation_error(self):
        pt = MockPipelineTemplate(id=1, name="pt")
        tmpl = MockCommonTemplate(id=1, pipeline_template=pt)
        proj = MockProject(
            project_id=TEST_PROJECT_ID,
            name=TEST_PROJECT_NAME,
            bk_biz_id=TEST_BIZ_CC_ID,
            from_cmdb=True,
        )

        TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.reset_mock()

        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            with mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
                with mock.patch.object(
                    create_and_start_task,
                    "resolve_exclude_task_nodes_id",
                    MagicMock(side_effect=TaskNodeSelectionValidationError("invalid scheme")),
                ):
                    response = self.client.post(
                        path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                        data=json.dumps(
                            {
                                "name": "name",
                                "constants": {},
                                "template_source": "common",
                                "flow_type": "common",
                                "template_schemes_id": ["missing"],
                            }
                        ),
                        content_type="application/json",
                        HTTP_BK_APP_CODE=TEST_APP_CODE,
                    )

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
        self.assertEqual(data["message"], "invalid scheme")
        TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.assert_not_called()

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
                with mock.patch(APIGW_CREATE_AND_START_TASK_PREPARE_AND_START_TASK, TEST_PRE_PARE_AND_START_TASK):
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
                        create_method=TaskCreateMethod.API.value,
                        flow_type="common",
                        create_info=TEST_APP_CODE,
                        current_flow="execute_task",
                        engine_ver=2,
                        extra_info='{"keys_in_constants_parameter":[]}'
                    )

                    data = json.loads(response.content)

                    self.assertTrue(data["result"], msg=data)
                    self.assertEqual(data["data"], assert_data)

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
    @mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet()))
    @mock.patch(APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock(side_effect=jsonschema.ValidationError("")))
    def test_create_and_start_task__validate_fail(self):
        response = self.client.post(
            path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
            data=json.dumps({"name": "name", "constants": {}, "exclude_task_node_id": "exclude_task_node_id"}),
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
                project_id=TEST_PROJECT_ID,
                name=TEST_PROJECT_NAME,
                bk_biz_id=TEST_BIZ_CC_ID,
                from_cmdb=True,
            )
        ),
    )
    @mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet()))
    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(side_effect=Exception()))
    @mock.patch(APIGW_CREATE_ADN_STATRT_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_and_start_task__create_pipeline_raise(self):
        response = self.client.post(
            path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
            data=json.dumps({"name": "name", "constants": {}, "exclude_task_node_id": "exclude_task_node_id"}),
            content_type="application/json",
            HTPP_BK_APP_CODE=TEST_APP_CODE,
        )

        data = json.loads(response.content)

        self.assertFalse(data["result"])
        self.assertTrue("message" in data)

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID,
                name=TEST_PROJECT_NAME,
                bk_biz_id=TEST_BIZ_CC_ID,
            )
        ),
    )
    @mock.patch(COMMONTEMPLATE_GET, MagicMock(return_value=MockQuerySet()))
    @mock.patch(APIGW_CREATE_ADN_STATRT_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(return_value=MockQuerySet()))
    @mock.patch(TASKINSTANCE_CREATE, MagicMock(side_effect=Exception()))
    def test_create_and_start_task__create_taskinstance_raise(self):
        response = self.client.post(
            path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
            data=json.dumps({"name": "name", "constants": {}, "exclude_task_node_id": "exclude_task_node_id"}),
            content_type="application/json",
            HTTP_BK_APP_CODE=TEST_APP_CODE,
        )
        data = json.loads(response.content)

        self.assertFalse(data["result"])
        self.assertTrue("message" in data)
