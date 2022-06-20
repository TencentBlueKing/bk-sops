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

from django.test import TestCase

from gcloud.taskflow3.models import TaskFlowInstance

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class FunctionTaskClaimantTestCase(TestCase):
    # 如果任务流程类型不是职能化任务流程
    def test_not_common_func(self):
        taskflow = TaskFlowInstance()
        taskflow.flow_type = "common"
        self.assertEqual(taskflow.function_task_claimant, None)

    # 如果任务流程类型是职能化任务流程
    def test_common_func_get_claimant(self):
        _first = MagicMock(first=MagicMock(return_value="claimant"))

        _values_list = MagicMock(return_value=_first)

        _filter = MagicMock(values_list=_values_list)

        class FunctionTask:
            def __init__(self):
                self.filter = MagicMock(return_value=_filter)

        def _function_task(*args):
            return FunctionTask()

        def _mock_manager(*args):
            return _function_task

        def mock_manager(*args):
            return _mock_manager()

        with patch("django.db.models.fields.related_descriptors.create_reverse_many_to_one_manager", mock_manager):
            taskflow = TaskFlowInstance()
            taskflow.flow_type = "common_func"

            self.assertEqual(taskflow.function_task_claimant, "claimant")
