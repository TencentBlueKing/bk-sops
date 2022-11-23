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

from django.urls import reverse

from django_test_toolkit.data_generation.faker_generator import DjangoModelFakerFactory
from django_test_toolkit.testcases import ToolkitApiTestCase
from django_test_toolkit.mixins.account import SuperUserMixin
from django_test_toolkit.mixins.blueking import LoginExemptMixin, StandardResponseAssertionMixin
from django_test_toolkit.mixins.drf import DrfPermissionExemptMixin

from gcloud.contrib.function.models import FunctionTask
from gcloud.tests.periodictask.generate_model_data import GenerateFunctionTaskTestData


class FunctionTaskTestCase(
    ToolkitApiTestCase, SuperUserMixin, LoginExemptMixin, DrfPermissionExemptMixin, StandardResponseAssertionMixin,
):
    # DrfPermissionExemptMixin需要指定，用于豁免对应权限认证
    VIEWSET_PATH = "gcloud.core.apis.drf.viewsets.function_task.FunctionTaskViewSet"
    INITIAL_CLOCKED_TASK_NUMBER = 10
    base_params = {}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        class FunctionTaskFactory(DjangoModelFakerFactory):
            task = GenerateFunctionTaskTestData().set_and_get_data()
            creator = "admin"
            claimant = "admin"
            rejecter = "admin"
            predecessor = "admin"

            class Meta:
                model = FunctionTask

        cls.function_tasks = FunctionTaskFactory.create_batch(cls.INITIAL_CLOCKED_TASK_NUMBER)

    @classmethod
    def tearDownClass(cls):
        GenerateFunctionTaskTestData().destory_data()
        super().tearDownClass()

    def test_list_action_fetch_all_objects(self):
        url = reverse("function_task-list")
        response = self.client.get(url)
        self.assertStandardSuccessResponse(response)
        self.assertEqual(len(response.data["data"]["results"]), len(self.function_tasks))
