# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import datetime
from datetime import timedelta

import factory
from bamboo_engine import states
from django.conf import settings
from django.db.models import signals
from django_test_toolkit.mixins.account import SuperUserMixin
from django_test_toolkit.mixins.blueking import LoginExemptMixin, StandardResponseAssertionMixin
from django_test_toolkit.mixins.drf import DrfPermissionExemptMixin
from django_test_toolkit.testcases import ToolkitApiTestCase
from pipeline.eri.models import State
from pipeline.models import PipelineInstance, PipelineTemplate, Snapshot

from gcloud.core.models import Project, ProjectConfig
from gcloud.taskflow3.models import TaskFlowInstance


class TestTaskInstanceView(
    ToolkitApiTestCase,
    SuperUserMixin,
    LoginExemptMixin,
    DrfPermissionExemptMixin,
    StandardResponseAssertionMixin,
):
    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def setUp(self):
        super(TestTaskInstanceView, self).setUp()
        self.node_id = "node_id"
        self.root_id = "root_id"
        self.test_snapshot = Snapshot.objects.create_snapshot({})
        self.pipeline_template = PipelineTemplate.objects.create(
            template_id="template_id", creator="creator", snapshot=self.test_snapshot
        )
        self.pipeline_instance = PipelineInstance.objects.create(
            instance_id=self.root_id,
            creator="creator",
            snapshot=self.test_snapshot,
            template=self.pipeline_template,
            is_finished=False,
            is_started=True,
            is_revoked=False,
            start_time=datetime.datetime.now(),
        )
        self.test_project = Project.objects.create(
            name="proj",
            creator="creator",
        )

        self.task_url = "/api/v3/taskflow/"

        self.state = State.objects.create(
            node_id=self.node_id, root_id=self.root_id, name=states.RUNNING, version="version"
        )

        self.taskflow_instance = TaskFlowInstance.objects.create(
            project=self.test_project,
            pipeline_instance=self.pipeline_instance,
            template_id=self.pipeline_template.id,
            engine_ver=2,
        )

    def test_filter_failed_task_list(self):
        query_params = {
            "pipeline_instance__is_started": True,
            "pipeline_instance__is_finished": False,
            "pipeline_instance__is_revoked": False,
            "project__id": self.test_project.id,
            "task_instance_status": "failed",
        }

        self.taskflow_instance.engine_ver = 1
        self.taskflow_instance.save()

        resp = self.client.get(path=self.task_url, data=query_params)
        self.assertFalse(resp.data["result"])
        self.assertEqual(resp.data["message"], "最近180天有v1引擎的任务, 不支持筛选")

        self.taskflow_instance.engine_ver = 2
        self.taskflow_instance.save()

        resp = self.client.get(path=self.task_url, data=query_params)
        self.assertTrue(resp.data["result"])
        self.assertEqual(resp.data["data"]["count"], 0)

        self.state.name = states.FAILED
        self.state.save()

        resp = self.client.get(path=self.task_url, data=query_params)
        self.assertTrue(resp.data["result"])
        self.assertEqual(resp.data["data"]["count"], 1)

    def test_filter_pause_task_list(self):
        query_params = {
            "pipeline_instance__is_started": True,
            "pipeline_instance__is_finished": False,
            "pipeline_instance__is_revoked": False,
            "project__id": self.test_project.id,
            "task_instance_status": "pause",
        }

        resp = self.client.get(path=self.task_url, data=query_params)
        self.assertTrue(resp.data["result"])
        self.assertEqual(resp.data["data"]["count"], 0)

        self.state.node_id = self.root_id
        self.state.name = states.SUSPENDED
        self.state.save()

        resp = self.client.get(path=self.task_url, data=query_params)
        self.assertTrue(resp.data["result"])
        self.assertEqual(resp.data["data"]["count"], 1)

    def test_filter_running_task_list(self):
        query_params = {
            "pipeline_instance__is_started": True,
            "pipeline_instance__is_finished": False,
            "pipeline_instance__is_revoked": False,
            "project__id": self.test_project.id,
            "task_instance_status": "running",
        }

        resp = self.client.get(path=self.task_url, data=query_params)
        self.assertTrue(resp.data["result"])
        self.assertEqual(resp.data["data"]["count"], 1)

    def test_task_list_filter_days_disabled(self):
        """测试当项目配置了 task_list_filter_days 为 False 时，跳过日期过滤"""
        # 创建一个超过过滤天数的旧任务
        old_days = getattr(settings, "TASK_LIST_STATUS_FILTER_DAYS", 180) + 10
        old_create_time = datetime.datetime.now() - timedelta(days=old_days)
        old_start_time = datetime.datetime.now() - timedelta(days=old_days)

        old_root_id = "old_root_id"
        old_pipeline_instance = PipelineInstance.objects.create(
            instance_id=old_root_id,
            creator="creator",
            snapshot=self.test_snapshot,
            template=self.pipeline_template,
            is_finished=False,
            is_started=True,
            is_revoked=False,
        )
        # 更新创建时间和开始时间，使其超过过滤天数
        PipelineInstance.objects.filter(instance_id=old_root_id).update(
            create_time=old_create_time, start_time=old_start_time
        )
        old_pipeline_instance.refresh_from_db()

        old_taskflow_instance = TaskFlowInstance.objects.create(
            project=self.test_project,
            pipeline_instance=old_pipeline_instance,
            template_id=self.pipeline_template.id,
            engine_ver=2,
        )

        # 测试1: 没有配置 custom_display_configs 时，应该过滤掉旧任务
        query_params = {"project__id": self.test_project.id}
        resp = self.client.get(path=self.task_url, data=query_params)
        self.assertTrue(resp.data["result"])
        # 旧任务应该被过滤掉，只返回新任务
        task_ids = [task["id"] for task in resp.data["data"]["results"]]
        self.assertNotIn(old_taskflow_instance.id, task_ids)

        # 测试2: 配置了 task_list_filter_days 为 False 时，应该包含旧任务
        ProjectConfig.objects.create(
            project_id=self.test_project.id,
            custom_display_configs={"task_list_filter_days": False},
        )
        resp = self.client.get(path=self.task_url, data=query_params)
        self.assertTrue(resp.data["result"])
        # 旧任务应该被包含
        task_ids = [task["id"] for task in resp.data["data"]["results"]]
        self.assertIn(old_taskflow_instance.id, task_ids)

        # 测试3: 配置了 task_list_filter_days 为 True 时，应该过滤掉旧任务
        ProjectConfig.objects.filter(project_id=self.test_project.id).update(
            custom_display_configs={"task_list_filter_days": True}
        )
        resp = self.client.get(path=self.task_url, data=query_params)
        self.assertTrue(resp.data["result"])
        task_ids = [task["id"] for task in resp.data["data"]["results"]]
        self.assertNotIn(old_taskflow_instance.id, task_ids)

        # 测试4: 配置为空字典时，应该过滤掉旧任务
        ProjectConfig.objects.filter(project_id=self.test_project.id).update(custom_display_configs={})
        resp = self.client.get(path=self.task_url, data=query_params)
        self.assertTrue(resp.data["result"])
        task_ids = [task["id"] for task in resp.data["data"]["results"]]
        self.assertNotIn(old_taskflow_instance.id, task_ids)

    def test_task_list_filter_days_disabled_with_status(self):
        """测试当配置了 task_list_filter_days 为 False 且带 task_instance_status 参数时，跳过日期过滤"""
        # 创建一个超过过滤天数的旧任务
        old_days = getattr(settings, "TASK_LIST_STATUS_FILTER_DAYS", 180) + 10
        old_create_time = datetime.datetime.now() - timedelta(days=old_days)
        old_start_time = datetime.datetime.now() - timedelta(days=old_days)

        old_root_id = "old_root_id_for_status"
        old_pipeline_instance = PipelineInstance.objects.create(
            instance_id=old_root_id,
            creator="creator",
            snapshot=self.test_snapshot,
            template=self.pipeline_template,
            is_finished=False,
            is_started=True,
            is_revoked=False,
        )
        # 更新创建时间和开始时间，使其超过过滤天数
        PipelineInstance.objects.filter(instance_id=old_root_id).update(
            create_time=old_create_time, start_time=old_start_time
        )
        old_pipeline_instance.refresh_from_db()

        old_taskflow_instance = TaskFlowInstance.objects.create(
            project=self.test_project,
            pipeline_instance=old_pipeline_instance,
            template_id=self.pipeline_template.id,
            engine_ver=2,
        )

        # 为旧任务创建失败状态
        State.objects.create(node_id="old_node_id", root_id=old_root_id, name=states.FAILED, version="version")

        # 配置 task_list_filter_days 为 False
        ProjectConfig.objects.create(
            project_id=self.test_project.id,
            custom_display_configs={"task_list_filter_days": False},
        )

        # 测试带 task_instance_status 参数时，应该包含旧任务
        query_params = {
            "project__id": self.test_project.id,
            "task_instance_status": "failed",
        }
        resp = self.client.get(path=self.task_url, data=query_params)
        self.assertTrue(resp.data["result"])
        # 旧任务应该被包含
        task_ids = [task["id"] for task in resp.data["data"]["results"]]
        self.assertIn(old_taskflow_instance.id, task_ids)

        # 测试没有配置时，应该过滤掉旧任务
        ProjectConfig.objects.filter(project_id=self.test_project.id).delete()
        resp = self.client.get(path=self.task_url, data=query_params)
        self.assertTrue(resp.data["result"])
        task_ids = [task["id"] for task in resp.data["data"]["results"]]
        self.assertNotIn(old_taskflow_instance.id, task_ids)

    def test_task_list_filter_days_without_project_id(self):
        """测试没有 project__id 参数时，应该正常进行日期过滤"""
        # 创建一个超过过滤天数的旧任务
        old_days = getattr(settings, "TASK_LIST_STATUS_FILTER_DAYS", 180) + 10
        old_create_time = datetime.datetime.now() - timedelta(days=old_days)

        old_root_id = "old_root_id_no_project"
        old_pipeline_instance = PipelineInstance.objects.create(
            instance_id=old_root_id,
            creator="creator",
            snapshot=self.test_snapshot,
            template=self.pipeline_template,
            is_finished=False,
            is_started=True,
            is_revoked=False,
        )
        # 更新创建时间，使其超过过滤天数
        PipelineInstance.objects.filter(instance_id=old_root_id).update(create_time=old_create_time)
        old_pipeline_instance.refresh_from_db()

        old_taskflow_instance = TaskFlowInstance.objects.create(
            project=self.test_project,
            pipeline_instance=old_pipeline_instance,
            template_id=self.pipeline_template.id,
            engine_ver=2,
        )

        # 即使项目配置了 task_list_filter_days 为 False，但没有 project__id 参数时，应该过滤掉旧任务
        ProjectConfig.objects.create(
            project_id=self.test_project.id,
            custom_display_configs={"task_list_filter_days": False},
        )

        query_params = {}  # 没有 project__id
        resp = self.client.get(path=self.task_url, data=query_params)
        self.assertTrue(resp.data["result"])
        task_ids = [task["id"] for task in resp.data["data"]["results"]]
        # 应该过滤掉旧任务
        self.assertNotIn(old_taskflow_instance.id, task_ids)
