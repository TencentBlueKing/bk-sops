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
from datetime import datetime
import pytz

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.iam_auth import IAMMeta

from .utils import APITest, TEST_USERNAME


# Mock类定义
class MockClockedTask:
    """Mock ClockedTask类"""

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 1)
        self.project_id = kwargs.get("project_id", 123)
        self.task_id = kwargs.get("task_id", None)
        self.task_name = kwargs.get("task_name", "test_task")
        self.template_id = kwargs.get("template_id", 1)
        self.template_name = kwargs.get("template_name", "test_template")
        self.template_source = kwargs.get("template_source", "project")
        self.clocked_task_id = kwargs.get("clocked_task_id", None)
        self.creator = kwargs.get("creator", "creator")
        self.create_time = kwargs.get("create_time", datetime.now())
        self.editor = kwargs.get("editor", "editor")
        self.edit_time = kwargs.get("edit_time", datetime.now())
        self.plan_start_time = kwargs.get("plan_start_time", datetime.now())
        self.task_params = kwargs.get("task_params", '{\"constants\": {}}')
        self.notify_type = kwargs.get("notify_type", "[]")
        self.notify_receivers = kwargs.get("notify_receivers", "{}")
        self.state = kwargs.get("state", "started")


class MockQuerySet:
    """Mock QuerySet类，支持切片操作"""

    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return iter(self.data)

    def count(self):
        return len(self.data)

    def __getitem__(self, key):
        if isinstance(key, slice):
            # 处理切片操作
            start = key.start if key.start is not None else 0
            stop = key.stop if key.stop is not None else len(self.data)
            step = key.step if key.step is not None else 1
            return self.data[start:stop:step]
        else:
            # 处理索引操作
            return self.data[key]


# Mock常量定义
CLOCKED_TASK_FILTER = "gcloud.clocked_task.models.ClockedTask.objects.filter"

MOCK_GET_FLOW_ALLOWED_ACTIONS = "gcloud.apigw.views.get_clocked_task_list.get_flow_allowed_actions_for_user"

TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_APP_CODE = "app_code"
TEST_CLOCKED_TASK_LIST = [
    {
        "id": 1,
        "project_id": 123,
        "task_name": "test_task_1",
        "template_id": 1,
        "template_name": "test_template",
        "template_source": "project",
        "creator": "creator1",
        "editor": "editor1",
        "state": "started",
        "plan_start_time": datetime(2026, 4, 17, 10, 0, 0, tzinfo=pytz.timezone("Asia/Shanghai")),
        "create_time": datetime(2026, 4, 17, 9, 0, 0, tzinfo=pytz.timezone("Asia/Shanghai")),
        "edit_time": datetime(2026, 4, 17, 9, 30, 0, tzinfo=pytz.timezone("Asia/Shanghai")),
        "task_params": '{\"constants\": {\"key\": \"value\"}}',
        "notify_type": "[]",
        "notify_receivers": "{}",
        "task_id": None,
        "template_source": "project",
        "clocked_task_id": None
    },
    {
        "id": 2,
        "project_id": 123,
        "task_name": "test_task_2",
        "template_id": 2,
        "template_name": "test_template_2",
        "template_source": "project",
        "creator": "creator2",
        "editor": "editor2",
        "state": "finished",
        "plan_start_time": datetime(2026, 4, 17, 11, 0, 0, tzinfo=pytz.timezone("Asia/Shanghai")),
        "create_time": datetime(2026, 4, 17, 9, 30, 0, tzinfo=pytz.timezone("Asia/Shanghai")),
        "edit_time": datetime(2026, 4, 17, 10, 0, 0, tzinfo=pytz.timezone("Asia/Shanghai")),
        "task_params": '{\"constants\": {\"key2\": \"value2\"}}',
        "notify_type": "[]",
        "notify_receivers": "{}",
        "task_id": None,
        "template_source": "project",
        "clocked_task_id": None
    },
]
TEST_AUTH_ACTIONS = {
    1: [IAMMeta.CLOCKED_TASK_VIEW_ACTION, IAMMeta.CLOCKED_TASK_EDIT_ACTION],
    2: [IAMMeta.CLOCKED_TASK_VIEW_ACTION],
}
TEST_TEMPLATE_VIEW_ACTIONS = {
    "1": {IAMMeta.FLOW_VIEW_ACTION: True},
    "2": {IAMMeta.FLOW_VIEW_ACTION: False},
}


