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

from gcloud.iam_auth.view_interceptors.apigw.create_template import CreateTemplateInterceptor


class CreateTemplateInterceptorTestCase(TestCase):
    @mock.patch("gcloud.iam_auth.view_interceptors.apigw.create_template.allow_or_raise_auth_failed")
    @mock.patch("gcloud.iam_auth.view_interceptors.apigw.create_template.res_factory.resources_for_project_obj")
    @mock.patch(
        "gcloud.iam_auth.view_interceptors.apigw.create_template.res_factory.resources_for_project",
        side_effect=AssertionError("resources_for_project should not be used here"),
    )
    def test_process__use_injected_project_for_scope_lookup(
        self,
        mocked_resources_for_project,
        mocked_resources_for_project_obj,
        mocked_allow_or_raise_auth_failed,
    ):
        interceptor = CreateTemplateInterceptor()
        request = SimpleNamespace(
            is_trust=False,
            user=SimpleNamespace(username="tester"),
            project=SimpleNamespace(id=42, name="project-for-biz-100605"),
        )
        mocked_resources_for_project_obj.return_value = ["project-resource"]

        interceptor.process(request, project_id="100605")

        mocked_resources_for_project_obj.assert_called_once_with(request.project)
        mocked_allow_or_raise_auth_failed.assert_called_once()
