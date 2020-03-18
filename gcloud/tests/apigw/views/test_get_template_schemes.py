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

from pipeline.utils.collections import FancyDict

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud import err_code

from .utils import APITest

TEST_PROJECT_ID = "1"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "2"
TEST_TASK_TEMPLATE_ID = "3"
TEST_PIPELINE_TEMPLATE_ID = "4"


class GetTemplateSchemesAPITest(APITest):
    def url(self):
        return "/apigw/get_template_schemes/{project_id}/{template_id}/"

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
        MagicMock(
            return_value=FancyDict(
                pipeline_template=FancyDict(id=TEST_PIPELINE_TEMPLATE_ID)
            )
        ),
    )
    @patch(
        TEMPLATESCHEME_FILTER,
        MagicMock(
            return_value=[
                FancyDict(unique_id="id1", name="name1", data="data1"),
                FancyDict(unique_id="id2", name="name2", data="data2"),
            ]
        ),
    )
    def test_get_template_schemes(self):
        response = self.client.get(
            path=self.url().format(
                project_id=TEST_PROJECT_ID, template_id=TEST_TASK_TEMPLATE_ID
            )
        )

        data = json.loads(response.content)

        self.assertTrue(data["result"])
        self.assertEqual(data["code"], err_code.SUCCESS.code)
        self.assertEqual(
            data["data"],
            [
                {"id": "id1", "name": "name1", "data": "data1"},
                {"id": "id2", "name": "name2", "data": "data2"},
            ],
        )
