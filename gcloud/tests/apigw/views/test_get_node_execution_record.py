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
from datetime import datetime

from django.conf import settings

from gcloud import err_code
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest

TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_TEMPLATE_ID = "1"
TEST_TEMPLATE_NODE_ID = "node123"


class _NodeExecutionRecordQuerySet(object):
    def __init__(self, rows):
        self.rows = rows
        self.count_called = False
        self.sliced_limits = []

    def order_by(self, *args):
        return self

    def values(self, *args):
        return self

    def count(self):
        self.count_called = True
        return len(self.rows)

    def __getitem__(self, item):
        self.sliced_limits.append((item.start, item.stop))
        return self.rows[item]


class GetNodeExecutionRecordTest(APITest):
    def url(self):
        return "/apigw/get_node_execution_record/{template_id}/{project_id}/"

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
    def test_get_node_execution_record_success(self):
        rows = [
            {"archived_time": datetime(2026, 1, 1, 10, 0, 0), "elapsed_time": 10},
            {"archived_time": datetime(2026, 1, 1, 10, 1, 0), "elapsed_time": 12},
        ]
        queryset = _NodeExecutionRecordQuerySet(rows)

        with mock.patch(TASKFLOWEXECUTEDNODE_STATISTICS_FILTER, MagicMock(return_value=queryset)):
            response = self.client.get(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data={"template_node_id": TEST_TEMPLATE_NODE_ID},
            )

            data = json.loads(response.content)
            self.assertTrue(data["result"])
            self.assertEqual(data["data"]["total"], 2)
            self.assertEqual(len(data["data"]["execution_time"]), 2)
            self.assertEqual(queryset.sliced_limits, [(None, settings.MAX_RECORDED_NODE_EXECUTION_TIMES)])

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
    def test_get_node_execution_record_without_template_node_id(self):
        with mock.patch(TASKFLOWEXECUTEDNODE_STATISTICS_FILTER, MagicMock()):
            response = self.client.get(path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID))

            data = json.loads(response.content)
            self.assertFalse(data["result"])
            self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
