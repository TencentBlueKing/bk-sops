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


import unittest

import ujson as json

from gcloud.apigw.views.get_task_list import TASK_ACTIONS, _fetch_ordered_task_details_by_id_queryset
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import TEST_USERNAME, APITest

MOCK_FORMAT_TASK_LIST_DATA = "gcloud.apigw.views.get_task_list.format_task_list_data"
MOCK_GET_TASK_ALLOWED_ACTIONS = "gcloud.apigw.views.get_task_list.get_task_allowed_actions_for_user"
MOCK_PAGINATE_LIST_DATA = "gcloud.apigw.views.get_task_list.paginate_list_data"
MOCK_FETCH_ORDERED_TASK_DETAILS = "gcloud.apigw.views.get_task_list._fetch_ordered_task_details_by_id_queryset"
MOCK_TASKFLOW_FILTER = "gcloud.apigw.views.get_task_list.TaskFlowInstance.objects.filter"

TEST_PROJECT_ID = "123"
TEST_TENANT_ID = "system"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
SUCCESS_CODE = 0
TEST_APP_CODE = "test_code"
TEST_TASK_LIST = [{"id": "1"}, {"id": "2"}]
TEST_TASK_ID_LIST = [1, 2]
TEST_ALLOWED_ACTIONS = {
    "1": {"TEST_ACTION": True},
    "2": {"TEST_ACTION": True},
}
TEST_TASKS = [MagicMock(id=1), MagicMock(id=2)]
TEST_TASK_IDS_QUERYSET = [1, 2]
TEST_COUNT = 2


class GetTaskListAPITest(APITest):
    def url(self):
        return "/apigw/get_task_list/{project_id}/"

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
    @mock.patch(TASKINSTANCE_GET, MagicMock(return_value=MockQuerySet()))
    def test_get_task_list__success(self):
        id_queryset = MagicMock()
        task_queryset = MagicMock()
        task_queryset.values_list.return_value = id_queryset
        with mock.patch(MOCK_TASKFLOW_FILTER, MagicMock(return_value=task_queryset)):
            with mock.patch(
                MOCK_PAGINATE_LIST_DATA, MagicMock(return_value=(TEST_TASK_IDS_QUERYSET, TEST_COUNT))
            ) as mocked_paginate:
                with mock.patch(
                    MOCK_FETCH_ORDERED_TASK_DETAILS, MagicMock(return_value=TEST_TASKS)
                ) as mocked_fetch_tasks:
                    with mock.patch(
                        MOCK_FORMAT_TASK_LIST_DATA, MagicMock(return_value=(TEST_TASK_LIST, TEST_TASK_ID_LIST))
                    ) as mocked_format_task_list_data:
                        with mock.patch(
                            MOCK_GET_TASK_ALLOWED_ACTIONS, MagicMock(return_value=TEST_ALLOWED_ACTIONS)
                        ) as mocked_get_task_allowed_data:
                            response = self.client.get(
                                path=self.url().format(project_id=TEST_PROJECT_ID),
                                data={"is_started": "true", "is_finished": "false"},
                                HTTP_BK_APP_CODE=TEST_APP_CODE,
                                HTTP_BK_USERNAME=TEST_USERNAME,
                            )

                            task_queryset.values_list.assert_called_once_with("id", flat=True)
                            self.assertIs(mocked_paginate.call_args[0][1], id_queryset)
                            mocked_fetch_tasks.assert_called_once_with(TEST_TASK_IDS_QUERYSET)
                            mocked_format_task_list_data.assert_called_once()
                            mocked_get_task_allowed_data.assert_called_once_with(
                                TEST_USERNAME, TASK_ACTIONS, TEST_TASK_ID_LIST, TEST_TENANT_ID
                            )

                            assert_data = [
                                {"id": "1", "auth_actions": ["TEST_ACTION"]},
                                {"id": "2", "auth_actions": ["TEST_ACTION"]},
                            ]

                            response = json.loads(response.content)

                            self.assertTrue(response["result"])
                            self.assertEqual(response["data"], assert_data)
                            self.assertEqual(response["count"], TEST_COUNT)
                            self.assertEqual(response["code"], SUCCESS_CODE)


class MockTask:
    def __init__(self, task_id):
        self.id = task_id


class FetchOrderedTaskDetailsTest(unittest.TestCase):
    def test_fetch_ordered_task_details_by_id_queryset__preserve_page_order(self):
        task_ids = [3, 1, 2]
        task_1 = MockTask(1)
        task_2 = MockTask(2)
        task_3 = MockTask(3)
        detail_queryset = MagicMock()
        detail_queryset.filter.return_value = [task_1, task_2, task_3]

        with mock.patch("gcloud.apigw.views.get_task_list.TaskFlowInstance.objects.select_related") as select_related:
            select_related.return_value = detail_queryset

            tasks = _fetch_ordered_task_details_by_id_queryset(task_ids)

        select_related.assert_called_once_with("pipeline_instance")
        detail_queryset.filter.assert_called_once_with(id__in=task_ids)
        self.assertEqual(tasks, [task_3, task_1, task_2])

    def test_fetch_ordered_task_details_by_id_queryset__empty_page(self):
        with mock.patch("gcloud.apigw.views.get_task_list.TaskFlowInstance.objects.select_related") as select_related:
            tasks = _fetch_ordered_task_details_by_id_queryset([])

        select_related.assert_not_called()
        self.assertEqual(tasks, [])
