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
TEST_PROJECT_ID = "123"
TEST_TEMPLATE_IDS = ["1", "2"]
TEST_ENDPOINT = "https://example.com/webhook"
TEST_EVENTS = ["*"]
TEST_EXTRA_INFO = {}


class ApplyWebhookConfigsAPITest(APITest):
    def url(self):
        return "/apigw/apply_webhook_configs/{project_id}/"

    @mock.patch(PROJECT_GET, MagicMock(return_value=MockProject(project_id=TEST_PROJECT_ID, name="test_project")))
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.WebhookSerializer")
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.WebhookModel.objects.filter")
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.Scope.objects.bulk_create")
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.Subscription.objects.filter")
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.Subscription.objects.bulk_create")
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.WebhookModel.objects.bulk_create")
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.WebhookModel.objects.bulk_update")
    def test_apply_webhook_configs__success(
        self,
        mock_bulk_update,
        mock_bulk_create,
        mock_sub_bulk_create,
        mock_sub_filter,
        mock_scope_bulk_create,
        mock_webhook_filter,
        mock_serializer,
    ):
        """测试成功应用webhook配置"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.validated_data = {
            "endpoint": TEST_ENDPOINT,
            "events": TEST_EVENTS,
            "extra_info": TEST_EXTRA_INFO,
            "template_ids": TEST_TEMPLATE_IDS,
        }
        mock_serializer.return_value = mock_serializer_instance

        mock_webhook_filter.return_value.values.return_value = [
            {"scope_code": "1", "id": 1},
            {"scope_code": "2", "id": 2},
        ]

        # Mock IAM拦截器中的模板验证
        with mock.patch(
            "gcloud.iam_auth.view_interceptors.apigw.apply_webhook_configs.TaskTemplate.objects.filter"
        ) as mock_task_filter:
            mock_task_filter.return_value.values_list.return_value = TEST_TEMPLATE_IDS
            response = self.client.post(
                path=self.url().format(project_id=TEST_PROJECT_ID),
                data=json.dumps(
                    {
                        "endpoint": TEST_ENDPOINT,
                        "events": TEST_EVENTS,
                        "extra_info": TEST_EXTRA_INFO,
                        "template_ids": TEST_TEMPLATE_IDS,
                    }
                ),
                content_type="application/json",
                HTTP_BK_APP_CODE=TEST_APP_CODE,
            )

            data = json.loads(response.content)
            self.assertTrue(data["result"])
            self.assertEqual(data["message"], "success")

    @mock.patch(PROJECT_GET, MagicMock(return_value=MockProject(project_id=TEST_PROJECT_ID, name="test_project")))
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.WebhookSerializer")
    def test_apply_webhook_configs__validate_fail(self, mock_serializer):
        """测试参数验证失败的情况"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = False
        mock_serializer_instance.errors = {"endpoint": ["This field is required."]}
        mock_serializer.return_value = mock_serializer_instance

        response = self.client.post(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data=json.dumps({"events": TEST_EVENTS, "extra_info": TEST_EXTRA_INFO, "template_ids": TEST_TEMPLATE_IDS}),
            content_type="application/json",
            HTTP_BK_APP_CODE=TEST_APP_CODE,
        )

        data = json.loads(response.content)
        self.assertFalse(data["result"])

    @mock.patch(PROJECT_GET, MagicMock(return_value=MockProject(project_id=TEST_PROJECT_ID, name="test_project")))
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.WebhookSerializer")
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.WebhookModel.objects.filter")
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.Scope.objects.bulk_create")
    def test_apply_webhook_configs__database_error(self, mock_scope_bulk_create, mock_webhook_filter, mock_serializer):
        """测试数据库操作异常的情况"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.validated_data = {
            "endpoint": TEST_ENDPOINT,
            "events": TEST_EVENTS,
            "extra_info": TEST_EXTRA_INFO,
            "template_ids": TEST_TEMPLATE_IDS,
        }
        mock_serializer.return_value = mock_serializer_instance

        mock_webhook_filter.return_value.values.return_value = []
        mock_scope_bulk_create.side_effect = Exception("Database connection error")

        response = self.client.post(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data=json.dumps(
                {
                    "endpoint": TEST_ENDPOINT,
                    "events": TEST_EVENTS,
                    "extra_info": TEST_EXTRA_INFO,
                    "template_ids": TEST_TEMPLATE_IDS,
                }
            ),
            content_type="application/json",
            HTTP_BK_APP_CODE=TEST_APP_CODE,
        )

        data = json.loads(response.content)
        self.assertFalse(data["result"])

    @mock.patch(PROJECT_GET, MagicMock(return_value=MockProject(project_id=TEST_PROJECT_ID, name="test_project")))
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.WebhookSerializer")
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.WebhookModel.objects.filter")
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.Scope.objects.bulk_create")
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.Subscription.objects.filter")
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.WebhookModel.objects.bulk_create")
    def test_apply_webhook_configs__transaction_rollback(
        self, mock_bulk_create, mock_sub_filter, mock_scope_bulk_create, mock_webhook_filter, mock_serializer
    ):
        """测试事务回滚的情况"""
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.validated_data = {
            "endpoint": TEST_ENDPOINT,
            "events": TEST_EVENTS,
            "extra_info": TEST_EXTRA_INFO,
            "template_ids": TEST_TEMPLATE_IDS,
        }
        mock_serializer.return_value = mock_serializer_instance

        mock_webhook_filter.return_value.values.return_value = []
        mock_bulk_create.side_effect = Exception("Bulk create failed")

        response = self.client.post(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data=json.dumps(
                {
                    "endpoint": TEST_ENDPOINT,
                    "events": TEST_EVENTS,
                    "extra_info": TEST_EXTRA_INFO,
                    "template_ids": TEST_TEMPLATE_IDS,
                }
            ),
            content_type="application/json",
            HTTP_BK_APP_CODE=TEST_APP_CODE,
        )

        data = json.loads(response.content)
        self.assertFalse(data["result"])
