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


from gcloud.core.utils import format_datetime
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.commons.template.models import CommonTemplate
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest

TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_TEMPLATE_ID = "1"


class GetTemplateInfoAPITest(APITest):
    def url(self):
        return "/apigw/get_template_info/{template_id}/{project_id}/"

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
    def test_get_template_info__for_project_template(self):
        pt1 = MockPipelineTemplate(id=1, name="pt1")

        tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)

        with mock.patch(
            TASKTEMPLATE_SELECT_RELATE,
            MagicMock(return_value=MockQuerySet(get_result=tmpl)),
        ):
            pipeline_tree = copy.deepcopy(tmpl.pipeline_tree)
            assert_data = {
                "id": tmpl.id,
                "name": tmpl.pipeline_template.name,
                "creator": tmpl.pipeline_template.creator,
                "create_time": format_datetime(tmpl.pipeline_template.create_time),
                "editor": tmpl.pipeline_template.editor,
                "edit_time": format_datetime(tmpl.pipeline_template.edit_time),
                "category": tmpl.category,
                "project_id": TEST_PROJECT_ID,
                "project_name": TEST_PROJECT_NAME,
                "bk_biz_id": TEST_BIZ_CC_ID,
                "bk_biz_name": TEST_PROJECT_NAME,
                "pipeline_tree": pipeline_tree,
            }

            response = self.client.get(
                path=self.url().format(
                    template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID
                )
            )

            data = json.loads(response.content)

            self.assertTrue(data["result"], msg=data)
            self.assertEqual(assert_data, data["data"])

    @mock.patch(
        TASKTEMPLATE_SELECT_RELATE,
        MagicMock(return_value=MockQuerySet(get_raise=TaskTemplate.DoesNotExist())),
    )
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
    def test_get_template_info__for_project_template_does_not_exists(self):
        response = self.client.get(
            path=self.url().format(
                template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID
            )
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
    def test_get_template_info__for_common_template(self):
        pt1 = MockPipelineTemplate(id=1, name="pt1")

        tmpl = MockCommonTemplate(id=1, pipeline_template=pt1)

        with mock.patch(
            COMMONTEMPLATE_SELECT_RELATE,
            MagicMock(return_value=MockQuerySet(get_result=tmpl)),
        ):
            pipeline_tree = copy.deepcopy(tmpl.pipeline_tree)
            assert_data = {
                "id": tmpl.id,
                "name": tmpl.pipeline_template.name,
                "creator": tmpl.pipeline_template.creator,
                "create_time": format_datetime(tmpl.pipeline_template.create_time),
                "editor": tmpl.pipeline_template.editor,
                "edit_time": format_datetime(tmpl.pipeline_template.edit_time),
                "category": tmpl.category,
                "project_id": TEST_PROJECT_ID,
                "project_name": TEST_PROJECT_NAME,
                "bk_biz_id": TEST_BIZ_CC_ID,
                "bk_biz_name": TEST_PROJECT_NAME,
                "pipeline_tree": pipeline_tree,
            }

            response = self.client.get(
                path=self.url().format(
                    template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID
                ),
                data={"template_source": "common"},
            )

            data = json.loads(response.content)

            self.assertTrue(data["result"], msg=data)
            self.assertEqual(assert_data, data["data"])

    @mock.patch(
        COMMONTEMPLATE_SELECT_RELATE,
        MagicMock(return_value=MockQuerySet(get_raise=CommonTemplate.DoesNotExist())),
    )
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
    def test_get_template_info__for_common_template_does_not_exists(self):
        response = self.client.get(
            path=self.url().format(
                template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID
            ),
            data={"template_source": "common"},
        )

        data = json.loads(response.content)

        self.assertFalse(data["result"])
        self.assertTrue("message" in data)
