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
import factory
from django.db.models import signals
from django.test import TestCase
from mock import MagicMock, patch
from pipeline.eri.models import State
from pipeline.models import PipelineInstance

from gcloud.constants import COMMON, PROJECT
from gcloud.core.models import Project
from gcloud.taskflow3.models import TaskConfig, TaskFlowInstance
from gcloud.taskflow3.reliable_events import ACTIVE, SHADOW, resolve_mode

TAKEOVER_PATH = "gcloud.taskflow3.reliable_events.TaskConfig.objects.enable_active_callback_takeover"


class ResolveModeTestCase(TestCase):
    """`resolve_mode` 的链路测试：State.root_id -> TaskFlowInstance -> TaskConfig 白名单"""

    def setUp(self):
        self.node_id = "node_id_token"
        self.root_id = "root_instance_id"
        self.version = "version_token"

    def _create_state(self, root_id=None):
        return State.objects.create(
            node_id=self.node_id,
            root_id=self.root_id if root_id is None else root_id,
            name="RUNNING",
            version=self.version,
        )

    # PipelineInstance 与 TaskFlowInstance 的 post_save 都会 .delay() 投递统计任务，单测环境没有 broker，
    # kombu 建连会无限重试把整轮测试挂死。造数据不需要这些副作用，所有写库都收在这里并静默信号。
    @factory.django.mute_signals(signals.post_save)
    def _create_taskflow(self, template_id="8", template_source=PROJECT, root_id=None, is_deleted=False):
        project = Project.objects.create(name="project_for_resolve_mode", creator="tester", time_zone="Asia/Shanghai")
        pipeline_instance = PipelineInstance.objects.create(
            instance_id=self.root_id if root_id is None else root_id,
            name="instance_for_resolve_mode",
            creator="tester",
        )
        taskflow = TaskFlowInstance.objects.create(
            project=project,
            pipeline_instance=pipeline_instance,
            template_id=template_id,
            template_source=template_source,
            is_deleted=is_deleted,
        )
        return project, taskflow

    def test_state_not_found__shadow(self):
        with patch(TAKEOVER_PATH, MagicMock(return_value=True)) as takeover:
            self.assertEqual(resolve_mode(self.node_id, self.version), SHADOW)
        takeover.assert_not_called()

    def test_state_root_id_empty__shadow(self):
        self._create_state(root_id="")
        with patch(TAKEOVER_PATH, MagicMock(return_value=True)) as takeover:
            self.assertEqual(resolve_mode(self.node_id, self.version), SHADOW)
        takeover.assert_not_called()

    def test_taskflow_not_found__shadow(self):
        self._create_state()
        with patch(TAKEOVER_PATH, MagicMock(return_value=True)) as takeover:
            self.assertEqual(resolve_mode(self.node_id, self.version), SHADOW)
        takeover.assert_not_called()

    def test_deleted_taskflow__shadow(self):
        self._create_state()
        self._create_taskflow(is_deleted=True)
        with patch(TAKEOVER_PATH, MagicMock(return_value=True)) as takeover:
            self.assertEqual(resolve_mode(self.node_id, self.version), SHADOW)
        takeover.assert_not_called()

    def test_project_template_in_whitelist__active(self):
        self._create_state()
        project, _ = self._create_taskflow(template_id="8", template_source=PROJECT)
        with patch(TAKEOVER_PATH, MagicMock(return_value=True)) as takeover:
            self.assertEqual(resolve_mode(self.node_id, self.version), ACTIVE)
        takeover.assert_called_once_with(project_id=project.id, template_id=8)

    def test_project_template_not_in_whitelist__shadow(self):
        self._create_state()
        project, _ = self._create_taskflow(template_id="8", template_source=PROJECT)
        with patch(TAKEOVER_PATH, MagicMock(return_value=False)) as takeover:
            self.assertEqual(resolve_mode(self.node_id, self.version), SHADOW)
        takeover.assert_called_once_with(project_id=project.id, template_id=8)

    def test_common_template__negative_template_id_and_real_project_id(self):
        """公共流程：template_id 取负（命中 scope_id=-template_id 的模板级配置），project_id 仍是真实项目 id"""
        self._create_state()
        project, _ = self._create_taskflow(template_id="8", template_source=COMMON)
        with patch(TAKEOVER_PATH, MagicMock(return_value=True)) as takeover:
            self.assertEqual(resolve_mode(self.node_id, self.version), ACTIVE)
        takeover.assert_called_once_with(project_id=project.id, template_id=-8)
        self.assertNotEqual(project.id, -1)

    def test_blank_template_id__shadow(self):
        self._create_state()
        self._create_taskflow(template_id="", template_source=PROJECT)
        with patch(TAKEOVER_PATH, MagicMock(return_value=True)) as takeover:
            self.assertEqual(resolve_mode(self.node_id, self.version), SHADOW)
        takeover.assert_not_called()

    def test_non_numeric_template_id__shadow(self):
        self._create_state()
        self._create_taskflow(template_id="not-a-number", template_source=PROJECT)
        with patch(TAKEOVER_PATH, MagicMock(return_value=True)) as takeover:
            self.assertEqual(resolve_mode(self.node_id, self.version), SHADOW)
        takeover.assert_not_called()

    def test_resolve_project_template_raise__shadow(self):
        with patch(
            "gcloud.taskflow3.reliable_events._resolve_project_template",
            MagicMock(side_effect=Exception("resolve error")),
        ):
            self.assertEqual(resolve_mode(self.node_id, self.version), SHADOW)

    def test_takeover_raise__shadow(self):
        self._create_state()
        self._create_taskflow(template_id="8", template_source=PROJECT)
        with patch(TAKEOVER_PATH, MagicMock(side_effect=Exception("db error"))):
            self.assertEqual(resolve_mode(self.node_id, self.version), SHADOW)


