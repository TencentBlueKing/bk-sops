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


from gcloud.periodictask.models import PeriodicTask
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest


TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_PERIODIC_TASK_ID = "3"


class ModifyConstantsForPeriodicTaskAPITest(APITest):
    def url(self):
        return "/apigw/modify_constants_for_periodic_task/{task_id}/{project_id}/"

    def test_modify_constants_for_periodic_task__success(self):
        task = MockPeriodicTask()
        constants = {"k": "v"}
        proj = MockProject(
            project_id=TEST_PROJECT_ID,
            name=TEST_PROJECT_NAME,
            bk_biz_id=TEST_BIZ_CC_ID,
            from_cmdb=True,
        )

        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            with mock.patch(PERIODIC_TASK_GET, MagicMock(return_value=task)):
                response = self.client.post(
                    path=self.url().format(
                        task_id=TEST_PERIODIC_TASK_ID, project_id=TEST_PROJECT_ID
                    ),
                    data=json.dumps({"constants": constants}),
                    content_type="application/json",
                )

                task.modify_constants.assert_called_once_with(constants)

                data = json.loads(response.content)

                self.assertTrue(data["result"], msg=data)
                self.assertEqual(data["data"], task.modify_constants.return_value)

    @mock.patch(PERIODIC_TASK_GET, MagicMock(side_effect=PeriodicTask.DoesNotExist))
    def test_modify_constants_for_periodic_task__task_does_not_exist(self):
        response = self.client.post(
            path=self.url().format(
                task_id=TEST_PERIODIC_TASK_ID, project_id=TEST_PROJECT_ID
            ),
            content_type="application/json",
        )

        data = json.loads(response.content)

        self.assertFalse(data["result"])
        self.assertTrue("message" in data)

    def test_modify_constants_for_periodic_task__modify_constants_raise(self):
        biz = MockBusiness()
        task = MockPeriodicTask()
        task.modify_constants = MagicMock(side_effect=Exception())

        with mock.patch(BUSINESS_GET, MagicMock(return_value=biz)):
            with mock.patch(PERIODIC_TASK_GET, MagicMock(return_value=task)):
                response = self.client.post(
                    path=self.url().format(
                        task_id=TEST_PERIODIC_TASK_ID, project_id=TEST_PROJECT_ID
                    ),
                    content_type="application/json",
                )

                data = json.loads(response.content)

                self.assertFalse(data["result"])
                self.assertTrue("message" in data)
