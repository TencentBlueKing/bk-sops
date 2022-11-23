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
import json

from django.urls import reverse

from django_test_toolkit.data_generation.faker_generator import DjangoModelFakerFactory
from django_test_toolkit.testcases import ToolkitApiTestCase
from django_test_toolkit.mixins.account import SuperUserMixin
from django_test_toolkit.mixins.blueking import LoginExemptMixin, StandardResponseAssertionMixin
from django_test_toolkit.mixins.drf import DrfPermissionExemptMixin

from gcloud.periodictask.models import PeriodicTask
from gcloud.tests.periodictask.generate_model_data import GeneratePeriodicTaskTestData


# def customer_create_batch(size, kwargs):
#     for i in range(size + 1):
#         PeriodicTask.objects.create(**kwargs)
#     return PeriodicTask.objects.all()

class PeriodicTaskTestCase(
    ToolkitApiTestCase, SuperUserMixin, LoginExemptMixin, DrfPermissionExemptMixin, StandardResponseAssertionMixin,
):
    # DrfPermissionExemptMixin需要指定，用于豁免对应权限认证
    VIEWSET_PATH = "gcloud.core.apis.drf.viewsets.periodic_task.PeriodicTaskViewSet"
    INITIAL_CLOCKED_TASK_NUMBER = 10
    base_params = {}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        class PeriodicTaskFactory(DjangoModelFakerFactory):
            """
                工厂类外键关联属性定义说明，作用域要在测试用例类中。如果在该作用域外，使用的DB就不是测试数据库。
            """
            project, template, pipeline_tree = GeneratePeriodicTaskTestData().set_and_get_data()
            cron = {"minute": "*/5", "hour": "*", "day_of_week": "*", "day_of_month": "*", "month_of_year": "*"}
            name = "new20221115095047_周期执行"
            creator = "admin"
            template_source = "project"

            class Meta:
                model = PeriodicTask
        cls.periodic_tasks = PeriodicTaskFactory.create_batch(cls.INITIAL_CLOCKED_TASK_NUMBER)

        cls.base_params = {
            "project": PeriodicTaskFactory.project.id,
            "template_id": PeriodicTaskFactory.template.template_id,
            "pipeline_tree": json.dumps(PeriodicTaskFactory.pipeline_tree),
            "cron": PeriodicTaskFactory.cron,
            "name": PeriodicTaskFactory.name,
            "template_scheme_ids": []
        }

    @classmethod
    def tearDownClass(cls):
        GeneratePeriodicTaskTestData().destory_data()
        super().tearDownClass()

    def test_list_action_fetch_all_objects(self):
        url = reverse("periodic_task-list")
        response = self.client.get(url)
        self.assertStandardSuccessResponse(response)
        self.assertEqual(len(response.data["data"]), len(self.periodic_tasks))

    def test_create_periodic_task(self):
        data = json.dumps(self.base_params)
        url = reverse("periodic_task-list")
        response = self.client.post(url, data=data, content_type="application/json")
        self.assertStandardSuccessResponse(response)
        new_task = PeriodicTask.objects.filter(id=self.INITIAL_CLOCKED_TASK_NUMBER + 1).first()
        self.assertNotEqual(new_task, None)

    def test_partial_update_periodic_task(self):
        task_id = 1
        data = json.dumps({"name": "test_template"})
        url = reverse("periodic_task-detail", args=[task_id])
        response = self.client.patch(url, data=data, content_type="application/json")
        self.assertStandardSuccessResponse(response)
        modified_task = PeriodicTask.objects.get(id=task_id)
        self.assertEqual(modified_task.name, "test_template")

    def test_update_periodic_task(self):
        self.base_params["name"] = "XXXX"
        data = json.dumps(self.base_params)
        task_id = 1
        url = reverse("periodic_task-detail", args=[task_id])
        response = self.client.put(url, data=data, content_type="application/json")
        self.assertStandardSuccessResponse(response)
        modified_task = PeriodicTask.objects.get(id=task_id)
        self.assertEqual(modified_task.name, "XXXX")

    def test_destroy_periodic_task(self):
        task_id = 1
        url = reverse("periodic_task-detail", args=[task_id])
        response = self.client.delete(url, content_type="application/json")
        self.assertEqual(204, response.status_code)
        self.assertEqual(len(self.periodic_tasks) - 1, PeriodicTask.objects.count())
