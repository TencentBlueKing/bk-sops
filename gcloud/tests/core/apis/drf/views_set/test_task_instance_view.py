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

import factory
from bamboo_engine import states
from django.db.models import signals
from django_test_toolkit.mixins.account import SuperUserMixin
from django_test_toolkit.mixins.blueking import (
    LoginExemptMixin,
    StandardResponseAssertionMixin,
)
from django_test_toolkit.mixins.drf import DrfPermissionExemptMixin
from django_test_toolkit.testcases import ToolkitApiTestCase
from pipeline.eri.models import State
from pipeline.models import PipelineInstance, PipelineTemplate, Snapshot

from gcloud.core.models import Project
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
        self.assertEqual(resp.data["message"], "最近30天有v1引擎的任务, 不支持筛选")

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
