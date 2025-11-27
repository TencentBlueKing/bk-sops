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

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest

TEST_APP_CODE = "app_code"
TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"


class ApplyWebhookConfigsAPITest(APITest):
    def url(self):
        return "/apigw/apply_webhook_configs/{project_id}/"

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
    def test_apply_webhook_configs__success(self):
        """测试成功应用webhook配置"""
        template_ids = [1, 2]
        webhook_data = {
            "endpoint": "https://example.com/webhook",
            "events": ["*"],
            "extra_info": {},
            "template_ids": template_ids,
        }

        mock_queryset = MagicMock()
        mock_queryset.values_list.return_value = [1, 2]

        mock_filter = MagicMock(return_value=mock_queryset)

        with patch(
            "gcloud.iam_auth.view_interceptors.apigw.apply_webhook_configs.TaskTemplate.objects.filter", mock_filter
        ):
            response = self.client.post(
                path=self.url().format(project_id=TEST_PROJECT_ID),
                data=json.dumps(webhook_data),
                content_type="application/json",
                HTTP_BK_APP_CODE=TEST_APP_CODE,
            )

        data = json.loads(response.content)
        self.assertTrue(data["result"])
        self.assertEqual(data["message"], "success")
        self.assertEqual(data["code"], 0)

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
    def test_apply_webhook_configs__validation_fail(self):
        """测试参数验证失败（如无效 endpoint、空 events、空 template_ids）"""
        invalid_data = {"endpoint": "not-a-valid-url", "events": [], "template_ids": []}

        response = self.client.post(
            path=self.url().format(project_id=TEST_PROJECT_ID),
            data=json.dumps(invalid_data),
            content_type="application/json",
            HTTP_BK_APP_CODE=TEST_APP_CODE,
        )

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertTrue("message" in data)

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
    def test_apply_webhook_configs__subscription_apply_fail(self):
        """测试订阅事件失败"""
        template_ids = [1]
        webhook_data = {
            "endpoint": "https://example.com/webhook",
            "events": ["template_create"],
            "extra_info": {},
            "template_ids": template_ids,
        }

        mock_queryset = MagicMock()
        mock_queryset.values_list.return_value = [1]
        mock_filter = MagicMock(return_value=mock_queryset)

        with patch(
            "gcloud.iam_auth.view_interceptors.apigw.apply_webhook_configs.TaskTemplate.objects.filter", mock_filter
        ):
            response = self.client.post(
                path=self.url().format(project_id=TEST_PROJECT_ID),
                data=json.dumps(webhook_data),
                content_type="application/json",
                HTTP_BK_APP_CODE=TEST_APP_CODE,
            )

            data = json.loads(response.content)
            self.assertFalse(data["result"])
            self.assertFalse("fail: Subscription apply failed" in data["message"])

    def test_apply_webhook_configs__project_not_found(self):
        """测试项目不存在"""

        def mock_filter(**kwargs):
            if "id__in" in kwargs and "project_id" in kwargs:
                requested_ids = kwargs["id__in"]
                mock_queryset = MagicMock()
                mock_queryset.values_list = MagicMock(return_value=list(requested_ids))
                return mock_queryset
            return MagicMock()

        filter_mock = MagicMock(side_effect=mock_filter)

        with mock.patch(PROJECT_GET, MagicMock(side_effect=Exception("Project not found"))):
            with mock.patch(
                "gcloud.iam_auth.view_interceptors.apigw.apply_webhook_configs.TaskTemplate.objects.filter", filter_mock
            ):
                webhook_data = {
                    "endpoint": "https://example.com/webhook",
                    "events": ["*"],
                    "extra_info": {},
                    "template_ids": [1],
                }

                response = self.client.post(
                    path=self.url().format(project_id=TEST_PROJECT_ID),
                    data=json.dumps(webhook_data),
                    content_type="application/json",
                    HTTP_BK_APP_CODE=TEST_APP_CODE,
                )

                data = json.loads(response.content)
                self.assertFalse(data["result"])
                self.assertTrue("message" in data)
