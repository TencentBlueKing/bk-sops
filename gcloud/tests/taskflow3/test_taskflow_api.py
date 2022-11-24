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

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tests.periodictask.generate_model_data import GenerateTaskFlowTestData


class TaskFlowTestCase(
    ToolkitApiTestCase, SuperUserMixin, LoginExemptMixin, DrfPermissionExemptMixin, StandardResponseAssertionMixin,
):
    # DrfPermissionExemptMixin需要指定，用于豁免对应权限认证
    VIEWSET_PATH = "gcloud.core.apis.drf.viewsets.taskflow.TaskFlowInstanceViewSet"
    INITIAL_CLOCKED_TASK_NUMBER = 10
    base_params = {}
    project_id = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        class TaskFlowFactory(DjangoModelFakerFactory):
            """
                工厂类外键关联属性定义说明，作用域要在测试用例类中。如果在该作用域外，使用的DB就不是测试数据库。
            """
            project, pipeline_instance = GenerateTaskFlowTestData().set_and_get_data()
            template_id = "1"
            create_info = "1"
            current_flow = "finished"

            cls.project_id = project.id

            cls.base_params = {
                "name": "new20221117113020_20221118185124",
                "description": "",
                "project": project.id,
                "template": pipeline_instance.template.id,
                "creator": "admin",
                "pipeline_tree": json.dumps(pipeline_instance.snapshot.data),
                "create_method": "app",
                "create_info": "0",
                "flow_type": "common",
                "template_source": "project"
            }

            class Meta:
                model = TaskFlowInstance

        cls.periodic_tasks = TaskFlowFactory.create_batch(cls.INITIAL_CLOCKED_TASK_NUMBER)

    @classmethod
    def tearDownClass(cls):
        GenerateTaskFlowTestData().destory_data()
        super().tearDownClass()

    def test_list_action_fetch_all_objects(self):
        url = reverse("taskflow-list")
        response = self.client.get(url)
        self.assertStandardSuccessResponse(response)
        self.assertEqual(len(response.data["data"]["results"]), len(self.periodic_tasks))

    def test_retrieve_taskflow(self):
        task_id = 1
        url = reverse("taskflow-detail", args=[task_id])
        response = self.client.get(url)
        self.assertStandardSuccessResponse(response)
        self.assertEqual(response.data["data"]["id"], task_id)

    def test_create_taskflow(self):
        data = json.dumps(self.base_params)
        url = reverse("taskflow-list")
        response = self.client.post(url, data=data, content_type="application/json")
        self.assertStandardSuccessResponse(response)
        new_task = TaskFlowInstance.objects.filter(id=self.INITIAL_CLOCKED_TASK_NUMBER + 1).first()
        self.assertNotEqual(new_task, None)

    def test_destroy_taskflow(self):
        task_id = 1
        url = reverse("taskflow-detail", args=[task_id])
        # 该接口response内容为b''
        self.client.delete(url, content_type="application/json")
        destroy_result = TaskFlowInstance.objects.filter(pk=task_id).first().is_deleted
        self.assertEqual(True, destroy_result)