class GetClockedTaskListAPITest(APITest):
    def url(self):
        return "/apigw/get_clocked_task_list/{project_id}/"

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
    def test_get_clocked_task_list__success(self):
        """测试正常获取clocked task列表"""
        ct1 = MockClockedTask(**TEST_CLOCKED_TASK_LIST[0])
        ct2 = MockClockedTask(**TEST_CLOCKED_TASK_LIST[1])
        clocked_tasks = MockQuerySet([ct1, ct2])

        assert_data = [
            {
                "id": task["id"],
                "task_parameters": json.loads(task["task_params"]),
                "creator": task["creator"],
                "editor": task["editor"],
                "state": task["state"],
                "plan_start_time": task["plan_start_time"].strftime("%Y-%m-%d %H:%M:%S %z"),
                "create_time": task["create_time"].strftime("%Y-%m-%d %H:%M:%S %z"),
                "edit_time": task["edit_time"].strftime("%Y-%m-%d %H:%M:%S %z"),
                "project_id": task["project_id"],
                "task_id": task["task_id"],
                "task_name": task["task_name"],
                "template_id": task["template_id"],
                "template_name": task["template_name"],
                "template_source": task["template_source"],
                "clocked_task_id": task["clocked_task_id"],
                "auth_actions": TEST_AUTH_ACTIONS[task["id"]]
            }
            for task in TEST_CLOCKED_TASK_LIST
        ]

        with mock.patch(CLOCKED_TASK_FILTER, MagicMock(return_value=clocked_tasks)):
            with mock.patch(
                    "gcloud.apigw.views.get_clocked_task_list.clocked_task_viewset.iam_get_instances_auth_actions",
                    MagicMock(return_value=TEST_AUTH_ACTIONS),
            ):
                with mock.patch(
                        MOCK_GET_FLOW_ALLOWED_ACTIONS, MagicMock(return_value=TEST_TEMPLATE_VIEW_ACTIONS)
                ):
                    response = self.client.get(
                        path=self.url().format(project_id=TEST_PROJECT_ID),
                        HTTP_BK_APP_CODE=TEST_APP_CODE,
                        HTTP_BK_USERNAME=TEST_USERNAME,
                    )

                    data = json.loads(response.content)
                    self.assertTrue(data["result"])
                    self.assertEqual(data["data"], assert_data)
                    self.assertEqual(data["count"], 2)

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
    def test_get_clocked_task_list__invalid_pagination_params(self):
        """测试非法分页参数的错误返回"""
        # 测试offset为负数
        response = self.client.get(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data={"offset": -1},
            HTTP_BK_APP_CODE=TEST_APP_CODE,
            HTTP_BK_USERNAME=TEST_USERNAME,
        )
        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertIn("offset and limit must be greater or equal", data["message"])

        # 测试limit为负数
        response = self.client.get(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data={"limit": -1},
            HTTP_BK_APP_CODE=TEST_APP_CODE,
            HTTP_BK_USERNAME=TEST_USERNAME,
        )
        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertIn("offset and limit must be greater or equal", data["message"])

        # 测试offset和limit都为负数
        response = self.client.get(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data={"offset": -1, "limit": -1},
            HTTP_BK_APP_CODE=TEST_APP_CODE,
            HTTP_BK_USERNAME=TEST_USERNAME,
        )
        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertIn("offset and limit must be greater or equal", data["message"])

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
    def test_get_clocked_task_list__timezone_effective(self):
        """测试expected_timezone生效的断言"""
        ct1 = MockClockedTask(**TEST_CLOCKED_TASK_LIST[0])
        ct2 = MockClockedTask(**TEST_CLOCKED_TASK_LIST[1])
        clocked_tasks = MockQuerySet([ct1, ct2])

        # 目标时区：UTC
        target_timezone = "UTC"

        with mock.patch(CLOCKED_TASK_FILTER, MagicMock(return_value=clocked_tasks)):
            with mock.patch(
                "gcloud.apigw.views.get_clocked_task_list.clocked_task_viewset.iam_get_instances_auth_actions",
                MagicMock(return_value=TEST_AUTH_ACTIONS),
            ):
                with mock.patch(
                    MOCK_GET_FLOW_ALLOWED_ACTIONS, MagicMock(return_value=TEST_TEMPLATE_VIEW_ACTIONS)
                ):
                    response = self.client.get(
                        path=self.url().format(project_id=TEST_PROJECT_ID),
                        data={"expected_timezone": target_timezone},
                        HTTP_BK_APP_CODE=TEST_APP_CODE,
                        HTTP_BK_USERNAME=TEST_USERNAME,
                    )
                    print('测试expected_timezone生效的断言')
                    data = json.loads(response.content)
                    print('data', data)
                    self.assertTrue(data["result"])

                    # 验证时区转换生效
                    for item in data["data"]:
                        # 检查时间字段是否包含UTC时区信息（format_datetime 会在时间和时区间加空格）
                        self.assertIn(" +0000", item["plan_start_time"])
                        self.assertIn(" +0000", item["create_time"])
                        self.assertIn(" +0000", item["edit_time"])
