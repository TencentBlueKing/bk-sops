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

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.periodictask.models import PeriodicTaskHistory
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa`

TASK_INSTANCE_GET_RETURN = 'TASK_INSTANCE_GET_RETURN'
PERIODIC_TASK_GET_RETURN = 'PERIODIC_TASK_GET_RETURN'


class PeriodicTaskHistoryTestCase(TestCase):

    @patch(TASKINSTANCE_GET, MagicMock(return_value=TASK_INSTANCE_GET_RETURN))
    @patch(PERIODIC_TASK_GET, MagicMock(return_value=PERIODIC_TASK_GET_RETURN))
    @patch(PERIODIC_TASK_HISTORY_CREATE, MagicMock())
    def test_record_history(self):
        periodic_task_history = MockPipelinePeriodicTaskHistory()
        PeriodicTaskHistory.objects.record_history(periodic_task_history)

        PeriodicTaskHistory.objects.create.assert_called_once_with(
            history=periodic_task_history,
            task=PERIODIC_TASK_GET_RETURN,
            flow_instance=TASK_INSTANCE_GET_RETURN,
            ex_data=periodic_task_history.ex_data,
            start_at=periodic_task_history.start_at,
            start_success=periodic_task_history.start_success
        )

    @patch(TASKINSTANCE_GET, MagicMock())
    @patch(PERIODIC_TASK_GET, MagicMock(return_value=PERIODIC_TASK_GET_RETURN))
    @patch(PERIODIC_TASK_HISTORY_CREATE, MagicMock())
    def test_record_history__start_success_is_false(self):
        periodic_task_history = MockPipelinePeriodicTaskHistory(start_success=False)
        PeriodicTaskHistory.objects.record_history(periodic_task_history)

        TaskFlowInstance.objects.get.assert_not_called()

        PeriodicTaskHistory.objects.create.assert_called_once_with(
            history=periodic_task_history,
            task=PERIODIC_TASK_GET_RETURN,
            flow_instance=None,
            ex_data=periodic_task_history.ex_data,
            start_at=periodic_task_history.start_at,
            start_success=periodic_task_history.start_success
        )

    @patch(TASKINSTANCE_GET, MagicMock(side_effect=TaskFlowInstance.DoesNotExist))
    @patch(PERIODIC_TASK_GET, MagicMock(return_value=PERIODIC_TASK_GET_RETURN))
    @patch(PERIODIC_TASK_HISTORY_CREATE, MagicMock())
    def test_record_history__taskflow_not_exist(self):
        periodic_task_history = MockPipelinePeriodicTaskHistory()
        PeriodicTaskHistory.objects.record_history(periodic_task_history)

        PeriodicTaskHistory.objects.create.assert_called_once_with(
            history=periodic_task_history,
            task=PERIODIC_TASK_GET_RETURN,
            flow_instance=None,
            ex_data=periodic_task_history.ex_data,
            start_at=periodic_task_history.start_at,
            start_success=periodic_task_history.start_success
        )
