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

from gcloud.contrib.analysis.analyse_items import task_flow_instance

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest


TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_DATA = "data"


class QueryTaskCountAPITest(APITest):
    def url(self):
        return "/apigw/query_task_count/{project_id}/"

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
    @mock.patch(
        TASKINSTANCE_EXTEN_CLASSIFIED_COUNT, MagicMock(return_value=(True, TEST_DATA))
    )
    def test_query_task_count__success(self):
        response = self.client.post(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data=json.dumps({"group_by": "category"}),
            content_type="application/json",
        )

        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        self.assertEqual(data["data"], TEST_DATA)

    def test_query_task_count__conditions_is_not_dict(self):
        response = self.client.post(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data=json.dumps({"conditions": []}),
            content_type="application/json",
        )

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertTrue("message" in data)

    def test_query_task_count__group_by_is_not_valid(self):
        response = self.client.post(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data=json.dumps({"group_by": "invalid_value"}),
            content_type="application/json",
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
    @mock.patch(
        TASKINSTANCE_EXTEN_CLASSIFIED_COUNT, MagicMock(return_value=(False, ""))
    )
    def test_query_task_count__dispatch_fail(self):
        response = self.client.post(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data=json.dumps({"group_by": "category"}),
            content_type="application/json",
        )

        task_flow_instance.dispatch.assert_called_once_with(
            "category", {"project_id": TEST_BIZ_CC_ID, "is_deleted": False}
        )
        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertTrue("message" in data)
