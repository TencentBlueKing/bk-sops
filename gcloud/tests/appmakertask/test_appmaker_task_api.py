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

from gcloud.contrib.appmaker.models import AppMaker
from gcloud.tests.periodictask.generate_model_data import GenerateAppMakerTestData


class AppMakerTaskTestCase(
    ToolkitApiTestCase, SuperUserMixin, LoginExemptMixin, DrfPermissionExemptMixin, StandardResponseAssertionMixin,
):
    # DrfPermissionExemptMixin需要指定，用于豁免对应权限认证
    VIEWSET_PATH = "gcloud.core.apis.drf.viewsets.appmaker.AppmakerListViewSet"
    INITIAL_CLOCKED_TASK_NUMBER = 10
    base_params = {}
    project_id = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        class AppMakerTaskFactory(DjangoModelFakerFactory):
            project, task_template = GenerateAppMakerTestData().set_and_get_data()
            cls.project_id = project.id
            name = "XXX"
            code = "XXX"
            link = ""
            creator = "admin"
            category = "Default"
            template_scheme_id = ""

            class Meta:
                model = AppMaker

        cls.appmaker_tasks = AppMakerTaskFactory.create_batch(cls.INITIAL_CLOCKED_TASK_NUMBER)
        cls.base_params = {
            "id": 0,
            "template_id": AppMakerTaskFactory.task_template.id,
            "category": "Default",
            "name": "new20221118162218"
        }

    @classmethod
    def tearDownClass(cls):
        GenerateAppMakerTestData().destory_data()
        super().tearDownClass()

    def test_list_action_fetch_all_objects(self):
        url = reverse("appmaker-list") + f"?project__id={self.project_id}"
        response = self.client.get(url)
        self.assertStandardSuccessResponse(response)
        self.assertEqual(len(response.data["data"]), len(self.appmaker_tasks))

    def test_retrieve_appmaker_task(self):
        task_id = 1
        url = reverse("appmaker-detail", args=[task_id])
        response = self.client.get(url)
        self.assertStandardSuccessResponse(response)
        appmaker = AppMaker.objects.get(pk=task_id)
        self.assertEqual(task_id, appmaker.id)

    def test_destroy_appmaker_task(self):
        task_id = 1
        url = reverse("appmaker-detail", args=[task_id])
        response = self.client.delete(url, content_type="application/json")
        self.assertEqual(204, response.status_code)
        destroy_status = AppMaker.objects.get(pk=task_id).is_deleted
        self.assertEqual(True, destroy_status)
