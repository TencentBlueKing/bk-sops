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
import datetime
import json
from unittest.mock import patch

import pytz
from django.conf import settings
from django.urls import reverse
from django_test_toolkit.data_generation.faker_generator import DjangoModelFakerFactory
from django_test_toolkit.mixins.account import SuperUserMixin
from django_test_toolkit.mixins.blueking import LoginExemptMixin, StandardResponseAssertionMixin
from django_test_toolkit.mixins.drf import DrfPermissionExemptMixin
from django_test_toolkit.testcases import ToolkitApiTestCase

from gcloud.clocked_task.models import ClockedTask
from gcloud.clocked_task.serializer import ClockedTaskSerializer
from gcloud.core.models import Project


class ClockedTaskFactory(DjangoModelFakerFactory):
    notify_receivers = "{}"
    notify_type = "[]"
    task_params = "{}"

    class Meta:
        model = ClockedTask


class ClockedTaskTestCase(
    ToolkitApiTestCase,
    SuperUserMixin,
    LoginExemptMixin,
    DrfPermissionExemptMixin,
    StandardResponseAssertionMixin,
):
    # DrfPermissionExemptMixin需要指定，用于豁免对应权限认证
    VIEWSET_PATH = "gcloud.clocked_task.viewset.ClockedTaskViewSet"
    INITIAL_CLOCKED_TASK_NUMBER = 10

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # 创建一个测试项目
        cls.test_project = Project.objects.create(
            name="test_project",
            bk_biz_id=1,
            from_cmdb=True,
        )
        # 创建定时任务时关联到这个项目
        cls.clocked_tasks = []
        for _ in range(cls.INITIAL_CLOCKED_TASK_NUMBER):
            clocked_task = ClockedTaskFactory.create(project_id=cls.test_project.id)
            cls.clocked_tasks.append(clocked_task)

    @classmethod
    def tearDownClass(cls):
        ClockedTask.objects.all().delete()
        if hasattr(cls, "test_project"):
            cls.test_project.delete()
        super().tearDownClass()

    @patch("django.conf.settings.ENABLE_MULTI_TENANT_MODE", False)
    def test_list_action_fetch_all_objects(self):
        url = reverse("clocked_task-list")
        response = self.client.get(url)
        self.assertStandardSuccessResponse(response)
        self.assertEqual(len(response.data["data"]), len(self.clocked_tasks))

    @patch("django.conf.settings.ENABLE_MULTI_TENANT_MODE", False)
    def test_retrieve_action_fetch_specific_object(self):
        test_clocked_task = self.clocked_tasks[0]
        url = reverse("clocked_task-detail", args=[test_clocked_task.id])
        response = self.client.get(url)
        self.assertStandardSuccessResponse(response)
        self.assertEqual(test_clocked_task.task_name, response.data["data"]["task_name"])

    @patch("django.conf.settings.ENABLE_MULTI_TENANT_MODE", False)
    def test_create_clocked_task(self):
        task_serialized_data = ClockedTaskSerializer(instance=self.clocked_tasks[0]).data
        task_serialized_data.pop("id")
        plan_start_time = datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) + datetime.timedelta(hours=1)
        task_serialized_data["plan_start_time"] = plan_start_time.strftime("%Y-%m-%d %H:%M:%S%z")
        task_serialized_data["task_parameters"] = {
            "constants": {},
            "template_schemes_id": [],
        }
        data = json.dumps(task_serialized_data)
        url = reverse("clocked_task-list")
        response = self.client.post(url, data=data, content_type="application/json")
        self.assertStandardSuccessResponse(response)
        new_task = ClockedTask.objects.filter(id=self.INITIAL_CLOCKED_TASK_NUMBER + 1).first()
        self.assertNotEqual(new_task, None)

    @patch("django.conf.settings.ENABLE_MULTI_TENANT_MODE", False)
    def test_create_clocked_task_with_multiple_appoint_method(self):
        task_serialized_data = ClockedTaskSerializer(instance=self.clocked_tasks[0]).data
        task_serialized_data.pop("id")
        plan_start_time = datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) + datetime.timedelta(hours=1)
        task_serialized_data["plan_start_time"] = plan_start_time.strftime("%Y-%m-%d %H:%M:%S%z")
        task_serialized_data["task_parameters"] = {
            "constants": {},
            "exclude_task_nodes_id": [],
            "template_schemes_id": [1],
            "appoint_task_nodes_id": ["node1"],
        }
        data = json.dumps(task_serialized_data)
        url = reverse("clocked_task-list")
        response = self.client.post(url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        res_data = json.loads(response.content)
        self.assertEqual(res_data["result"], False)

    @patch("django.conf.settings.ENABLE_MULTI_TENANT_MODE", False)
    def test_create_clocked_task_start_time_earlier_than_now(self):
        task_serialized_data = ClockedTaskSerializer(instance=self.clocked_tasks[0]).data
        task_serialized_data.pop("id")
        plan_start_time = datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) - datetime.timedelta(hours=1)
        task_serialized_data["plan_start_time"] = plan_start_time.strftime("%Y-%m-%d %H:%M:%S%z")
        data = json.dumps(task_serialized_data)
        url = reverse("clocked_task-list")
        response = self.client.post(url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        res_data = json.loads(response.content)
        self.assertEqual(res_data["result"], False)

    @patch("django.conf.settings.ENABLE_MULTI_TENANT_MODE", False)
    def test_update_clocked_task(self):
        task_id = 1
        data = json.dumps({"template_name": "test_template"})
        url = reverse("clocked_task-detail", args=[task_id])
        response = self.client.patch(url, data=data, content_type="application/json")
        self.assertStandardSuccessResponse(response)
        modified_task = ClockedTask.objects.get(id=task_id)
        self.assertEqual(modified_task.template_name, "test_template")
