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
from bamboo_engine.states import FINISHED, RUNNING
from bamboo_engine.template import Template
from django.utils.translation import gettext_lazy as _
from pipeline.eri.runtime import BambooDjangoRuntime

from gcloud.core.models import EngineConfig


class TaskConstantsHandler:
    """
    进行任务参数相关操作
    """

    def __init__(self, task):
        self.task = task
        self.runtime = BambooDjangoRuntime()

    def get_all_constant_keys(self) -> set:
        return set([context.key for context in self.runtime.get_context(self.task.pipeline_instance.instance_id)])

    def get_rendered_constant_keys(self) -> set:
        if self.task.engine_ver != EngineConfig.ENGINE_VER_V2:
            raise NotImplementedError(_("非法操作: 仅支持 V2 版本的任务 | get_rendered_constant_keys"))
        return self._get_v2_task_rendered_constant_keys()

    def get_unused_constant_keys(self) -> set:
        return self.get_all_constant_keys() - self.get_rendered_constant_keys()

    def _get_v2_task_rendered_constant_keys(self) -> set:
        RENDERED_STATE_TYPES = {FINISHED, RUNNING}
        rendered_node_ids = [
            state.node_id
            for state in self.runtime.get_state_by_root(self.task.pipeline_instance.instance_id)
            if state.name in RENDERED_STATE_TYPES and state.skip is False
        ]
        batch_data = self.runtime.get_batch_data(rendered_node_ids).values()
        need_render_inputs = [data.need_render_inputs() for data in batch_data]
        inputs_refs = set(Template(need_render_inputs).get_reference())
        additional_refs = self.runtime.get_context_key_references(
            pipeline_id=self.task.pipeline_instance.instance_id, keys=inputs_refs
        )
        inputs_refs = inputs_refs.union(additional_refs)
        return inputs_refs
