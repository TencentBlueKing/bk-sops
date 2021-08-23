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

from gcloud import err_code
from gcloud.taskflow3.domains.dispatchers.task import TaskCommandDispatcher
from gcloud.taskflow3.domains.context import TaskContext

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class RenderCurrentConstantsV1TestCase(TestCase):
    def test_is_not_started(self):
        pipeline_instance = MagicMock()
        pipeline_instance.is_started = False

        dispatcher = TaskCommandDispatcher(
            engine_ver=1, taskflow_id=1, pipeline_instance=pipeline_instance, project_id=1
        )
        result = dispatcher.render_current_constants_v1()
        self.assertEqual(
            result,
            {"result": False, "data": None, "code": err_code.INVALID_OPERATION.code, "message": "task is not running"},
        )

    def test_is_finished(self):
        pipeline_instance = MagicMock()
        pipeline_instance.is_started = True
        pipeline_instance.is_finished = True

        dispatcher = TaskCommandDispatcher(
            engine_ver=1, taskflow_id=1, pipeline_instance=pipeline_instance, project_id=1
        )
        result = dispatcher.render_current_constants_v1()
        self.assertEqual(
            result,
            {"result": False, "data": None, "code": err_code.INVALID_OPERATION.code, "message": "task is not running"},
        )

    def test_is_revoked(self):
        pipeline_instance = MagicMock()
        pipeline_instance.is_started = True
        pipeline_instance.is_revoked = True

        dispatcher = TaskCommandDispatcher(
            engine_ver=1, taskflow_id=1, pipeline_instance=pipeline_instance, project_id=1
        )
        result = dispatcher.render_current_constants_v1()
        self.assertEqual(
            result,
            {"result": False, "data": None, "code": err_code.INVALID_OPERATION.code, "message": "task is not running"},
        )

    def test_normal(self):
        pipeline_instance = MagicMock()
        pipeline_instance.is_started = True
        pipeline_instance.is_finished = False
        pipeline_instance.is_revoked = False
        pipeline_instance.instance_id = "instance_id_token"
        pipeline_model = MagicMock()

        class TestTaskContext(TaskContext):
            def __init__(self):
                self.value = "TestTaskContext"

        class TestValueVar:
            def __init__(self, value):
                self.value = value

        var1 = TestTaskContext()

        var2 = MagicMock()
        var2.get = MagicMock(return_value="val2")

        var3 = TestValueVar("val3")

        var4 = MagicMock()
        var4.get = MagicMock(side_effect=Exception)

        pipeline_model.process.root_pipeline.context.variables = {
            "k1": var1,
            "k2": var2,
            "k3": var3,
            "k4": var4,
        }

        pipeline_model_cls = MagicMock()
        pipeline_model_cls.objects.get = MagicMock(return_value=pipeline_model)

        with mock.patch(TASKFLOW_DISPATCHERS_TASK_PIPELINE_MODEL, pipeline_model_cls):
            dispatcher = TaskCommandDispatcher(
                engine_ver=1, taskflow_id=1, pipeline_instance=pipeline_instance, project_id=1
            )
            result = dispatcher.render_current_constants_v1()

        pipeline_model_cls.objects.get.assert_called_once_with(id=pipeline_instance.instance_id)
        self.assertEqual(
            result,
            {
                "result": True,
                "data": [
                    {"key": "k1", "value": "TestTaskContext"},
                    {"key": "k2", "value": "val2"},
                    {"key": "k3", "value": "val3"},
                    {"key": "k4", "value": "[ERROR]value resolve error"},
                ],
                "code": err_code.SUCCESS.code,
                "message": "",
            },
        )
