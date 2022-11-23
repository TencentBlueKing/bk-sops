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

from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tests.periodictask.generate_model_data import GenerateTemplateTestData


class TaskTemplateTestCase(
    ToolkitApiTestCase, SuperUserMixin, LoginExemptMixin, DrfPermissionExemptMixin, StandardResponseAssertionMixin,
):
    # DrfPermissionExemptMixin需要指定，用于豁免对应权限认证
    VIEWSET_PATH = "gcloud.core.apis.drf.viewsets.task_template.TaskTemplateViewSet"
    INITIAL_CLOCKED_TASK_NUMBER = 10
    base_params = {}
    project_id = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        class TaskTemplateFactory(DjangoModelFakerFactory):
            project, pipeline_template = GenerateTemplateTestData().set_and_get_data()
            cls.project_id = project.id
            category = "Default"
            default_flow_type = "common"
            notify_type = json.dumps(
                {
                    "success": [],
                    "fail": []
                }
            )

            class Meta:
                model = TaskTemplate

        cls.template_tasks = TaskTemplateFactory.create_batch(cls.INITIAL_CLOCKED_TASK_NUMBER)

        cls.base_params = {
            "name": "new20221118162218",
            "project": TaskTemplateFactory.project.id,
            "category": "Default",
            "default_flow_type": "common",
            "template_labels": [],
            "notify_type": {
                "success": [],
                "fail": []
            },
            "pipeline_tree": json.dumps(TaskTemplateFactory.pipeline_template.snapshot.data)
        }

    @classmethod
    def tearDownClass(cls):
        GenerateTemplateTestData().destroy_data()
        super().tearDownClass()

    def test_list_template_task(self):
        url = reverse("template-list")
        response = self.client.get(url)
        self.assertStandardSuccessResponse(response)
        self.assertEqual(len(response.data["data"]), len(self.template_tasks))

    def test_retrieve_template_task(self):
        test_template_task = self.template_tasks[0]
        url = reverse("template-detail", args=[test_template_task.id])
        response = self.client.get(url)
        self.assertStandardSuccessResponse(response)
        self.assertEqual(response.data["data"]["id"], test_template_task.id)

    def test_create_template_task(self):
        task_id = 11
        data = json.dumps(self.base_params)
        url = reverse("template-list")
        response = self.client.post(url, data=data, content_type="application/json")
        self.assertStandardSuccessResponse(response)
        new_task = TaskTemplate.objects.get(id=task_id).id
        self.assertEqual(new_task, task_id)

    def test_update_template_task(self):
        task_id = 10
        self.base_params["name"] = "XXXX"
        data = json.dumps(self.base_params)
        url = reverse("template-detail", args=[task_id])
        response = self.client.put(url, data=data, content_type="application/json")
        self.assertStandardSuccessResponse(response)
        modified_task = TaskTemplate.objects.get(id=task_id)
        self.assertEqual(modified_task.name, "XXXX")

    def test_destroy_template_task(self):
        task_id = 10
        url = reverse("template-detail", args=[task_id])
        response = self.client.delete(url, content_type="application/json")
        self.assertEqual(204, response.status_code)
        self.assertEqual(True, TaskTemplate.objects.get(pk=task_id).is_deleted)

    def test_list_with_top_collection(self):
        """
        路由处理需要优化
        @return:
        """
        url = reverse("template-list") + f'list_with_top_collection/?project__id={self.project_id}'
        response = self.client.get(url)
        self.assertStandardSuccessResponse(response)
        self.assertEqual(len(response.data["data"]), len(self.template_tasks))
