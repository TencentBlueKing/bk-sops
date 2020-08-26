# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase

from gcloud.core.models import ProjectConfig


class ProjectConfigTestCase(TestCase):
    def test_task_executor_for_project(self):
        ProjectConfig.objects.create(project_id=1)
        ProjectConfig.objects.create(project_id=2, executor_proxy="proxy_1")
        ProjectConfig.objects.create(project_id=3, executor_proxy="proxy_2", executor_proxy_exempts="op1,op2")

        # 没有项目配置的情况
        self.assertEqual("tester", ProjectConfig.objects.task_executor_for_project(0, "tester"))
        # 没有配置执行者的情况
        self.assertEqual("tester", ProjectConfig.objects.task_executor_for_project(1, "tester"))
        # 配置了执行者的情况
        self.assertEqual("proxy_1", ProjectConfig.objects.task_executor_for_project(2, "tester"))
        self.assertEqual("proxy_1", ProjectConfig.objects.task_executor_for_project(2, "tester_1"))
        # 配置了执行代理豁免的情况
        self.assertEqual("op1", ProjectConfig.objects.task_executor_for_project(3, "op1"))
        self.assertEqual("op2", ProjectConfig.objects.task_executor_for_project(3, "op2"))
        self.assertEqual("proxy_2", ProjectConfig.objects.task_executor_for_project(3, "op3"))
