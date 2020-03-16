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


import ujson as json


from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud import err_code
from gcloud.apigw.views import preview_task_tree

from .utils import APITest

TEST_PROJECT_ID = "1"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "2"
TEST_TASK_TEMPLATE_ID = "3"
PREVIEW_TEMPLATE_TREE_RETURN = "PREVIEW_TEMPLATE_TREE_RETURN"


class PreviewTaskTreeAPITest(APITest):
    def url(self):
        return "/apigw/preview_task_tree/{project_id}/{template_id}/"

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
    def test_preview_task_tree__invalid_json_req(self):
        response = self.client.post(
            path=self.url().format(
                project_id=TEST_PROJECT_ID, template_id=TEST_TASK_TEMPLATE_ID
            ),
            data="invalid json",
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
    def test_preview_task_tree__invalid_exclude_task_node_id(self):
        response = self.client.post(
            path=self.url().format(
                project_id=TEST_PROJECT_ID, template_id=TEST_TASK_TEMPLATE_ID
            ),
            data=json.dumps({"exclude_task_nodes_id": "invalid array"}),
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
        TASKTEMPLATE_GET,
        MagicMock(return_value=MockTaskTemplate(id=TEST_TASK_TEMPLATE_ID)),
    )
    @patch(
        APIGW_PREVIEW_TASK_TREE_PREVIEW_TEMPLATE_TREE,
        MagicMock(side_effect=Exception()),
    )
    def test_preview_task_tree__preview_template_tree_raise(self):
        response = self.client.post(
            path=self.url().format(
                project_id=TEST_PROJECT_ID, template_id=TEST_TASK_TEMPLATE_ID
            ),
            data=json.dumps({"exclude_task_nodes_id": []}),
            content_type="application/json",
        )

        data = json.loads(response.content)

        self.assertFalse(data["result"])
        self.assertTrue("message" in data)
        self.assertEqual(data["code"], err_code.UNKNOW_ERROR.code)

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
        TASKTEMPLATE_GET,
        MagicMock(return_value=MockTaskTemplate(id=TEST_TASK_TEMPLATE_ID)),
    )
    @patch(
        APIGW_PREVIEW_TASK_TREE_PREVIEW_TEMPLATE_TREE,
        MagicMock(return_value=PREVIEW_TEMPLATE_TREE_RETURN),
    )
    def test_preview_task_tree__success(self):
        response = self.client.post(
            path=self.url().format(
                project_id=TEST_PROJECT_ID, template_id=TEST_TASK_TEMPLATE_ID
            ),
            data=json.dumps({"exclude_task_nodes_id": []}),
            content_type="application/json",
        )

        data = json.loads(response.content)

        self.assertTrue(data["result"])
        self.assertEqual(data["code"], err_code.SUCCESS.code)
        self.assertEqual(data["data"], PREVIEW_TEMPLATE_TREE_RETURN)

        preview_task_tree.preview_template_tree.assert_called_once_with(
            TEST_PROJECT_ID, preview_task_tree.PROJECT, TEST_TASK_TEMPLATE_ID, None, []
        )
