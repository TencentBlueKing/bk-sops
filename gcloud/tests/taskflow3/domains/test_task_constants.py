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
import copy

from mock import MagicMock

from django.test import TestCase

from gcloud.core.models import EngineConfig
from gcloud.taskflow3.domains.task_constants import TaskConstantsHandler


class TaskConstantsHandlerTestCase(TestCase):
    def setUp(self):
        task = MagicMock()
        task.pipeline_instance = MagicMock()
        task.pipeline_instance.instance_id = 1
        self.task = task

    def test_get_all_constant_keys(self):
        handler = TaskConstantsHandler(self.task)
        contexts = [MagicMock() * 10]
        for i, context in enumerate(contexts):
            context.key = f"key_{i}"
        handler.runtime.get_context = MagicMock(return_value=contexts)
        result = handler.get_all_constant_keys()
        self.assertEqual(result, {f"key_{i}" for i in range(len(contexts))})

    def test_get_rendered_constant_keys_v1(self):
        v1_task = copy.deepcopy(self.task)
        v1_task.engine_ver = EngineConfig.ENGINE_VER_V1
        handler = TaskConstantsHandler(v1_task)
        self.assertRaises(NotImplementedError, handler.get_rendered_constant_keys)

    def test_get_rendered_constant_keys_v2(self):
        mock_data = MagicMock()
        mock_data.need_render_inputs = MagicMock(return_value={"bk_inputs": "${a+1}", "timing": "${b+2}"})

        v2_task = copy.deepcopy(self.task)
        v2_task.engine_ver = EngineConfig.ENGINE_VER_V2
        handler = TaskConstantsHandler(v2_task)
        handler.runtime.get_state_by_root = MagicMock(return_value=[])
        handler.runtime.get_batch_data = MagicMock(return_value={"node_1": mock_data})
        handler.runtime.get_context_key_references = MagicMock(return_value=set())
        result = handler.get_rendered_constant_keys()
        self.assertEqual(result, {"${a}", "${b}"})
