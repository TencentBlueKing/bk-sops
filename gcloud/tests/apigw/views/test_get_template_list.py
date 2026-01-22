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

from gcloud.utils.dates import format_datetime
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest, TEST_USERNAME


MOCK_GET_FLOW_ALLOWED_ACTIONS = "gcloud.apigw.views.get_template_list.get_flow_allowed_actions_for_user"


TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_APP_CODE = "test_code"
TEST_TASK_LIST = [{"id": "1"}, {"id": "2"}]
TEST_TASK_ID_LIST = [1, 2]
TEST_ALLOWED_ACTIONS = {
    "1": {"TEST_ACTION": True},
    "2": {"TEST_ACTION": True},
}


class GetTemplateListAPITest(APITest):
    def url(self):
        return "/apigw/get_template_list/{project_id}/"

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
    def test_get_template_list__for_project_template(self):
        pt1 = MockPipelineTemplate(id=1, name="pt1")
        pt2 = MockPipelineTemplate(id=2, name="pt2")

        task_tmpl1 = MockTaskTemplate(id=1, pipeline_template=pt1)
        task_tmpl2 = MockTaskTemplate(id=2, pipeline_template=pt2)

        task_templates = [task_tmpl1, task_tmpl2]

        with patch(
            TASKTEMPLATE_SELECT_RELATE,
            MagicMock(return_value=MockQuerySet(filter_result=task_templates)),
        ):
            with patch(MOCK_GET_FLOW_ALLOWED_ACTIONS, MagicMock(return_value=TEST_ALLOWED_ACTIONS)):
                assert_data = [
                    {
                        "id": tmpl.id,
                        "name": tmpl.pipeline_template.name,
                        "creator": tmpl.pipeline_template.creator,
                        "create_time": format_datetime(tmpl.pipeline_template.create_time),
                        "editor": tmpl.pipeline_template.editor,
                        "edit_time": format_datetime(tmpl.pipeline_template.edit_time),
                        "category": tmpl.category,
                        "project_id": TEST_PROJECT_ID,
                        "project_name": TEST_PROJECT_NAME,
                        "bk_biz_id": TEST_PROJECT_ID,
                        "bk_biz_name": TEST_PROJECT_NAME,
                        "auth_actions": ["TEST_ACTION"],
                        "description": tmpl.pipeline_template.description,
                    }
                    for tmpl in task_templates
                ]

                response = self.client.get(
                    path=self.url().format(project_id=TEST_PROJECT_ID),
                    HTTP_BK_APP_CODE=TEST_APP_CODE,
                    HTTP_BK_USERNAME=TEST_USERNAME,
                )

                self.assertEqual(response.status_code, 200)

                data = json.loads(response.content)

                self.assertTrue(data["result"], msg=data)
                self.assertEqual(data["data"], assert_data)

            with patch(
                TASKTEMPLATE_SELECT_RELATE,
                MagicMock(return_value=MockQuerySet(filter_result=[])),
            ):
                assert_data = []

                response = self.client.get(
                    path=self.url().format(project_id=TEST_PROJECT_ID),
                    HTTP_BK_APP_CODE=TEST_APP_CODE,
                    HTTP_BK_USERNAME=TEST_USERNAME,
                )

                data = json.loads(response.content)

                self.assertTrue(data["result"], msg=data)
                self.assertEqual(data["data"], assert_data)

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
    def test_get_template_list__for_common_template(self):
        pt1 = MockPipelineTemplate(id=1, name="pt1")
        pt2 = MockPipelineTemplate(id=2, name="pt2")

        task_tmpl1 = MockCommonTemplate(id=1, pipeline_template=pt1)
        task_tmpl2 = MockCommonTemplate(id=2, pipeline_template=pt2)

        task_templates = [task_tmpl1, task_tmpl2]

        with patch(
            COMMONTEMPLATE_SELECT_RELATE,
            MagicMock(return_value=MockQuerySet(filter_result=task_templates)),
        ):
            assert_data = [
                {
                    "id": tmpl.id,
                    "name": tmpl.pipeline_template.name,
                    "creator": tmpl.pipeline_template.creator,
                    "create_time": format_datetime(tmpl.pipeline_template.create_time),
                    "editor": tmpl.pipeline_template.editor,
                    "edit_time": format_datetime(tmpl.pipeline_template.edit_time),
                    "category": tmpl.category,
                    "project_id": TEST_PROJECT_ID,
                    "project_name": TEST_PROJECT_NAME,
                    "bk_biz_id": TEST_PROJECT_ID,
                    "bk_biz_name": TEST_PROJECT_NAME,
                    "auth_actions": [],
                    "description": tmpl.pipeline_template.description,
                }
                for tmpl in task_templates
            ]

            response = self.client.get(
                path=self.url().format(project_id=TEST_PROJECT_ID),
                data={"template_source": "common"},
                HTTP_BK_APP_CODE=TEST_APP_CODE,
                HTTP_BK_USERNAME=TEST_USERNAME,
            )

            self.assertEqual(response.status_code, 200)

            data = json.loads(response.content)

            self.assertTrue(data["result"], msg=data)
            self.assertEqual(data["data"], assert_data)

        with patch(
            COMMONTEMPLATE_SELECT_RELATE,
            MagicMock(return_value=MockQuerySet(filter_result=[])),
        ):
            assert_data = []

            response = self.client.get(
                path=self.url().format(project_id=TEST_PROJECT_ID),
                data={"template_source": "common"},
                HTTP_BK_APP_CODE=TEST_APP_CODE,
                HTTP_BK_USERNAME=TEST_USERNAME,
            )

            data = json.loads(response.content)

            self.assertTrue(data["result"], msg=data)
            self.assertEqual(data["data"], assert_data)
