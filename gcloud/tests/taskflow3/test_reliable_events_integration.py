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
from django.test import TestCase, override_settings
from pipeline.contrib.reliable_events import collector
from pipeline.contrib.reliable_events.models import EngineEventInbox
from pipeline.eri.models import State
from pipeline.models import PipelineInstance

from gcloud.constants import PROJECT
from gcloud.core.models import Project
from gcloud.taskflow3.models import TaskConfig, TaskFlowInstance


class ReliableEventsWiringTestCase(TestCase):
    """
    Part B 验收测试：验证「settings 挂钩子 + 白名单配置 + 引擎 collector」三者组合后的实际落库模式。

    单元测试各自只覆盖一环（B1 挂路径、B2 存白名单、B3 解析模式），这里从引擎侧真实入口
    collector.record_callback_receipt 进入，断言写出的事件 mode 与白名单配置一致。
    """

    # PipelineInstance 的 post_save 挂着 pipeline.contrib.statistics 的统计任务，落库即 .delay() 投递 celery，
    # 而单测环境没有 broker，kombu 建连会一直重试把测试挂死。造数据不需要这些副作用，直接静默信号。
    @factory.django.mute_signals(signals.post_save)
    def setUp(self):
        self.node_id = "wiring_node_id"
        self.root_id = "wiring_root_id"
        self.version = "wiring_version"
        self.template_id = 77
        # collector 的建表探测结果会缓存在模块级变量里，测试库中表是存在的，这里重置避免受其他用例影响
        collector._INBOX_TABLE_AVAILABLE = None

        self.project = Project.objects.create(name="project_for_wiring", creator="tester", time_zone="Asia/Shanghai")
        State.objects.create(node_id=self.node_id, root_id=self.root_id, name="RUNNING", version=self.version)
        pipeline_instance = PipelineInstance.objects.create(
            instance_id=self.root_id, name="instance_for_wiring", creator="tester"
        )
        TaskFlowInstance.objects.create(
            project=self.project,
            pipeline_instance=pipeline_instance,
            template_id=str(self.template_id),
            template_source=PROJECT,
        )

    def _record(self, callback_data_id):
        return collector.record_callback_receipt(
            node_id=self.node_id, version=self.version, callback_data_id=callback_data_id, data={"state": "SUCCESS"}
        )

    def _whitelist(self, config_value):
        TaskConfig.objects.create(
            scope=TaskConfig.SCOPE_TYPE_TEMPLATE,
            scope_id=self.template_id,
            config_type=TaskConfig.CONFIG_TYPE_ACTIVE_CALLBACK,
            config_value=config_value,
        )

    @override_settings(PIPELINE_RELIABLE_EVENTS_SHADOW_ENABLED=True, PIPELINE_RELIABLE_EVENTS_ACTIVE_ENABLED=True)
    def test_whitelisted_template_records_active_event(self):
        self._whitelist(TaskConfig.ENABLE_ACTIVE_CALLBACK)

        self._record(callback_data_id=1001)

        event = EngineEventInbox.objects.get(node_id=self.node_id, version=self.version)
        self.assertEqual(event.mode, "ACTIVE")

    @override_settings(PIPELINE_RELIABLE_EVENTS_SHADOW_ENABLED=True, PIPELINE_RELIABLE_EVENTS_ACTIVE_ENABLED=True)
    def test_not_whitelisted_template_records_shadow_event(self):
        self._record(callback_data_id=1002)

        event = EngineEventInbox.objects.get(node_id=self.node_id, version=self.version)
        self.assertEqual(event.mode, "SHADOW")

    @override_settings(PIPELINE_RELIABLE_EVENTS_SHADOW_ENABLED=True, PIPELINE_RELIABLE_EVENTS_ACTIVE_ENABLED=False)
    def test_active_switch_off_downgrades_whitelisted_template_to_shadow(self):
        """全局开关是白名单之上的总闸：ACTIVE 关闭时，命中白名单也只能写 SHADOW"""
        self._whitelist(TaskConfig.ENABLE_ACTIVE_CALLBACK)

        self._record(callback_data_id=1003)

        event = EngineEventInbox.objects.get(node_id=self.node_id, version=self.version)
        self.assertEqual(event.mode, "SHADOW")

    def test_all_switches_off_records_nothing(self):
        """默认态（四个开关全关）必须零写入，这是本 PR「合入即零行为」的核心保证"""
        self._whitelist(TaskConfig.ENABLE_ACTIVE_CALLBACK)

        self.assertIsNone(self._record(callback_data_id=1004))
        self.assertEqual(EngineEventInbox.objects.count(), 0)
