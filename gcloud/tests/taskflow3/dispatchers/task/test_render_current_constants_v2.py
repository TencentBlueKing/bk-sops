# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase

from bamboo_engine.eri.models import DataInput

from gcloud import err_code
from gcloud.taskflow3.domains.dispatchers.task import TaskCommandDispatcher, SystemObject

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class RenderCurrentConstantsV2TestCase(TestCase):
    def test_normal(self):
        pipeline_instance = MagicMock()
        pipeline_instance.instance_id = "instance_id_token"

        runtime = MagicMock()
        runtime.get_context = MagicMock(return_value="context_value_return")
        runtime.get_data_inputs = MagicMock(return_value={"root_key": DataInput(need_render=False, value="root_val")})

        context = MagicMock()
        context.hydrate = MagicMock(return_value={"k1": SystemObject({"system_key": "system_val"}), "k2": "val2"})

        runtime_cls = MagicMock(return_value=runtime)
        context_cls = MagicMock(return_value=context)

        with mock.patch(TASKFLOW_DISPATCHERS_TASK_BAMBOO_DJANGO_RUNTIME, runtime_cls):
            with mock.patch(TASKFLOW_DISPATCHERS_TASK_CONTEXT, context_cls):
                dispatcher = TaskCommandDispatcher(
                    engine_ver=2, taskflow_id=1, pipeline_instance=pipeline_instance, project_id=1
                )
                result = dispatcher.render_current_constants_v2()

        runtime.get_context.assert_called_once_with(pipeline_instance.instance_id)
        runtime.get_data_inputs.assert_called_once_with(pipeline_instance.instance_id)
        context_cls.assert_called_once_with(runtime, "context_value_return", {"root_key": "root_val"})
        context.hydrate.assert_called_once()

        self.assertEqual(
            result,
            {
                "result": True,
                "data": [{"key": "k1", "value": {"system_key": "system_val"}}, {"key": "k2", "value": "val2"}],
                "code": err_code.SUCCESS.code,
                "message": "",
            },
        )
