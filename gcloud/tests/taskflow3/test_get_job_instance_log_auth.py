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

from types import SimpleNamespace
from unittest import TestCase, mock

import ujson as json
from iam.exceptions import RawAuthFailedException

from gcloud import err_code
from gcloud.core.models import Project
from gcloud.iam_auth import IAMMeta
from gcloud.taskflow3.apis.django import api


def _build_request(username="tester", job_instance_id="100"):
    return SimpleNamespace(
        method="GET",
        user=SimpleNamespace(username=username),
        GET={"job_instance_id": job_instance_id, "bk_scope_type": "biz"},
        META={},
    )


class GetJobInstanceLogAuthTestCase(TestCase):
    """``get_job_instance_log`` 现在要求调用方在 bk-sops 对应项目内具备
    ``PROJECT_VIEW_ACTION``，避免 BAC：拥有其它产品权限但与 bk-sops 项目无关的用户
    借助本接口跨业务获取作业平台日志。"""

    @mock.patch("gcloud.taskflow3.apis.django.api.Project.objects.get")
    def test_project_missing_in_bksops_returns_content_not_exist(self, mocked_project_get):
        mocked_project_get.side_effect = Project.DoesNotExist
        request = _build_request()

        response = api.get_job_instance_log(request, biz_cc_id="123")

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.CONTENT_NOT_EXIST.code)

    @mock.patch("gcloud.taskflow3.apis.django.api.get_client_by_user")
    @mock.patch("gcloud.taskflow3.apis.django.api.res_factory.resources_for_project")
    @mock.patch("gcloud.taskflow3.apis.django.api.allow_or_raise_auth_failed")
    @mock.patch("gcloud.taskflow3.apis.django.api.Project.objects.get")
    def test_iam_called_with_internal_project_id_not_bk_biz_id(
        self,
        mocked_project_get,
        mocked_allow_or_raise,
        mocked_resources_for_project,
        mocked_get_client_by_user,
    ):
        """关键防御：IAM 校验必须使用 bk-sops 内部 ``project.id``，而不是用户传入的
        ``bk_biz_id``，否则攻击者只要在另一个绑定了同 ``bk_biz_id`` 的产品中拥有项目
        权限就能跨过本系统的项目隔离。"""
        project = mock.MagicMock(id=42)
        mocked_project_get.return_value = project
        mocked_resources_for_project.return_value = ["proj-42"]
        client = mock.MagicMock()
        client.job.get_job_instance_log.return_value = {"result": True, "data": "log"}
        mocked_get_client_by_user.return_value = client
        request = _build_request()

        response = api.get_job_instance_log(request, biz_cc_id="123")

        mocked_resources_for_project.assert_called_once_with(42)
        mocked_allow_or_raise.assert_called_once()
        kwargs = mocked_allow_or_raise.call_args[1]
        self.assertEqual(kwargs["system"], IAMMeta.SYSTEM_ID)
        self.assertEqual(kwargs["subject"].id, "tester")
        self.assertEqual(kwargs["action"].id, IAMMeta.PROJECT_VIEW_ACTION)
        self.assertEqual(kwargs["resources"], ["proj-42"])

        data = json.loads(response.content)
        self.assertTrue(data["result"])

    @mock.patch("gcloud.taskflow3.apis.django.api.get_client_by_user")
    @mock.patch("gcloud.taskflow3.apis.django.api.res_factory.resources_for_project")
    @mock.patch("gcloud.taskflow3.apis.django.api.allow_or_raise_auth_failed")
    @mock.patch("gcloud.taskflow3.apis.django.api.Project.objects.get")
    def test_iam_denied_short_circuits_before_calling_job(
        self,
        mocked_project_get,
        mocked_allow_or_raise,
        mocked_resources_for_project,
        mocked_get_client_by_user,
    ):
        """IAM 拒绝时必须直接抛错，不能继续调用 Job 平台 SDK，
        否则会产生借代用户向 Job 平台发请求的副作用。"""
        mocked_project_get.return_value = mock.MagicMock(id=42)
        mocked_resources_for_project.return_value = ["proj-42"]
        mocked_allow_or_raise.side_effect = RawAuthFailedException(permissions={})
        request = _build_request()

        with self.assertRaises(RawAuthFailedException):
            api.get_job_instance_log(request, biz_cc_id="123")

        mocked_get_client_by_user.assert_not_called()