class ResolveModeIntegrationTestCase(TestCase):
    """不 mock 任何一层，真实创建 State / PipelineInstance / TaskFlowInstance / TaskConfig 走完整链路"""

    # 同上：PipelineInstance 落库触发的统计任务投递会在无 broker 环境挂死
    @factory.django.mute_signals(signals.post_save)
    def setUp(self):
        self.node_id = "integration_node_id"
        self.root_id = "integration_root_id"
        self.version = "integration_version"
        self.template_id = 66
        self.project = Project.objects.create(
            name="project_for_integration", creator="tester", time_zone="Asia/Shanghai"
        )
        State.objects.create(node_id=self.node_id, root_id=self.root_id, name="RUNNING", version=self.version)
        pipeline_instance = PipelineInstance.objects.create(
            instance_id=self.root_id, name="instance_for_integration", creator="tester"
        )
        self.pipeline_instance = pipeline_instance

    # TaskFlowInstance 的 post_save 也会 .delay() 投递统计任务，同样必须静默
    @factory.django.mute_signals(signals.post_save)
    def _create_taskflow(self, template_source):
        return TaskFlowInstance.objects.create(
            project=self.project,
            pipeline_instance=self.pipeline_instance,
            template_id=str(self.template_id),
            template_source=template_source,
        )

    def _create_config(self, scope, scope_id, config_value=TaskConfig.ENABLE_ACTIVE_CALLBACK):
        return TaskConfig.objects.create(
            scope=scope,
            scope_id=scope_id,
            config_type=TaskConfig.CONFIG_TYPE_ACTIVE_CALLBACK,
            config_value=config_value,
        )

    def test_project_template_config_hit__active(self):
        self._create_taskflow(PROJECT)
        self._create_config(TaskConfig.SCOPE_TYPE_TEMPLATE, self.template_id)
        self.assertEqual(resolve_mode(self.node_id, self.version), ACTIVE)

    def test_no_config__shadow(self):
        self._create_taskflow(PROJECT)
        self.assertEqual(resolve_mode(self.node_id, self.version), SHADOW)

    def test_common_template_config_hit_on_negative_scope_id__active(self):
        self._create_taskflow(COMMON)
        self._create_config(TaskConfig.SCOPE_TYPE_TEMPLATE, -self.template_id)
        self.assertEqual(resolve_mode(self.node_id, self.version), ACTIVE)

    def test_common_template_config_on_positive_scope_id__shadow(self):
        """公共流程的配置存在 +template_id 上时不应命中，证明负号约定确实生效"""
        self._create_taskflow(COMMON)
        self._create_config(TaskConfig.SCOPE_TYPE_TEMPLATE, self.template_id)
        self.assertEqual(resolve_mode(self.node_id, self.version), SHADOW)

    def test_common_template_fallback_to_real_project_config__active(self):
        """公共流程也能回落到「按真实项目整体开启」的项目级配置（传 project_id=-1 会废掉这条路径）"""
        self._create_taskflow(COMMON)
        self._create_config(TaskConfig.SCOPE_TYPE_PROJECT, self.project.id)
        self.assertEqual(resolve_mode(self.node_id, self.version), ACTIVE)

    def test_template_config_disable_overrides_project_config__shadow(self):
        self._create_taskflow(PROJECT)
        self._create_config(TaskConfig.SCOPE_TYPE_PROJECT, self.project.id)
        self._create_config(
            TaskConfig.SCOPE_TYPE_TEMPLATE, self.template_id, config_value=TaskConfig.DISABLE_ACTIVE_CALLBACK
        )
        self.assertEqual(resolve_mode(self.node_id, self.version), SHADOW)
