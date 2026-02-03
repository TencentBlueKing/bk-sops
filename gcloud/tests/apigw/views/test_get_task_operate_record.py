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
from gcloud.contrib.operate_record.constants import OperateSource, OperateType
from gcloud.contrib.operate_record.models import TaskOperateRecord
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest

TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_TASK_ID = "123"


class GetTaskOperateRecordTest(APITest):
    def setUp(self):
        super().setUp()
        self.test_data = {
            "instance_id": TEST_TASK_ID,
            "project_id": TEST_PROJECT_ID,
            "operator": "admin",
            "operate_type": "start",
            "operate_source": "app",
            "operate_date": datetime.now(),
            "node_id": "node123",
            "extra_info": {},
        }
        self.task_operate_record = TaskOperateRecord.objects.create(**self.test_data)

    def tearDown(self):
        super().tearDown()
        TaskOperateRecord.objects.all().delete()

    def url(self):
        return "/apigw/get_task_operate_record/{task_id}/{project_id}/"

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
    def test_get_task_operate_record_success(self):
        mock_filter = TaskOperateRecord.objects.filter(pk=self.task_operate_record.pk)

        with mock.patch(TASK_OPERATE_RECORD_FILTER, MagicMock(return_value=mock_filter)):
            response = self.client.get(path=self.url().format(task_id=TEST_TASK_ID, project_id=TEST_PROJECT_ID))

            data = json.loads(response.content)
            self.assertTrue(data["result"])
            self.assertEqual(OperateType[self.test_data["operate_type"]].value, data["data"][0]["operate_type_name"])
            self.assertEqual(
                OperateSource[self.test_data["operate_source"]].value, data["data"][0]["operate_source_name"]
            )
