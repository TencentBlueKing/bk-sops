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

from django.http import HttpResponse, HttpResponseForbidden

from gcloud.contrib.appmaker.decorators import check_db_object_exists
from gcloud.iam_auth import IAMMeta


class CheckDbObjectExistsTestCase(TestCase):
    @mock.patch("gcloud.contrib.appmaker.decorators.allow_or_raise_auth_failed")
    @mock.patch("gcloud.contrib.appmaker.decorators.res_factory.resources_for_mini_app_obj")
    @mock.patch("gcloud.contrib.appmaker.decorators.AppMaker")
    def test_check_app_maker__check_mini_app_permission(
        self,
        mocked_app_maker_model,
        mocked_resources_for_mini_app_obj,
        mocked_allow_or_raise_auth_failed,
    ):
        app_maker = SimpleNamespace(id=1, project_id=2, creator="tester", name="mini-app")
        request = SimpleNamespace(user=SimpleNamespace(username="tester"))
        mocked_app_maker_model.objects.filter.return_value.first.return_value = app_maker
        mocked_resources_for_mini_app_obj.return_value = ["mini-app-resource"]

        @check_db_object_exists("AppMaker", iam_action=IAMMeta.MINI_APP_VIEW_ACTION)
        def view_func(request, app_id, project_id):
            return HttpResponse("ok")

        response = view_func(request, app_id=1, project_id=2)

        self.assertEqual(response.status_code, 200)
        mocked_app_maker_model.objects.filter.assert_called_once_with(pk=1, project_id=2, is_deleted=False)
        mocked_resources_for_mini_app_obj.assert_called_once_with(app_maker)
        mocked_allow_or_raise_auth_failed.assert_called_once()
        self.assertEqual(mocked_allow_or_raise_auth_failed.call_args[1]["action"].id, IAMMeta.MINI_APP_VIEW_ACTION)

    @mock.patch("gcloud.contrib.appmaker.decorators.allow_or_raise_auth_failed")
    @mock.patch("gcloud.contrib.appmaker.decorators.AppMaker")
    def test_check_app_maker__forbidden_when_app_maker_not_exists(
        self,
        mocked_app_maker_model,
        mocked_allow_or_raise_auth_failed,
    ):
        request = SimpleNamespace(user=SimpleNamespace(username="tester"))
        mocked_app_maker_model.objects.filter.return_value.first.return_value = None
        view_func = mock.Mock(return_value=HttpResponse("ok"))

        response = check_db_object_exists("AppMaker", iam_action=IAMMeta.MINI_APP_VIEW_ACTION)(view_func)(
            request, app_id=1, project_id=2
        )

        self.assertIsInstance(response, HttpResponseForbidden)
        view_func.assert_not_called()
        mocked_allow_or_raise_auth_failed.assert_not_called()
