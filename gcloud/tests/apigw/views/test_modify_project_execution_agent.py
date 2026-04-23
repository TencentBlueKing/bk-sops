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

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest

TEST_APP_CODE = "app_code"
TEST_USERNAME = "tester"
# MockProject 不做类型转换，保持与真实 request.project.id 一致用 int
TEST_PROJECT_ID = 123
TEST_PROJECT_NAME = "test_project"

# view 实际模块路径
MODIFY_VIEW_MODULE = "gcloud.apigw.views.modify_project_executor_proxy"


class ModifyProjectExecutorProxyAPITest(APITest):
    def url(self):
        return "/apigw/modify_project_executor_proxy/{project_id}/"

    @mock.patch(PROJECT_GET, MagicMock(return_value=MockProject(project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME)))
    @mock.patch(MODIFY_VIEW_MODULE + ".ProjectConfig.objects.get_or_create")
    @mock.patch(MODIFY_VIEW_MODULE + ".ProjectExecutorProxySerializer")
    def test_modify_project_executor_proxy__success(self, mock_serializer_cls, mock_get_or_create):
        """正常请求：参数合法，serializer 保存成功，返回 project_id 及预期字段。"""
        project_config = MagicMock()
        mock_get_or_create.return_value = (project_config, False)

        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.validated_data = {
            "executor_proxy": TEST_USERNAME,
            "executor_proxy_exempts": "user1,user2",
        }
        mock_serializer_cls.return_value = mock_serializer

        response = self.client.post(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data=json.dumps(
                {
                    "executor_proxy": TEST_USERNAME,
                    "executor_proxy_exempts": "user1,user2",
                }
            ),
            content_type="application/json",
            HTTP_BK_USERNAME=TEST_USERNAME,
            HTTP_BK_APP_CODE=TEST_APP_CODE,
        )

        mock_get_or_create.assert_called_once_with(project_id=TEST_PROJECT_ID)
        mock_serializer.save.assert_called_once()

        data = json.loads(response.content)
        self.assertTrue(data["result"])
        self.assertEqual(data["data"]["executor_proxy"], TEST_USERNAME)
        self.assertEqual(data["data"]["executor_proxy_exempts"], "user1,user2")
        self.assertEqual(data["data"]["project_id"], TEST_PROJECT_ID)

    @mock.patch(PROJECT_GET, MagicMock(return_value=MockProject(project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME)))
    @mock.patch(MODIFY_VIEW_MODULE + ".ProjectConfig.objects.get_or_create")
    @mock.patch(MODIFY_VIEW_MODULE + ".ProjectExecutorProxySerializer")
    def test_modify_project_executor_proxy__only_expected_fields_updated(
        self, mock_serializer_cls, mock_get_or_create
    ):
        """
        只允许更新预期字段：即使请求体带了 custom_display_configs / 其它未知字段，
        serializer 也只会以声明的 fields 处理，返回结果中不会出现这些额外字段。
        """
        mock_get_or_create.return_value = (MagicMock(), False)

        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.validated_data = {
            "executor_proxy": TEST_USERNAME,
            "executor_proxy_exempts": "",
        }
        mock_serializer_cls.return_value = mock_serializer

        response = self.client.post(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data=json.dumps(
                {
                    "executor_proxy": TEST_USERNAME,
                    "executor_proxy_exempts": "",
                    # 以下字段应被序列化器忽略
                    "custom_display_configs": {"hack": True},
                    "unknown_field": "x",
                }
            ),
            content_type="application/json",
            HTTP_BK_USERNAME=TEST_USERNAME,
            HTTP_BK_APP_CODE=TEST_APP_CODE,
        )

        data = json.loads(response.content)
        self.assertTrue(data["result"])
        self.assertEqual(
            set(data["data"].keys()),
            {"executor_proxy", "executor_proxy_exempts", "project_id"},
        )
        self.assertNotIn("custom_display_configs", data["data"])
        self.assertNotIn("unknown_field", data["data"])

    @mock.patch(PROJECT_GET, MagicMock(return_value=MockProject(project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME)))
    @mock.patch(MODIFY_VIEW_MODULE + ".ProjectConfig.objects.get_or_create")
    def test_modify_project_executor_proxy__empty_body_required_fail(self, mock_get_or_create):
        """空请求体：两个字段均为 required=True，应两者都报 required 错误，且不保存。"""
        project_config = MagicMock()
        mock_get_or_create.return_value = (project_config, False)

        response = self.client.post(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data=json.dumps({}),
            content_type="application/json",
            HTTP_BK_USERNAME=TEST_USERNAME,
            HTTP_BK_APP_CODE=TEST_APP_CODE,
        )

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertIn("executor_proxy", data["message"])
        self.assertIn("executor_proxy_exempts", data["message"])
        project_config.save.assert_not_called()

    @mock.patch(PROJECT_GET, MagicMock(return_value=MockProject(project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME)))
    @mock.patch(MODIFY_VIEW_MODULE + ".ProjectConfig.objects.get_or_create")
    def test_modify_project_executor_proxy__only_one_field_required_fail(self, mock_get_or_create):
        """只传其中一个字段：缺失的那个应报 required 错误，且不保存。"""
        project_config = MagicMock()
        mock_get_or_create.return_value = (project_config, False)

        # 只传 executor_proxy，缺 executor_proxy_exempts
        response = self.client.post(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data=json.dumps({"executor_proxy": TEST_USERNAME}),
            content_type="application/json",
            HTTP_BK_USERNAME=TEST_USERNAME,
            HTTP_BK_APP_CODE=TEST_APP_CODE,
        )

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertIn("executor_proxy_exempts", data["message"])
        self.assertNotIn("executor_proxy", data["message"])
        project_config.save.assert_not_called()
