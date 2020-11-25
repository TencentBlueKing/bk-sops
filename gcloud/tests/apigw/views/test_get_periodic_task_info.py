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


import ujson as json


from gcloud.utils.dates import format_datetime
from gcloud.periodictask.models import PeriodicTask
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest


TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_PERIODIC_TASK_ID = "3"


class GetPeriodicTaskInfoAPITest(APITest):
    def url(self):
        return "/apigw/get_periodic_task_info/{task_id}/{project_id}/"

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    def test_get_periodic_task_info__success(self):
        task = MockPeriodicTask()
        assert_data = {
            "id": task.id,
            "name": task.name,
            "template_id": task.template_id,
            "template_source": "project",
            "creator": task.creator,
            "cron": task.cron,
            "enabled": task.enabled,
            "last_run_at": format_datetime(task.last_run_at),
            "total_run_count": task.total_run_count,
            "form": task.form,
            "pipeline_tree": task.pipeline_tree,
        }

        with mock.patch(PERIODIC_TASK_GET, MagicMock(return_value=task)):
            response = self.client.get(
                path=self.url().format(task_id=TEST_PERIODIC_TASK_ID, project_id=TEST_PROJECT_ID)
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
    def test_get_periodic_task_info__common_template(self):
        task = MockPeriodicTask(template_source="common")
        assert_data = {
            "id": task.id,
            "name": task.name,
            "template_id": task.template_id,
            "template_source": "common",
            "creator": task.creator,
            "cron": task.cron,
            "enabled": task.enabled,
            "last_run_at": format_datetime(task.last_run_at),
            "total_run_count": task.total_run_count,
            "form": task.form,
            "pipeline_tree": task.pipeline_tree,
        }

        with mock.patch(PERIODIC_TASK_GET, MagicMock(return_value=task)):
            response = self.client.get(
                path=self.url().format(task_id=TEST_PERIODIC_TASK_ID, project_id=TEST_PROJECT_ID)
            )

            data = json.loads(response.content)

            self.assertTrue(data["result"], msg=data)
            self.assertEqual(data["data"], assert_data)

    @mock.patch(PERIODIC_TASK_GET, MagicMock(side_effect=PeriodicTask.DoesNotExist))
    def test_periodic_task_info__task_does_not_exist(self):
        response = self.client.get(path=self.url().format(task_id=TEST_PERIODIC_TASK_ID, project_id=TEST_PROJECT_ID))

        data = json.loads(response.content)

        self.assertFalse(data["result"])
        self.assertTrue("message" in data)
