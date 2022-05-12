# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json

from django.urls import reverse

from django_test_toolkit.data_generation.faker_generator import DjangoModelFakerFactory
from django_test_toolkit.testcases import ToolkitApiTestCase
from django_test_toolkit.mixins.account import SuperUserMixin
from django_test_toolkit.mixins.blueking import LoginExemptMixin, StandardResponseAssertionMixin
from django_test_toolkit.mixins.drf import DrfPermissionExemptMixin
from gcloud.clocked_task.models import ClockedTask
from gcloud.clocked_task.serializer import ClockedTaskSerializer


class ClockedTaskFactory(DjangoModelFakerFactory):
    notify_receivers = "{}"
    notify_type = "[]"
    task_params = "{}"

    class Meta:
        model = ClockedTask


class ClockedTaskTestCase(
    ToolkitApiTestCase, SuperUserMixin, LoginExemptMixin, DrfPermissionExemptMixin, StandardResponseAssertionMixin,
):
    # DrfPermissionExemptMixin需要指定，用于豁免对应权限认证
    VIEWSET_PATH = "gcloud.clocked_task.viewset.ClockedTaskViewSet"
    INITIAL_CLOCKED_TASK_NUMBER = 10

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.clocked_tasks = ClockedTaskFactory.create_batch(cls.INITIAL_CLOCKED_TASK_NUMBER)

    @classmethod
    def tearDownClass(cls):
        ClockedTask.objects.all().delete()
        super().tearDownClass()

    def test_list_action_fetch_all_objects(self):
        url = reverse("clocked_task-list")
        response = self.client.get(url)
        self.assertStandardSuccessResponse(response)
        self.assertEqual(len(response.data["data"]), len(self.clocked_tasks))

    def test_retrieve_action_fetch_specific_object(self):
        test_clocked_task = self.clocked_tasks[0]
        url = reverse("clocked_task-detail", args=[test_clocked_task.id])
        response = self.client.get(url)
        self.assertStandardSuccessResponse(response)
        self.assertEqual(test_clocked_task.task_name, response.data["data"]["task_name"])

    def test_create_clocked_task(self):
        task_serialized_data = ClockedTaskSerializer(instance=self.clocked_tasks[0]).data
        task_serialized_data.pop("id")
        data = json.dumps(task_serialized_data)
        url = reverse("clocked_task-list")
        response = self.client.post(url, data=data, content_type="application/json")
        self.assertStandardSuccessResponse(response)
        new_task = ClockedTask.objects.filter(id=self.INITIAL_CLOCKED_TASK_NUMBER + 1).first()
        self.assertNotEqual(new_task, None)

    def test_update_clocked_task(self):
        task_id = 1
        data = json.dumps({"template_name": "test_template"})
        url = reverse("clocked_task-detail", args=[task_id])
        response = self.client.patch(url, data=data, content_type="application/json")
        self.assertStandardSuccessResponse(response)
        modified_task = ClockedTask.objects.get(id=task_id)
        self.assertEqual(modified_task.template_name, "test_template")
